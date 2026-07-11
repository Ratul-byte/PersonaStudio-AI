"""Local JSON-file database implementation.

Good enough for the hackathon MVP running inside JupyterLab. Implements the
same ``Database`` interface as the future Supabase-backed implementation so
no service code needs to change when we move to production.
"""
import asyncio
import json
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.logger import get_logger
from app.database.base import Database
from app.models.records import GenerationRecord, VideoRecord

logger = get_logger(__name__)


def _serialize(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


class JSONDatabase(Database):
    """A minimal, file-backed persistence layer."""

    def __init__(self, path: str):
        self._path = path
        self._lock = asyncio.Lock()
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if not os.path.exists(path):
            self._write({"videos": {}, "generations": []})

    def _read(self) -> Dict[str, Any]:
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: Dict[str, Any]) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, default=_serialize, indent=2)

    async def save_video(self, video: VideoRecord) -> VideoRecord:
        async with self._lock:
            data = self._read()
            data["videos"][video.video_id] = asdict(video)
            self._write(data)
            logger.info("Saved video %s", video.video_id)
            return video

    async def get_video(self, video_id: str) -> Optional[VideoRecord]:
        data = self._read()
        raw = data["videos"].get(video_id)
        if raw is None:
            return None
        return VideoRecord(**raw)

    async def update_video(self, video: VideoRecord) -> VideoRecord:
        return await self.save_video(video)

    async def list_videos(self) -> List[VideoRecord]:
        data = self._read()
        return [VideoRecord(**v) for v in data["videos"].values()]

    async def save_generation(self, record: GenerationRecord) -> GenerationRecord:
        async with self._lock:
            data = self._read()
            data["generations"].append(asdict(record))
            self._write(data)
            logger.info("Saved generation %s for video %s", record.id, record.video_id)
            return record

    async def list_generations(self, video_id: Optional[str] = None) -> List[GenerationRecord]:
        data = self._read()
        records = [GenerationRecord(**g) for g in data["generations"]]
        if video_id:
            records = [r for r in records if r.video_id == video_id]
        return records
