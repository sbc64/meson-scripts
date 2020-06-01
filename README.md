# Scripts that are used to spawn a new mixnet

WARNING: Scripts are very ugly and hacky.

I hope to make something more usable in the future with Nixops.

Steps:
- spawn-droplets.py
- ansible-playbook -i hosts/hashcloak playbooks/all-roles.yml --ask-become-pass --tags docker,common
- testnet.py
- start-monitoring.py
- scp_configs.py
- start_testnet.sh
