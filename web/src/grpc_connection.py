

import asyncio

from grpc.aio import Channel, insecure_channel
from src.api.repos.docker_repo import docker_repo


class GrpcConnection:

    def __init__(self):
        self.channel = None
        self._channels = {}

    async def _on_startup(self):
        await docker_repo.init()
        while True:
            async for node_ip in docker_repo.get_nodes_ip():
                if node_ip not in self._channels:
                    channel = await insecure_channel(f'{node_ip}:50051').__aenter__()
                    self._channels[node_ip] = channel

            await asyncio.sleep(300)  # one for 5 minutes

    def release(self, node_ip: str):
        pass

    @property
    def channels(self) -> dict[str, Channel]:
        return self._channels

    async def on_startup(self):
        asyncio.create_task(self._on_startup())  # noqa: RUF006
        # self.channel = await insecure_channel('localhost:50051').__aenter__()

    async def on_shutdown(self):
        for channel in self.channels.values():
            await channel.__aexit__(None, None, None)


grpc_connection = GrpcConnection()
