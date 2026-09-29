"""
OptiCode Backend A — Message schemas.

Defines Pydantic request and response models for messages.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(StrEnum):
    """Allowed roles for a message."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageCreate(BaseModel):
    """Payload for creating a message in a conversation."""

    role: MessageRole = Field(
        default=MessageRole.USER,
        description="Role of the message sender.",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Text content of the message.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured metadata such as code snippets or analysis details.",
    )


class MessageResponse(BaseModel):
    """Public representation of a message."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    metadata: dict[str, Any]
    created_at: datetime
