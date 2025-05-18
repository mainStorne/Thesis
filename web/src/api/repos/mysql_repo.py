

import secrets

from sqlmodel import select

from src.api.db.resource import MySQLDataBase
from src.api.repos.base import BaseSQLRepo


class MySQLRepo(BaseSQLRepo[MySQLDataBase]):
    __root__ = MySQLDataBase

    async def is_exists(self, session,  name: str) -> bool:
        return bool((await session.exec(select(MySQLDataBase).where(MySQLDataBase.name == name))).one_or_none())

    async def create(self, session, name: str):
        return await super().create(session, MySQLDataBase(name=name, root_password=secrets.token_urlsafe(16)))


mysql_repo = MySQLRepo()
