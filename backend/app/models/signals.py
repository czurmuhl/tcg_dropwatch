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
    from app.models.catalog.sources import RetailerSource


class DropSignalBase(SQLModel):
    product_id: uuid.UUID = Field(foreign_key="product.id", ondelete="CASCADE")
    source_id: uuid.UUID | None = Field(
        default=None, foreign_key="retailer_source.id", ondelete="CASCADE"
    )
    observed_price: float = Field(gt=0)
    stock_status: str = Field(min_length=1, max_length=80, index=True)
    source_type: str = Field(default="manual", min_length=1, max_length=40, index=True)
    url: str | None = Field(default=None, max_length=2048)
    observed_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class DropSignalCreate(DropSignalBase):
    pass


class DropSignalUpdate(SQLModel):
    product_id: uuid.UUID | None = None
    source_id: uuid.UUID | None = None
    observed_price: float | None = Field(default=None, gt=0)
    stock_status: str | None = Field(default=None, min_length=1, max_length=80)
    source_type: str | None = Field(default=None, min_length=1, max_length=40)
    url: str | None = Field(default=None, max_length=2048)
    observed_at: datetime | None = None


class DropSignal(DropSignalBase, table=True):
    __tablename__ = "drop_signal"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    product: "Product" = Relationship(back_populates="signals")
    source: "RetailerSource" = Relationship(back_populates="signals")
    alert_events: list["AlertEvent"] = Relationship(
        back_populates="signal", cascade_delete=True
    )


class DropSignalPublic(DropSignalBase):
    id: uuid.UUID
    created_at: datetime | None = None


class DropSignalsPublic(SQLModel):
    data: list[DropSignalPublic]
    count: int
