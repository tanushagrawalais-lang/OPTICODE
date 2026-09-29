"""Tests for error response consistency and handler behavior."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import AuthenticationError, AuthorizationError, NotFoundError


def test_app_error_returns_consistent_json(app: FastAPI, client: TestClient):
    """AppError subclasses produce the canonical error envelope."""

    @app.get("/test-not-found")
    async def _trigger():
        raise NotFoundError("Thing xyz not found")

    response = client.get("/test-not-found")
    assert response.status_code == 404

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert data["error"]["message"] == "Thing xyz not found"
    assert "request_id" in data["error"]


def test_auth_error_returns_401(app: FastAPI, client: TestClient):
    """AuthenticationError maps to 401."""

    @app.get("/test-auth")
    async def _trigger():
        raise AuthenticationError()

    response = client.get("/test-auth")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


def test_authorization_error_returns_403(app: FastAPI, client: TestClient):
    """AuthorizationError maps to 403."""

    @app.get("/test-authz")
    async def _trigger():
        raise AuthorizationError("Not your conversation")

    response = client.get("/test-authz")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AUTHORIZATION_ERROR"


def test_unhandled_exception_returns_safe_500(app: FastAPI, client: TestClient):
    """Unexpected exceptions return generic 500 without leaking internals."""

    @app.get("/test-crash")
    async def _trigger():
        raise RuntimeError("SECRET_DB_PASSWORD=hunter2")

    response = client.get("/test-crash")
    assert response.status_code == 500

    body = response.text
    assert "SECRET_DB_PASSWORD" not in body
    assert "hunter2" not in body
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"


def test_http_exception_uses_consistent_format(client: TestClient):
    """501 stubs (HTTPException) also use the error envelope."""
    response = client.post("/auth/signup")
    assert response.status_code == 501

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_ERROR"
    assert "not yet implemented" in data["error"]["message"].lower()


def test_all_stub_routes_return_501(client: TestClient):
    """Every remaining placeholder route returns 501 with a clear message."""
    stubs = [
        ("POST", "/auth/signup"),
        ("POST", "/auth/login"),
        ("POST", "/auth/logout"),
        ("POST", "/auth/refresh"),
        ("POST", "/code/optimize"),
        ("POST", "/code/fix"),
        ("POST", "/code/explain"),
    ]
    for method, path in stubs:
        response = client.request(method, path)
        assert response.status_code == 501, f"{method} {path} returned {response.status_code}"


def test_error_response_always_has_request_id(app: FastAPI, client: TestClient):
    """Error responses include the request_id for traceability."""

    @app.get("/test-rid-error")
    async def _trigger():
        raise NotFoundError("gone")

    response = client.get("/test-rid-error")
    assert "request_id" in response.json()["error"]
