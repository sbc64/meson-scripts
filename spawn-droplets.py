import digitalocean as do
import time
import sys
import click
import random

import pet_names
import do_slugs

# remember to
#export DIGITALOCEAN_ACCESS_TOKEN=''
manager = do.Manager()
nix_default="""#cloud-config
write_files:
- path: /etc/nixos/host.nix
  permissions: '0644'
  content: |
    {}
runcmd:
    - curl https://raw.githubusercontent.com/elitak/nixos-infect/master/nixos-infect | PROVIDER=digitalocean NIXOS_IMPORT=./host.nix NIX_CHANNEL=nixos-20.03 bash 2>&1 | tee /tmp/infect.log
"""

def create(name: str, ssh_keys: list, user_data: str, region:str,
    image:str, size_slug: str, tags:str,
):
    droplet = do.Droplet(
        name=name,
        region=region,
        image=image,
        size_slug=size_slug,
        ssh_keys=manager.get_all_sshkeys(),
        tags=tags,
        backups=False,
        monitoring=True,
        user_data=user_data,
    )
    droplet.create()
    print("Created droplet:", droplet.name, droplet.ip_address)

def destroy_tag(tag):
    droplets = manager.get_all_droplets(tag_name=tag)
    for droplet in droplets:
        if "monitoring" != droplet.name:
            droplet.destroy()
            print("Destroyed: ", droplet.name)

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

@click.command()
@click.option('--count', default=1)
@click.option('--organization', '--org', default="")
@click.option('--name', default="random")
@click.option('--tags', required=True)
@click.option('--remove', '-r', 'remove', flag_value=True, default=False)
@click.option(
    '--size-slug',
    '--size',
    default='s-1vcpu-1gb',
    type=click.Choice(do_slugs.sizes, case_sensitive=False)
)
@click.option(
    '--region',
    default=random.choice(do_slugs.locations),
    type=click.Choice(do_slugs.locations, case_sensitive=True)
)
@click.option(
    '--image',
    default='ubuntu-16-04-x64',
    type=click.Choice(do_slugs.images, case_sensitive=False)
)
@click.option(
    '--nix-path',
    default="./nix_configs/default.nix",
    help="File path containing a nix expression",
)
def main(count, organization, name, tags, remove,
    size_slug, region, image, nix_path,
):

    ssh_keys = manager.get_all_sshkeys()

    with open(nix_path, 'r') as f:
        user_data = nix_default.format("    ".join(f.readlines()))

    if remove: destroy_tag(tags)
    else:
        for i in range(count):
            # These values are random so we need to check
            tempName=name
            if name == "random":
                tempName=pet_names.random_person()
            tempRegion=region
            if region == "random":
                tempRegion=random.choice(do_slugs.locations)

            create(
                tempName,
                ssh_keys=ssh_keys,
                image=image,
                user_data = user_data,
                size_slug=size_slug,
                tags=tags,
                region=tempRegion,
            )

    print("Rate limit remaining: ", manager.ratelimit_remaining)

if __name__ == '__main__':
    main()
