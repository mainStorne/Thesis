from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from structlog import get_logger

from src.api.db.users import Account, Student
from src.api.repos.account_repo import account_repo

log = get_logger()


class UsersRepo:
    async def create_student(self, session, student: Student):
        student.account.hashed_password = account_repo.hash_password(
            student.account.hashed_password)
        session.add(student)
        await session.commit()

    async def get_user_by_token(self, session: AsyncSession, token: str) -> Account | None:
        payload = account_repo.decode_token(token)
        stmt = select(Account).where(Account.id == payload.id).options(
            joinedload(Account.student), joinedload(Account.teacher))
        return (await session.exec(stmt)).one_or_none()


users_repo = UsersRepo()
