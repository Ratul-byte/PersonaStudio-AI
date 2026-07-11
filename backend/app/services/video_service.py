"""Video ingestion service.

Handles receiving an uploaded video, persisting it via the storage adapter,
extracting lightweight metadata, and recording it in the database. This
service does NOT perform semantic understanding — that's the DNA service's
job — it only deals with the raw file.
"""
import uuid
from datetime import datetime
from typing import Optional

from app.core.exceptions import UnsupportedFileTypeError, VideoNotFoundError
from app.core.logger import get_logger
from app.database.base import Database
from app.models.records import VideoRecord
from app.services.storage_service import StorageProvider

logger = get_logger(__name__)

SUPPORTED_CONTENT_TYPES = {"video/mp4", "video/quicktime", "video/x-matroska", "video/webm"}


class VideoService:
    """Coordinates video upload, storage, and metadata lookups."""

    def __init__(self, db: Database, storage: StorageProvider):
        self._db = db
        self._storage = storage

    async def upload_video(
        self, filename: str, content: bytes, content_type: Optional[str]
    ) -> VideoRecord:
        """Validate, store, and record a newly uploaded video."""
        if content_type and content_type not in SUPPORTED_CONTENT_TYPES:
            raise UnsupportedFileTypeError(filename)

        video_id = f"vid_{uuid.uuid4().hex[:12]}"
        stored_filename = f"{video_id}_{filename}"
        storage_path = await self._storage.save(stored_filename, content)

        duration_seconds = self._try_extract_duration(storage_path)

        record = VideoRecord(
            video_id=video_id,
            filename=filename,
            storage_path=storage_path,
            content_type=content_type,
            size_bytes=len(content),
            duration_seconds=duration_seconds,
            status="uploaded",
            uploaded_at=datetime.utcnow(),
        )
        await self._db.save_video(record)
        logger.info("Uploaded video %s (%s bytes)", video_id, len(content))
        return record

    async def get_video(self, video_id: str) -> VideoRecord:
        record = await self._db.get_video(video_id)
        if record is None:
            raise VideoNotFoundError(video_id)
        return record

    def _try_extract_duration(self, storage_path: str) -> Optional[float]:
        """Best-effort duration extraction via OpenCV; never fails the upload."""
        try:
            import cv2  # local import: optional / heavy dependency

            capture = cv2.VideoCapture(storage_path)
            fps = capture.get(cv2.CAP_PROP_FPS)
            frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
            capture.release()
            if fps and frame_count:
                return round(frame_count / fps, 2)
        except Exception as exc:  # noqa: BLE001 - best-effort, never fatal
            logger.warning("Could not extract video duration: %s", exc)
        return None
