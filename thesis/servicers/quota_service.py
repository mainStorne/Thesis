import asyncio
from asyncio.subprocess import create_subprocess_shell
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession
from structlog import get_logger

from ..db import User

log = get_logger()


class CreateUserException(Exception):
    pass


class QuotaService:
    def __init__(self, session: AsyncSession):
        self._session = session()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self._session.get(User, user_id)

    async def create_user(self, user: User):
        proc = await create_subprocess_shell(
            f"sudo useradd -mU -b /test/filesystem/home/ -G students -c student_{user.name} {user.name}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        await log.ainfo(f"Creating user exited with {proc.returncode}")
        if stdout:
            await log.awarning(f"Creating user has stdout {stdout.decode()}")
        if stderr:
            await log.aerror(stderr.decode())
            raise CreateUserException

        # TODO: change hardcoded container name to something else
        proc = await create_subprocess_shell(
            f"sudo docker exec -it some-mysql psql -U postgres -c 'CREATE USER {user.name}'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
