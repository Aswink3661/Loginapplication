from functools import lru_cache
from typing import Any, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_bool(value: Any) -> Any:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug", "development", "dev"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "production", "prod"}:
            return False
    return value


class Settings(BaseSettings):
    # -------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------
    APP_NAME: str = "Todo API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # -------------------------------------------------------------------
    # Server
    # -------------------------------------------------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # -------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"
    LOG_TO_FILE: bool = True

    # -------------------------------------------------------------------
    # OpenTelemetry / MELT
    # -------------------------------------------------------------------
    OTEL_ENABLED: bool = True
    OTEL_EXPORTER: Literal["none", "console", "otlp"] = "otlp"
    OTEL_SERVICE_NAMESPACE: str = "loginapplication"
    OTEL_SERVICE_NAME: str = "todo-api"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    OTEL_EXPORTER_OTLP_HEADERS: str = ""
    OTEL_METRIC_EXPORT_INTERVAL_MS: int = 60_000

    # -------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("DEBUG", "LOG_TO_FILE", "OTEL_ENABLED", mode="before")
    @classmethod
    def parse_bool_settings(cls, value: Any) -> Any:
        return _parse_bool(value)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once at startup)."""
    return Settings()
