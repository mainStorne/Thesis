from abc import ABC, abstractmethod

from passlib.hash import pbkdf2_sha256
from sqlmodel import select
from structlog import get_logger

from src.db.users import Account

log = get_logger()


class IAccountRepo(ABC):
    def __init__(self, session):
        self._session = session
        super().__init__()

    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:
        pass

    @abstractmethod
    async def login_user(self, login: str, password: str):
        pass


class AcountRepo(IAccountRepo):
    def hash_password(self, password):
        return pbkdf2_sha256.hash(password, salt=b"secret")

    def verify(self, password, hashed_password):
        return pbkdf2_sha256.verify(password, hashed_password)

    async def login_user(self, login, hashed_password):
        return (
            await self._session.exec(
                select(Account).where((Account.login == login) & (
                    Account.hashed_password == hashed_password))
            )
        ).one_or_none()
