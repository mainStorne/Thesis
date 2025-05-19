from asyncio.subprocess import PIPE, create_subprocess_shell

from structlog import get_logger

from src.api.repos.base import RepoError
from src.conf import app_settings

log = get_logger()


class CreateUserException(RepoError):
    pass


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
            raise CreateUserException

    async def set_quotas_to_student(self, login: str, quota: str):
        proc = await create_subprocess_shell(
            f"sudo setquota {login} {quota} {quota} 0 0 {app_settings.quota.students_shared_base_dir}",
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"settings quota exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"set quota has stdout {stdout.decode()}")
        if stderr:
            await log.aerror(stderr.decode())
            raise CreateUserException

    async def unregister_student_from_mysql(self, login: str):
        proc = await create_subprocess_shell(
            f"""sudo docker exec mysql mysql --password={app_settings.mysql} --execute="drop user '{login}'@'%';
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
            raise CreateUserException

    async def create_student_to_filesystem(self, login: str):
        proc = await create_subprocess_shell(
            f"sudo useradd -mU -b {app_settings.quota.students_home_base_dir} -G students {login}",
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"create_student_to_filesystem exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"create_student_to_filesystem has stdout {stdout.decode()}")
        if stderr:
            await log.aerror(stderr.decode())
            raise CreateUserException


quota_repo = QuotaRepo()
