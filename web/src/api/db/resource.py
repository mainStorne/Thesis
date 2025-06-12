from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, String

from src.api.db.mixins import DateMixin, UUIDMixin

if TYPE_CHECKING:
    from .users import Account


class Project(UUIDMixin, DateMixin, SQLModel, table=True):
    __tablename__ = "projects"
    account_id: UUID = Field(foreign_key="accounts.id")
    name: str = Field(sa_type=String(128))
    cpu: str | None = None
    ram: str | None = None
    byte_size: int = 0
    project_url: str
    account: 'Account' = Relationship(back_populates='projects')

    @property
    def view_created_at(self) -> str:
        return self.created_at.strftime(r'%Y.%d.%m, %H:%M:%S')
