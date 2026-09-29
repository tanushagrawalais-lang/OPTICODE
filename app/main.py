"""
OptiCode Backend A — FastAPI application factory.

Creates and configures the FastAPI application instance.
Use create_app() for testability; the module-level `app` is for uvicorn.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.config import Settings
from app.core.error_handlers import register_error_handlers
from app.core.logging import setup_logging
from app.middleware.cors import add_cors_middleware
from app.middleware.request_id import RequestIDMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    logger.info("OptiCode Backend A starting")
    yield
    logger.info("OptiCode Backend A shutting down")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        settings: Optional settings override (useful for testing).
                  If None, loads from environment / .env file.

    Returns:
        Fully configured FastAPI application.
    """
    if settings is None:
        settings = Settings()

    setup_logging(log_level=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "OptiCode Backend A — Core application orchestration layer "
            "for the AI-powered coding workspace."
        ),
        version="0.1.0",
        lifespan=_lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Store settings on app state for access in dependencies if needed.
    app.state.settings = settings

    # --- Middleware (last added = first executed) ---
    add_cors_middleware(app, settings)
    app.add_middleware(RequestIDMiddleware)

    # --- Exception handlers ---
    register_error_handlers(app)

    # --- Routes ---
    app.include_router(api_router)

    return app


# Module-level instance for: uvicorn app.main:app
app = create_app()
