from sqlmodel import Field, SQLModel, String

from .mixins import UUIDMixin


class User(UUIDMixin, SQLModel, table=True):
    __tablename__ = "users"
    name: str


class Role(UUIDMixin, SQLModel, table=True):
    __tablename__ = "roles"
    name: str = Field(sa_type=String(128))
