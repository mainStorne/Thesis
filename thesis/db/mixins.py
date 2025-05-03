from uuid import UUID

from sqlmodel import Field, text


class UUIDMixin:
    id: UUID = Field(
        primary_key=True,
        # TODO set extension to alembic revisions
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
    )
