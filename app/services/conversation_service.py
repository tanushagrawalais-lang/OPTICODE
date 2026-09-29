"""
OptiCode Backend A — Conversation Service.

Orchestrates conversation business logic and strictly enforces
user ownership boundaries.
"""

from uuid import UUID

from app.core.errors import AuthorizationError, NotFoundError
from app.repositories.conversation_repo import ConversationRepository
from app.schemas.conversations import ConversationResponse


class ConversationService:
    """Business logic service for conversations."""

    def __init__(self, repo: ConversationRepository):
        self._repo = repo

    def create_conversation(self, user_id: UUID, title: str) -> ConversationResponse:
        """Create a new conversation for the authenticated user."""
        row = self._repo.create(user_id=user_id, title=title)
        return ConversationResponse.model_validate(row)

    def get_conversation(self, user_id: UUID, conversation_id: UUID) -> ConversationResponse:
        """Retrieve a conversation by ID, verifying user ownership.

        Raises:
            NotFoundError: If the conversation does not exist.
            AuthorizationError: If the conversation belongs to another user.
        """
        row = self._repo.get_by_id(conversation_id)
        if not row:
            raise NotFoundError(f"Conversation {conversation_id} not found.")

        if str(row["user_id"]) != str(user_id):
            raise AuthorizationError("You do not have access to this conversation.")

        return ConversationResponse.model_validate(row)

    def list_conversations(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ConversationResponse]:
        """List all conversations belonging to the authenticated user."""
        rows = self._repo.list_for_user(user_id=user_id, limit=limit, offset=offset)
        return [ConversationResponse.model_validate(r) for r in rows]

    def update_conversation(
        self,
        user_id: UUID,
        conversation_id: UUID,
        title: str,
    ) -> ConversationResponse:
        """Update a conversation title after verifying ownership."""
        # Enforces ownership check first
        self.get_conversation(user_id, conversation_id)

        row = self._repo.update(conversation_id=conversation_id, title=title)
        if not row:
            raise NotFoundError(f"Conversation {conversation_id} not found.")
        return ConversationResponse.model_validate(row)

    def delete_conversation(self, user_id: UUID, conversation_id: UUID) -> None:
        """Delete a conversation after verifying ownership."""
        # Enforces ownership check first
        self.get_conversation(user_id, conversation_id)

        self._repo.delete(conversation_id=conversation_id)
