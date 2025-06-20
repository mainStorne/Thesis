from io import BytesIO
from uuid import UUID

from aiodocker import DockerError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.db.resource import Project
from src.api.db.users import Account
from src.api.repos.account_repo import account_repo
from src.api.repos.base import BaseSQLRepo
from src.api.repos.docker_repo import docker_repo
from src.api.repos.traefik_repo import traefik_repo
from src.api.services.base import NotFound
from src.conf import app_settings, queue_var
from src.schemas import DomainLikeName


class ProjectService(BaseSQLRepo):

    async def get_user_projects(self, session: AsyncSession, token: str):
        payload = account_repo.decode_token(token)

        stmt = select(Project).join(Account, Account.id == Project.account_id
                                    ).where(Account.id == payload.id)

        return await session.exec(stmt)

    async def delete_student_project(self, session: AsyncSession, account: Account, project: Project):
        await self.delete_project(session,  account, project)
        account.student.logical_limit -= project.byte_size
        session.add(account.student)
        await session.commit()

    async def delete_project(self, session: AsyncSession, account: Account, project: Project):
        service_name = self.get_service_name(account, project.name)
        try:
            await docker_repo.delete_service(service_name)
        except DockerError as e:
            if e.status != 404:
                raise
        await traefik_repo.delete_service(service_name)
        await session.delete(project)
        await session.commit()

    async def get_by_id(self, session, id: UUID) -> Project | None:
        return (await session.exec(select(Project).where(Project.id == str(id)))).one_or_none()

    def get_service_name(self, account: Account, project_name: str) -> str:
        return f'{account.login}_{project_name}'

    async def update_project(self, project: Project, account: Account, buffer: BytesIO):
        domain_name = f'{project.name}.{account.login}'
        service_name = self.get_service_name(account, project.name)
        await docker_repo.delete_service(service_name)
        image = await docker_repo.build_project(buffer, tag=domain_name)
        await docker_repo.create_serverless_service(service_name,  middleware=f"{service_name}@file", image=image, domain=domain_name)
        queue = queue_var.get()
        await queue.put('Сервис обновлен')

    async def create_project(
            self, project_name: DomainLikeName, account: Account, buffer: BytesIO, session: AsyncSession, filesize: int) -> Project:

        service_name = self.get_service_name(account, project_name.root)
        if await docker_repo.is_service_name_exists(service_name):
            raise NotFound(detail='Project exists')

        project_url = await self._build_project(project_name.root, service_name, buffer, account)
        project = await project_service._create_project(project_name.root, session, project_url, filesize, account)
        return project

    async def _create_project(self, project_name: str, session: AsyncSession, project_url: str, filesize: int, account: Account):
        project = Project(
            name=project_name, byte_size=filesize, project_url=project_url)
        project.account = account
        session.add(project)
        await session.commit()

        return project

    async def _build_project(self, project_name: str, service_name: str, buffer, account):
        domain_name = f'{project_name}.{account.login}'
        image = await docker_repo.build_project(buffer, tag=domain_name)
        middleware_name = await traefik_repo.add_service(service_name)
        await docker_repo.create_serverless_service(service_name,  middleware=middleware_name, image=image, domain=domain_name)

        queue = queue_var.get()
        await queue.put('Сервис создан')
        project_url = f'http://{domain_name}.{app_settings.domain}'
        return project_url


project_service = ProjectService()
