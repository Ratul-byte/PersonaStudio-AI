"""Aggregates all route modules into a single API router."""
from fastapi import APIRouter

from app.api.routes import analyze, generate, history, upload, video

api_router = APIRouter()
api_router.include_router(upload.router)
api_router.include_router(video.router)
api_router.include_router(analyze.router)
api_router.include_router(generate.router)
api_router.include_router(history.router)
