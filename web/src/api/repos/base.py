from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class RepoError(Exception):
    pass


class BaseSQLRepo[SQLModel]:
    __root__: SQLModel

    async def create(self, session: AsyncSession, instance: SQLModel):
        session.add(instance)
        await session.commit()

    async def list(self, session: AsyncSession) -> list[SQLModel]:
        return await session.exec(select(self.__root__))
