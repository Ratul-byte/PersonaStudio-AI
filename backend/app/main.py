"""PersonaStudio AI — FastAPI application entrypoint.

Runs locally inside AMD Developer Cloud JupyterLab during Phase 1, and
unchanged on Render during Phase 2 — all environment differences are
handled via app/core/config.py.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="One Video. Infinite Content. Every Audience.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/", tags=["health"])
    async def root() -> dict:
        return {"service": settings.app_name, "status": "ok"}

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return {"status": "healthy", "environment": settings.environment}

    logger.info("%s initialized (environment=%s, ai_provider=%s)",
                settings.app_name, settings.environment, settings.ai_provider)
    return app


app = create_app()
