from typing import List
from subprocess import run, check_output, PIPE, STDOUT
from os import mkdir, path, listdir
import fileinput

from utils import readSSH, generate_service, get_public_key



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
            print('{} {}'.format(fileinput.filelineno(), line), end='')

def scp(confDir, hosts):
    del hosts["monitoring"]

    for host in hosts.keys():
        args="ssh -F ssh_config {host} 'rm -rf /root/config'".format(host=host)
        run(args, shell=True)
        args="scp -F ssh_config -r {confDir}/{host} {host}:config".format(
                confDir=confDir,
                host=host
                )
    run(args, shell=True)

def main():
    hosts = readSSH()
    del hosts["monitoring"]
    confDir = "mixnet_conf"
    if not path.exists(confDir):
        print(generate_mixnet_config(hosts["auth"], confDir))

    oldIp = hosts["auth"]
    del hosts["auth"]
    update_auth_ip(confDir, oldIp, hosts)

    scp(confDir, readSSH())

if __name__ == "__main__":
    main()
