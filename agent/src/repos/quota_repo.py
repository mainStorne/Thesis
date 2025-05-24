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

    async def register_student_to_mysql(self, login: str, password: str):
        proc = await create_subprocess_shell(
            f"""sudo docker exec mysql mysql --password={app_settings.mysql} --user=root --execute="create user '{login}'@'%' identified by '{password}';
create database {login};
grant  all on {login}.* to '{login}'@'%';"
""",
            stderr=PIPE,
            stdout=PIPE,
        )
        stdout, stderr = await proc.communicate()
        await log.ainfo(f"register_student_to_mysql exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"Creating user has stdout {stdout.decode()}")
        stderr = stderr.replace(
            b"mysql: [Warning] Using a password on the command line interface can be insecure.\n", b""
        )
        if stderr:
            await log.aerror(stderr.decode())
            raise QuotaError

    async def set_quota(self, username: str, limit: str):

        proc = await create_subprocess_shell(
            f"setquota {username} {limit} {limit} 0 0 /fs",
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

    async def unregister_student_from_mysql(self, login: str):
        proc = await create_subprocess_shell(
            f"""  docker exec mysql mysql --password={app_settings.mysql} --execute="drop user '{login}'@'%';
drop database {login};"
""",
            stderr=PIPE,
            stdout=PIPE,
        )
        stdout, stderr = await proc.communicate()
        await log.ainfo(f"unregister_student_from_mysql exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"unregister_student_from_mysql has stdout {stdout.decode()}")
        stderr = stderr.replace(
            b"mysql: [Warning] Using a password on the command line interface can be insecure.\n", b""
        )
        if stderr:
            await log.aerror(stderr.decode())
            raise QuotaError

    async def repquota(self):
        proc = await create_subprocess_shell(
            "  repquota -O csv /fs", stderr=PIPE, stdout=PIPE
        )
        stdout, stderr = await proc.communicate()
        if stderr:
            raise QuotaError
        # User,BlockStatus,FileStatus,BlockUsed,BlockSoftLimit,BlockHardLimit,BlockGrace,FileUsed,FileSoftLimit,FileHardLimit,FileGrace
        return pd.read_csv(
            BytesIO(stdout), index_col='User')

    async def create_student_to_filesystem(self, username: str):
        proc = await create_subprocess_shell(
            f"  useradd -mU -b {app_settings.quota.students_home_base_dir} -G students {username}",
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
            f"  userdel -r {username}",
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
