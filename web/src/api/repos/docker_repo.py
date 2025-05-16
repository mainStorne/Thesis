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
            node_status = node['Status']
            yield node_status['Addr']

    async def build(self, buffer: BytesIO, tag: str):
        image = await self._docker_client.images.build(fileobj=buffer, encoding='gzip', path_dockerfile='Dockerfile', tag=tag)
        return await self._docker_client.containers.run({'Image': tag})


docker_repo = DockerRepo()
