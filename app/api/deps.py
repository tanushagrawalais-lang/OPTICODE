"""
OptiCode Backend A — Shared FastAPI dependencies.

Provides reusable Depends callables for configuration, authentication,
data access, and services. Designed to be cleanly overridable in tests
via app.dependency_overrides.
"""

import json
from base64 import urlsafe_b64decode
from functools import lru_cache
from typing import Any
from uuid import UUID

from fastapi import Depends, Header

from app.config import Settings
from app.core.errors import AuthenticationError
from app.integrations.supabase_client import get_supabase_client
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.repositories.user_repo import UserRepository
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()


def get_supabase(settings: Settings = Depends(get_settings)) -> Any:
    """Provide the Supabase client instance.

    Override in tests:
        app.dependency_overrides[get_supabase] = lambda: mock_supabase_client
    """
    return get_supabase_client(settings)


# --- Repositories ---


def get_user_repo(supabase: Any = Depends(get_supabase)) -> UserRepository:
    """Provide a UserRepository bound to the current Supabase client."""
    return UserRepository(client=supabase)


def get_conversation_repo(
    supabase: Any = Depends(get_supabase),
) -> ConversationRepository:
    """Provide a ConversationRepository bound to the current Supabase client."""
    return ConversationRepository(client=supabase)


def get_message_repo(
    supabase: Any = Depends(get_supabase),
) -> MessageRepository:
    """Provide a MessageRepository bound to the current Supabase client."""
    return MessageRepository(client=supabase)


# --- Services ---


def get_conversation_service(
    repo: ConversationRepository = Depends(get_conversation_repo),
) -> ConversationService:
    """Provide a ConversationService."""
    return ConversationService(repo=repo)


def get_message_service(
    msg_repo: MessageRepository = Depends(get_message_repo),
    conv_repo: ConversationRepository = Depends(get_conversation_repo),
) -> MessageService:
    """Provide a MessageService."""
    return MessageService(message_repo=msg_repo, conversation_repo=conv_repo)


# --- Authentication / User Context ---


def get_current_user_id(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> UUID:
    """Extract and identify the authenticated user ID from the request headers.

    Accepts:
      - Authorization: Bearer <uuid>
      - Authorization: Bearer <jwt> (extracts 'sub' claim)
      - X-User-Id: <uuid> (development / test bypass)

    Raises:
        AuthenticationError: If credentials are missing or invalid.
    """
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_user_id:
        token = x_user_id.strip()

    if not token:
        raise AuthenticationError("Authentication required.")

    # Try 1: Direct UUID string
    try:
        return UUID(token)
    except ValueError:
        pass

    # Try 2: Unverified JWT payload inspection for 'sub'
    if token.count(".") == 2:
        try:
            payload_segment = token.split(".")[1]
            padded = payload_segment + "=" * (-len(payload_segment) % 4)
            claims = json.loads(urlsafe_b64decode(padded).decode("utf-8"))
            sub = claims.get("sub")
            if sub:
                return UUID(str(sub))
        except Exception:
            pass

    raise AuthenticationError("Invalid authentication credentials.")
