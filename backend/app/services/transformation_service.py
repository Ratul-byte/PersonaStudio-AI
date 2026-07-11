"""Transformation Engine.

Takes an existing Content DNA plus (audience, platform, purpose, tone) and
produces one piece of generated content. Never re-analyzes the video.
"""
import uuid
from datetime import datetime

from app.core.logger import get_logger
from app.database.base import Database
from app.models.records import GenerationRecord
from app.schemas.content_dna import ContentDNA
from app.schemas.generation import GenerationRequest, GenerationResult
from app.services.fireworks_service import AIProvider
from app.utils.prompt_loader import load_prompt

logger = get_logger(__name__)


class TransformationService:
    """Generates persona/platform/purpose/tone-specific content from Content DNA."""

    def __init__(self, db: Database, ai_provider: AIProvider):
        self._db = db
        self._ai = ai_provider

    async def generate(self, request: GenerationRequest, dna: ContentDNA) -> GenerationResult:
        style_guide = load_prompt(request.tone.value)

        prompt = load_prompt("transformation").format(
            content_dna=dna.model_dump_json(),
            persona=request.persona.value,
            platform=request.platform.value,
            purpose=request.purpose.value,
            style_guide=style_guide,
        )

        content = await self._ai.complete(prompt, max_tokens=900, temperature=0.75)

        record = GenerationRecord(
            id=f"gen_{uuid.uuid4().hex[:12]}",
            video_id=request.video_id,
            persona=request.persona.value,
            platform=request.platform.value,
            purpose=request.purpose.value,
            tone=request.tone.value,
            content=content.strip(),
            created_at=datetime.utcnow(),
        )
        await self._db.save_generation(record)
        logger.info(
            "Generated content %s for video=%s persona=%s platform=%s purpose=%s tone=%s",
            record.id, request.video_id, request.persona, request.platform, request.purpose, request.tone,
        )

        return GenerationResult(
            id=record.id,
            video_id=record.video_id,
            persona=request.persona,
            platform=request.platform,
            purpose=request.purpose,
            tone=request.tone,
            content=record.content,
            created_at=record.created_at,
        )
