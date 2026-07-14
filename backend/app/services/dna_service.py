"""Understanding Engine.

Extracts a video's Content DNA exactly once and persists it. All downstream
transformations reuse this structured representation instead of touching
the source video again.

Supports two understanding methods, selectable per-request via
`understanding_method` on POST /analyze:

  "whisper"      (default) — extract audio via ffmpeg, transcribe it with
                  Groq's Whisper Large v3, then feed the transcript to a
                  Fireworks text LLM to build Content DNA.

  "gemma_vision"  — sample a handful of frames from the video with ffmpeg
                  and send them directly to a vision-capable model (e.g.
                  Gemma 4) via OpenRouter. No audio transcription happens
                  at all in this path.

Both paths converge on the same ContentDNA schema, so nothing downstream
(transformation, frontend) needs to know which method produced it.
"""
import asyncio
import base64
import json
import os
from datetime import datetime
from typing import List, Optional

import ffmpeg
import httpx
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

from app.core.exceptions import AIProviderError
from app.core.logger import get_logger
from app.database.base import Database
from app.models.records import VideoRecord
from app.schemas.content_dna import ContentDNA
from app.services.fireworks_service import AIProvider
from app.utils.prompt_loader import load_prompt

logger = get_logger(__name__)
load_dotenv()


# ---------------------------------------------------------------------------
# Shared helper: resolve a local, on-disk copy of the video regardless of
# whether it lives on local disk or in Supabase Storage. Used by both the
# whisper (audio) path and the gemma_vision (frames) path.
# ---------------------------------------------------------------------------

def _resolve_local_video_copy(video_id: str, filename: str) -> Optional[str]:
    """Return a local filesystem path to the video, downloading it from
    Supabase Storage first if needed. Returns None if it can't be resolved.

    Caller is responsible for deleting the file afterwards if it was
    downloaded (i.e. if the returned path is under `storage/cloud_temp_*`).
    """
    provider = os.getenv("STORAGE_PROVIDER", "local").lower()
    stored_filename = f"{video_id}_{filename}"

    if provider == "supabase":
        bucket_name = os.getenv("SUPABASE_BUCKET", "PersonaStudio_AI")
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not (supabase_url and supabase_key):
            logger.error("Supabase credentials missing from environment variables.")
            return None

        local_temp_path = os.path.abspath(
            os.path.join(os.getcwd(), "storage", f"cloud_temp_{stored_filename}")
        )

        logger.info("Downloading '%s' from Supabase bucket '%s'...", stored_filename, bucket_name)
        try:
            os.makedirs(os.path.dirname(local_temp_path), exist_ok=True)
            supabase_client: Client = create_client(supabase_url, supabase_key)
            response = supabase_client.storage.from_(bucket_name).download(stored_filename)
            with open(local_temp_path, "wb") as f:
                f.write(response)
            return local_temp_path
        except Exception as err:
            logger.error("Failed to download file from Supabase: %s", err)
            return None

    # Local storage: the video is already on disk at this path.
    local_path = os.path.abspath(os.path.join(os.getcwd(), "storage", stored_filename))
    if os.path.exists(local_path):
        return local_path
    logger.error("Video file not found at expected local path: %s", local_path)
    return None


def _cleanup_temp_file(path: Optional[str]) -> None:
    """Delete a temp file if it exists. Safe to call with None."""
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError as exc:
            logger.warning("Could not remove temp file %s: %s", path, exc)


# ---------------------------------------------------------------------------
# Method A: Whisper transcription (existing behavior)
# ---------------------------------------------------------------------------

def get_video_transcript_via_groq(video_id: str, filename: str) -> str:
    """Downloads the video if needed, extracts its audio track via ffmpeg,
    and transcribes it via Groq's Whisper Large v3.
    """
    video_source_path = _resolve_local_video_copy(video_id, filename)
    is_downloaded_copy = os.getenv("STORAGE_PROVIDER", "local").lower() == "supabase"

    if not video_source_path:
        return ""

    audio_path = video_source_path.rsplit(".", 1)[0] + "_temp.mp3"

    try:
        logger.info("Extracting audio track from %s using ffmpeg...", video_source_path)
        (
            ffmpeg
            .input(video_source_path)
            .output(audio_path, **{"ac": 1, "ar": "16000", "map": "a"})
            .run(quiet=True, overwrite_output=True)
        )

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY missing from environment variables.")
            return ""

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}

        logger.info("Sending audio file to Groq Whisper Large v3...")
        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f, "audio/mpeg")}
            data = {
                "model": "whisper-large-v3",
                "temperature": "0.0",
                "response_format": "verbose_json",
            }
            response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code != 200:
            logger.error("Groq API error: Status %s - %s", response.status_code, response.text)
            return ""

        result = response.json()

        if "segments" in result:
            timestamped_transcript = ""
            for segment in result["segments"]:
                start = round(segment.get("start", 0.0), 1)
                end = round(segment.get("end", 0.0), 1)
                text = segment.get("text", "").strip()
                timestamped_transcript += f"[{start}s - {end}s] {text}\n"
            return timestamped_transcript.strip()

        return result.get("text", "")

    except Exception as e:
        logger.error("Error during video transcription via Groq: %s", e)
        return ""

    finally:
        _cleanup_temp_file(audio_path)
        if is_downloaded_copy:
            _cleanup_temp_file(video_source_path)


