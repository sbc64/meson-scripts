from typing import List
from os import path
from collections import defaultdict

def readSSH():
    host = defaultdict(str)
    temp=[]
    with open('ssh_config', 'r') as f:
        for line in f:
            if "Host" in line and "StrictHostKeyChecking" not in line and "UserKnownHosts" not in line:
                temp.append(line)

    for index in range(0, len(temp), 2):
        host[temp[index].split(' ')[-1].strip()] = temp[index+1].split(' ')[-1].strip()

    return host 

def check_docker_is_installed() -> None:
    try:
        check_output(["docker", "info"])
    except:
        print("Docker not found. Please install docker")
        sys.exit(1)

def get_public_key(dirPath: str) -> str:
    """Gets the public key from identity.public.pem file in given directory"""
    with open(path.join(dirPath, "identity.public.pem"), 'r') as f:
        return f.read().split("\n")[1] # line index 1


def get_mixnet_port(path: str) -> str:
    """Gets mixnet port number from a given katzenpost.toml file"""
    with open(path, 'r') as f:
        for line in f:
            if "Addresses = [" in line:
                return line.split('"')[1].split(":")[1]

def get_user_registration_port(path: str) -> str:
    """Gets the user registration port from a given katzenpost.toml file"""
    with open(path, 'r') as f:
        for line in f:
            if "UserRegistrationHTTPAddresses" in line:
                return line.split('"')[1].split(":")[1]

def get_data_dir(path: str) -> str:
    """Gets the config directory path from the given config file"""
    with open(path, 'r') as f:
        for line in f:
            if "DataDir =" in line:
                return line.split('=')[-1].replace('"', '').strip()

def checkout_repo(repoPath: str, repoUrl: str, commitOrBranch: str) -> None:
    """Clones, and git checkouts a repository given a path, repo url and a commit or branch"""
    output = run(["git", "clone", repoUrl, repoPath], stdout=PIPE, stderr=STDOUT)
    safeError = 'already exists and is not an empty directory' in output.stdout.decode()
    log(output.stdout.decode().strip(), not safeError)
    if safeError:
        log("Ignoring last error, continuing...")

    run(["git", "fetch"], check=True, cwd=repoPath)
    run(["git", "reset", "--hard"], check=True, cwd=repoPath)
    run(["git", "-c", "advice.detachedHead=false", "checkout", commitOrBranch], check=True, cwd=repoPath)

def generate_service(
    name: str,
    image: str,
    ports: List[str] = [],
    volumes: List[str] = [],
    dependsOn: List[str] = [],
) -> str:
    """
    Creates a string with docker compose service specification.
    Arguments are a list of values that need to be added to each section
    named after the parameter. i.e. the volume arguments are for the
    volumes section of the service config.
    """
    indent = '  '
    service = "{s}{name}:\n{s}{s}image: {image}\n".format(
        s=indent,
        name=name,
        image=image,
    )

    if ports:
        service += "{s}ports:\n".format(s=indent*2)
        for port in ports:
            service += '{s}- "{port}"\n'.format(s=indent*3, port=port)

    if volumes:
        service += "{s}volumes:\n".format(s=indent*2)
        for vol in volumes:
            service += '{s}- {vol}\n'.format(s=indent*3, vol=vol)

    if dependsOn:
        service += "{s}depends_on:\n".format(s=indent*2)
        for item in dependsOn:
            service += '{s}- "{dep}"\n'.format(s=indent*3, dep=item)

    return service
