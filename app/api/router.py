"""
OptiCode Backend A — Top-level API router aggregator.

Collects all route modules and exposes a single router for the application.
"""

from fastapi import APIRouter

from app.api.routes import auth, code, conversations, health, messages

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(conversations.router)
api_router.include_router(messages.router)
api_router.include_router(code.router)
