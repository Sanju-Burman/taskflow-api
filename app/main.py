from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import register_exception_handlers
from app.core.middleware import setup_middleware
from app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables are created (especially helpful for SQLite/dev setups before migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Dispose DB connection engine
    await engine.dispose()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Production-grade Task Management REST API built with FastAPI, PostgreSQL, and JWT Authentication.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # CORS Middleware
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Custom Middleware & Exceptions
    setup_middleware(application)
    register_exception_handlers(application)

    # Include API Routers
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()
