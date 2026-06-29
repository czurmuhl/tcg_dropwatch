from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_active_superuser
from app.models import ScrapeRunPublic, ScrapeRunRequest

router = APIRouter(
    prefix="/scrapes",
    tags=["scrapes"],
    dependencies=[Depends(get_current_active_superuser)],
)


@router.post("/run", response_model=ScrapeRunPublic)
def run_scrape(scrape_in: ScrapeRunRequest | None = None) -> Any:
    source_id = scrape_in.source_id if scrape_in else None
    return ScrapeRunPublic(
        message="Scrape runner is scaffolded but not implemented yet.",
        source_id=source_id,
    )
