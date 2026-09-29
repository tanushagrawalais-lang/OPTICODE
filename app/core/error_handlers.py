"""
OptiCode Backend A — FastAPI exception handlers.

Registers handlers that convert exceptions into consistent JSON error
responses. Internal details (stack traces, file paths, secrets) are
logged but never sent to clients.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.core.context import get_request_id
from app.core.errors import AppError

logger = logging.getLogger(__name__)


def _error_body(status_code: int, code: str, message: str) -> dict:
    """Build the canonical error response dict."""
    body: dict = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    rid = get_request_id()
    if rid:
        body["error"]["request_id"] = rid
    return body


async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    """Handle application-defined errors (AppError subclasses)."""
    logger.warning("app_error: code=%s message=%s", exc.code, exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, exc.code, exc.message),
    )


async def _handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle Starlette/FastAPI HTTPExceptions with consistent format."""
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, "HTTP_ERROR", detail),
    )


async def _handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic request-validation errors with a user-friendly summary."""
    messages = []
    for err in exc.errors():
        loc = " → ".join(str(p) for p in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        messages.append(f"{loc}: {msg}" if loc else msg)
    detail = "; ".join(messages) if messages else "Invalid request data."
    return JSONResponse(
        status_code=422,
        content=_error_body(422, "VALIDATION_ERROR", detail),
    )


async def _handle_unhandled(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected exceptions. Log full traceback; return safe 500."""
    logger.exception("unhandled_error: %s", type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content=_error_body(500, "INTERNAL_ERROR", "An unexpected error occurred."),
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application."""
    app.add_exception_handler(AppError, _handle_app_error)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _handle_validation_error)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _handle_unhandled)  # type: ignore[arg-type]
