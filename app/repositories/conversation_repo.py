"""
OptiCode Backend A — Conversation Repository.

Handles database persistence for conversations table via Supabase client.
No business logic belongs here.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.errors import ExternalServiceError


class ConversationRepository:
    """Data-access repository for conversation records in Supabase."""

    def __init__(self, client: Any):
        self._client = client

    def create(self, user_id: UUID, title: str) -> dict[str, Any]:
        """Insert a new conversation owned by user_id."""
        try:
            now = datetime.now(UTC).isoformat()
            payload = {
                "user_id": str(user_id),
                "title": title,
                "created_at": now,
                "updated_at": now,
            }
            response = self._client.table("conversations").insert(payload).execute()
            data = getattr(response, "data", [])
            if not data:
                raise ExternalServiceError("Failed to create conversation record.")
            return data[0]
        except ExternalServiceError:
            raise
        except Exception as exc:
            raise ExternalServiceError(f"Database error creating conversation: {exc}") from exc

    def get_by_id(self, conversation_id: UUID) -> dict[str, Any] | None:
        """Fetch a conversation by ID. Returns None if not found."""
        try:
            response = (
                self._client.table("conversations")
                .select("*")
                .eq("id", str(conversation_id))
                .execute()
            )
            data = getattr(response, "data", [])
            return data[0] if data else None
        except Exception as exc:
            raise ExternalServiceError(f"Database error fetching conversation: {exc}") from exc

    def list_for_user(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List conversations belonging to a user, ordered by updated_at desc."""
        try:
            query = (
                self._client.table("conversations")
                .select("*")
                .eq("user_id", str(user_id))
                .order("updated_at", desc=True)
            )
            if limit > 0:
                query = query.range(offset, offset + limit - 1)
            response = query.execute()
            return getattr(response, "data", []) or []
        except Exception as exc:
            raise ExternalServiceError(f"Database error listing conversations: {exc}") from exc

    def update(
        self,
        conversation_id: UUID,
        title: str,
    ) -> dict[str, Any] | None:
        """Update conversation title and refreshed updated_at timestamp."""
        try:
            now = datetime.now(UTC).isoformat()
            payload = {"title": title, "updated_at": now}
            response = (
                self._client.table("conversations")
                .update(payload)
                .eq("id", str(conversation_id))
                .execute()
            )
            data = getattr(response, "data", [])
            return data[0] if data else None
        except Exception as exc:
            raise ExternalServiceError(f"Database error updating conversation: {exc}") from exc

    def touch(self, conversation_id: UUID) -> None:
        """Update updated_at timestamp when a new message is added."""
        try:
            now = datetime.now(UTC).isoformat()
            self._client.table("conversations").update({"updated_at": now}).eq(
                "id", str(conversation_id)
            ).execute()
        except Exception:
            # Touching timestamp should be non-blocking
            pass

    def delete(self, conversation_id: UUID) -> bool:
        """Delete a conversation by ID."""
        try:
            response = (
                self._client.table("conversations")
                .delete()
                .eq("id", str(conversation_id))
                .execute()
            )
            data = getattr(response, "data", [])
            return bool(data)
        except Exception as exc:
            raise ExternalServiceError(f"Database error deleting conversation: {exc}") from exc
