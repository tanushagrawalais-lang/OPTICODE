"""Tests for the health check endpoint."""


def test_health_returns_200(client):
    """GET /health succeeds with 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_structure(client):
    """Health response contains the expected fields."""
    data = client.get("/health").json()
    assert data["status"] == "ok"
    assert data["service"] == "opticode-backend-a"


def test_health_includes_request_id_header(client):
    """Every response includes an X-Request-Id header."""
    response = client.get("/health")
    rid = response.headers.get("x-request-id")
    assert rid is not None
    assert len(rid) > 0
