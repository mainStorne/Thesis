from sqlalchemy.exc import SQLAlchemyError
from structlog import get_logger

from src.db.users import Account, Student
from src.schemas.generated.quota_pb2 import CreateUserRequest
from src.services.account_service import IAccountService
from src.services.quota_service import CreateUserException, QuotaService
from src.services.security_service import ISecurityService

log = get_logger()


class QuotaRepositoryException(Exception): ...


class UserNotFoundException(QuotaRepositoryException):
    pass


class AuthRepository:
    def __init__(
        self, quota_service: QuotaService, account_service: IAccountService, security_service: ISecurityService
    ):
        self._quota_service = quota_service
        self._account_service = account_service
        self._security_service = security_service

    async def login_user(self, login: str, password: str):
        hashed_password = self._account_service.hash_password(password)
        account = await self._account_service.login_user(login, hashed_password)
        if not account:
            raise UserNotFoundException
        return self._security_service.generate_token(account)

    async def create_user(self, user: CreateUserRequest.Student | CreateUserRequest.Teacher):
        if isinstance(user, CreateUserRequest.Teacher):
            raise
        else:
            plain_password = user.profile.account.password
            login = user.profile.account.login
            await self._quota_service.create_student_to_filesystem(login)

            try:
                await self._quota_service.set_quotas_to_student(login, user.resource_limit)
            except CreateUserException:
                await self._quota_service.delete_student_from_filesystem(login)
                raise

            try:
                await self._quota_service.register_student_to_mysql(login, plain_password)
            except CreateUserException:
                await self._quota_service.delete_student_from_filesystem(login)
                raise

            try:
                student = user
                student.profile.account.password = self._account_service.hash_password(user.profile.account.password)

                account = Account(login=student.profile.account.login, hashed_password=student.profile.account.password)
                student = Student(
                    first_name=student.profile.first_name,
                    middle_name=student.profile.middle_name,
                    last_name=student.profile.last_name,
                    group_id=student.group_id,
                    resource_limit=student.resource_limit,
                )
                student.account = account
                login = account.login
                await self._quota_service.create_student(student)
            except SQLAlchemyError as e:
                await self._quota_service.delete_student_from_filesystem(login)
                await self._quota_service.unregister_student_from_mysql(login)
                raise CreateUserException from e
            except Exception as e:
                await log.aerror("Unexpected error in create_user!", exc_info=e)
                await self._quota_service.delete_student_from_filesystem(login)
                await self._quota_service.unregister_student_from_mysql(login)
                raise

            return student.id, self._security_service.generate_token(account)
