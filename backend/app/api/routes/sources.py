import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    Message,
    Product,
    RetailerSource,
    RetailerSourceCreate,
    RetailerSourcePublic,
    RetailerSourcesPublic,
    RetailerSourceUpdate,
)

router = APIRouter(
    prefix="/sources",
    tags=["sources"],
    dependencies=[Depends(get_current_active_superuser)],
)


def _get_product_or_404(session: SessionDep, product_id: uuid.UUID) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/", response_model=RetailerSourcesPublic)
def read_sources(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    count_statement = select(func.count()).select_from(RetailerSource)
    count = session.exec(count_statement).one()
    statement = (
        select(RetailerSource)
        .order_by(col(RetailerSource.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    sources = session.exec(statement).all()
    return RetailerSourcesPublic(
        data=[RetailerSourcePublic.model_validate(source) for source in sources],
        count=count,
    )


@router.get("/{id}", response_model=RetailerSourcePublic)
def read_source(session: SessionDep, id: uuid.UUID) -> Any:
    source = session.get(RetailerSource, id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.post("/", response_model=RetailerSourcePublic)
def create_source(*, session: SessionDep, source_in: RetailerSourceCreate) -> Any:
    _get_product_or_404(session, source_in.product_id)
    source = RetailerSource.model_validate(source_in)
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


@router.put("/{id}", response_model=RetailerSourcePublic)
def update_source(
    *, session: SessionDep, id: uuid.UUID, source_in: RetailerSourceUpdate
) -> Any:
    source = session.get(RetailerSource, id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    update_dict = source_in.model_dump(exclude_unset=True)
    if "product_id" in update_dict:
        _get_product_or_404(session, update_dict["product_id"])
    source.sqlmodel_update(update_dict)
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


@router.delete("/{id}")
def delete_source(session: SessionDep, id: uuid.UUID) -> Message:
    source = session.get(RetailerSource, id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    session.delete(source)
    session.commit()
    return Message(message="Source deleted successfully")
