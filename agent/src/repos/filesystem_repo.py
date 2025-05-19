from asyncio.subprocess import PIPE, create_subprocess_shell

from structlog import get_logger

from src.conf import app_settings
from src.repos.base import RepoError

log = get_logger()


class FileSystemError(RepoError):
    ...


class FilesystemRepo:

    def __init__(self):
        self.shared_base_dir = '/fs/shared'

    async def create_shared_resource(self, name: str) -> None:
        await self.create_resource(self.shared_base_dir, name)

    async def create_resource(self, base_dir: str, username: str):
        proc = await create_subprocess_shell(
            f"sudo useradd -mU -b {base_dir} -G students {username}",
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"create_student_to_filesystem exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"create_student_to_filesystem has stdout {stdout.decode()}")
        if stderr:
            await log.aerror(stderr.decode())
            raise FileSystemError

    async def create_user(self, username: str):
        proc = await create_subprocess_shell(
            f"sudo useradd -mU -b {app_settings.quota.students_home_base_dir} -G students {username}",
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"create_student_to_filesystem exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"create_student_to_filesystem has stdout {stdout.decode()}")
        if stderr:
            await log.aerror(stderr.decode())
            raise FileSystemError

    async def delete_user(self, username: str):
        proc = await create_subprocess_shell(
            f"sudo userdel -r {username}",
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"Creating user exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"Creating user has stdout {stdout.decode()}")
        if stderr:
            await log.awarning(stderr.decode())


filesystem_repo = FilesystemRepo()
