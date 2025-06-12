import asyncio

from grpc.aio import Channel, insecure_channel
from src.api.repos.docker_repo import DockerRepoError, docker_repo
from src.conf import log


class GrpcPool:
    def __init__(self):
        self.channel = None
        self._channels = {}

    async def _pooling(self):
        async for agent_ip in docker_repo.get_agent_ips():
            channel = await insecure_channel(f"{agent_ip}:50051").__aenter__()
            self._channels[agent_ip] = channel

    async def pooling(self):
        # pooling until at least on agent is active
        while True:
            await log.ainfo("Start polling agents")
            try:
                await self._pooling()
            except DockerRepoError:
                await log.awarning("Agents not found, pooling again")
                await asyncio.sleep(60)
                continue
            if self._channels:
                await log.ainfo("Agents found")
                break
            await log.awarning("Agents not found, pooling again")
            await asyncio.sleep(60)  # wait for 1 minute

    def release(self, agent_ip: str):
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
