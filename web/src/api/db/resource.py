from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, String

from src.api.db.mixins import DateMixin, UUIDMixin

if TYPE_CHECKING:
    from .users import Account


class ProjectTemplate(UUIDMixin, SQLModel, table=True):
    __tablename__ = "project_templates"
    name: str = Field(sa_type=String(128))
    dockerfile: str
    projects: 'Project' = Relationship(
        back_populates='project_template')


class MysqlAccount(UUIDMixin, SQLModel, table=True):
    __tablename__ = 'mysql_accounts'
    login: str = Field(sa_type=String(30))
    password: str = Field(sa_type=String(30))
    account: 'Account' = Relationship(back_populates='mysql_accounts')
    account_id: UUID = Field(foreign_key='accounts.id')


class Project(UUIDMixin, DateMixin, SQLModel, table=True):
    __tablename__ = "projects"
    project_template_id: UUID = Field(foreign_key="project_templates.id")
    account_id: UUID = Field(foreign_key="accounts.id")
    name: str = Field(sa_type=String(128))
    cpu: str | None = None
    ram: str | None = None
    byte_size: int = 0
    project_template: ProjectTemplate = Relationship(
        back_populates='projects')
    account: 'Account' = Relationship(back_populates='projects')

    @property
    def view_created_at(self) -> str:
        return self.created_at.strftime(r'%Y.%d.%m, %H:%M:%S')
