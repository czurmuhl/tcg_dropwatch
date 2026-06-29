from fastapi import APIRouter

from app.api.routes import (
    login,
    private,
    products,
    scrapes,
    signals,
    sources,
    users,
    utils,
    watchlists,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(products.router)
api_router.include_router(sources.router)
api_router.include_router(signals.router)
api_router.include_router(watchlists.router)
api_router.include_router(scrapes.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
