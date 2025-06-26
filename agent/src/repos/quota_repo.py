from asyncio.subprocess import PIPE, create_subprocess_shell
from io import BytesIO

import pandas as pd
from structlog import get_logger

from src.conf import app_settings
from src.repos.base import RepoError

log = get_logger()


class QuotaError(RepoError):
    pass


class QuotaRepo:

    async def set_quota(self, username: str, limit: str):

        proc = await create_subprocess_shell(
            f"setquota {username} {limit} {limit} 0 0 /",
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"settings quota exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"set quota has stdout {stdout.decode()}")
        if stderr:
            await log.aerror(stderr.decode())
            raise QuotaError

    async def repquota(self):
        proc = await create_subprocess_shell(
            "repquota -O csv /", stderr=PIPE, stdout=PIPE
        )
        stdout, stderr = await proc.communicate()
        if stderr:
            raise QuotaError
        # User,BlockStatus,FileStatus,BlockUsed,BlockSoftLimit,BlockHardLimit,BlockGrace,FileUsed,FileSoftLimit,FileHardLimit,FileGrace
        return pd.read_csv(
            BytesIO(stdout), index_col='User')

    async def create_student_to_filesystem(self, username: str):
        proc = await create_subprocess_shell(
            f"useradd -mU -b {app_settings.quota.students_home_base_dir} -G students {username}",
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"create_student_to_filesystem exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"create_student_to_filesystem has stdout {stdout.decode()}")
        if stderr:
            await log.aerror(stderr.decode())
            raise QuotaError

    async def delete_student_from_filesystem(self, username: str):
        proc = await create_subprocess_shell(
            f"userdel -r {username}",
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"Creating user exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"Creating user has stdout {stdout.decode()}")
        if stderr:
            await log.aerror(stderr.decode())


quota_repo = QuotaRepo()
