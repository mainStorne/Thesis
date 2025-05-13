FROM httpd
LABEL traefik.http.routers.httpd.rule=PathPrefix(`/httpd`)
LABEL sablier.enable=true
LABEL traefik.http.routers.httpd.middlewares=7isp@file
LABEL sablier.group=7isp
