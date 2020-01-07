
docker service rm authority
for i in $(seq 0 1); do
  docker service rm provider-$i
done

for i in $(seq 0 5); do
  docker service rm node-$i
done
