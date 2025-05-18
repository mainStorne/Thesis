from uuid import UUID

from sqlmodel import Field, SQLModel, String

from src.api.db.mixins import UUIDMixin


class ResourceTemplate(UUIDMixin, SQLModel, table=True):
    __tablename__ = "resource_templates"
    name: str = Field(sa_type=String(128))
    dockerfile: str


class MySQLDataBase(UUIDMixin, SQLModel, table=True):
    __tablename__ = 'mysql_databases'
    name: str = Field(sa_type=String(50))
    root_password: str


class StudentProject(UUIDMixin, SQLModel, table=True):
    __tablename__ = "student_projects"
    resource_template_id: UUID = Field(foreign_key="resource_templates.id")
    student_id: UUID = Field("students.id")
    name: str = Field(sa_type=String(128))
    cpu: str | None = None
    ram: str | None = None
