import digitalocean as do
import argparse
import time

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
    "mix-0",
    "mix-1",
    "mix-2",
    "mix-3",
    "mix-4",
    "mix-5",
]
names.extend(floatinIps.keys())

def create():
    for name in names:
        droplet = do.Droplet(
                            name=name,
                            region='lon1',
                            image='debian-10-x64',
                            size_slug='s-1vcpu-1gb',
                            ssh_keys=manager.get_all_sshkeys(),
                            tags=tag,
                            backups=False,
                            monitoring=True,
                        )
        droplet.create()
        print("Created droplet:", droplet.name)

def remove():
    droplets = manager.get_all_droplets(tag_name=tag)
    for droplet in droplets:
        droplet.destroy()

def saveIps():
    droplets = manager.get_all_droplets(tag_name=tag)
    with open('hosts/hashcloak', 'w+') as f:
        f.write("[mixnet]\n")
        for droplet in droplets:
            f.write(droplet.ip_address+" ansible_user=root ansible_ssh_private_key_file=~/.ssh/hashcloak ansible_python_interpreter=/usr/bin/python3\n")

    print("Saved ips for droplets")


def dropletsReady(droplets):
    print("Waiting for droplets to be ready", end='')
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
    my_list = [x for x in droplets if x.name in floatinIps.keys()]
    for droplet in my_list: 
        flip = do.FloatingIP(ip=floatinIps[droplet.name])
        flip.assign(droplet.id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("-r", "--remove", action='store_true')
    parser.add_argument("-s", "--save", action='store_false')
    args = parser.parse_args()
    if args.remove:
        remove()
    else:
        create()
        droplets = manager.get_all_droplets(tag_name=tag)
        dropletsReady(droplets)
        assignFloatings(droplets)
        saveIps()

    print("Rate limit remaining: ", manager.ratelimit_remaining)
