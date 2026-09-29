"""API tests for /conversations endpoints including ownership and error states."""

from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_conversation_repo
from app.repositories.conversation_repo import ConversationRepository


def _make_fake_conv(conv_id, user_id, title="Test Conversation"):
    now = datetime.now(UTC).isoformat()
    return {
        "id": str(conv_id),
        "user_id": str(user_id),
        "title": title,
        "created_at": now,
        "updated_at": now,
    }


def test_conversations_unauthenticated_returns_401(client: TestClient):
    """Requests without auth header return 401."""
    response = client.get("/conversations")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


def test_create_conversation_success(app: FastAPI, client: TestClient):
    """POST /conversations creates a new conversation with 201."""
    user_id = uuid4()
    conv_id = uuid4()

    mock_repo = MagicMock(spec=ConversationRepository)
    mock_repo.create.return_value = _make_fake_conv(conv_id, user_id, "Code Review")
    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = client.post(
        "/conversations",
        headers={"Authorization": f"Bearer {user_id}"},
        json={"title": "Code Review"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == str(conv_id)
    assert data["user_id"] == str(user_id)
    assert data["title"] == "Code Review"


def test_create_conversation_validation_error(app: FastAPI, client: TestClient):
    """Empty title returns 422 validation error."""
    user_id = uuid4()
    mock_repo = MagicMock(spec=ConversationRepository)
    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = client.post(
        "/conversations",
        headers={"Authorization": f"Bearer {user_id}"},
        json={"title": ""},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_list_conversations_success(app: FastAPI, client: TestClient):
    """GET /conversations lists user's conversations."""
    user_id = uuid4()
    mock_repo = MagicMock(spec=ConversationRepository)
    mock_repo.list_for_user.return_value = [
        _make_fake_conv(uuid4(), user_id, "Conv 1"),
        _make_fake_conv(uuid4(), user_id, "Conv 2"),
    ]
    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = client.get(
        "/conversations?limit=10&offset=0",
        headers={"Authorization": f"Bearer {user_id}"},
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2


def test_get_conversation_success(app: FastAPI, client: TestClient):
    """GET /conversations/{id} returns conversation for owner."""
    user_id = uuid4()
    conv_id = uuid4()
    mock_repo = MagicMock(spec=ConversationRepository)
    mock_repo.get_by_id.return_value = _make_fake_conv(conv_id, user_id, "Detail Conv")
    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = client.get(
        f"/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {user_id}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(conv_id)


def test_get_conversation_not_found(app: FastAPI, client: TestClient):
    """GET /conversations/{id} returns 404 if conversation does not exist."""
    user_id = uuid4()
    conv_id = uuid4()
    mock_repo = MagicMock(spec=ConversationRepository)
    mock_repo.get_by_id.return_value = None
    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = client.get(
        f"/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {user_id}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_conversation_unauthorized_user_returns_403(app: FastAPI, client: TestClient):
    """User B attempting to read User A's conversation receives 403."""
    owner_id = uuid4()
    attacker_id = uuid4()
    conv_id = uuid4()

    mock_repo = MagicMock(spec=ConversationRepository)
    mock_repo.get_by_id.return_value = _make_fake_conv(conv_id, owner_id, "Private Chat")
    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = client.get(
        f"/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {attacker_id}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AUTHORIZATION_ERROR"


def test_update_conversation_success(app: FastAPI, client: TestClient):
    """PATCH /conversations/{id} updates title for owner."""
    user_id = uuid4()
    conv_id = uuid4()

    mock_repo = MagicMock(spec=ConversationRepository)
    mock_repo.get_by_id.return_value = _make_fake_conv(conv_id, user_id, "Original")
    mock_repo.update.return_value = _make_fake_conv(conv_id, user_id, "Renamed")
    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = client.patch(
        f"/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {user_id}"},
        json={"title": "Renamed"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Renamed"


def test_update_conversation_unauthorized_returns_403(app: FastAPI, client: TestClient):
    """PATCH /conversations/{id} by non-owner returns 403."""
    owner_id = uuid4()
    attacker_id = uuid4()
    conv_id = uuid4()

    mock_repo = MagicMock(spec=ConversationRepository)
    mock_repo.get_by_id.return_value = _make_fake_conv(conv_id, owner_id, "Original")
    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = client.patch(
        f"/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {attacker_id}"},
        json={"title": "Hacked"},
    )
    assert response.status_code == 403


def test_delete_conversation_success(app: FastAPI, client: TestClient):
    """DELETE /conversations/{id} returns 204 for owner."""
    user_id = uuid4()
    conv_id = uuid4()

    mock_repo = MagicMock(spec=ConversationRepository)
    mock_repo.get_by_id.return_value = _make_fake_conv(conv_id, user_id)
    mock_repo.delete.return_value = True
    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = client.delete(
        f"/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {user_id}"},
    )
    assert response.status_code == 204
    assert response.text == ""


def test_delete_conversation_unauthorized_returns_403(app: FastAPI, client: TestClient):
    """DELETE /conversations/{id} by non-owner returns 403."""
    owner_id = uuid4()
    attacker_id = uuid4()
    conv_id = uuid4()

    mock_repo = MagicMock(spec=ConversationRepository)
    mock_repo.get_by_id.return_value = _make_fake_conv(conv_id, owner_id)
    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = client.delete(
        f"/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {attacker_id}"},
    )
    assert response.status_code == 403
