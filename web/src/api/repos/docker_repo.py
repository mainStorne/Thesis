from io import BytesIO

from aiodocker import Docker


class DockerRepo:
    def __init__(self):
        self._docker_client = None

    async def init(self):
        self._docker_client = Docker()

    async def get_nodes_ip(self):
        # self._docker_client.services.list(filters={'id'})
        for node in await self._docker_client.nodes.list():
            node_status = node["Status"]
            yield node_status["Addr"]

    async def push_to_registry(self, ):
        await self._docker_client.images.push(
            '127.0.0.1:5000'
        )

    async def create_service(self, ):
        # docker service create -l traefik.enable=true -l traefik.http.routers.whoami.rule='PathPrefix(`/whoami`)' -l traefik.http.services.whoami.loadbalancer.server.port=80 --name whoami --network dev_default testcase1
        pass

    async def build(self, buffer: BytesIO, tag: str):
        image = await self._docker_client.images.build(
            fileobj=buffer, encoding="gzip", path_dockerfile="Dockerfile", tag=tag
        )
        # image = await self._docker_client.images.push(
        # fileobj=buffer, encoding="gzip", path_dockerfile="Dockerfile", tag=tag
        # )


docker_repo = DockerRepo()
