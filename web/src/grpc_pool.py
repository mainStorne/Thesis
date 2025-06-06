import asyncio

from grpc.aio import Channel, insecure_channel
from src.api.repos.docker_repo import docker_repo
from src.conf import log


class GrpcPool:
    def __init__(self):
        self.channel = None
        self._channels = {}

    async def _pooling(self):
        async for node_id, node_ip in docker_repo.get_agents():
            if node_ip not in self._channels:
                channel = await insecure_channel(f"{node_ip}:50051").__aenter__()
                self._channels[node_id] = channel

    async def pooling(self):
        # pooling until at least on agent is active
        while True:
            await log.ainfo("Start polling agents")
            await self._pooling()
            if self._channels:
                await log.ainfo("Agents found")
                break
            await log.awarning("Agents not found, pooling again")
            await asyncio.sleep(60)  # wait for 1 minute

    def release(self, node_ip: str):
        pass

    @property
    def channels(self) -> dict[str, Channel]:
        return self._channels

    async def on_startup(self):
        await docker_repo.init()
        await self.pooling()

    async def on_shutdown(self):
        for channel in self.channels.values():
            await channel.__aexit__(None, None, None)


grpc_pool = GrpcPool()
