from subprocess import run, check_output, PIPE, STDOUT
from os import mkdir, path, listdir
from typing import List
import fileinput

from utils import (
        readSSH,
        generate_service,
        get_public_key,
        get_mixnet_port,
        get_user_registration_port,
        get_data_dir
    )

clientTomlTemplate = """
[Logging]
  Disable = false
  Level = "DEBUG"
  File = ""

[UpstreamProxy]
  Type = "none"

[Debug]
  DisableDecoyTraffic = {}
  CaseSensitiveUserIdentifiers = false
  PollingInterval = 1

[NonvotingAuthority]
    Address = "{}:{}"
    PublicKey = "{}"
"""


def write_service(name: str, compose: str) -> None:
    with open("mixnet_conf/"+name+"/container.yml", "w") as f:
        f.write('version: "3.7"\nservices:\n'+compose)

def generate_mixnet_config(ip: str, confDir: str) -> List[str]:
    mkdir(confDir)
    output = run([
        "genconfig",
        "-o",
        confDir,
        "-a",
        ip,
    ], stdout=PIPE, stderr=STDOUT)
    return [p.split(" ")[-1] for p in output.stdout.decode().strip().split("\n")]

def update_auth_ip(confPath, oldIp, hosts):
    for key, newIp in hosts.items():
        f = path.join(confPath, key, "katzenpost.toml")
        for line in fileinput.input(f, inplace=True):
            if oldIp in line and "30000" not in line:
                line = line.replace(oldIp, newIp)
            print('{}'.format(line), end='')

def generate_containers_yaml(confDir):
    hosts = readSSH()
    del hosts["monitoring"]
    for host in hosts.keys():
        toml = path.join(confDir, host, "katzenpost.toml")
        name=host
        containerPath=host
        image="hashcloak/meson:master"

        if host == "auth":
            name="auth"
            containerPath="nonvoting"
            toml = path.join(confDir, "nonvoting", "authority.toml")
            image = "hashcloak/authority:master"

        ports = [
            "{0}:{0}".format(get_mixnet_port(toml)),
            "{0}:{0}".format("6543"),
        ]
        if get_user_registration_port(toml):
            ports.append("{0}:{0}".format(get_user_registration_port(toml)))

        write_service(containerPath, generate_service(
            image=image,
            name=host,
            ports=ports,
            volumes=[
                "{}:{}".format("/root/config", get_data_dir(toml))
            ]
        ))


def main():
    confDir = "mixnet_conf"
    if not path.exists(confDir):
        print(generate_mixnet_config(readSSH()["auth"], confDir))

    hosts = readSSH()
    oldIp = hosts["auth"]
    del hosts["auth"]
    del hosts["monitoring"]
    update_auth_ip(confDir, oldIp, hosts)

    generate_containers_yaml(confDir)

    
    with open("client.toml", 'w') as f:
        f.write(clientTomlTemplate.format(
            "true",
            readSSH()["auth"],
            get_mixnet_port(path.join(confDir, "nonvoting", "authority.toml")),
            get_public_key("mixnet_conf/nonvoting")
        ))


if __name__ == "__main__":
    main()
