import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    DropSignal,
    DropSignalCreate,
    DropSignalPublic,
    DropSignalsPublic,
    Message,
    Product,
    RetailerSource,
)

router = APIRouter(prefix="/signals", tags=["signals"])


def _validate_signal_references(
    *, session: SessionDep, product_id: uuid.UUID, source_id: uuid.UUID | None
) -> None:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if source_id is None:
        return
    source = session.get(RetailerSource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    if source.product_id != product_id:
        raise HTTPException(status_code=400, detail="Source does not belong to product")


@router.get("/", response_model=DropSignalsPublic)
def read_signals(
    session: SessionDep, _current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    count_statement = select(func.count()).select_from(DropSignal)
    count = session.exec(count_statement).one()
    statement = (
        select(DropSignal)
        .order_by(col(DropSignal.observed_at).desc())
        .offset(skip)
        .limit(limit)
    )
    signals = session.exec(statement).all()
    return DropSignalsPublic(
        data=[DropSignalPublic.model_validate(signal) for signal in signals],
        count=count,
    )


@router.get("/{id}", response_model=DropSignalPublic)
def read_signal(session: SessionDep, _current_user: CurrentUser, id: uuid.UUID) -> Any:
    signal = session.get(DropSignal, id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=DropSignalPublic,
)
def create_signal(*, session: SessionDep, signal_in: DropSignalCreate) -> Any:
    _validate_signal_references(
        session=session,
        product_id=signal_in.product_id,
        source_id=signal_in.source_id,
    )
    signal = DropSignal.model_validate(signal_in)
    session.add(signal)
    session.commit()
    session.refresh(signal)
    return signal


@router.delete("/{id}", dependencies=[Depends(get_current_active_superuser)])
def delete_signal(session: SessionDep, id: uuid.UUID) -> Message:
    signal = session.get(DropSignal, id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    session.delete(signal)
    session.commit()
    return Message(message="Signal deleted successfully")
