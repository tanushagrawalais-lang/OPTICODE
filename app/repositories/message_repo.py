"""
OptiCode Backend A — Message Repository.

Handles database persistence for messages table via Supabase client.
No business logic belongs here.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.errors import ExternalServiceError


class MessageRepository:
    """Data-access repository for message records in Supabase."""

    def __init__(self, client: Any):
        self._client = client

    def create(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Insert a new message into a conversation."""
        try:
            now = datetime.now(UTC).isoformat()
            payload = {
                "conversation_id": str(conversation_id),
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "created_at": now,
            }
            response = self._client.table("messages").insert(payload).execute()
            data = getattr(response, "data", [])
            if not data:
                raise ExternalServiceError("Failed to create message record.")
            return data[0]
        except ExternalServiceError:
            raise
        except Exception as exc:
            raise ExternalServiceError(f"Database error creating message: {exc}") from exc

    def list_for_conversation(
        self,
        conversation_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List messages in a conversation ordered chronologically (created_at ASC)."""
        try:
            query = (
                self._client.table("messages")
                .select("*")
                .eq("conversation_id", str(conversation_id))
                .order("created_at", desc=False)
            )
            if limit > 0:
                query = query.range(offset, offset + limit - 1)
            response = query.execute()
            return getattr(response, "data", []) or []
        except Exception as exc:
            raise ExternalServiceError(f"Database error listing messages: {exc}") from exc

    def get_by_id(self, message_id: UUID) -> dict[str, Any] | None:
        """Fetch a single message by ID."""
        try:
            response = (
                self._client.table("messages")
                .select("*")
                .eq("id", str(message_id))
                .execute()
            )
            data = getattr(response, "data", [])
            return data[0] if data else None
        except Exception as exc:
            raise ExternalServiceError(f"Database error fetching message: {exc}") from exc
