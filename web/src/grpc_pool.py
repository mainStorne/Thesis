from contextlib import suppress

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
        # single discovery pass; if no agent is found, _channels stays empty
        # and callers are expected to handle that (see ResourceService.create_mysql)
        await log.ainfo("Looking for agents")
        with suppress(DockerRepoError):
            await self._pooling()
        if self._channels:
            await log.ainfo("Agents found")
        else:
            await log.awarning("No agents found, continuing without one")

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
