import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Message,
    Product,
    ProductCreate,
    ProductPublic,
    ProductsPublic,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductsPublic)
def read_products(
    session: SessionDep,
    _current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    game: str | None = None,
    product_type: str | None = None,
) -> Any:
    count_statement = select(func.count()).select_from(Product)
    statement = select(Product)
    if q:
        search = f"%{q}%"
        search_filter = or_(
            col(Product.name).ilike(search),
            col(Product.game).ilike(search),
            col(Product.product_type).ilike(search),
        )
        count_statement = count_statement.where(search_filter)
        statement = statement.where(search_filter)
    if game:
        count_statement = count_statement.where(Product.game == game)
        statement = statement.where(Product.game == game)
    if product_type:
        count_statement = count_statement.where(Product.product_type == product_type)
        statement = statement.where(Product.product_type == product_type)
    count = session.exec(count_statement).one()
    statement = (
        statement.order_by(col(Product.created_at).desc()).offset(skip).limit(limit)
    )
    products = session.exec(statement).all()
    return ProductsPublic(
        data=[ProductPublic.model_validate(product) for product in products],
        count=count,
    )


@router.get("/{id}", response_model=ProductPublic)
def read_product(session: SessionDep, _current_user: CurrentUser, id: uuid.UUID) -> Any:
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProductPublic,
)
def create_product(*, session: SessionDep, product_in: ProductCreate) -> Any:
    product = Product.model_validate(product_in)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.put(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProductPublic,
)
def update_product(
    *, session: SessionDep, id: uuid.UUID, product_in: ProductUpdate
) -> Any:
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_dict = product_in.model_dump(exclude_unset=True)
    product.sqlmodel_update(update_dict)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{id}", dependencies=[Depends(get_current_active_superuser)])
def delete_product(session: SessionDep, id: uuid.UUID) -> Message:
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return Message(message="Product deleted successfully")
