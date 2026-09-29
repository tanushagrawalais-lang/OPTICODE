"""
OptiCode Backend A — Common / shared schemas.

Provides shared pagination and utility schemas.
"""

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Standard query parameters for paginated endpoints."""

    limit: int = Field(default=50, ge=1, le=100, description="Number of items to return.")
    offset: int = Field(default=0, ge=0, description="Offset for pagination.")


class PaginatedResponse[T](BaseModel):
    """Standard generic wrapper for paginated list responses."""

    items: list[T]
    total: int
    limit: int
    offset: int