# ---------------------------------------------------------------------------
# Method B: Direct vision analysis via OpenRouter (Gemma 4), no transcription
# ---------------------------------------------------------------------------

def extract_video_frames(video_path: str, num_frames: int = 4) -> List[str]:
    """Extract `num_frames` evenly-spaced frames from a video and return
    them as base64-encoded JPEG strings. Best-effort: skips any frame that
    fails to extract rather than aborting the whole batch.
    """
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe["format"]["duration"])
    except Exception as exc:
        logger.warning("Could not probe video duration, defaulting to 10s: %s", exc)
        duration = 10.0

    frames_b64: List[str] = []
    for i in range(num_frames):
        timestamp = max(0.0, duration * (i + 1) / (num_frames + 1))
        frame_path = f"{video_path}_frame_{i}.jpg"
        try:
            (
                ffmpeg
                .input(video_path, ss=timestamp)
                .output(frame_path, vframes=1, **{"q:v": 2})
                .run(quiet=True, overwrite_output=True)
            )
            with open(frame_path, "rb") as f:
                frames_b64.append(base64.b64encode(f.read()).decode("utf-8"))
        except Exception as exc:
            logger.warning("Failed to extract frame at %.1fs: %s", timestamp, exc)
        finally:
            _cleanup_temp_file(frame_path)

    return frames_b64


