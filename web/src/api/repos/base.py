from abc import ABC, abstractmethod

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.api.db.resource import Project


class RepoError(Exception):
    pass


class BaseSQLRepo[SQLModel]:
    __root__: SQLModel

    async def create(self, session: AsyncSession, instance: SQLModel):
        session.add(instance)
        await session.commit()

    async def list(self, session: AsyncSession) -> list[SQLModel]:
        return await session.exec(select(self.__root__))

    async def get_by_id(self, session,  id):
        return await session.exec(select(self.__root__).where(self.__root__.id == id))


class IIntegration(ABC):

    @abstractmethod
    async def on_create_project(self, student_project: Project):
        pass
