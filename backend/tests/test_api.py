"""End-to-end smoke tests for the core PersonaStudio AI flow.

Uses AI_PROVIDER=mock (see conftest/env) so tests run without any external
API key or network access.
"""
import io
import os

os.environ.setdefault("AI_PROVIDER", "mock")
os.environ.setdefault("DATABASE_PROVIDER", "json")
os.environ.setdefault("STORAGE_PROVIDER", "local")
os.environ.setdefault("JSON_DB_PATH", "./storage/test_db.json")
os.environ.setdefault("LOCAL_STORAGE_PATH", "./storage/test_uploads")

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_full_pipeline():
    # 1. Upload
    fake_video = io.BytesIO(b"not-a-real-video-but-good-enough-for-a-smoke-test")
    response = client.post(
        "/api/v1/upload",
        files={"file": ("demo.mp4", fake_video, "video/mp4")},
    )
    assert response.status_code == 200
    video_id = response.json()["video_id"]

    # 2. Analyze (Understanding Engine)
    response = client.post("/api/v1/analyze", json={"video_id": video_id})
    assert response.status_code == 200
    dna = response.json()
    assert dna["video_id"] == video_id

    # 3. Generate (Transformation Engine)
    response = client.post(
        "/api/v1/generate",
        json={
            "video_id": video_id,
            "persona": "developer",
            "platform": "linkedin",
            "purpose": "caption",
            "tone": "formal",
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["video_id"] == video_id
    assert len(result["content"]) > 0

    # 4. History
    response = client.get(f"/api/v1/history?video_id={video_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
