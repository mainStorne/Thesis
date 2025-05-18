
from structlog import get_logger

from src.api.repos.account_repo import account_repo

log = get_logger()


class QuotaRepositoryException(Exception):
    ...


class UserNotFoundException(QuotaRepositoryException):
    pass


class AuthService:

    async def login(self, session, login: str, password: str) -> str:
        hashed_password = account_repo.hash_password(password)
        account = await account_repo.login(session, login, hashed_password)
        if not account:
            raise UserNotFoundException

        return account_repo.generate_token(account)


auth_service = AuthService()
