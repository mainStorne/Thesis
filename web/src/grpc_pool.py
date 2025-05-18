import asyncio

from grpc.aio import Channel, insecure_channel
from src.api.repos.docker_repo import docker_repo


class GrpcPool:
    def __init__(self):
        self.channel = None
        self._channels = {}

    async def _pooling(self):
        async for node_id, node_ip in docker_repo.get_nodes():
            if node_ip not in self._channels:
                channel = await insecure_channel(f"{node_ip}:50051").__aenter__()
                self._channels[node_id] = channel

    async def pooling(self):
        while True:
            await asyncio.sleep(300)  # one for 5 minutes
            await self._pooling()

    def release(self, node_ip: str):
        pass

    @property
    def channels(self) -> dict[str, Channel]:
        return self._channels

    async def on_startup(self):
        await docker_repo.init()
        await self._pooling()
        asyncio.create_task(self.pooling())  # noqa: RUF006

    async def on_shutdown(self):
        for channel in self.channels.values():
            await channel.__aexit__(None, None, None)


grpc_pool = GrpcPool()
