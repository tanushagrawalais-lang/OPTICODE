"""
OptiCode Backend A — Health check route.

GET /health — Liveness probe for container orchestrators and load balancers.
No external dependencies required.
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return service liveness status.

    Confirms the Backend A process is running and handling HTTP.
    Does NOT verify external dependencies (Supabase, Backend B, AI).
    """
    return {
        "status": "ok",
        "service": "opticode-backend-a",
    }
