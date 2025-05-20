

import secrets

from pydantic import MySQLDsn
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import select, text
from sqlmodel.ext.asyncio.session import AsyncSession
from structlog import get_logger

from src.api.db.resource import MysqlAccount, Project
from src.api.repos.base import BaseSQLRepo, IIntegration
from src.conf import app_settings

log = get_logger()


class MySQLRepo(IIntegration, BaseSQLRepo[MysqlAccount]):
    __root__ = MysqlAccount

    def __init__(self):
        self._sqlalchemy_url = MySQLDsn.build(
            scheme="mysql+asyncmy",
            username='root',
            password=app_settings.mysql.password,
            host=app_settings.mysql.host,
            port=3306,
        )

        self._engine = create_async_engine(str(self._sqlalchemy_url))
        self.session_maker = async_sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession)
        super().__init__()

    async def is_exists(self, session,  name: str) -> bool:
        return bool((await session.exec(select(MysqlAccount).where(MysqlAccount.login == name))).one_or_none())

    async def on_create_project(self, student_project: Project):
        login = secrets.token_urlsafe(10)
        password = secrets.token_urlsafe(10)
        sql = text(
            f"""create user '{login}'@'%' identified by '{password}';""")
        try:
            async with self.session_maker() as session, session.begin():
                await session.execute(sql)
                db_name = f"{student_project.student.account.login}_{student_project.name}"
                sql = text(f"""create database {db_name};
grant  all on {db_name}.* to '{login}'@'%';""")
                await session.execute(sql)
        except SQLAlchemyError as e:
            await log.awarning('Error in create project hook', exc_inf=e)
            return
        mysql = MysqlAccount(login=login, password=password,
                             )
        mysql.student_project = student_project
        return mysql


mysql_repo = MySQLRepo()
