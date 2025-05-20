from asyncio import Queue
from io import BytesIO

from aiodocker import Docker

from src.api.repos.archive_repo import archive_repo
from src.conf import app_settings, queue_var


class DockerRepo:
    def __init__(self):
        self._private_registry = '127.0.0.1:5000'
        self._docker_client = None

    async def init(self):
        self._docker_client = Docker()

    async def get_nodes(self):
        for node in await self._docker_client.nodes.list():
            node_status = node["Status"]
            yield node['ID'], node_status["Addr"]

    async def push_to_registry(self, name: str):
        await self._docker_client.images.push(
            name
        )

    async def delete_service(self, name: str):
        pass

    async def _delete_image_from_registry(self, name: str):
        ...

    async def create_service(self, name: str, labels: dict[str, str], task_template: dict):
        return await self._docker_client.services.create(
            task_template=task_template,
            labels=labels,
            name=name,
            registry=self._private_registry,
            endpoint_spec={"Mode": "vip"},
            networks=[app_settings.swarm.overlay_network_name]
        )

    async def is_service_name_exists(self, name: str):
        services = await self._docker_client.services.list(filters={'name': name})
        if not services:
            return False
        return any(service['Spec']['Name'] == name for service in services)

    async def create_serverless_service(self, name: str, domain: str,  middleware: str, image: str, port: str = '80'):
        labels = {'sablier.enable': 'true',   'traefik.enable': 'true',
                  "traefik.docker.lbswarm": "true",
                  f'traefik.http.routers.{name}.rule': f'Host(`{domain}.{app_settings.domain}`)',
                  f'traefik.http.routers.{name}.middlewares': middleware,
                  f'traefik.http.services.{name}.loadbalancer.server.port': port,
                  f"traefik.http.routers.{name}.entrypoints": "http"}

        return await self.create_service(
            name, labels=labels, task_template={'ContainerSpec': {"Image": image}})

    async def build_student_project(self, dockerfile: str,  student_project: BytesIO, tag: str):
        queue = queue_var.get()
        queue.put_nowait('Создаю docker образ приложения')
        tar = await archive_repo.create_tar(dockerfile, student_project)
        queue.put_nowait('Docker Образ приложения создан')
        tag = f"{self._private_registry}/{tag}"
        async for content in self._docker_client.images.build(
            fileobj=tar, encoding="gzip", tag=tag, stream=True
        ):
            message = content.get('stream', None)
            if message is None:
                continue
            queue.put_nowait(message)
        await self.push_to_registry(tag)
        return tag


docker_repo = DockerRepo()
