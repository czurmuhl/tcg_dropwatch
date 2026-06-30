import uuid

from sqlmodel import SQLModel


class ScrapeRunRequest(SQLModel):
    source_id: uuid.UUID | None = None


class ScrapeRunPublic(SQLModel):
    message: str
    source_id: uuid.UUID | None = None
