from src.api.repos.docker_repo import docker_repo
from src.grpc.quota_pb2 import CreateSharedResourceRequest, CreateSharedResourceResponse
from src.grpc.quota_pb2_grpc import ResourcesStub
from src.grpc_pool import GrpcPool

from .base import ServiceError


class MysqlExists(ServiceError):
    ...


class ResourceService:

    async def create_mysql(self, session, name: str, root_password: str, limit: str, grpc_pool: GrpcPool):
        if await docker_repo.is_service_name_exists(name):
            raise MysqlExists
        node_id, channel = next(iter(grpc_pool.channels.items()))
        stub = ResourcesStub(channel)
        response: CreateSharedResourceResponse = await stub.CreateSharedResource(CreateSharedResourceRequest(limit=limit, name=name))
        await docker_repo.create_service(name,
                                         labels={"traefik.enable": "true", f"traefik.tcp.routers.{name}.rule":
                                                 'HostSNI(`*`)', f"traefik.tcp.routers.{name}.entrypoints": "mysql", f"traefik.tcp.services.{name}.loadbalancer.server.port": "3306"},

                                         task_template={
                                             'ContainerSpec': {
                                                 "Image": 'mysql',
                                                 "User": f"{response.uid}:{response.gid}",
                                                 "Env": {'MYSQL_ROOT_PASSWORD': root_password},
                                                 'Mounts': [{'target': '/var/lib/mysql', 'source': response.volume_path, 'type': 'bind'}],
                                                 "Placement": [{'Constraints': [f'node.id=={node_id}']}],
                                                 "Args": ['--bind-address=0.0.0.0']

                                             }
                                         })


resource_service = ResourceService()
