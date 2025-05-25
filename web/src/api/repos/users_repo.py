from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from structlog import get_logger

from src.api.db.users import Account
from src.api.repos.account_repo import account_repo
from src.api.repos.mysql_repo import mysql_repo

log = get_logger()


class UsersRepo:
    async def create_user(self, account: Account):
        password = account.hashed_password
        account.hashed_password = account_repo.hash_password(
            account.hashed_password)
        await mysql_repo.create_user_account(account, password=password)

    async def get_user_by_token(self, session: AsyncSession, token: str) -> Account | None:
        payload = account_repo.decode_token(token)
        stmt = select(Account).where(Account.id == payload.id).options(
            joinedload(Account.student), joinedload(Account.teacher))
        return (await session.exec(stmt)).one_or_none()


users_repo = UsersRepo()
