"""
OptiCode Backend A — Conversation routes.

CRUD operations for /conversations.
Strict user ownership enforced on all operations via service layer.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_conversation_service, get_current_user_id
from app.schemas.conversations import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
)
async def create_conversation(
    payload: ConversationCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    """Create a new conversation belonging to the authenticated user."""
    return service.create_conversation(user_id=user_id, title=payload.title)


@router.get(
    "",
    response_model=list[ConversationResponse],
    summary="List conversations",
)
async def list_conversations(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: UUID = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> list[ConversationResponse]:
    """List conversations belonging to the authenticated user."""
    return service.list_conversations(user_id=user_id, limit=limit, offset=offset)


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get conversation by ID",
)
async def get_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    """Retrieve a single conversation, verifying that the user is the owner."""
    return service.get_conversation(user_id=user_id, conversation_id=conversation_id)


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Update conversation title",
)
async def update_conversation(
    conversation_id: UUID,
    payload: ConversationUpdate,
    user_id: UUID = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    """Update conversation title after verifying user ownership."""
    return service.update_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
        title=payload.title,
    )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
)
async def delete_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> None:
    """Delete a conversation after verifying user ownership."""
    service.delete_conversation(user_id=user_id, conversation_id=conversation_id)
