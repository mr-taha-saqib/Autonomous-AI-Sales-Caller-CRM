"""Centralised application settings, loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App
    APP_NAME: str = "Algorixe Sales Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_BASE_URL: str = "http://localhost:8000"
    PUBLIC_BASE_URL: str = "http://localhost:8000"
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    LOG_LEVEL: str = "INFO"

    # Security
    SECRET_KEY: str = "dev-insecure-change-me-please-0123456789abcdef"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_BCRYPT_ROUNDS: int = 12
    RATE_LIMIT_PER_MINUTE: int = 120

    # Database
    DATABASE_URL: str = (
        "postgresql+psycopg://algorixe:algorixe_secret@db:5432/algorixe"
    )

    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_CALLER_ID: str = ""
    TWILIO_VOICE: str = "Polly.Joanna-Neural"
    TWILIO_REGION: str = "us1"

    # Claude
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-opus-4-8"
    CLAUDE_FAST_MODEL: str = "claude-sonnet-4-6"
    CLAUDE_MAX_TOKENS: int = 1024
    CLAUDE_TEMPERATURE: float = 0.6

    @property
    def cors_origins(self) -> List[str]:
        return [self.FRONTEND_ORIGIN, "http://localhost:3000"]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @field_validator("DATABASE_URL")
    @classmethod
    def _normalize_db_url(cls, v: str) -> str:
        # Allow plain `postgresql://` and upgrade to the psycopg v3 driver.
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
