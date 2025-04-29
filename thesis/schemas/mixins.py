from uuid import UUID, uuid4

from sqlmodel import Field


class UUIDMixin:
    id: UUID = Field(primary_key=True, default_factory=uuid4)
