"""
OptiCode Backend A — Request-scoped context variables.

Provides context variables available throughout the request lifecycle:
middleware, services, error handlers, and logging.
"""

import contextvars

request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


def get_request_id() -> str:
    """Return the current request ID, or empty string if outside a request."""
    return request_id_ctx.get("")
