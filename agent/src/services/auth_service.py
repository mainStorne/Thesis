from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError
from src.conf import settings
from src.db.users import Account, Student
from src.grpc.quota_pb2 import CreateUserRequest
from src.repos.account_repo import AcountRepo, IAccountRepo
from src.repos.quota_repo import QuotaError, QuotaRepo
from src.repos.security_repo import ISecurityRepo, JwtSecurityRepo
from structlog import get_logger

log = get_logger()


class QuotaRepositoryException(Exception):
    ...


class UserNotFoundException(QuotaRepositoryException):
    pass


class AuthService:
    def __init__(
        self, quota_repo: QuotaRepo, account_repo: IAccountRepo, security_repo: ISecurityRepo
    ):
        self._quota_repo = quota_repo
        self._account_repo = account_repo
        self._security_repo = security_repo

    async def login_user(self, login: str, password: str):
        hashed_password = self._account_repo.hash_password(password)
        account = await self._account_repo.login_user(login, hashed_password)
        if not account:
            raise UserNotFoundException
        return self._security_repo.generate_token(account)

    async def create_user(self, user: CreateUserRequest.Student | CreateUserRequest.Teacher):
        if isinstance(user, CreateUserRequest.Teacher):
            raise
        else:
            plain_password = user.profile.account.password
            login = user.profile.account.login
            await self._quota_repo.create_student_to_filesystem(login)

            try:
                await self._quota_repo.set_quotas_to_student(login, user.resource_limit)
            except QuotaError:
                await self._quota_repo.delete_student_from_filesystem(login)
                raise

            try:
                # don't know how to solve this...
                await self._quota_repo.register_student_to_mysql(login, plain_password)
            except QuotaError:
                await self._quota_repo.delete_student_from_filesystem(login)
                raise

            try:
                student = user
                student.profile.account.password = self._account_repo.hash_password(
                    user.profile.account.password)

                account = Account(login=student.profile.account.login,
                                  hashed_password=student.profile.account.password)
                student = Student(
                    first_name=student.profile.first_name,
                    middle_name=student.profile.middle_name,
                    last_name=student.profile.last_name,
                    group_id=student.group_id,
                    resource_limit=student.resource_limit,
                )
                student.account = account
                login = account.login
                await self._quota_repo.create_student(student)
            except SQLAlchemyError as e:
                await self._quota_repo.delete_student_from_filesystem(login)
                await self._quota_repo.unregister_student_from_mysql(login)
                raise QuotaError from e
            except Exception as e:
                await log.aerror("Unexpected error in create_user!", exc_info=e)
                await self._quota_repo.delete_student_from_filesystem(login)
                await self._quota_repo.unregister_student_from_mysql(login)
                raise

            return student.id, self._security_repo.generate_token(account)


@asynccontextmanager
async def get_auth_service(state: dict):
    session = state.get("session")
    state['auth_service'] = AuthService(
        QuotaRepo(session=session), AcountRepo(
            session), JwtSecurityRepo(settings.jwt_secret, "HS256")
    )
    yield
