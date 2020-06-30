import digitalocean as do
import argparse
import time

nix="""#cloud-config
write_files:
- path: /etc/nixos/host.nix
  permissions: '0644'
  content: |
    {pkgs, ...}:
    {
      environment.systemPackages = with pkgs; [ vim ];
    }
runcmd:
  - curl https://raw.githubusercontent.com/elitak/nixos-infect/master/nixos-infect | NIXOS_IMPORT=./host.nix NIX_CHANNEL=nixos-20.03 bash 2>&1 | tee /tmp/infect.log
  """

# remember to
#export DIGITALOCEAN_ACCESS_TOKEN=''
manager = do.Manager()
tag="mixnet"
floatinIps = {
        "auth": "159.65.210.250",
        "monitoring": "157.245.28.48"
    }
names = [
    "provider-0",
    "provider-1",
    "node-0",
    "node-1",
    "node-2",
    "node-3",
    "node-4",
    "node-5",
]
names.extend(floatinIps.keys())

def create(
    name,
    ssh_keys=[],
    user_data="",
    region="lon1",
    image="ubuntu-16-04-x64",
    size_slug='s-1vcpu-1gb',
    tags="mixnet",
):
    print(ssh_keys)
    # Avoid duplicates with the set substraction
    droplet = do.Droplet(
        name=name,
        region=region,
        image=image,
        size_slug=size_slug,
        ssh_keys=manager.get_all_sshkeys(),
        tags=tag,
        backups=False,
        monitoring=True,
        user_data=user_data,
    )
    droplet.create()
    print("Created droplet:", droplet.name, droplet.ip_address)

def remove():
    droplets = manager.get_all_droplets(tag_name=tag)
    for droplet in droplets:
        if "monitoring" != droplet.name:
            droplet.destroy()
            print("Destroyed: ", droplet.name)

def generateSSHConfig():
    droplets = manager.get_all_droplets(tag_name=tag)
    with open('ssh_config', 'w+') as f:
        for droplet in droplets:
            f.write("Host {}\n".format(droplet.name))
            f.write("\tHostname {}\n".format(droplet.ip_address))
            f.write("\tUser root\n")
            f.write("\tIdentityFile ~/.ssh/hashcloak\n")
            f.write("\tStrictHostKeyChecking no\n")
            f.write("\tServerAliveInterval 60\n")
            f.write("\tUserKnownHostsFile /dev/null\n")
            f.write("\n")

    print("Generated ssh_config")

def saveIps():
    droplets = manager.get_all_droplets(tag_name=tag)
    with open('hosts/hashcloak', 'w+') as f:
        f.write("[mixnet]\n")
        for droplet in droplets:
            f.write(droplet.ip_address+" ansible_user=root ansible_ssh_private_key_file=~/.ssh/hashcloak ansible_python_interpreter=/usr/bin/python3\n")

    print("saved ips for droplets")


def dropletsReady(droplets):
    print("Waiting for droplets to be ready")
    for droplet in droplets:
        while True:
            action = droplet.get_actions()[0]
            if action.status == "completed":
                print("Droplet {} completed".format(droplet.name))
                break
            print(".", end='')
            time.sleep(10)

    return True

def assignFloatings(droplets):
    for droplet in [x for x in droplets if x.name in floatinIps.keys()]:
        flip = do.FloatingIP(ip=floatinIps[droplet.name])
        try:
            flip.assign(droplet.id)
            print("Asiggned {} to {}".format(flip.ip, droplet.name))
        except do.DataReadError as e:
            print(e)
            print("Continuing")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-r", "--remove", action='store_true')
    parser.add_argument("-s", "--save", action='store_false')
    parser.add_argument("-o", "--one", action='store_true')
    args = parser.parse_args()

    ssh_keys = manager.get_all_sshkeys(),
    if args.remove:
        remove()
    elif args.save and not args.one:
        droplets = manager.get_all_droplets(tag_name=tag)
        for name in list(set(names)-set([d.name for d in droplets])):
            create(name, image='debian-10-x64', ssh_keys=ssh_keys)

        dropletsReady(droplets)
        assignFloatings(droplets)
        saveIps()
        generateSSHConfig()
    elif args.one:
        print(ssh_keys)
        create("nixos", ssh_keys=ssh_keys, user_data=nix)

    print("Rate limit remaining: ", manager.ratelimit_remaining)
