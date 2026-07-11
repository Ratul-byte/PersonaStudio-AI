"""GET /video/{id} — returns stored metadata for a video."""
from fastapi import APIRouter, Depends

from app.api.deps import get_video_service
from app.schemas.video import VideoMetadata
from app.services.video_service import VideoService

router = APIRouter(tags=["video"])


@router.get("/video/{video_id}", response_model=VideoMetadata)
async def get_video(
    video_id: str,
    video_service: VideoService = Depends(get_video_service),
) -> VideoMetadata:
    """Return metadata for a previously uploaded video."""
    record = await video_service.get_video(video_id)
    return VideoMetadata(
        video_id=record.video_id,
        filename=record.filename,
        duration_seconds=record.duration_seconds,
        size_bytes=record.size_bytes,
        content_type=record.content_type,
        storage_path=record.storage_path,
        status=record.status,
        uploaded_at=record.uploaded_at,
        analyzed_at=record.analyzed_at,
    )
