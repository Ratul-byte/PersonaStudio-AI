"""Schemas for the content transformation ("/generate") endpoint."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Persona(str, Enum):
    """Audience the generated content should be tailored for."""

    DEVELOPER = "developer"
    RESEARCHER = "researcher"
    TEACHER = "teacher"
    STUDENT = "student"
    INVESTOR = "investor"
    JOURNALIST = "journalist"
    MARKETING = "marketing"
    RECRUITER = "recruiter"
    CEO = "ceo"


class Platform(str, Enum):
    """Destination platform for the generated content."""

    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    X = "x"
    YOUTUBE = "youtube"
    BLOG = "blog"
    NEWSLETTER = "newsletter"


class Purpose(str, Enum):
    """The kind of content to generate."""

    CAPTION = "caption"
    SUMMARY = "summary"
    BLOG = "blog"
    ARTICLE = "article"
    MEETING_NOTES = "meeting_notes"
    DOCUMENTATION = "documentation"
    RESEARCH_DRAFT = "research_draft"
    PRESS_RELEASE = "press_release"


class Tone(str, Enum):
    """Tone / preset applied to the generated content."""

    FORMAL = "formal"
    SARCASTIC = "sarcastic"
    HUMOROUS_TECH = "humorous_tech"
    HUMOROUS_NON_TECH = "humorous_non_tech"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"


class GenerationRequest(BaseModel):
    """Input payload for POST /generate."""

    video_id: str
    persona: Persona
    platform: Platform
    purpose: Purpose
    tone: Tone = Tone.PROFESSIONAL


class GenerationResult(BaseModel):
    """A single generated piece of content, persisted for history."""

    id: str
    video_id: str
    persona: Persona
    platform: Platform
    purpose: Purpose
    tone: Tone
    content: str
    created_at: datetime
