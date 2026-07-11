"""FastAPI dependency-injection providers.

Centralizes how services are constructed so routes stay thin and testable.
"""
from app.database.base import Database
from app.database.factory import get_database
from app.services.dna_service import DNAService
from app.services.fireworks_service import AIProvider, get_ai_provider
from app.services.storage_service import StorageProvider, get_storage_provider
from app.services.transformation_service import TransformationService
from app.services.video_service import VideoService


def get_db() -> Database:
    return get_database()


def get_storage() -> StorageProvider:
    return get_storage_provider()


def get_ai() -> AIProvider:
    return get_ai_provider()


def get_video_service() -> VideoService:
    return VideoService(db=get_db(), storage=get_storage())


def get_dna_service() -> DNAService:
    return DNAService(db=get_db(), ai_provider=get_ai())


def get_transformation_service() -> TransformationService:
    return TransformationService(db=get_db(), ai_provider=get_ai())
