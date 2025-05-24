#!/bin/bash
docker service create --name registry --publish published=5000,target=5000 registry:2
dokcer compose -f dokcer-compose.prod.yaml build agent
dokcer compose -f dokcer-compose.prod.yaml push agent
dokcer stack deploy -c dokcer-compose.prod.yaml thesis
