"""
OptiCode Backend A — Message Service.

Orchestrates message business logic and enforces parent conversation
ownership boundaries.
"""

from typing import Any
from uuid import UUID

from app.core.errors import AuthorizationError, NotFoundError
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.schemas.messages import MessageResponse


class MessageService:
    """Business logic service for messages."""

    def __init__(
        self,
        message_repo: MessageRepository,
        conversation_repo: ConversationRepository,
    ):
        self._message_repo = message_repo
        self._conversation_repo = conversation_repo

    def _verify_conversation_ownership(self, user_id: UUID, conversation_id: UUID) -> None:
        """Ensure the parent conversation exists and belongs to the authenticated user.

        Raises:
            NotFoundError: If the parent conversation does not exist.
            AuthorizationError: If the conversation belongs to another user.
        """
        conv = self._conversation_repo.get_by_id(conversation_id)
        if not conv:
            raise NotFoundError(f"Conversation {conversation_id} not found.")

        if str(conv["user_id"]) != str(user_id):
            raise AuthorizationError("You do not have access to this conversation.")

    def create_message(
        self,
        user_id: UUID,
        conversation_id: UUID,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> MessageResponse:
        """Create a new message inside a user-owned conversation."""
        self._verify_conversation_ownership(user_id, conversation_id)

        row = self._message_repo.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata=metadata,
        )
        self._conversation_repo.touch(conversation_id)
        return MessageResponse.model_validate(row)

    def list_messages(
        self,
        user_id: UUID,
        conversation_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MessageResponse]:
        """List messages in a conversation after verifying ownership."""
        self._verify_conversation_ownership(user_id, conversation_id)

        rows = self._message_repo.list_for_conversation(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset,
        )
        return [MessageResponse.model_validate(r) for r in rows]
