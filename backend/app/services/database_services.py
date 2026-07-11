import os
from abc import ABC, abstractmethod
import json
import asyncio
from typing import Any
from supabase import create_client, Client

from app.core.config import get_settings
from app.core.logger import get_logger
from datetime import datetime, timezone

logger = get_logger(__name__)

class VideoRecord:
    """Dynamic model wrapper to offer robust property lookups and fallbacks 

    for Supabase rows, ensuring API and Pydantic serialization safety.
    """
    def __init__(self, d: dict):
        # Set every column key from Supabase as a class attribute dynamically
        for key, value in d.items():
            setattr(self, key, value)
        
        # Baseline explicit structural property map
        if not hasattr(self, "video_id"):          self.video_id = d.get("video_id")
        if not hasattr(self, "filename"):          self.filename = d.get("filename")
        if not hasattr(self, "storage_path"):      self.storage_path = d.get("storage_path")
        if not hasattr(self, "raw_signal"):        self.raw_signal = d.get("raw_signal")

    def __getattr__(self, name: str) -> Any:
        """Catch-all fallback handler for any missing attributes."""
        # Capture the record's creation timestamp or default to now
        db_timestamp = self.__dict__.get("created_at")
        if isinstance(db_timestamp, str):
            try:
                fallback_dt = datetime.fromisoformat(db_timestamp.replace("Z", "+00:00"))
            except Exception:
                fallback_dt = datetime.now(timezone.utc)
        else:
            fallback_dt = datetime.now(timezone.utc)

        # Specific type-safe defaults for fields requested across routes
        defaults = {
            "duration_seconds": 0.0,
            "size_bytes": 0,
            "content_type": "video/mp4",
            "status": "completed",
            "uploaded_at": fallback_dt,
            "analyzed_at": fallback_dt,
            
            # --- ADD THESE VALID CODES FOR THE HISTORICAL ENUMS ---
            "platform": "linkedin",         # Must be 'linkedin', 'instagram', 'x', 'youtube', 'blog' or 'newsletter'
            "purpose": "caption",          # Must be 'caption', 'summary', 'blog', 'article', etc.
            "tone": "professional",        # Must be 'formal', 'sarcastic', 'professional', 'casual', etc.
            "persona": "developer",  # Must be 'developer', 'researcher', 'teacher', 'ceo', etc.
            "content": ""                  # Must be a valid text string string
            # ------------------------------------------------------
        }
        return defaults.get(name, None)


class DatabaseProvider(ABC):
    """Abstract interface for persisting video metadata records."""
    @abstractmethod
    async def save_video_metadata(self, video_id: str, filename: str, storage_path: str) -> dict:
        ...

    @abstractmethod
    async def update_video_transcript(self, video_id: str, transcript: str) -> bool:
        ...


class JsonDatabaseProvider(DatabaseProvider):
    """Fallback database using a local JSON file on disk."""
    def __init__(self, file_path: str):
        self.file_path = file_path

    async def save_video_metadata(self, video_id: str, filename: str, storage_path: str) -> dict:
        # Existing local JSON saving code...
        pass

    async def update_video_transcript(self, video_id: str, transcript: str) -> bool:
        # Existing local JSON updating code...
        pass


