from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, get_current_active_superuser
from app.models import (
    ScrapeRunPublic,
    ScrapeRunRequest,
    SimulatedTwitterDropPublic,
    SimulatedTwitterDropsPublic,
    get_datetime_utc,
)

router = APIRouter(
    prefix="/scrapes",
    tags=["scrapes"],
)


@router.post(
    "/run",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ScrapeRunPublic,
)
def run_scrape(scrape_in: ScrapeRunRequest | None = None) -> Any:
    source_id = scrape_in.source_id if scrape_in else None
    return ScrapeRunPublic(
        message="Scrape runner is scaffolded but not implemented yet.",
        source_id=source_id,
    )


@router.get("/twitter/pokemon-drops", response_model=SimulatedTwitterDropsPublic)
def read_simulated_pokemon_twitter_drops(
    _current_user: CurrentUser,
    q: str | None = None,
    limit: int = Query(default=10, ge=1, le=25),
) -> Any:
    generated_at = get_datetime_utc()
    drops = [
        SimulatedTwitterDropPublic(
            id="tw-pkm-001",
            author_handle="@PokemonRestockHub",
            display_name="Pokemon Restock Hub",
            text=(
                "Pokemon 151 Booster Bundles are back at Target online. "
                "$26.94, limit 3, ships this week."
            ),
            product_name="Pokemon 151 Booster Bundle",
            game="Pokemon",
            url="https://x.example/pokemon-restock-hub/status/tw-pkm-001",
            observed_price=26.94,
            msrp=26.94,
            stock_status="in_stock",
            retailer_name="Target",
            posted_at=generated_at - timedelta(minutes=4),
            signal_hint="restock_at_msrp",
        ),
        SimulatedTwitterDropPublic(
            id="tw-pkm-002",
            author_handle="@SealedTCGDrops",
            display_name="Sealed TCG Drops",
            text=(
                "Pokemon Prismatic Evolutions ETB preorder queue is live at "
                "Best Buy near MSRP. Moving fast."
            ),
            product_name="Pokemon Prismatic Evolutions Elite Trainer Box",
            game="Pokemon",
            url="https://x.example/sealed-tcg-drops/status/tw-pkm-002",
            observed_price=49.99,
            msrp=49.99,
            stock_status="preorder_open",
            retailer_name="Best Buy",
            posted_at=generated_at - timedelta(minutes=11),
            signal_hint="preorder_open_at_msrp",
        ),
        SimulatedTwitterDropPublic(
            id="tw-pkm-003",
            author_handle="@CardShelfAlerts",
            display_name="Card Shelf Alerts",
            text=(
                "Surging Sparks Booster Box spotted at GameStop for $161.64. "
                "Online stock is limited."
            ),
            product_name="Pokemon Surging Sparks Booster Box",
            game="Pokemon",
            url="https://x.example/card-shelf-alerts/status/tw-pkm-003",
            observed_price=161.64,
            msrp=161.64,
            stock_status="low_stock",
            retailer_name="GameStop",
            posted_at=generated_at - timedelta(minutes=18),
            signal_hint="low_stock_at_msrp",
        ),
        SimulatedTwitterDropPublic(
            id="tw-pkm-004",
            author_handle="@PokeDropWatch",
            display_name="Poke Drop Watch",
            text=(
                "Crown Zenith Sea & Sky Premium Collection restocked at Sam's Club. "
                "Price is still close to MSRP."
            ),
            product_name="Pokemon Crown Zenith Sea & Sky Premium Collection",
            game="Pokemon",
            url="https://x.example/poke-drop-watch/status/tw-pkm-004",
            observed_price=39.98,
            msrp=39.99,
            stock_status="in_stock",
            retailer_name="Sam's Club",
            posted_at=generated_at - timedelta(minutes=27),
            signal_hint="near_msrp_restock",
        ),
        SimulatedTwitterDropPublic(
            id="tw-pkm-005",
            author_handle="@TrainerDeals",
            display_name="Trainer Deals",
            text=(
                "Pokemon Paldea Adventure Chest is available again online. "
                "Not a huge discount, but under the alert threshold."
            ),
            product_name="Pokemon Paldea Adventure Chest",
            game="Pokemon",
            url="https://x.example/trainer-deals/status/tw-pkm-005",
            observed_price=44.99,
            msrp=49.99,
            stock_status="in_stock",
            retailer_name="Walmart",
            posted_at=generated_at - timedelta(minutes=39),
            signal_hint="price_drop_below_msrp",
        ),
    ]

    if q:
        normalized_query = q.casefold()
        drops = [
            drop
            for drop in drops
            if normalized_query in drop.product_name.casefold()
            or normalized_query in drop.text.casefold()
            or (
                drop.retailer_name is not None
                and normalized_query in drop.retailer_name.casefold()
            )
        ]

    limited_drops = drops[:limit]
    return SimulatedTwitterDropsPublic(
        data=limited_drops,
        count=len(limited_drops),
        generated_at=generated_at,
    )
