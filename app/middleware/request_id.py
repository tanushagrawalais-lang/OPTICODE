"""
OptiCode Backend A — Request ID middleware.

Ensures every request has a unique, traceable ID that is:
  - stored in a context variable (accessible to logging and error handlers)
  - attached to request.state
  - returned in the X-Request-Id response header
"""

import re
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import request_id_ctx

HEADER_NAME = "X-Request-Id"

# Accept only safe request IDs: alphanumeric with hyphens, max 64 chars.
_SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9\-]{1,64}$")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that attaches a unique request ID to every request/response cycle."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming = request.headers.get(HEADER_NAME, "")
        rid = incoming if incoming and _SAFE_ID_PATTERN.match(incoming) else str(uuid.uuid4())

        request.state.request_id = rid
        token = request_id_ctx.set(rid)
        try:
            response = await call_next(request)
            response.headers[HEADER_NAME] = rid
            return response
        finally:
            request_id_ctx.reset(token)
