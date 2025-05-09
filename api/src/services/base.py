from sqlalchemy import delete
from sqlmodel import SQLModel


class BaseCRUDService:
    __table__ = type[SQLModel]

    async def delete(self):
        delete()
