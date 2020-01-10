#!/usr/bin/env bash
docker service create --name authority -d \
  -p 30000:30000 \
  --mount type=bind,source=$HOME/configs/nonvoting,destination=/conf \
  hashcloak/katzenpost-auth:1c00188

for i in $(seq 0 1); do
  port=$(($i+1))
  docker service create --name provider-$i -d \
    -p 3000$port:3000$port \
    -p 4000$port:4000$port \
    --mount type=bind,source=$HOME/configs/provider-$i,destination=/conf \
    hashcloak/meson:master

done

for i in $(seq 0 5); do
  echo "PORT $port"
  port=$(($i+3))
  docker service create --name node-$i -d \
    -p 3000$port:3000$port \
    --mount type=bind,source=$HOME/configs/node-$i,destination=/conf \
    hashcloak/meson:master
done
