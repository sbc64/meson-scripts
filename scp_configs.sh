#!/usr/bin/env bash


genconfig -a 159.65.210.250

hosts=$(grep Host\  ssh_config| grep -v monitoring | grep -v auth | cut -f2 -d' ')

scp -F ssh_config \
  -o StrictHostKeyChecking=no \
  -r output/nonvoting auth:config

for h in $hosts; do
  scp -F ssh_config \
    -o StrictHostKeyChecking=no \
    -r output/$h $h:config
done
