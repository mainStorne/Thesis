from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import DateTime, Field, text


class UUIDMixin:
    id: UUID = Field(
        primary_key=True,
        # TODO set extension to alembic revisions
        sa_column_kwargs={"server_default": text("uuid_generate_v4()")},
    )


class DateMixin:
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": text("current_timestamp")},
        sa_type=DateTime(True),
    )

    updated_at: datetime | None = Field(sa_type=DateTime(True), default=None)
