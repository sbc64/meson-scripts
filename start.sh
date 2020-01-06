#!/usr/bin/env bash
docker run --name authority --rm -d -p 30000:30000 -v ~/configs/nonvoting:/conf hashcloak/katzenpost-auth:master

for i in $(seq 0 1); do
  port=$(($i+1))

  echo "PORT $port"
  docker run --name provider-$i --rm -d \
    -p 3000$port:3000$port \
    -p 4000$port:4000$port \
    -v ~/configs/provider-$i:/conf hashcloak/meson:master

done

for i in $(seq 0 5); do
  echo $i
  port=$(($i + 3))
  echo "PORT $port"
  docker run --name node-$i --rm -d -p 3000$port:3000$port -v ~/configs/node-$i:/conf hashcloak/meson:master
done
