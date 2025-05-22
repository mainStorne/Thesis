from datetime import datetime, timezone
from typing import TYPE_CHECKING, Union
from uuid import UUID

from sqlmodel import DateTime, Field, Relationship, SQLModel, String, text

from src.api.db.mixins import UUIDMixin

if TYPE_CHECKING:
    from .resource import MysqlAccount, Project


class UserMixin:

    @property
    def fio(self) -> str:
        return f'{self.last_name.capitalize()} {self.first_name[0].upper()}.{f" {self.middle_name[0].upper()}." if self.middle_name else ''}'


class Account(UUIDMixin, SQLModel, table=True):
    __tablename__ = "accounts"
    login: str = Field(sa_type=String(80), unique=True)
    hashed_password: str
    last_login: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": text("current_timestamp")},
        sa_type=DateTime(True),
    )
    is_stuff: bool = False
    student: Union["Student", None] = Relationship(back_populates="account")
    teacher: Union["Teacher", None] = Relationship(back_populates="account")
    projects: list['Project'] = Relationship(back_populates='account')
    mysql_accounts: list['MysqlAccount'] = Relationship(
        back_populates='account')


class Student(UUIDMixin, UserMixin, SQLModel, table=True):
    __tablename__ = "students"
    first_name: str = Field(sa_type=String(256))
    middle_name: str | None = Field(sa_type=String(256), nullable=True)
    last_name: str = Field(sa_type=String(256))
    logical_limit: int
    logical_used: int = 0

    group_id: UUID = Field(foreign_key="groups.id")
    account_id: UUID = Field(foreign_key="accounts.id")
    account: Account = Relationship(back_populates="student")
    group: 'Group' = Relationship(back_populates='students')


class Teacher(UUIDMixin, UserMixin, SQLModel, table=True):

    account_id: UUID = Field(foreign_key="accounts.id")
    first_name: str = Field(sa_type=String(256))
    middle_name: str | None = Field(sa_type=String(256), nullable=True)
    last_name: str = Field(sa_type=String(256))
    account: Union["Account", None] = Relationship(
        back_populates="teacher")


class Group(UUIDMixin, SQLModel, table=True):
    __tablename__ = "groups"
    name: str = Field(sa_type=String(265))
    students: list[Student] = Relationship(back_populates='group')
