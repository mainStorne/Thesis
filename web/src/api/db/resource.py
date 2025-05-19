from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, String

from src.api.db.mixins import DateMixin, UUIDMixin

if TYPE_CHECKING:
    from .users import Student


class ProjectTemplate(UUIDMixin, SQLModel, table=True):
    __tablename__ = "project_templates"
    name: str = Field(sa_type=String(128))
    dockerfile: str
    student_projects: list['StudentProject'] = Relationship(
        back_populates='project_template')


class MysqlAccount(UUIDMixin, SQLModel, table=True):
    __tablename__ = 'mysql_accounts'
    login: str = Field(sa_type=String(30))
    password: str = Field(sa_type=String(30))
    student_project_id: UUID = Field(foreign_key='student_projects.id')
    student_project: "StudentProject" = Relationship(
        back_populates='mysql_account')


class StudentProject(UUIDMixin, DateMixin, SQLModel, table=True):
    __tablename__ = "student_projects"
    project_template_id: UUID = Field(foreign_key="project_templates.id")
    student_id: UUID = Field(foreign_key="students.id")
    name: str = Field(sa_type=String(128))
    cpu: str | None = None
    ram: str | None = None
    byte_size: int = 0
    project_template: ProjectTemplate = Relationship(
        back_populates='student_projects')

    project_url: str = Field(
        sa_column_kwargs={'server_default': 'thesis.com'})

    student: 'Student' = Relationship(back_populates='projects')
    mysql_account: MysqlAccount | None = Relationship(
        back_populates='student_project')

    @property
    def view_created_at(self) -> str:
        return self.created_at.strftime(r'%Y.%d.%m, %H:%M:%S')
