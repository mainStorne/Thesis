from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import DateTime, Field, Relationship, SQLModel, String, text

from src.db.mixins import DateMixin, UUIDMixin


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
    student: "Student" = Relationship(back_populates="account")


class Student(UUIDMixin, SQLModel, table=True):
    __tablename__ = "students"
    account_id: UUID = Field(foreign_key="accounts.id")
    first_name: str = Field(sa_type=String(256))
    middle_name: str | None = Field(sa_type=String(256), nullable=True)
    last_name: str = Field(sa_type=String(256))
    group_id: UUID = Field(foreign_key="groups.id")
    resource_limit: str = Field(sa_type=String(10), default="200MB")  # 1GB 10GB 100MB

    account: Account = Relationship(back_populates="student")


class Teacher(UUIDMixin, SQLModel, table=True):
    account_id: UUID = Field(foreign_key="accounts.id")
    first_name: str = Field(sa_type=String(256))
    middle_name: str | None = Field(sa_type=String(256), nullable=True)
    last_name: str = Field(sa_type=String(256))


class Resource(DateMixin, UUIDMixin, SQLModel, table=True):
    __tablename__ = "resources"
    name: str = Field(sa_type=String(265))
    path_url: str


class StudentResource(UUIDMixin, SQLModel, table=True):
    __tablename__ = "student_resources"
    resource_id: UUID = Field("resources.id")
    student_id: UUID = Field("students.id")


class Group(UUIDMixin, SQLModel, table=True):
    __tablename__ = "groups"
    name: str = Field(sa_type=String(265))
