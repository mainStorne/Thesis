from contextlib import asynccontextmanager
from io import BytesIO

from src.conf import app_settings
from src.db.users import Account
from src.grpc.quota_pb2 import CreateStudentRequest
from src.repos.archive_repo import ArchiveRepo, IArchiveRepo
from src.repos.docker_repo import docker_repo
from src.repos.quota_repo import QuotaError, QuotaRepo
from src.repos.traefik_repo import traefik_repo

from agent.src.services.base import ServiceError


class RepQuotaException(ServiceError):
    pass


class QuotaExcitedError(ServiceError):
    pass


class ArchiveError(ServiceError):
    ...


class QuotaService:

    def __init__(self, user_account: Account, quota_repo: QuotaRepo, archive_repo: IArchiveRepo):
        self._user_account = user_account
        self._quota_repo = quota_repo
        self._archive_repo = archive_repo

    async def upload_user_app(self, buffer: BytesIO, buffer_size: int, filename: str):
        users_df = await self._quota_repo.repquota()
        user_df = users_df.loc[self._user_account.username]
        if user_df['BlockStatus'] == 'hard':
            raise QuotaExcitedError

        if user_df['BlockUsed'] + buffer_size > user_df['BlockHardLimit']:
            raise QuotaExcitedError
        path = app_settings.quota.students_home_base_dir / \
            self._user_account.username / filename
        try:
            archived = await self._archive_repo.create_tar(path, buffer, self._user_account.username, self._user_account.username)
        except Exception as e:
            raise ArchiveError from e
        # filename is `file.zip` in tag this name need to be `file`
        container = await docker_repo.build(archived, f'{self._user_account.username}-{filename[:4]}')

        await traefik_repo.add_student_container(container)

    async def create_student(self, student: CreateStudentRequest):
        username = student.username
        await self._quota_repo.create_student_to_filesystem(username)

        try:
            await self._quota_repo.set_quota(username, student.resource_limit)
        except QuotaError:
            await self._quota_repo.delete_student_from_filesystem(username)
            raise


@asynccontextmanager
async def get_quota_service(state: dict):
    user_account: Account = state['account']
    quota_repo = QuotaRepo(session=state['session'])
    state['quota_service'] = QuotaService(
        user_account, quota_repo, ArchiveRepo())
    yield
