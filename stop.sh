
docker stop authority
for i in $(seq 0 1); do
  docker stop provider-$i
done

for i in $(seq 0 5); do
  docker stop node-$i
done
