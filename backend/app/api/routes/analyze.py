"""POST /analyze — runs the Understanding Engine and produces Content DNA."""
from pydantic import BaseModel

from fastapi import APIRouter, Depends

from app.api.deps import get_dna_service, get_video_service
from app.schemas.content_dna import ContentDNA
from app.services.dna_service import DNAService
from app.services.video_service import VideoService

router = APIRouter(tags=["analyze"])


class AnalyzeRequest(BaseModel):
    video_id: str
    raw_signal: str | None = None  # optional transcript / frame captions if available


@router.post("/analyze", response_model=ContentDNA)
async def analyze_video(
    payload: AnalyzeRequest,
    video_service: VideoService = Depends(get_video_service),
    dna_service: DNAService = Depends(get_dna_service),
) -> ContentDNA:
    """Extract (or reuse) Content DNA for a video.

    This is designed to run exactly once per video — subsequent calls
    return the already-persisted Content DNA instead of re-analyzing.
    """
    video = await video_service.get_video(payload.video_id)
    dna = await dna_service.analyze(video, raw_signal=payload.raw_signal)
    return dna
