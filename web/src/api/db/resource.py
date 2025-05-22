from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, String

from src.api.db.mixins import DateMixin, UUIDMixin

if TYPE_CHECKING:
    from .users import Account


class ProjectImage(UUIDMixin, SQLModel, table=True):
    __tablename__ = "project_images"
    name: str = Field(sa_type=String(128))
    dockerfile: str
    projects: list['Project'] = Relationship(
        back_populates='project_image')
    # cpu
    # ram


class Project(UUIDMixin, DateMixin, SQLModel, table=True):
    __tablename__ = "projects"
    project_image_id: UUID = Field(foreign_key="project_images.id")
    account_id: UUID = Field(foreign_key="accounts.id")
    name: str = Field(sa_type=String(128))
    cpu: str | None = None
    ram: str | None = None
    byte_size: int = 0
    project_url: str
    project_image: ProjectImage = Relationship(
        back_populates='projects')
    account: 'Account' = Relationship(back_populates='projects')

    @property
    def view_created_at(self) -> str:
        return self.created_at.strftime(r'%Y.%d.%m, %H:%M:%S')
