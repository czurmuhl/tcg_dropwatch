# ruff: noqa: UP037

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.common import get_datetime_utc

if TYPE_CHECKING:
    from app.models.signals import DropSignal
    from app.models.users import User
    from app.models.watchlists import Watchlist


class AlertEventBase(SQLModel):
    watchlist_id: uuid.UUID = Field(foreign_key="watchlist.id", ondelete="CASCADE")
    signal_id: uuid.UUID = Field(foreign_key="drop_signal.id", ondelete="CASCADE")
    channel: str = Field(default="email", min_length=1, max_length=40, index=True)
    status: str = Field(min_length=1, max_length=40, index=True)
    sent_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))  # type: ignore
    error_code: str | None = Field(default=None, max_length=80)
    error: str | None = Field(default=None, max_length=2048)
    public_message: str | None = Field(default=None, max_length=255)


class AlertEventCreate(AlertEventBase):
    owner_id: uuid.UUID


class AlertEvent(AlertEventBase, table=True):
    __tablename__ = "alert_event"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: "User" = Relationship(back_populates="alert_events")
    watchlist: "Watchlist" = Relationship(back_populates="alert_events")
    signal: "DropSignal" = Relationship(back_populates="alert_events")


class AlertEventPublic(AlertEventBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class AlertEventsPublic(SQLModel):
    data: list[AlertEventPublic]
    count: int
