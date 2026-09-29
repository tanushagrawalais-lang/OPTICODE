"""
OptiCode Backend A — Code operation routes.

POST /code/optimize, /code/fix, /code/explain

Not yet implemented — requires Backend B + AI provider integration (Phase 3+).
"""

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/code", tags=["code"])


@router.post("/optimize")
async def optimize_code() -> None:
    """Optimize submitted source code."""
    raise HTTPException(status_code=501, detail="Code operations not yet implemented.")


@router.post("/fix")
async def fix_code() -> None:
    """Fix bugs in submitted source code."""
    raise HTTPException(status_code=501, detail="Code operations not yet implemented.")


@router.post("/explain")
async def explain_code() -> None:
    """Explain submitted source code."""
    raise HTTPException(status_code=501, detail="Code operations not yet implemented.")
