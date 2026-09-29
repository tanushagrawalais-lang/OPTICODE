"""
OptiCode Backend A — Conversation schemas.

Defines Pydantic request and response models for conversations.
Internal database implementation details are not leaked.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    """Payload for creating a new conversation."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Title or summary of the conversation.",
    )


class ConversationUpdate(BaseModel):
    """Payload for updating an existing conversation."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Updated title of the conversation.",
    )


class ConversationResponse(BaseModel):
    """Public representation of a conversation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
