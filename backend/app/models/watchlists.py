# ruff: noqa: UP037

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.common import get_datetime_utc

if TYPE_CHECKING:
    from app.models.alerts import AlertEvent
    from app.models.catalog.products import Product
    from app.models.users import User


class WatchlistBase(SQLModel):
    product_id: uuid.UUID = Field(foreign_key="product.id", ondelete="CASCADE")
    msrp_margin_percent: float = Field(default=10, ge=0)
    max_price: float | None = Field(default=None, gt=0)
    email_enabled: bool = True


class WatchlistCreate(WatchlistBase):
    pass


class WatchlistUpdate(SQLModel):
    product_id: uuid.UUID | None = None
    msrp_margin_percent: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, gt=0)
    email_enabled: bool | None = None


class Watchlist(WatchlistBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: "User" = Relationship(back_populates="watchlists")
    product: "Product" = Relationship(back_populates="watchlists")
    alert_events: list["AlertEvent"] = Relationship(
        back_populates="watchlist", cascade_delete=True
    )


class WatchlistPublic(WatchlistBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class WatchlistsPublic(SQLModel):
    data: list[WatchlistPublic]
    count: int
