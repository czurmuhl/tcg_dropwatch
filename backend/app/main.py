import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), 
                    enable_tracing=True,     # Add data like request headers and IP for users,
                    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
                    send_default_pii=True,
                    # Enable sending logs to Sentry
                    enable_logs=True,
                    # Set traces_sample_rate to 1.0 to capture 100%
                    # of transactions for tracing.
                    traces_sample_rate=1.0,
                    # Set profile_session_sample_rate to 1.0 to profile 100%
                    # of profile sessions.
                    profile_session_sample_rate=1.0,
                    # Set profile_lifecycle to "trace" to automatically
                    # run the profiler on when there is an active transaction
                    profile_lifecycle="trace")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
