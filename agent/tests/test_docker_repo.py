from io import BytesIO
from pathlib import Path

import pytest

from src.repos.archive_repo import ArchiveRepo
from src.repos.docker_repo import docker_repo


@pytest.fixture(autouse=True)
async def init():
    await docker_repo.init()
    yield
    await docker_repo._docker_client.close()


async def test_repo():
    path = Path(__file__).parent / 'fixture.tar.gz'
    with open(path, 'rb') as file:
        async for value in docker_repo._docker_client.images.build(fileobj=file, tag='test:v1', stream=True, encoding='gzip'):
            print(value)

    await docker_repo._docker_client.containers.run(
        {
            "Image": "test:v1"
        }
    )


@pytest.fixture
def loop(event_loop):
    return event_loop


@pytest.mark.asyncio
async def test_uploadfile(monkeypatch):
    monkeypatch.setattr('shutil.chown', lambda *args: None)
    repo = ArchiveRepo()
    path = Path(__file__).parent / 'tests' / 'hello.zip'
    with open(Path(__file__).parent / 'fixture.zip', 'rb') as buffer:
        tar = await repo.create_tar(path, BytesIO(buffer.read()), 'dima4', 'dima4')

    image = await docker_repo.build(tar, 'test1')
    container = await docker_repo._docker_client.containers.run({'Image': 'test1'})

    print(image)
    print(container)
    tar.close()
