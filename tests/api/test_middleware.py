"""Tests for middleware behavior: request ID and CORS."""

import uuid


class TestRequestIDMiddleware:
    """Tests for the X-Request-Id middleware."""

    def test_generates_id_when_missing(self, client):
        """Requests without X-Request-Id get a UUID generated."""
        response = client.get("/health")
        rid = response.headers["x-request-id"]
        uuid.UUID(rid)  # Raises if not a valid UUID

    def test_preserves_safe_incoming_id(self, client):
        """Safe incoming X-Request-Id values are echoed back."""
        custom_id = "my-request-abc-123"
        response = client.get("/health", headers={"X-Request-Id": custom_id})
        assert response.headers["x-request-id"] == custom_id

    def test_replaces_unsafe_id(self, client):
        """IDs with special characters are replaced with a fresh UUID."""
        unsafe = "<script>alert(1)</script>"
        response = client.get("/health", headers={"X-Request-Id": unsafe})
        rid = response.headers["x-request-id"]
        assert rid != unsafe
        uuid.UUID(rid)  # Should be a valid UUID

    def test_replaces_overlong_id(self, client):
        """IDs exceeding 64 characters are replaced."""
        long_id = "a" * 100
        response = client.get("/health", headers={"X-Request-Id": long_id})
        rid = response.headers["x-request-id"]
        assert rid != long_id
        uuid.UUID(rid)


class TestCORSMiddleware:
    """Tests for CORS header behavior."""

    def test_allowed_origin_gets_cors_header(self, client):
        """Configured origins receive Access-Control-Allow-Origin."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_disallowed_origin_no_cors_header(self, client):
        """Unconfigured origins do not receive CORS headers."""
        response = client.get(
            "/health",
            headers={"Origin": "http://evil-site.com"},
        )
        allow = response.headers.get("access-control-allow-origin")
        assert allow != "http://evil-site.com"

    def test_preflight_returns_cors_headers(self, client):
        """OPTIONS preflight from allowed origin gets proper CORS headers."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_request_id_exposed_in_cors(self, client):
        """X-Request-Id is listed in Access-Control-Expose-Headers."""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        exposed = response.headers.get("access-control-expose-headers", "")
        assert "x-request-id" in exposed.lower()
