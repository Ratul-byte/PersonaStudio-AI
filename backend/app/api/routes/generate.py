"""POST /generate — transforms existing Content DNA into new content."""
from fastapi import APIRouter, Depends

from app.api.deps import get_transformation_service, get_video_service
from app.core.exceptions import ContentDNANotFoundError
from app.schemas.content_dna import ContentDNA
from app.schemas.generation import GenerationRequest, GenerationResult
from app.services.transformation_service import TransformationService
from app.services.video_service import VideoService

router = APIRouter(tags=["generate"])


@router.post("/generate", response_model=GenerationResult)
async def generate_content(
    request: GenerationRequest,
    video_service: VideoService = Depends(get_video_service),
    transformation_service: TransformationService = Depends(get_transformation_service),
) -> GenerationResult:
    """Generate one piece of content for (persona, platform, purpose, tone).

    Requires that ``/analyze`` has already been called for this video —
    the video itself is never touched here, only its Content DNA.
    """
    video = await video_service.get_video(request.video_id)
    if not video.content_dna:
        raise ContentDNANotFoundError(request.video_id)

    dna = ContentDNA(**video.content_dna)
    result = await transformation_service.generate(request, dna)
    return result
