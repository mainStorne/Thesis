from sqlalchemy.orm import contains_eager
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.db.resource import MySQLDataBase, ProjectTemplate, StudentProject
from src.api.db.users import Account, Student
from src.api.repos.account_repo import account_repo


class ProjectService:

    async def get_student_projects(self, session: AsyncSession, token: str):
        payload = account_repo.decode_token(token)

        stmt = select(StudentProject).join(ProjectTemplate, ProjectTemplate.id == StudentProject.project_template_id).join(Student, Student.id == StudentProject.student_id).join(
            Account, Account.id == Student.account_id).where(Account.id == payload.id).options(contains_eager(StudentProject.project_template))

        return await session.exec(stmt)

    async def create_student_project(self, session, grpc_pool):
        pass

    async def get_project_templates(self, session: AsyncSession) -> list[ProjectTemplate]:
        return await session.exec(select(ProjectTemplate))

    async def get_integrations(self, session: AsyncSession):
        await session.exec(select(MySQLDataBase))


project_service = ProjectService()
