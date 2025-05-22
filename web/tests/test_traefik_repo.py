
import yaml

from src.api.repos.traefik_repo import traefik_repo


# @pytest.mark.asyncio
async def test_repo():
    service_name = 'test1'
    middleware_name = await traefik_repo.add_service(service_name)
    with open('/dynamic.yml', 'r+') as file:
        config = yaml.safe_load(file)
        assert config['http']['middlewares'][service_name]['plugin']['sablier']
