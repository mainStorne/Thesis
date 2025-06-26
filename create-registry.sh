docker service create --name registry --mount type=volume,src=registry-volume,destination=/var/lib/registry --publish published=5000,target=5000 registry:2
docker pull mysql
docker tag mysql 127.0.0.1:5000/mysql
docker push 127.0.0.1:5000/mysql
