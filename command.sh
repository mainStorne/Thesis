
docker service create -l sablier.enable=true -l traefik.docker.lbswarm=true -l traefik.enable=true -l traefik.http.routers.whoami.middlewares=7isp@file -l traefik.http.routers.whoami.rule='PathPrefix(`/whoami`)' -l traefik.http.services.whoami.loadbalancer.server.port=80 --name whoami --network dev_default testcase1
