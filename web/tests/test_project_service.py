from io import BytesIO
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.api.repos.docker_repo import docker_repo
from src.api.services.project_service import project_service


@pytest.fixture()
async def project(monkeypatch):
    session_mock = AsyncMock()
    project_name = 'test1'
    service_name = 'dima_test1'
    student = MagicMock()
    template = MagicMock()
    template.dockerfile = """FROM traefik/whoami"""
    monkeypatch.setattr('src.conf.queue_var', MagicMock())
    monkeypatch.setattr('src.api.repos.docker_repo.queue_var', MagicMock())

    project_url, student_project = await project_service._create_project(project_name, session_mock, service_name, 10, BytesIO(b'hello-world'), student, template)
    assert await docker_repo.is_service_name_exists(service_name) is True


async def test_delete_project(project):
    pass
