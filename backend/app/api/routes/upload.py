"""POST /upload — accepts a video file and returns a video_id."""
from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_video_service
from app.schemas.video import VideoUploadResponse
from app.services.video_service import VideoService

router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    video_service: VideoService = Depends(get_video_service),
) -> VideoUploadResponse:
    """Upload a video. The video is stored but NOT analyzed yet.

    Call ``POST /analyze`` afterwards to run the Understanding Engine.
    """
    content = await file.read()
    record = await video_service.upload_video(
        filename=file.filename or "upload.mp4",
        content=content,
        content_type=file.content_type,
    )
    return VideoUploadResponse(
        video_id=record.video_id,
        filename=record.filename,
        status=record.status,
        uploaded_at=record.uploaded_at,
    )
