"""Application configuration.

All configuration is environment-variable driven so the same codebase can run
unchanged inside AMD Developer Cloud JupyterLab (Phase 1) and on Render /
Vercel / Supabase in production (Phase 2). Never hardcode secrets or
localhost-only assumptions here.
"""
from functools import lru_cache
from typing import List, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings, loaded from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "PersonaStudio AI"
    environment: Literal["development", "production", "test"] = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    # AI Provider
    ai_provider: Literal["fireworks", "mock"] = "mock"
    fireworks_api_key: str = ""
    fireworks_base_url: str = "https://api.fireworks.ai/inference/v1"
    gemma_model: str = "accounts/fireworks/models/gemma2-9b-it"

    # Storage
    storage_provider: Literal["local", "supabase"] = "local"
    local_storage_path: str = "./storage"
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_bucket: str = "videos"

    # Database
    database_provider: Literal["json", "supabase"] = "json"
    database_url: str = ""
    json_db_path: str = "./storage/db.json"

    # Queue (future use)
    redis_url: str = "redis://localhost:6379/0"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (avoids re-parsing env on every call)."""
    return Settings()
