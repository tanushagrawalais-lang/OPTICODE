"""
OptiCode Backend A — Structured exception hierarchy.

All application errors inherit from AppError. Each error type
maps to a specific HTTP status code and a machine-readable code
used in the JSON error response.
"""


class AppError(Exception):
    """Base exception for all OptiCode application errors."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str = "An internal error occurred."):
        self.message = message
        super().__init__(message)


class ValidationError(AppError):
    """Request data failed application-level validation."""

    status_code = 422
    code = "VALIDATION_ERROR"

    def __init__(self, message: str = "Invalid request data."):
        super().__init__(message)


class AuthenticationError(AppError):
    """Request lacks valid authentication credentials."""

    status_code = 401
    code = "AUTHENTICATION_ERROR"

    def __init__(self, message: str = "Authentication required."):
        super().__init__(message)


class AuthorizationError(AppError):
    """Authenticated user lacks permission for the resource."""

    status_code = 403
    code = "AUTHORIZATION_ERROR"

    def __init__(self, message: str = "Access denied."):
        super().__init__(message)


class NotFoundError(AppError):
    """Requested resource does not exist."""

    status_code = 404
    code = "NOT_FOUND"

    def __init__(self, message: str = "Resource not found."):
        super().__init__(message)


class ExternalServiceError(AppError):
    """An external dependency (Backend B, AI provider) failed."""

    status_code = 502
    code = "EXTERNAL_SERVICE_ERROR"

    def __init__(self, message: str = "An external service is unavailable."):
        super().__init__(message)


class ConfigurationError(AppError):
    """Application configuration is invalid or incomplete."""

    status_code = 500
    code = "CONFIGURATION_ERROR"

    def __init__(self, message: str = "Application configuration error."):
        super().__init__(message)


class InternalError(AppError):
    """Catch-all for unexpected internal failures."""

    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str = "An unexpected error occurred."):
        super().__init__(message)
