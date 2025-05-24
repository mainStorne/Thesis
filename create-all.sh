#!/bin/bash
docker service create --name registry --publish published=5000,target=5000 registry:2
docker compose -f docker-compose.prod.yaml build agent web
docker compose -f docker-compose.prod.yaml push agent web
docker stack deploy -c docker-compose.prod.yaml thesis
