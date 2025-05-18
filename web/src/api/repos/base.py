from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from abc import ABC, abstractmethod

from src.api.db.resource import StudentProject


class RepoError(Exception):
    pass


class BaseSQLRepo[SQLModel]:
    __root__: SQLModel

    async def create(self, session: AsyncSession, instance: SQLModel):
        session.add(instance)
        await session.commit()

    async def list(self, session: AsyncSession) -> list[SQLModel]:
        return await session.exec(select(self.__root__))


class IIntegration(ABC):

    @abstractmethod
    async def on_create_project(self, student_project: StudentProject):
        pass
