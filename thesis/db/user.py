from sqlmodel import SQLModel

from .mixins import UUIDMixin


class User(UUIDMixin, SQLModel, table=True):
    __tablename__ = "users"
    name: str
