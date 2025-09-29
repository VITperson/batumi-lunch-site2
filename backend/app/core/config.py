from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env files."""

    model_config = SettingsConfigDict(env_file=('.env', '.env.local'), env_file_encoding='utf-8', case_sensitive=False)

    project_name: str = Field(default="Batumi Lunch Platform")
    environment: Literal['local', 'test', 'development', 'staging', 'production'] = Field(default='local')
    api_v1_str: str = Field(default="/api/v1")
    database_url: str = Field(default="postgresql+asyncpg:///batumi_lunch")
    redis_url: str = Field(default="redis://localhost:6379/0")
    secret_key: str = Field(default="changeme")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=30)
    sms_sender_name: str = Field(default="BatumiLunch")
    sms_provider_url: str = Field(default="https://sms-gateway.local/send")
    s3_endpoint_url: str = Field(default="http://localhost:9000")
    s3_bucket_name: str = Field(default="batumi-lunch-media")
    gtm_id: str | None = Field(default=None)
    enable_feature_flags: bool = Field(default=True)
    feature_flags_cache_ttl: int = Field(default=60)

    sentry_dsn: str | None = Field(default=None)
    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=True)
    log_to_stdout: bool = Field(default=True)

    stripe_public_key: str | None = Field(default=None)
    stripe_secret_key: str | None = Field(default=None)
    sms_api_key: str | None = Field(default=None)

    root_path: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2])

    @property
    def is_debug(self) -> bool:
        return self.environment in {"local", "development"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


settings = get_settings()
