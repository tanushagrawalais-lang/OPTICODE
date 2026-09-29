"""
OptiCode Backend A — Message routes.

GET/POST /conversations/{conversation_id}/messages
Parent conversation ownership strictly enforced via MessageService.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user_id, get_message_service
from app.schemas.messages import MessageCreate, MessageResponse
from app.services.message_service import MessageService

router = APIRouter(prefix="/conversations", tags=["messages"])


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
    summary="List messages in a conversation",
)
async def list_messages(
    conversation_id: UUID,
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: UUID = Depends(get_current_user_id),
    service: MessageService = Depends(get_message_service),
) -> list[MessageResponse]:
    """Retrieve messages in a conversation, verifying user ownership of the conversation."""
    return service.list_messages(
        user_id=user_id,
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message in a conversation",
)
async def create_message(
    conversation_id: UUID,
    payload: MessageCreate,
    user_id: UUID = Depends(get_current_user_id),
    service: MessageService = Depends(get_message_service),
) -> MessageResponse:
    """Add a message to a conversation after verifying user ownership."""
    return service.create_message(
        user_id=user_id,
        conversation_id=conversation_id,
        role=payload.role.value,
        content=payload.content,
        metadata=payload.metadata,
    )
