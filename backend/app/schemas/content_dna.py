"""Content DNA schema.

Content DNA is the single structured representation of "what a video means".
It is extracted exactly once per video and reused for every downstream
content transformation, so we never analyze the same video twice.
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """A single notable moment within the video."""

    timestamp_seconds: float = Field(..., description="Offset into the video, in seconds.")
    label: str = Field(..., description="Short description of what happens at this moment.")


class ContentDNA(BaseModel):
    """Structured, reusable understanding of a video's content.

    This object is generated once by the Understanding Engine and persisted.
    Every call to /generate reuses this object instead of re-analyzing the
    source video.
    """

    video_id: str
    title: str
    summary: str
    core_message: str
    tone: str = Field(..., description="Overall detected tone, e.g. 'informative', 'energetic'.")
    sentiment: str = Field(..., description="Overall sentiment, e.g. 'positive', 'neutral'.")

    timeline: List[TimelineEvent] = Field(default_factory=list)
    key_events: List[str] = Field(default_factory=list)
    detected_objects: List[str] = Field(default_factory=list)
    people: List[str] = Field(default_factory=list)
    activities: List[str] = Field(default_factory=list)
    important_timestamps: List[TimelineEvent] = Field(default_factory=list)

    keywords: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    context: str = ""

    model_config = {
        "json_schema_extra": {
            "example": {
                "video_id": "vid_123",
                "title": "Launching our new AI feature",
                "summary": "A short walkthrough of a new product feature and its impact.",
                "core_message": "This feature saves users significant time.",
                "tone": "energetic",
                "sentiment": "positive",
                "timeline": [{"timestamp_seconds": 4.5, "label": "Feature demo begins"}],
                "key_events": ["Product demo", "Customer testimonial"],
                "detected_objects": ["laptop", "dashboard UI"],
                "people": ["speaker"],
                "activities": ["presenting", "typing"],
                "important_timestamps": [],
                "keywords": ["AI", "productivity", "automation"],
                "entities": ["PersonaStudio AI"],
                "topics": ["product launch", "AI tooling"],
                "context": "Internal product demo video for a SaaS feature launch.",
            }
        }
    }
