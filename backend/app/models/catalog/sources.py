# ruff: noqa: UP037

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.common import get_datetime_utc

if TYPE_CHECKING:
    from app.models.catalog.products import Product
    from app.models.signals import DropSignal
    from app.models.users import User


class RetailerSourceBase(SQLModel):
    product_id: uuid.UUID | None = Field(
        default=None, foreign_key="product.id", ondelete="CASCADE"
    )
    retailer_name: str = Field(min_length=1, max_length=120, index=True)
    label: str | None = Field(default=None, max_length=120)
    source_kind: str = Field(
        default="retailer_site", min_length=1, max_length=40, index=True
    )
    url: str = Field(min_length=1, max_length=2048)
    platform: str | None = Field(default=None, max_length=80)
    account_name: str | None = Field(default=None, max_length=255)
    price_selector: str | None = Field(default=None, max_length=255)
    stock_selector: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class RetailerSourceCreate(RetailerSourceBase):
    pass


class RetailerSourceUpdate(SQLModel):
    product_id: uuid.UUID | None = None
    retailer_name: str | None = Field(default=None, min_length=1, max_length=120)
    label: str | None = Field(default=None, max_length=120)
    source_kind: str | None = Field(default=None, min_length=1, max_length=40)
    url: str | None = Field(default=None, min_length=1, max_length=2048)
    platform: str | None = Field(default=None, max_length=80)
    account_name: str | None = Field(default=None, max_length=255)
    price_selector: str | None = Field(default=None, max_length=255)
    stock_selector: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class RetailerSource(RetailerSourceBase, table=True):
    __tablename__ = "retailer_source"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    last_checked_at: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True)
    )  # type: ignore
    last_error_at: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True)
    )  # type: ignore
    last_error_message: str | None = Field(default=None, max_length=2048)
    owner_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    owner: "User" = Relationship(back_populates="sources")
    product: "Product" = Relationship(back_populates="sources")
    signals: list["DropSignal"] = Relationship(back_populates="source")


class RetailerSourcePublic(RetailerSourceBase):
    id: uuid.UUID
    owner_id: uuid.UUID | None = None
    created_at: datetime | None = None
    last_checked_at: datetime | None = None
    last_error_at: datetime | None = None
    last_error_message: str | None = None


class RetailerSourcesPublic(SQLModel):
    data: list[RetailerSourcePublic]
    count: int
