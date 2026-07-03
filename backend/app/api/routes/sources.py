import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy import or_
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
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
)


def _get_product_or_404(session: SessionDep, product_id: uuid.UUID) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def _get_visible_source_or_404(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> RetailerSource:
    source = session.get(RetailerSource, id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    if current_user.is_superuser:
        return source
    if source.owner_id == current_user.id:
        return source
    raise HTTPException(status_code=403, detail="Not enough permissions")


@router.get("/", response_model=RetailerSourcesPublic)
def read_sources(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    count_statement = select(func.count()).select_from(RetailerSource)
    statement = select(RetailerSource)
    if not current_user.is_superuser:
        visible_filter = or_(
            RetailerSource.owner_id == current_user.id,
            RetailerSource.owner_id.is_(None),
        )
        count_statement = count_statement.where(visible_filter)
        statement = statement.where(visible_filter)
    count = session.exec(count_statement).one()
    statement = (
        statement.order_by(col(RetailerSource.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    sources = session.exec(statement).all()
    return RetailerSourcesPublic(
        data=[RetailerSourcePublic.model_validate(source) for source in sources],
        count=count,
    )


@router.get("/{id}", response_model=RetailerSourcePublic)
def read_source(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    return _get_visible_source_or_404(session=session, current_user=current_user, id=id)


@router.post("/", response_model=RetailerSourcePublic)
def create_source(
    *, session: SessionDep, current_user: CurrentUser, source_in: RetailerSourceCreate
) -> Any:
    if source_in.product_id is not None:
        _get_product_or_404(session, source_in.product_id)
    source = RetailerSource.model_validate(
        source_in, update={"owner_id": current_user.id}
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


@router.put("/{id}", response_model=RetailerSourcePublic)
def update_source(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    source_in: RetailerSourceUpdate,
) -> Any:
    source = _get_visible_source_or_404(
        session=session, current_user=current_user, id=id
    )
    update_dict = source_in.model_dump(exclude_unset=True)
    if "product_id" in update_dict and update_dict["product_id"] is not None:
        _get_product_or_404(session, update_dict["product_id"])
    source.sqlmodel_update(update_dict)
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


@router.delete("/{id}")
def delete_source(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    source = _get_visible_source_or_404(
        session=session, current_user=current_user, id=id
    )
    session.delete(source)
    session.commit()
    return Message(message="Source deleted successfully")
