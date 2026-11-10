"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "ClauseClear"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1

    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    secret_key: str = "change-me-in-production"
    max_upload_size_mb: int = 25
    request_timeout_seconds: int = 30
    max_extracted_chars: int = 200_000

    rate_limit_health: int = 60
    rate_limit_ingest: int = 10
    rate_limit_analyze: int = 10
    rate_limit_chat: int = 20
    rate_limit_default: int = 60

    llm_provider: str = "none"  # none | ollama | openai-compatible
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    database_url: str = "sqlite:///./clauseclear.db"

    document_retention_days: int = 30

    export_max_chars: int = 500_000

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def validate_production_settings(s: Settings) -> list[str]:
    """Return warnings for production-deployed settings that are unsafe."""
    warnings: list[str] = []
    if s.is_production:
        if s.secret_key == "change-me-in-production":
            warnings.append("SECRET_KEY is using the default insecure value")
        if s.debug:
            warnings.append("DEBUG is enabled in production")
        if "*" in s.cors_origins:
            warnings.append("CORS_ORIGINS allows all origins (*)")
        if s.llm_provider == "none":
            warnings.append("No LLM provider configured — running rule-based only")
    return warnings
