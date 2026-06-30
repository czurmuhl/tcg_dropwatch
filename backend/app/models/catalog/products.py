# ruff: noqa: UP037

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.common import get_datetime_utc

if TYPE_CHECKING:
    from app.models.catalog.sources import RetailerSource
    from app.models.signals import DropSignal
    from app.models.watchlists import Watchlist


class ProductBase(SQLModel):
    game: str = Field(min_length=1, max_length=80, index=True)
    name: str = Field(min_length=1, max_length=255, index=True)
    product_type: str = Field(min_length=1, max_length=120)
    msrp: float = Field(gt=0)
    image_url: str | None = Field(default=None, max_length=2048)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    game: str | None = Field(default=None, min_length=1, max_length=80)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    product_type: str | None = Field(default=None, min_length=1, max_length=120)
    msrp: float | None = Field(default=None, gt=0)
    image_url: str | None = Field(default=None, max_length=2048)


class Product(ProductBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    sources: list["RetailerSource"] = Relationship(
        back_populates="product", cascade_delete=True
    )
    signals: list["DropSignal"] = Relationship(
        back_populates="product", cascade_delete=True
    )
    watchlists: list["Watchlist"] = Relationship(
        back_populates="product", cascade_delete=True
    )


class ProductPublic(ProductBase):
    id: uuid.UUID
    created_at: datetime | None = None


class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int
