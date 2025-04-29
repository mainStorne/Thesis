from contextvars import ContextVar
from functools import wraps

from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .settings import Settings

session_var = ContextVar("session_var", default=None)


def scoped(func):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        result = await func(*args, **kwargs)
        session = session_var.get()
        await session.__aexit__(None, None, None)
        return result

    return wrapped


class Database:
    def __init__(self, settings: Settings):
        self._sqlalchemy_url = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=settings["user"],
            password=settings["password"],
            host=settings["host"],
            port=settings["port"],
            path=settings["db"],
        )

        self._engine = create_async_engine(str(self._sqlalchemy_url))
        self._session_maker = async_sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)

    def get_session(self) -> AsyncSession:  # type: ignore  # noqa: PGH003
        session = self._session_maker()
        session_var.set(session)
        return session
