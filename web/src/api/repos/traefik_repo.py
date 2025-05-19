import asyncio
import yaml
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple

TraefikMiddleware = namedtuple('TraefikMiddleware', ['group', 'middleware'])


class TraefikRepo:

    async def add_student_service(self, service_name: str) -> TraefikMiddleware:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(1) as pool:
            loop.run_in_executor(pool, self._get_dynamic_config, service_name)

    def _get_dynamic_config(self, service_name: str) -> dict:
        with open('/dynamic.yml', 'r+') as file:
            config = yaml.safe_load(file)
            config['http']
            yaml.dump()


traefik_repo = TraefikRepo()
