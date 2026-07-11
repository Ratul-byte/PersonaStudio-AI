"""Schemas related to video upload and metadata."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VideoUploadResponse(BaseModel):
    """Response returned immediately after a successful upload."""

    video_id: str
    filename: str
    status: str = "uploaded"
    uploaded_at: datetime


class VideoMetadata(BaseModel):
    """Metadata describing a stored video."""

    video_id: str
    filename: str
    duration_seconds: Optional[float] = None
    size_bytes: Optional[int] = None
    content_type: Optional[str] = None
    storage_path: str
    status: str = "uploaded"  # uploaded | analyzing | analyzed | failed
    uploaded_at: datetime
    analyzed_at: Optional[datetime] = None
