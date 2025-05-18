from src.api.repos.mysql_repo import mysql_repo
from src.api.repos.docker_repo import docker_repo
from src.grpc.quota_pb2 import CreateSharedResourceRequest
from src.grpc.quota_pb2_grpc import ResourcesStub
from src.grpc_pool import GrpcPool

from .base import ServiceError


class MysqlExists(ServiceError):
    ...


class ResourceService:

    async def create_mysql(self, session, name: str, limit: str, grpc_pool: GrpcPool):
        if await mysql_repo.is_exists(session, name):
            raise MysqlExists
        node_ip, channel = next(iter(grpc_pool.channels.items()))
        stub = ResourcesStub(channel)
        response = await stub.CreateSharedResource(CreateSharedResourceRequest(limit=limit, name=name))
        docker_repo.create_service()
        await mysql_repo.create(session, name)
