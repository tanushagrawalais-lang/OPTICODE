"""
OptiCode Backend A — Application configuration.

Loads and validates settings from environment variables via pydantic-settings.
All secrets come from env vars — never hard-coded in source.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # --- Application ---
    APP_NAME: str = "OptiCode"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_PREFIX: str = ""
    LOG_LEVEL: str = "INFO"

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- CORS ---
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000"])

    # --- Supabase (not required for Phase 1) ---
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # --- AI Provider (not required for Phase 1) ---
    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # --- Backend B (not required for Phase 1) ---
    BACKEND_B_URL: str = "http://localhost:8001"
    BACKEND_B_TIMEOUT: float = 30.0

    @property
    def is_development(self) -> bool:
        """True when running in the development environment."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """True when running in the production environment."""
        return self.ENVIRONMENT == "production"
