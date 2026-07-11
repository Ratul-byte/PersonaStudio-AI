"""File storage adapter.

Abstracts *where* uploaded video bytes live. Local disk is used for the
JupyterLab MVP; Supabase Storage (or any object store) is a drop-in
replacement in production via STORAGE_PROVIDER.
"""
import os
from abc import ABC, abstractmethod

import aiofiles
from supabase import create_client, Client  # Added for production deployment

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class StorageProvider(ABC):
    """Abstract interface for persisting and retrieving raw video bytes."""

    @abstractmethod
    async def save(self, filename: str, content: bytes) -> str:
        """Persist ``content`` and return a storage path/URL."""
        ...

    @abstractmethod
    def resolve_path(self, storage_path: str) -> str:
        """Return a local, readable filesystem path for a stored file."""
        ...


class LocalStorageProvider(StorageProvider):
    """Stores video files on local disk (used during Phase 1 in JupyterLab)."""

    def __init__(self, base_path: str):
        self._base_path = base_path
        os.makedirs(self._base_path, exist_ok=True)

    async def save(self, filename: str, content: bytes) -> str:
        full_path = os.path.join(self._base_path, filename)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)
        return full_path

    def resolve_path(self, storage_path: str) -> str:
        return storage_path


class SupabaseStorageProvider(StorageProvider):
    """Production Supabase Storage implementation for Phase 2 deployment."""

    def __init__(self, url: str, key: str, bucket: str):
        self._url = url
        self._key = key
        self._bucket = bucket
        
        if not (self._url and self._key):
            raise ValueError("Supabase URL and API Key must be set in environment variables.")
        
        # Initialize the official client bindings
        self.supabase_client: Client = create_client(self._url, self._key)

    async def save(self, filename: str, content: bytes) -> str:
        """Uploads video bytes directly to the custom Supabase storage bucket."""
        logger.info("Uploading file '%s' to Supabase bucket '%s'...", filename, self._bucket)
        try:
            # Sync wrapper or raw bytes stream execution
            self.supabase_client.storage.from_(self._bucket).upload(
                path=filename,
                file=content,
                file_options={"content-type": "video/mp4"}
            )
            logger.info("Successfully uploaded '%s' to Supabase!", filename)
            
            # Return the filename/identifier as the unique storage tracking path
            return filename
        except Exception as e:
            logger.error("Failed to upload file to Supabase bucket: %s", e)
            raise e

    def resolve_path(self, storage_path: str) -> str:
        """Returns the internal storage path token for downstream consumption."""
        # Because downstream processing (dna_service) extracts metadata based on this string,
        # we return the direct cloud object key reference.
        return storage_path


def get_storage_provider() -> StorageProvider:
    """Factory forcing the configured Supabase StorageProvider implementation."""
    settings = get_settings()
    
    # Force application to use Supabase (Enforces Phase 2 layout strictly)
    logger.info("Storage engine initialized. Enforcing production Supabase provider.")
    return SupabaseStorageProvider(
        url=settings.supabase_url,
        key=settings.supabase_key,
        bucket=settings.supabase_bucket,
    )

    # -------------------------------------------------------------
    # LOCAL STORAGE TEMPORARILY DISABLED (COMMENTED OUT AS REQUESTED)
    # -------------------------------------------------------------
    # if settings.storage_provider == "supabase":
    #     return SupabaseStorageProvider(
    #         url=settings.supabase_url,
    #         key=settings.supabase_key,
    #         bucket=settings.supabase_bucket,
    #     )
    # return LocalStorageProvider(settings.local_storage_path)