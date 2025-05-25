

from secrets import token_urlsafe

from pydantic import MySQLDsn
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import text
from sqlmodel.ext.asyncio.session import AsyncSession
from structlog import get_logger

from src.api.db.users import Account
from src.conf import app_settings

log = get_logger()


class MySQLRepo:

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

    async def create_database(self, account: Account):
        postfix = token_urlsafe(2)
        async with self.session_maker() as session, session.begin():
            db_name = f"{account.login}_{postfix}"
            sql = text(f"""create database {db_name};
grant  all on {db_name}.* to '{account.login}'@'%';""")
            await session.execute(sql)

    async def create_user_account(self, account: Account, password: str):
        sql = text(
            f"""create user '{account.login}'@'%' identified by '{password}';""")
        async with self.session_maker() as session, session.begin():
            await session.execute(sql)


mysql_repo = MySQLRepo()
