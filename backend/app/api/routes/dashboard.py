from typing import Any

from fastapi import APIRouter
from sqlmodel import SQLModel, col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    AlertEvent,
    AlertEventPublic,
    DropSignal,
    DropSignalPublic,
    Product,
    RetailerSource,
    Watchlist,
    WatchlistPublic,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardCounts(SQLModel):
    watchlists: int
    alerts: int
    products: int
    sources: int


class DashboardPublic(SQLModel):
    watchlists: list[WatchlistPublic]
    alerts: list[AlertEventPublic]
    signals: list[DropSignalPublic]
    counts: DashboardCounts


@router.get("/", response_model=DashboardPublic)
def read_dashboard(session: SessionDep, current_user: CurrentUser) -> Any:
    watchlist_statement = (
        select(Watchlist)
        .where(Watchlist.owner_id == current_user.id)
        .order_by(col(Watchlist.created_at).desc())
        .limit(25)
    )
    watchlists = session.exec(watchlist_statement).all()
    product_ids = [watchlist.product_id for watchlist in watchlists]

    alert_statement = (
        select(AlertEvent)
        .where(AlertEvent.owner_id == current_user.id)
        .order_by(col(AlertEvent.created_at).desc())
        .limit(25)
    )
    alerts = session.exec(alert_statement).all()

    if product_ids:
        signal_statement = (
            select(DropSignal)
            .where(col(DropSignal.product_id).in_(product_ids))
            .order_by(col(DropSignal.observed_at).desc())
            .limit(25)
        )
        signals = session.exec(signal_statement).all()
    else:
        signals = []

    watchlist_count = session.exec(
        select(func.count())
        .select_from(Watchlist)
        .where(Watchlist.owner_id == current_user.id)
    ).one()
    alert_count = session.exec(
        select(func.count())
        .select_from(AlertEvent)
        .where(AlertEvent.owner_id == current_user.id)
    ).one()
    product_count = session.exec(select(func.count()).select_from(Product)).one()
    source_count = session.exec(
        select(func.count())
        .select_from(RetailerSource)
        .where(RetailerSource.owner_id == current_user.id)
    ).one()

    return DashboardPublic(
        watchlists=[
            WatchlistPublic.model_validate(watchlist) for watchlist in watchlists
        ],
        alerts=[AlertEventPublic.model_validate(alert) for alert in alerts],
        signals=[DropSignalPublic.model_validate(signal) for signal in signals],
        counts=DashboardCounts(
            watchlists=watchlist_count,
            alerts=alert_count,
            products=product_count,
            sources=source_count,
        ),
    )
