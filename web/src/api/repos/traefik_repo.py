import asyncio
from concurrent.futures import ThreadPoolExecutor

import yaml


class TraefikRepo:

    async def add_student_service(self, service_name: str) -> str:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(1) as pool:
            return await loop.run_in_executor(
                pool, self._get_dynamic_config, service_name)

    def _get_dynamic_config(self, service_name: str) -> dict:
        with open('/dynamic.yml', 'r+') as file:
            config = yaml.safe_load(file)

            sablier = {}
            sablier['names'] = service_name
            sablier['dynamic'] = {'displayName': f'Starting {service_name}',
                                  'refreshFrequency': '5s', 'showDetails': 'true', 'theme': 'hacker-terminal'}
            sablier['sablierUrl'] = 'http://sablier:10000'
            sablier['sessionDuration'] = '2h'
            config['http']['middlewares'].update({
                service_name: {'plugin': {'sablier': sablier}}})
            file.seek(0)
            yaml.dump(config, file)
        return f'{service_name}@file'


traefik_repo = TraefikRepo()
