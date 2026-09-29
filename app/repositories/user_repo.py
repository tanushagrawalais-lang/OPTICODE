"""
OptiCode Backend A — User Repository.

Handles database persistence for users table via Supabase client.
No business logic belongs here.
"""

from typing import Any
from uuid import UUID

from app.core.errors import ExternalServiceError


class UserRepository:
    """Data-access repository for user records in Supabase."""

    def __init__(self, client: Any):
        self._client = client

    def get_by_id(self, user_id: UUID) -> dict[str, Any] | None:
        """Fetch a user by UUID. Returns None if not found."""
        try:
            response = (
                self._client.table("users")
                .select("*")
                .eq("id", str(user_id))
                .execute()
            )
            data = getattr(response, "data", [])
            return data[0] if data else None
        except Exception as exc:
            raise ExternalServiceError(f"Failed to retrieve user: {exc}") from exc

    def create_or_get(self, user_id: UUID) -> dict[str, Any]:
        """Ensure a user record exists, creating it if necessary."""
        try:
            existing = self.get_by_id(user_id)
            if existing:
                return existing

            payload = {"id": str(user_id)}
            response = self._client.table("users").insert(payload).execute()
            data = getattr(response, "data", [])
            if not data:
                raise ExternalServiceError("Failed to insert user record.")
            return data[0]
        except ExternalServiceError:
            raise
        except Exception as exc:
            raise ExternalServiceError(f"Failed to create user: {exc}") from exc
