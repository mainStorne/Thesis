
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.settings import DatabaseSettings


class Database:
    def __init__(self, settings: DatabaseSettings):
        self._sqlalchemy_url = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=settings.user,
            password=settings.password,
            host=settings.host,
            port=settings.port,
            path=settings.db,
        )

        self._engine = create_async_engine(str(self._sqlalchemy_url))
        self._session_maker = async_sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession)
