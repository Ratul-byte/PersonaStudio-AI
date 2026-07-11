"""Custom exceptions and centralized error handlers for the API."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logger import get_logger

logger = get_logger(__name__)


class PersonaStudioError(Exception):
    """Base exception for all application-specific errors."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class VideoNotFoundError(PersonaStudioError):
    """Raised when a requested video_id does not exist."""

    def __init__(self, video_id: str):
        super().__init__(
            f"Video '{video_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ContentDNANotFoundError(PersonaStudioError):
    """Raised when generation is requested before a video has been analyzed."""

    def __init__(self, video_id: str):
        super().__init__(
            f"No Content DNA exists yet for video '{video_id}'. Call /analyze first.",
            status_code=status.HTTP_409_CONFLICT,
        )


class UnsupportedFileTypeError(PersonaStudioError):
    """Raised when an uploaded file is not a supported video format."""

    def __init__(self, filename: str):
        super().__init__(
            f"Unsupported file type for '{filename}'.",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


class AIProviderError(PersonaStudioError):
    """Raised when the upstream AI provider (Fireworks/Gemma) fails."""

    def __init__(self, message: str):
        super().__init__(
            f"AI provider error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach centralized exception handlers to the FastAPI app."""

    @app.exception_handler(PersonaStudioError)
    async def handle_app_error(request: Request, exc: PersonaStudioError) -> JSONResponse:
        logger.warning("Handled error on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred.",
            },
        )
