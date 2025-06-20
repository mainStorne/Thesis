from io import BytesIO

from aiodocker import Docker

from src.api.repos.archive_repo import archive_repo
from src.api.repos.base import RepoError
from src.conf import app_settings, queue_var


class DockerRepoError(RepoError):
    ...


class DockerRepo:
    def __init__(self):
        self._private_registry = "127.0.0.1:5000"
        self._docker_client = None

    async def init(self):
        self._docker_client = Docker()

    async def get_agent_ips(self):
        tasks = await self._docker_client.tasks.list(filters={"name": "thesis_agent"})
        if not tasks:
            raise DockerRepoError
        for task in tasks:
            status = (await self._docker_client.nodes.inspect(node_id=task['NodeID']))['Status']
            if status['State'] != 'ready':
                continue

            yield status['Addr']

    async def push_to_registry(self, name: str):
        await self._docker_client.images.push(name)

    async def delete_service(self, name: str):
        await self._delete_image_from_registry(name)
        await self._docker_client.services.delete(name)

    async def _delete_image_from_registry(self, name: str):
        # TODO
        ...

    def stream_service_log(self, service_name: str):
        return self._docker_client.services.logs(service_name, stderr=True, stdout=True, timestamps=True, follow=True)

    async def create_service(self, name: str, labels: dict[str, str], task_template: dict):
        return await self._docker_client.services.create(
            task_template=task_template,
            labels=labels,
            name=name,
            registry=self._private_registry,
            endpoint_spec={"Mode": "vip"},
            networks=[app_settings.swarm.overlay_network_name],
        )

    async def is_service_name_exists(self, name: str):
        services = await self._docker_client.services.list(filters={"name": name})
        if not services:
            return False
        return any(service["Spec"]["Name"] == name for service in services)

    async def create_serverless_service(self, name: str, domain: str, middleware: str, image: str, port: str = "80"):
        labels = {
            "sablier.enable": "true",
            "traefik.enable": "true",
            "traefik.docker.lbswarm": "true",
            f"traefik.http.routers.{name}.rule": f"Host(`{domain}.{app_settings.domain}`)",
            f"traefik.http.routers.{name}.middlewares": middleware,
            f"traefik.http.services.{name}.loadbalancer.server.port": port,
            f"traefik.http.routers.{name}.entrypoints": "http",
        }

        return await self.create_service(name, labels=labels, task_template={"ContainerSpec": {"Image": image}})

    async def build_project(self, student_project: BytesIO, tag: str):
        queue = queue_var.get()
        await queue.put("Создаю docker образ приложения")
        tar = await archive_repo.create_tar(student_project)
        await queue.put("Docker Образ приложения создан")
        tag = f"{self._private_registry}/{tag}"
        async for content in self._docker_client.images.build(fileobj=tar, encoding="gzip", tag=tag, stream=True):
            message = content.get("stream", None)
            error = content.get("errorDetail", None)
            if error:
                queue.put(message)
                raise DockerRepoError
            if message is None:
                continue
            await queue.put(message)
        await self.push_to_registry(tag)
        return tag


docker_repo = DockerRepo()
