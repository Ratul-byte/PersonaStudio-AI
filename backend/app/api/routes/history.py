"""GET /history — list past generations (optionally filtered by video)."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.database.base import Database
from app.schemas.generation import GenerationResult

router = APIRouter(tags=["history"])


@router.get("/history", response_model=List[GenerationResult])
async def list_history(
    video_id: Optional[str] = Query(default=None),
    db: Database = Depends(get_db),
) -> List[GenerationResult]:
    """Return generation history, most recent first."""
    records = await db.list_generations(video_id=video_id)
    results = [
        GenerationResult(
            id=r.id,
            video_id=r.video_id,
            persona=r.persona,
            platform=r.platform,
            purpose=r.purpose,
            tone=r.tone,
            content=r.content,
            created_at=r.created_at,
        )
        for r in records
    ]
    return sorted(results, key=lambda r: r.created_at, reverse=True)