async def get_content_dna_via_openrouter_vision(frames_b64: List[str], video_metadata: dict) -> str:
    """Send extracted frames directly to a vision-capable model (e.g. Gemma 4)
    via OpenRouter and return the raw text response (expected to be JSON
    matching the Content DNA schema — parsed by the caller).
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise AIProviderError("OPENROUTER_API_KEY is not set.")

    model = os.getenv("OPENROUTER_VISION_MODEL", "google/gemma-4-31b-it")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    prompt_text = load_prompt("understanding_vision").format(
        video_metadata=json.dumps(video_metadata)
    )

    content: List[dict] = [{"type": "text", "text": prompt_text}]
    for b64 in frames_b64:
        content.append(
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        )

    payload = {
        "model": model,
        "max_tokens": 1200,
        "temperature": 0.4,
        "messages": [{"role": "user", "content": content}],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=90) as client:
        try:
            response = await client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("OpenRouter API call failed: %s", exc)
            raise AIProviderError(str(exc)) from exc

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise AIProviderError(f"Unexpected OpenRouter response shape: {data}") from exc


# ---------------------------------------------------------------------------
# Understanding Engine
# ---------------------------------------------------------------------------

class DNAService:
    """Builds and retrieves Content DNA for a video."""

    def __init__(self, db: Database, ai_provider: AIProvider):
        self._db = db
        self._ai = ai_provider

    async def analyze(
        self,
        video: VideoRecord,
        raw_signal: Optional[str] = None,
        understanding_method: str = "whisper",
    ) -> ContentDNA:
        """Run (or reuse) the Understanding Engine for a given video.

        If Content DNA already exists for this video, it is returned as-is —
        the core PersonaStudio principle is "never analyze the same video
        twice".

        Args:
            video: the video to analyze.
            raw_signal: an already-known transcript/description. If provided,
                it's used as-is and `understanding_method` is ignored.
            understanding_method: "whisper" (transcribe audio, default) or
                "gemma_vision" (analyze sampled frames directly, no audio).
        """
        if video.content_dna:
            logger.info("Reusing existing Content DNA for %s", video.video_id)
            return ContentDNA(**video.content_dna)

        if raw_signal:
            dna_dict = await self._analyze_via_text(video, raw_signal)
        elif understanding_method == "gemma_vision":
            dna_dict = await self._analyze_via_vision(video)
        else:
            transcript = await asyncio.to_thread(
                get_video_transcript_via_groq, video.video_id, video.filename
            )
            dna_dict = await self._analyze_via_text(video, transcript)

        dna = ContentDNA(**dna_dict)

        video.content_dna = dna.model_dump()
        video.status = "analyzed"
        video.analyzed_at = datetime.utcnow()
        await self._db.update_video(video)

        logger.info(
            "Generated new Content DNA for %s (method=%s)",
            video.video_id,
            understanding_method,
        )
        return dna

    async def _analyze_via_text(self, video: VideoRecord, raw_signal: Optional[str]) -> dict:
        """Whisper-transcript (or manually supplied text) → Fireworks LLM."""
        prompt = load_prompt("understanding").format(
            video_metadata=json.dumps(
                {
                    "filename": video.filename,
                    "duration_seconds": video.duration_seconds,
                    "content_type": video.content_type,
                }
            ),
            raw_signal=raw_signal or "No transcript provided; infer conservatively from filename/metadata only.",
        )
        raw_output = await self._ai.complete(prompt, max_tokens=1200, temperature=0.4)
        return self._parse_dna_json(raw_output, video.video_id)

    async def _analyze_via_vision(self, video: VideoRecord) -> dict:
        """Sampled frames → OpenRouter Gemma 4 vision. No transcription."""
        local_path = await asyncio.to_thread(
            _resolve_local_video_copy, video.video_id, video.filename
        )
        is_downloaded_copy = os.getenv("STORAGE_PROVIDER", "local").lower() == "supabase"

        if not local_path:
            logger.warning(
                "Could not resolve local video for vision analysis (%s); "
                "falling back to metadata-only understanding.",
                video.video_id,
            )
            return await self._analyze_via_text(video, raw_signal=None)

        try:
            frames = await asyncio.to_thread(extract_video_frames, local_path, 4)
        finally:
            if is_downloaded_copy:
                _cleanup_temp_file(local_path)

        if not frames:
            logger.warning(
                "No frames could be extracted for %s; falling back to metadata-only understanding.",
                video.video_id,
            )
            return await self._analyze_via_text(video, raw_signal=None)

        raw_output = await get_content_dna_via_openrouter_vision(
            frames,
            {
                "filename": video.filename,
                "duration_seconds": video.duration_seconds,
                "content_type": video.content_type,
            },
        )
        return self._parse_dna_json(raw_output, video.video_id)

    def _parse_dna_json(self, raw_output: str, video_id: str) -> dict:
        """Parse the model's JSON output and normalize the timeline structure."""
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]

        try:
            parsed = json.loads(cleaned)
            parsed["video_id"] = video_id
            
            # NORMALIZATION LOGIC FOR TIMELINE
            normalized_timeline = []
            
            # Support both `timeline` and `important_timestamps` in case the LLM varies
            raw_timeline = parsed.get("timeline") or parsed.get("important_timestamps") or []
            
            if isinstance(raw_timeline, list):
                for event in raw_timeline:
                    if not isinstance(event, dict):
                        continue
                        
                    # Catch all typical LLM timestamp outputs and cast to float
                    timestamp_val = event.get("timestamp_seconds") or event.get("timestamp") or event.get("start") or event.get("time") or 0.0
                    try:
                        timestamp_val = float(timestamp_val)
                    except (ValueError, TypeError):
                        timestamp_val = 0.0
                        
                    # Catch all typical LLM text outputs and force into 'label'
                    label_val = event.get("label") or event.get("description") or event.get("event") or event.get("text") or "Notable Event"
                    
                    normalized_timeline.append({
                        "timestamp_seconds": timestamp_val,
                        "label": str(label_val)
                    })
            
            # Explicitly overwrite with the normalized version
            parsed["timeline"] = normalized_timeline
            
            return parsed
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("Could not parse Content DNA JSON, using fallback skeleton: %s", exc)
            return {
                "video_id": video_id,
                "title": "Untitled video",
                "summary": raw_output[:500] if raw_output else "No summary available.",
                "core_message": "",
                "tone": "neutral",
                "sentiment": "neutral",
                "timeline": [],
                "key_events": [],
                "detected_objects": [],
                "people": [],
                "activities": [],
                "important_timestamps": [],
                "keywords": [],
                "entities": [],
                "topics": [],
                "context": "",
            }