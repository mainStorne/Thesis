import asyncio
from asyncio.subprocess import create_subprocess_shell
from uuid import UUID

from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession
from structlog import get_logger

from thesis.db import Student
from thesis.integrations import settings
from thesis.schemas.generated.quota_pb2 import CreateUserRequest

log = get_logger()


class CreateUserException(Exception):
    pass


class QuotaService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_by_id(self, user_id: UUID) -> Student | None:
        return await self._session.get(Student, user_id)

    async def delete_user(self, id: UUID):  # noqa: A002
        await self._session.exec(delete(Student).where(Student.id == id))
        await self._session.commit()

    async def register_student_to_mysql(self, login: str, password: str):
        proc = await create_subprocess_shell(
            f"""sudo docker exec mysql mysql --password={settings.mysql_root_password} --execute="create user '{login}'@'%' identified by '{password}';
create database {login};
grant  all on {login}.* to '{login}'@'%';"
""",
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
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
            f"sudo setquota {login} {quota} {quota} 0 0 {settings.quota.mount_point}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
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
            f"""sudo docker exec mysql mysql --password={settings.mysql_root_password} --execute="drop user '{login}'@'%';
drop database {login};"
""",
            stderr=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
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
            f"sudo useradd -mU -b {settings.quota.base_home_dir} -G students {login}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"create_student_to_filesystem exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"create_student_to_filesystem has stdout {stdout.decode()}")
        if stderr:
            await log.aerror(stderr.decode())
            raise CreateUserException

    async def delete_student_from_filesystem(self, login: str):
        proc = await create_subprocess_shell(
            f"sudo userdel -r {login}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"Creating user exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"Creating user has stdout {stdout.decode()}")
        if stderr:
            await log.aerror(stderr.decode())

    async def create_student(self, student: CreateUserRequest.Student) -> None:
        self._session.add(student)
        await self._session.commit()
