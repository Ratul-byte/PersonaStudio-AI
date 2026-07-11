"""Celery interface for future background/async processing.

Not yet wired into the request path — today, /analyze and /generate run
synchronously within the request. As videos and traffic grow, long-running
analysis can be moved here without changing the service layer, since
services already return plain data objects rather than HTTP responses.
"""
from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "personastudio",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="tasks.analyze_video_async")
def analyze_video_async(video_id: str) -> dict:
    """Placeholder task: would call DNAService.analyze() outside the request cycle.

    Left unimplemented intentionally — wire this up once queue-backed
    analysis is needed (e.g. very long videos, high concurrent load).
    """
    raise NotImplementedError("Async analysis task not yet implemented.")