class SupabaseDatabaseProvider(DatabaseProvider):
    """Production PostgreSQL database provider via Supabase."""
    def __init__(self, url: str, key: str):
        if not (url and key):
            raise ValueError("Supabase URL and API Key are required for the Database Provider.")
        self.supabase: Client = create_client(url, key)

    async def save_video(self, record: Any) -> None:
        """Called by video_service.py to save a pre-built record object."""
        logger.info("Inserting record into Supabase public.videos for video_id '%s'...", record.video_id)
        try:
            payload = {
                "video_id": record.video_id,
                "filename": record.filename,
                "storage_path": record.storage_path,
                "raw_signal": getattr(record, "raw_signal", None)
            }
            
            await asyncio.to_thread(
                self.supabase.table("videos").insert(payload).execute
            )
            logger.info("Successfully saved record to Supabase!")
        except Exception as e:
            logger.error("Failed to insert record into Supabase: %s", e)
            raise e

    async def save_video_metadata(self, video_id: str, filename: str, storage_path: str) -> dict:
        """Satisfies the abstract Base class 'Database' requirements."""
        logger.info("Fulfilling abstract interface call for save_video_metadata.")
        payload = {
            "video_id": video_id,
            "filename": filename,
            "storage_path": storage_path
        }
        try:
            res = await asyncio.to_thread(
                self.supabase.table("videos").insert(payload).execute
            )
            return res.data[0] if res.data else {}
        except Exception as e:
            logger.error("Failed in save_video_metadata: %s", e)
            raise e

    async def update_video(self, video: Any) -> None:
        """Updates an existing video record's dynamic properties in Supabase."""
        logger.info("Updating fields in Supabase public.videos for video_id '%s'...", video.video_id)
        try:
            payload = {
                "filename": getattr(video, "filename", None),
                "storage_path": getattr(video, "storage_path", None),
                "raw_signal": getattr(video, "raw_signal", None),
                
                # --- ADD THIS LINE HERE TO SAVE THE STRUCTURED JSON ---
                "content_dna": getattr(video, "content_dna", None),
                # ------------------------------------------------------
                
                "duration_seconds": getattr(video, "duration_seconds", 0.0),
                "size_bytes": getattr(video, "size_bytes", 0),
                "content_type": getattr(video, "content_type", "video/mp4"),
                "status": getattr(video, "status", "completed"),
            }
            
            payload = {k: v for k, v in payload.items() if v is not None or k in ["raw_signal", "content_dna"]}

            await asyncio.to_thread(
                self.supabase.table("videos")
                .update(payload)
                .eq("video_id", video.video_id)
                .execute
            )
            logger.info("Successfully updated record in Supabase!")
        except Exception as e:
            logger.error("Failed to update record in Supabase: %s", e)
            raise e
        
    async def save_generation(self, record: Any) -> None:
        """Persists a newly created content generation result into Supabase."""
        logger.info("Saving new generation result to database tracking layers...")
        try:
            # Safely handle both Pydantic schemas or standard objects/dictionaries
            if hasattr(record, "model_dump"):
                payload = record.model_dump()
            elif hasattr(record, "__dict__"):
                payload = {k: v for k, v in record.__dict__.items() if not k.startswith("_")}
            else:
                payload = dict(record)

            # Ensure any datetime objects are converted to ISO format strings for Postgres
            for key, val in payload.items():
                if hasattr(val, "isoformat"):
                    payload[key] = val.isoformat()

            await asyncio.to_thread(
                self.supabase.table("generations")
                .insert(payload)
                .execute
            )
            logger.info("Successfully saved generation item to Supabase table public.generations!")
        except Exception as e:
            logger.error("Failed to insert generation record into Supabase: %s", e)
            raise e

    async def update_video_transcript(self, video_id: str, transcript: str) -> bool:
        """Updates the transcript field (raw_signal) for a given video."""
        logger.info("Updating transcript for video_id '%s' in Supabase...", video_id)
        try:
            await asyncio.to_thread(
                self.supabase.table("videos")
                .update({"raw_signal": transcript})
                .eq("video_id", video_id)
                .execute
            )
            logger.info("Successfully updated transcript in Supabase!")
            return True
        except Exception as e:
            logger.error("Failed to update transcript in Supabase: %s", e)
            return False

    async def get_video(self, video_id: str) -> Any:
        """Retrieves a single video record from Supabase and packs it into a compatible object."""
        logger.info("Fetching record from Supabase public.videos for video_id '%s'...", video_id)
        try:
            res = await asyncio.to_thread(
                self.supabase.table("videos")
                .select("*")
                .eq("video_id", video_id)
                .execute
            )
            
            if not res.data:
                logger.warning("No record found in Supabase for video_id '%s'", video_id)
                return None
                
            logger.info("Successfully retrieved record from Supabase!")
            return VideoRecord(res.data[0])
        except Exception as e:
            logger.error("Failed to fetch record from Supabase: %s", e)
            raise e

    async def list_generations(self, video_id: str = None) -> list[Any]:
        """Retrieves history logs from Supabase, optionally filtering by video_id."""
        logger.info("Listing records from Supabase public.videos tracking system...")
        try:
            query = self.supabase.table("generations").select("*")
            if video_id:
                query = query.eq("video_id", video_id)
                
            # --- CHANGE 'descending=True' TO 'desc=True' HERE ---
            res = await asyncio.to_thread(
                query.order("created_at", desc=True).execute
            )
            # ----------------------------------------------------
            
            if not res.data:
                logger.info("No records returned for current history layout search parameters.")
                return []
                
            logger.info("Successfully retrieved %d history items from Supabase!", len(res.data))
            return [VideoRecord(row) for row in res.data]
        except Exception as e:
            logger.error("Failed to list generations from Supabase context layout: %s", e)
            raise e


def get_database_provider() -> DatabaseProvider:
    """Factory returning the configured DatabaseProvider implementation."""
    settings = get_settings()
    provider = os.getenv("DATABASE_PROVIDER", "json").lower()
    
    if provider == "supabase":
        logger.info("Database engine initialized: Switched to cloud Supabase provider.")
        return SupabaseDatabaseProvider(
            url=settings.supabase_url,
            key=settings.supabase_key
        )
        
    logger.info("Database engine initialized: Falling back to local JSON database.")
    return JsonDatabaseProvider(settings.json_db_path)