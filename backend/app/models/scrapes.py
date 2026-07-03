import uuid
from datetime import datetime

from sqlmodel import SQLModel


class ScrapeRunRequest(SQLModel):
    source_id: uuid.UUID | None = None


class ScrapeRunPublic(SQLModel):
    message: str
    source_id: uuid.UUID | None = None


class SimulatedTwitterDropPublic(SQLModel):
    id: str
    author_handle: str
    display_name: str
    text: str
    product_name: str
    game: str
    url: str
    observed_price: float | None = None
    msrp: float | None = None
    stock_status: str
    retailer_name: str | None = None
    posted_at: datetime
    signal_hint: str


class SimulatedTwitterDropsPublic(SQLModel):
    data: list[SimulatedTwitterDropPublic]
    count: int
    generated_at: datetime
