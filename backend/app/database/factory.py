"""Factory that returns the configured Database implementation.

Services and routes should depend on ``get_database`` (via FastAPI's
dependency injection) rather than importing a concrete implementation
directly. This keeps the persistence layer swappable.
"""
from functools import lru_cache

from app.core.config import get_settings
from app.database.base import Database
from app.database.json_db import JSONDatabase
# Import the new Supabase provider you just built
from app.services.database_services import SupabaseDatabaseProvider


@lru_cache
def get_database() -> Database:
    """Return a singleton Database instance based on DATABASE_PROVIDER."""
    settings = get_settings()

    if settings.database_provider == "supabase":
        # Initialize and return the live Supabase provider instead of raising an error
        return SupabaseDatabaseProvider(
            url=settings.supabase_url, 
            key=settings.supabase_key
        )

    return JSONDatabase(settings.json_db_path)