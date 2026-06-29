import uuid
from datetime import UTC, datetime

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    watchlists: list[Watchlist] = Relationship(
        back_populates="owner", cascade_delete=True
    )
    alert_events: list[AlertEvent] = Relationship(
        back_populates="owner", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Product properties
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
    sources: list[RetailerSource] = Relationship(
        back_populates="product", cascade_delete=True
    )
    signals: list[DropSignal] = Relationship(
        back_populates="product", cascade_delete=True
    )
    watchlists: list[Watchlist] = Relationship(
        back_populates="product", cascade_delete=True
    )


class ProductPublic(ProductBase):
    id: uuid.UUID
    created_at: datetime | None = None


class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int


# Retailer source properties
class RetailerSourceBase(SQLModel):
    product_id: uuid.UUID = Field(foreign_key="product.id", ondelete="CASCADE")
    retailer_name: str = Field(min_length=1, max_length=120, index=True)
    url: str = Field(min_length=1, max_length=2048)
    price_selector: str | None = Field(default=None, max_length=255)
    stock_selector: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class RetailerSourceCreate(RetailerSourceBase):
    pass


class RetailerSourceUpdate(SQLModel):
    product_id: uuid.UUID | None = None
    retailer_name: str | None = Field(default=None, min_length=1, max_length=120)
    url: str | None = Field(default=None, min_length=1, max_length=2048)
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
    product: Product | None = Relationship(back_populates="sources")
    signals: list[DropSignal] = Relationship(back_populates="source")


class RetailerSourcePublic(RetailerSourceBase):
    id: uuid.UUID
    created_at: datetime | None = None


class RetailerSourcesPublic(SQLModel):
    data: list[RetailerSourcePublic]
    count: int


# Drop signal properties
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
    product: Product | None = Relationship(back_populates="signals")
    source: RetailerSource | None = Relationship(back_populates="signals")
    alert_events: list[AlertEvent] = Relationship(
        back_populates="signal", cascade_delete=True
    )


class DropSignalPublic(DropSignalBase):
    id: uuid.UUID
    created_at: datetime | None = None


class DropSignalsPublic(SQLModel):
    data: list[DropSignalPublic]
    count: int


# Watchlist properties
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
    owner: User | None = Relationship(back_populates="watchlists")
    product: Product | None = Relationship(back_populates="watchlists")
    alert_events: list[AlertEvent] = Relationship(
        back_populates="watchlist", cascade_delete=True
    )


class WatchlistPublic(WatchlistBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class WatchlistsPublic(SQLModel):
    data: list[WatchlistPublic]
    count: int


# Alert event properties
class AlertEventBase(SQLModel):
    watchlist_id: uuid.UUID = Field(foreign_key="watchlist.id", ondelete="CASCADE")
    signal_id: uuid.UUID = Field(foreign_key="drop_signal.id", ondelete="CASCADE")
    channel: str = Field(default="email", min_length=1, max_length=40, index=True)
    status: str = Field(min_length=1, max_length=40, index=True)
    sent_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))  # type: ignore
    error: str | None = Field(default=None, max_length=2048)


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
    owner: User | None = Relationship(back_populates="alert_events")
    watchlist: Watchlist | None = Relationship(back_populates="alert_events")
    signal: DropSignal | None = Relationship(back_populates="alert_events")


class AlertEventPublic(AlertEventBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class AlertEventsPublic(SQLModel):
    data: list[AlertEventPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


class ScrapeRunRequest(SQLModel):
    source_id: uuid.UUID | None = None


class ScrapeRunPublic(SQLModel):
    message: str
    source_id: uuid.UUID | None = None


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
