"""
OptiCode Backend A — Authentication routes.

POST /auth/signup, /auth/login, /auth/logout, /auth/refresh

Not yet implemented — requires Supabase Auth integration (Phase 2).
"""

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup() -> None:
    """Register a new user via Supabase Auth."""
    raise HTTPException(status_code=501, detail="Authentication not yet implemented.")


@router.post("/login")
async def login() -> None:
    """Sign in with email and password via Supabase Auth."""
    raise HTTPException(status_code=501, detail="Authentication not yet implemented.")


@router.post("/logout")
async def logout() -> None:
    """Revoke the current session."""
    raise HTTPException(status_code=501, detail="Authentication not yet implemented.")


@router.post("/refresh")
async def refresh() -> None:
    """Refresh the access token."""
    raise HTTPException(status_code=501, detail="Authentication not yet implemented.")
