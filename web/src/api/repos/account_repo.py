from abc import ABC, abstractmethod

from passlib.hash import pbkdf2_sha256
from sqlmodel import select
from structlog import get_logger

from src.api.db.users import Account
from src.api.repos.security_repo import security_repo
from src.conf import settings

log = get_logger()


class IAccountRepo(ABC):
    @abstractmethod
    def generate_token(self, account: Account): ...

    @abstractmethod
    async def login(self, session, login: str, password: str):
        pass


class AccountRepo(IAccountRepo):
    async def login(self, session, login: str, hashed_password: str):
        return (
            await session.exec(
                select(Account).where((Account.login == login) & (
                    Account.hashed_password == hashed_password))
            )
        ).one_or_none()

    def generate_token(self, account: Account):
        return security_repo.encode({"id": str(account.id)})

    def hash_password(self, password):
        # todo change secret
        return pbkdf2_sha256.hash(password, salt=b'secret')

    def verify(self, password, hashed_password):
        return pbkdf2_sha256.verify(password, hashed_password)


account_repo = AccountRepo()
