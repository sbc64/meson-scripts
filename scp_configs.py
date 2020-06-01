from typing import List
from subprocess import run, check_output, PIPE, STDOUT
from os import mkdir, path, listdir
import fileinput

from utils import readSSH, generate_service, get_public_key



def scp(confDir, hosts):
    del hosts["monitoring"]
    for host in hosts.keys():
        print("COPYING to ", host)
        args="ssh -F ssh_config {host} 'rm -rf /root/config'".format(host=host)
        run(args, shell=True)
        dirName= "nonvoting" if host == "auth" else host
        args="scp -F ssh_config -r {confDir}/{dirName} {host}:config".format(
                confDir=confDir,
                host=host,
                dirName=dirName
                )
        run(args, shell=True)

def main():
    scp("mixnet_conf", readSSH())

if __name__ == "__main__":
    main()
