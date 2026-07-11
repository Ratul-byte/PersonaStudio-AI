"""Lightweight internal record types.

These sit between the persistence layer (app/database) and the API-facing
Pydantic schemas (app/schemas). Kept as dataclasses since they are internal
and don't need Pydantic's validation/serialization overhead.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class VideoRecord:
    """Internal representation of a stored video row."""

    video_id: str
    filename: str
    storage_path: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    status: str = "uploaded"
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    analyzed_at: Optional[datetime] = None
    content_dna: Optional[Dict[str, Any]] = None


@dataclass
class GenerationRecord:
    """Internal representation of a stored generation-history row."""

    id: str
    video_id: str
    persona: str
    platform: str
    purpose: str
    tone: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
