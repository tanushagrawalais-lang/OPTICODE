"""
OptiCode Backend A — CORS middleware configuration.

Applies Cross-Origin Resource Sharing headers based on application settings.
Origins are restricted to configured values — no wildcard in production.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings


def add_cors_middleware(app: FastAPI, settings: Settings) -> None:
    """Add CORS middleware to the application using configured origins."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-Id"],
    )
