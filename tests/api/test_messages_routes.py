"""API tests for /conversations/{conversation_id}/messages endpoints."""

from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_conversation_repo, get_message_repo
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository


def _make_fake_conv(conv_id, user_id):
    now = datetime.now(UTC).isoformat()
    return {
        "id": str(conv_id),
        "user_id": str(user_id),
        "title": "Parent Conversation",
        "created_at": now,
        "updated_at": now,
    }


def _make_fake_msg(msg_id, conv_id, role="user", content="Hello"):
    now = datetime.now(UTC).isoformat()
    return {
        "id": str(msg_id),
        "conversation_id": str(conv_id),
        "role": role,
        "content": content,
        "metadata": {},
        "created_at": now,
    }


def test_messages_unauthenticated_returns_401(client: TestClient):
    """Calling messages endpoint without auth header returns 401."""
    conv_id = uuid4()
    response = client.get(f"/conversations/{conv_id}/messages")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


def test_create_message_success(app: FastAPI, client: TestClient):
    """POST /conversations/{id}/messages creates a message with 201."""
    user_id = uuid4()
    conv_id = uuid4()
    msg_id = uuid4()

    mock_conv_repo = MagicMock(spec=ConversationRepository)
    mock_conv_repo.get_by_id.return_value = _make_fake_conv(conv_id, user_id)

    mock_msg_repo = MagicMock(spec=MessageRepository)
    mock_msg_repo.create.return_value = _make_fake_msg(
        msg_id, conv_id, role="user", content="Optimize this"
    )

    app.dependency_overrides[get_conversation_repo] = lambda: mock_conv_repo
    app.dependency_overrides[get_message_repo] = lambda: mock_msg_repo

    response = client.post(
        f"/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {user_id}"},
        json={"role": "user", "content": "Optimize this", "metadata": {"lang": "python"}},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == str(msg_id)
    assert data["conversation_id"] == str(conv_id)
    assert data["content"] == "Optimize this"


def test_create_message_validation_error(app: FastAPI, client: TestClient):
    """Empty content triggers 422 validation error."""
    user_id = uuid4()
    conv_id = uuid4()
    mock_conv_repo = MagicMock(spec=ConversationRepository)
    mock_msg_repo = MagicMock(spec=MessageRepository)
    app.dependency_overrides[get_conversation_repo] = lambda: mock_conv_repo
    app.dependency_overrides[get_message_repo] = lambda: mock_msg_repo

    response = client.post(
        f"/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {user_id}"},
        json={"role": "user", "content": ""},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_message_unauthorized_user_returns_403(app: FastAPI, client: TestClient):
    """User B trying to add a message to User A's conversation receives 403."""
    owner_id = uuid4()
    attacker_id = uuid4()
    conv_id = uuid4()

    mock_conv_repo = MagicMock(spec=ConversationRepository)
    mock_conv_repo.get_by_id.return_value = _make_fake_conv(conv_id, owner_id)
    mock_msg_repo = MagicMock(spec=MessageRepository)

    app.dependency_overrides[get_conversation_repo] = lambda: mock_conv_repo
    app.dependency_overrides[get_message_repo] = lambda: mock_msg_repo

    response = client.post(
        f"/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {attacker_id}"},
        json={"role": "user", "content": "Injected message"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AUTHORIZATION_ERROR"
    mock_msg_repo.create.assert_not_called()


def test_create_message_conversation_not_found_returns_404(app: FastAPI, client: TestClient):
    """Adding a message to a nonexistent conversation returns 404."""
    user_id = uuid4()
    conv_id = uuid4()

    mock_conv_repo = MagicMock(spec=ConversationRepository)
    mock_conv_repo.get_by_id.return_value = None
    mock_msg_repo = MagicMock(spec=MessageRepository)

    app.dependency_overrides[get_conversation_repo] = lambda: mock_conv_repo
    app.dependency_overrides[get_message_repo] = lambda: mock_msg_repo

    response = client.post(
        f"/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {user_id}"},
        json={"role": "user", "content": "Hello"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_list_messages_success(app: FastAPI, client: TestClient):
    """GET /conversations/{id}/messages returns chronological messages for owner."""
    user_id = uuid4()
    conv_id = uuid4()

    mock_conv_repo = MagicMock(spec=ConversationRepository)
    mock_conv_repo.get_by_id.return_value = _make_fake_conv(conv_id, user_id)

    mock_msg_repo = MagicMock(spec=MessageRepository)
    mock_msg_repo.list_for_conversation.return_value = [
        _make_fake_msg(uuid4(), conv_id, role="user", content="Step 1"),
        _make_fake_msg(uuid4(), conv_id, role="assistant", content="Step 2"),
    ]

    app.dependency_overrides[get_conversation_repo] = lambda: mock_conv_repo
    app.dependency_overrides[get_message_repo] = lambda: mock_msg_repo

    response = client.get(
        f"/conversations/{conv_id}/messages?limit=50&offset=0",
        headers={"Authorization": f"Bearer {user_id}"},
    )
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    assert messages[0]["content"] == "Step 1"


def test_list_messages_unauthorized_user_returns_403(app: FastAPI, client: TestClient):
    """User B trying to view messages in User A's conversation receives 403."""
    owner_id = uuid4()
    attacker_id = uuid4()
    conv_id = uuid4()

    mock_conv_repo = MagicMock(spec=ConversationRepository)
    mock_conv_repo.get_by_id.return_value = _make_fake_conv(conv_id, owner_id)
    mock_msg_repo = MagicMock(spec=MessageRepository)

    app.dependency_overrides[get_conversation_repo] = lambda: mock_conv_repo
    app.dependency_overrides[get_message_repo] = lambda: mock_msg_repo

    response = client.get(
        f"/conversations/{conv_id}/messages",
        headers={"Authorization": f"Bearer {attacker_id}"},
    )
    assert response.status_code == 403
    mock_msg_repo.list_for_conversation.assert_not_called()
