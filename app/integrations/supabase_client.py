"""
OptiCode Backend A — Supabase Client Integration.

Provides a managed Supabase client initialized from application settings.
Does not instantiate a connection at module import time so tests and
unrelated routes run without external credentials.
"""


from app.config import Settings
from app.core.errors import ConfigurationError
from supabase import Client, create_client

_client_instance: Client | None = None


def create_supabase_client(settings: Settings) -> Client:
    """Instantiate a Supabase client using configured credentials.

    Raises:
        ConfigurationError: If SUPABASE_URL or appropriate key is missing.
    """
    if not settings.SUPABASE_URL:
        raise ConfigurationError("SUPABASE_URL is not configured.")

    # Backend A uses the service role key for trusted server-side persistence.
    # Fall back to anon key if service role key is not set.
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
    if not key:
        raise ConfigurationError("SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY must be set.")

    try:
        return create_client(settings.SUPABASE_URL, key)
    except Exception as exc:
        raise ConfigurationError(f"Failed to initialize Supabase client: {exc}") from exc


def get_supabase_client(settings: Settings) -> Client:
    """Singleton accessor for the application Supabase client."""
    global _client_instance
    if _client_instance is None:
        _client_instance = create_supabase_client(settings)
    return _client_instance


def reset_supabase_client() -> None:
    """Reset the cached client instance (primarily for testing)."""
    global _client_instance
    _client_instance = None
