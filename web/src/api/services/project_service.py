from uuid import UUID

from sqlalchemy.orm import contains_eager, joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.db.resource import MysqlAccount, ProjectTemplate, StudentProject
from src.api.db.users import Account, Student
from src.api.repos.account_repo import account_repo
from src.api.repos.base import BaseSQLRepo


class ProjectService(BaseSQLRepo):

    async def get_student_projects(self, session: AsyncSession, token: str):
        payload = account_repo.decode_token(token)

        stmt = select(StudentProject).join(ProjectTemplate, ProjectTemplate.id == StudentProject.project_template_id).join(Student, Student.id == StudentProject.student_id).join(
            Account, Account.id == Student.account_id).where(Account.id == payload.id).options(contains_eager(StudentProject.project_template))

        return await session.exec(stmt)

    async def create_student_project(self, session, grpc_pool):
        pass

    async def get_project_templates(self, session: AsyncSession) -> list[ProjectTemplate]:
        return await session.exec(select(ProjectTemplate))

    async def get_by_id(self, session, id: UUID) -> StudentProject | None:
        return (await session.exec(select(StudentProject).where(StudentProject.id == str(id)).options(joinedload(StudentProject.mysql_account), joinedload(StudentProject.project_template)))).one_or_none()

    async def get_integrations(self, session: AsyncSession):
        await session.exec(select(MysqlAccount))


project_service = ProjectService()
