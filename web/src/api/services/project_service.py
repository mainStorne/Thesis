from io import BytesIO
from uuid import UUID

from sqlalchemy.orm import contains_eager, joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.db.resource import MysqlAccount, Project, ProjectTemplate
from src.api.db.users import Account, Student
from src.api.repos.account_repo import account_repo
from src.api.repos.base import BaseSQLRepo
from src.api.repos.docker_repo import docker_repo
from src.api.repos.traefik_repo import traefik_repo
from src.conf import app_settings, queue_var
from src.schemas import DomainLikeName


class ProjectService(BaseSQLRepo):

    async def get_student_projects(self, session: AsyncSession, token: str):
        payload = account_repo.decode_token(token)

        stmt = select(Project).join(ProjectTemplate, ProjectTemplate.id == Project.project_template_id).join(Student, Student.id == Project.student_id).join(
            Account, Account.id == Student.account_id).where(Account.id == payload.id).options(contains_eager(Project.project_template))

        return await session.exec(stmt)

    async def delete_project(self, project_name: str):
        pass

    async def get_project_templates(self, session: AsyncSession) -> list[ProjectTemplate]:
        return await session.exec(select(ProjectTemplate))

    async def get_by_id(self, session, id: UUID) -> Project | None:
        return (await session.exec(select(Project).where(Project.id == str(id)).options(joinedload(Project.mysql_account), joinedload(Project.project_template)))).one_or_none()

    async def get_integrations(self, session: AsyncSession):
        await session.exec(select(MysqlAccount))

    async def create_project(self, project_name: DomainLikeName): ...

    async def _create_project(self, project_name: str, session: AsyncSession, service_name: str, filesize: int, buffer: BytesIO, student: Student, template: ProjectTemplate):

        domain_name = f'{project_name}.{student.account.login}'
        image = await docker_repo.build_student_project(template.dockerfile, buffer, tag=domain_name)
        middleware_name = await traefik_repo.add_student_service(service_name)
        await docker_repo.create_serverless_service(service_name,  middleware=middleware_name, image=image, domain=domain_name)
        queue = queue_var.get()
        queue.put_nowait('Сервис создан')
        student.logical_used += filesize
        project_url = f'http://{domain_name}.{app_settings.domain}'

        student_project = Project(
            name=project_name, byte_size=filesize, project_url=project_url)
        student_project.student = student
        student_project.project_template = template
        session.add(student_project)
        await session.commit()

        return project_url, student_project


project_service = ProjectService()
