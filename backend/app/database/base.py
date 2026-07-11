"""Abstract database interface.

Any concrete backend (local JSON file for the hackathon MVP, Supabase in
production) implements this interface. Services depend only on this
abstraction, so switching DATABASE_PROVIDER in .env is the only change
needed at deployment time.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.records import GenerationRecord, VideoRecord


class Database(ABC):
    """Abstract persistence interface used by all services."""

    @abstractmethod
    async def save_video(self, video: VideoRecord) -> VideoRecord:
        ...

    @abstractmethod
    async def get_video(self, video_id: str) -> Optional[VideoRecord]:
        ...

    @abstractmethod
    async def update_video(self, video: VideoRecord) -> VideoRecord:
        ...

    @abstractmethod
    async def list_videos(self) -> List[VideoRecord]:
        ...

    @abstractmethod
    async def save_generation(self, record: GenerationRecord) -> GenerationRecord:
        ...

    @abstractmethod
    async def list_generations(self, video_id: Optional[str] = None) -> List[GenerationRecord]:
        ...
