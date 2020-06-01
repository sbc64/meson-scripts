#!/usr/bin/env bash

hosts=$(grep Host\  ssh_config| grep -v monitoring | cut -f2 -d' ')

for h in $hosts; do
  echo "$h"
  ssh -F ssh_config $h 'docker stack rm mixnet'
done

for h in $hosts; do
  echo "$h"
	ssh -F ssh_config $h 'while [ -n "`docker network ls --quiet --filter label=com.docker.stack.namespace=mixnet`" ]; do echo -n '.' && sleep 1; done'
done

for h in $hosts; do
  echo "$h"
  ssh -F ssh_config $h 'docker stack deploy mixnet -c /root/config/container.yml'
done
