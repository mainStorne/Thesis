docker service create --name registry --mount type=volume,src=registry-volume,destination=/var/lib/registry --publish published=5000,target=5000 registry:2
