import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    Product,
    Watchlist,
    WatchlistCreate,
    WatchlistPublic,
    WatchlistsPublic,
    WatchlistUpdate,
)

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


def _get_product_or_404(session: SessionDep, product_id: uuid.UUID) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def _get_owned_watchlist_or_404(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Watchlist:
    watchlist = session.get(Watchlist, id)
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist entry not found")
    if watchlist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return watchlist


@router.get("/", response_model=WatchlistsPublic)
def read_watchlists(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    count_statement = (
        select(func.count())
        .select_from(Watchlist)
        .where(Watchlist.owner_id == current_user.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Watchlist)
        .where(Watchlist.owner_id == current_user.id)
        .order_by(col(Watchlist.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    watchlists = session.exec(statement).all()
    return WatchlistsPublic(
        data=[WatchlistPublic.model_validate(watchlist) for watchlist in watchlists],
        count=count,
    )


@router.get("/{id}", response_model=WatchlistPublic)
def read_watchlist(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    return _get_owned_watchlist_or_404(
        session=session, current_user=current_user, id=id
    )


@router.post("/", response_model=WatchlistPublic)
def create_watchlist(
    *, session: SessionDep, current_user: CurrentUser, watchlist_in: WatchlistCreate
) -> Any:
    _get_product_or_404(session, watchlist_in.product_id)
    watchlist = Watchlist.model_validate(
        watchlist_in, update={"owner_id": current_user.id}
    )
    session.add(watchlist)
    session.commit()
    session.refresh(watchlist)
    return watchlist


@router.put("/{id}", response_model=WatchlistPublic)
def update_watchlist(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    watchlist_in: WatchlistUpdate,
) -> Any:
    watchlist = _get_owned_watchlist_or_404(
        session=session, current_user=current_user, id=id
    )
    update_dict = watchlist_in.model_dump(exclude_unset=True)
    if "product_id" in update_dict:
        _get_product_or_404(session, update_dict["product_id"])
    watchlist.sqlmodel_update(update_dict)
    session.add(watchlist)
    session.commit()
    session.refresh(watchlist)
    return watchlist


@router.delete("/{id}")
def delete_watchlist(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    watchlist = _get_owned_watchlist_or_404(
        session=session, current_user=current_user, id=id
    )
    session.delete(watchlist)
    session.commit()
    return Message(message="Watchlist entry deleted successfully")
