

import secrets

from pydantic import MySQLDsn
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import select, text
from sqlmodel.ext.asyncio.session import AsyncSession
from structlog import get_logger

from src.api.db.resource import MySQLDataBase, StudentProject
from src.api.db.users import Student
from src.api.repos.base import BaseSQLRepo, IIntegration
from src.conf import settings

log = get_logger()


class MySQLRepo(IIntegration, BaseSQLRepo[MySQLDataBase]):
    __root__ = MySQLDataBase

    def __init__(self):
        self._sqlalchemy_url = MySQLDsn.build(
            scheme="mysql+asyncmy",
            username='root',
            password=settings.mysql_root_password,
            host='mysql',  # TODO  Temporary failure in name resolution
            port=3306,
        )

        self._engine = create_async_engine(str(self._sqlalchemy_url))
        self.session_maker = async_sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession)
        super().__init__()

    async def is_exists(self, session,  name: str) -> bool:
        return bool((await session.exec(select(MySQLDataBase).where(MySQLDataBase.name == name))).one_or_none())

    async def create(self, session, name: str):
        return await super().create(session, MySQLDataBase(name=name, root_password=secrets.token_urlsafe(16)))

    async def on_student_create(self, student: Student, password: str):
        sql = f"""create user '{student.account.login}'@'%' identified by '{password}';
"""
        try:
            async with self.session_maker() as session:
                await session.exec(text(sql))
        except SQLAlchemyError as e:
            await log.awarning('Error in create student hook', exc_inf=e)

    async def on_create_project(self, student_project: StudentProject):
        database = f"{student_project.student.account.login}_{student_project.name}"
        sql = f"""create database {database};
grant  all on {database}.* to '{database}'@'%';
"""
        try:
            async with self.session_maker() as session:
                await session.exec(text(sql))
        except SQLAlchemyError as e:
            await log.awarning('Error in create project hook', exc_inf=e)


mysql_repo = MySQLRepo()
