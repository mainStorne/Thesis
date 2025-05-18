import os
from pwd import getpwnam

import pytest

from grpc.aio import insecure_channel
from src.grpc.quota_pb2 import CreateSharedResourceRequest
from src.grpc.quota_pb2_grpc import ResourcesStub
from src.repos.filesystem_repo import FileSystemError, filesystem_repo
from src.repos.quota_repo import quota_repo
from src.server import Server


@pytest.fixture(autouse=True)
async def server():
    server = Server(50051)
    await server._server.start()
    yield
    await server._server.wait_for_termination()


@pytest.fixture()
async def channel():
    async with insecure_channel('localhost:50051') as _channel:
        yield _channel


async def test_create_shared_resource(channel):
    resource_name = 'shared'
    limit = '500M'
    # volume_path, uid, gid = await resource_service.create_shared_resource(limit, resource_name)
    try:
        stub = ResourcesStub(channel)
        response = await stub.CreateSharedResource(CreateSharedResourceRequest(limit=limit, name=resource_name))
        getpwnam(resource_name)
        assert os.path.isdir(response.volume_path), 'Volume Dir not created'
        assert os.path.isdir(f'/fs/shared/{resource_name}'), 'User not created'
        df = await quota_repo.repquota()
        df.loc[resource_name]
        await filesystem_repo.delete_user(resource_name)
        with pytest.raises(KeyError):
            getpwnam(resource_name)
    except FileSystemError:
        raise
    except Exception:
        await filesystem_repo.delete_user(resource_name)
        raise
