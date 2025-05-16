from io import BytesIO

from aiodocker import Docker


class DockerRepo:

    def __init__(self):
        self._docker_client = None

    async def init(self):
        self._docker_client = Docker()

    async def build(self, buffer: BytesIO, tag: str):
        image = await self._docker_client.images.build(fileobj=buffer, encoding='gzip', path_dockerfile='Dockerfile', tag=tag)
        return await self._docker_client.containers.run({'Image': tag})

    async def build(self, tag: str):
        pass


docker_repo = DockerRepo()
