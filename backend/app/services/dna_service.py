"""Understanding Engine.

Extracts a video's Content DNA exactly once and persists it. All downstream
transformations reuse this structured representation instead of touching
the source video again.
"""
import asyncio
import base64
import json
import os
import requests
import ffmpeg
from dataclasses import asdict
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv  # Added to ensure keys are explicitly read

from app.core.exceptions import AIProviderError
from app.core.logger import get_logger
from app.database.base import Database
from app.models.records import VideoRecord
from app.schemas.content_dna import ContentDNA
from app.services.fireworks_service import AIProvider
from app.utils.prompt_loader import load_prompt
from supabase import create_client, Client  # Added for cloud bucket management

logger = get_logger(__name__)
load_dotenv()

def get_video_transcript_via_groq(video_path_or_id: str, original_filename: str = None) -> str:
    """Downloads a video if hosted on Supabase or maps local storage, 
    extracts the audio track using ffmpeg, and processes it via Groq.
    """
    provider = os.getenv("STORAGE_PROVIDER", "local").lower()
    local_temp_video = None
    
    # Check if we need to resolve a cloud object or standard local absolute path
    if provider == "supabase":
        bucket_name = os.getenv("SUPABASE_BUCKET", "PersonaStudio_AI")
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not (supabase_url and supabase_key):
            logger.error("Supabase credentials missing from environment variables.")
            return ""
            
        # Initialize client connection
        supabase_client: Client = create_client(supabase_url, supabase_key)
        
        # Build the structured filename your storage service uses
        stored_filename = f"{video_path_or_id}_{original_filename}"
        local_temp_video = os.path.abspath(os.path.join(os.getcwd(), "storage", f"cloud_temp_{stored_filename}"))
        
        logger.info("Downloading file %s from Supabase bucket '%s'...", stored_filename, bucket_name)
        try:
            # Create local storage directory if missing out of caution
            os.makedirs(os.path.dirname(local_temp_video), exist_ok=True)
            
            # Streaming download straight from Supabase storage network
            response = supabase_client.storage.from_(bucket_name).download(stored_filename)
            with open(local_temp_video, 'wb') as f:
                f.write(response)
            
            video_source_path = local_temp_video
        except Exception as err:
            logger.error("Failed to download file from Supabase: %s", err)
            return ""
    else:
        # Standard fallback to our absolute local setup
        video_source_path = video_path_or_id

    # Audio file setup targeting local disk space
    audio_path = video_source_path.replace(".mp4", "_temp.mp3")
    
    try:
        if not os.path.exists(video_source_path):
            logger.error("Target video not found on disk at: %s", video_source_path)
            return ""

        logger.info("Extracting audio track from %s using ffmpeg...", video_source_path)
        (
            ffmpeg
            .input(video_source_path)
            .output(audio_path, **{'ac': 1, 'ar': '16000', 'map': 'a'})
            .run(quiet=True, overwrite_output=True)
        )
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY missing from environment variables.")
            return ""

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        logger.info("Sending audio file to free Groq Whisper-Large-V3 gateway...")
        with open(audio_path, "rb") as f:
            files = {"file": (os.path.basename(audio_path), f, "audio/mpeg")}
            data = {"model": "whisper-large-v3", "temperature": "0.0"}
            response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code != 200:
            logger.error("Groq API error: Status %s - %s", response.status_code, response.text)
            return ""
            
        return response.json().get("text", "")

    except Exception as e:
        logger.error("Error during video transcription via Groq: %s", e)
        return ""

    finally:
        # Strict memory and storage cleanup cycle
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if local_temp_video and os.path.exists(local_temp_video):
            os.remove(local_temp_video)
            logger.info("Temporary cloud buffers successfully purged from local storage.")

class DNAService:
    """Builds and retrieves Content DNA for a video."""

    def __init__(self, db: Database, ai_provider: AIProvider):
        self._db = db
        self._ai = ai_provider

    async def analyze(self, video: VideoRecord, raw_signal: Optional[str] = None) -> ContentDNA:
        """Run (or reuse) the Understanding Engine for a given video.

        If Content DNA already exists for this video, it is returned as-is —
        the core PersonaStudio principle is "never analyze the same video
        twice".
        """
        if video.content_dna:
            logger.info("Reusing existing Content DNA for %s", video.video_id)
            return ContentDNA(**video.content_dna)

        # Automatically transcribe the local video if no explicit raw_signal was passed in
        if not raw_signal:
            # Reconstruct the local storage path using the backend's directory structure
            #backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            #stored_filename = f"{video.video_id}_{video.filename}"
            #video_path = os.path.abspath(os.path.join(os.getcwd(), "storage", stored_filename))
            provider = os.getenv("STORAGE_PROVIDER", "local").lower()
            logger.info("Content DNA processing triggered. Storage provider detected: '%s'", provider)
            
            if provider == "supabase": # | os.path.exists(video_path)
                #logger.info("Initiating transcription for file: %s", video_path)
                logger.info(
                    "Initiating cloud transcription pipeline. Fetching target metadata -> ID: %s, Filename: %s", 
                    video.video_id, 
                    video.filename
                )
                # Offload the synchronous transcription function to a worker thread
                # For Supabase, pass the ID and filename separately so it can fetch cleanly
                raw_signal = await asyncio.to_thread(
                    get_video_transcript_via_groq, 
                    video.video_id, 
                    video.filename
                )
                # raw_signal = await asyncio.to_thread(get_video_transcript_via_groq, video_path)
            else:
                logger.warning("Video file not found at %s. Proceeding with metadata only.", video_path)

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
        dna_dict = self._parse_dna_json(raw_output, video.video_id)
        dna = ContentDNA(**dna_dict)

        # Assign values to the object to be persisted in the DB
        video.content_dna = dna.model_dump()
        video.raw_signal = raw_signal  # <-- ADD THIS LINE HERE TO SAVE THE TRANSCRIPT!
        video.status = "analyzed"
        video.analyzed_at = datetime.utcnow()
        
        await self._db.update_video(video)

        logger.info("Generated new Content DNA for %s", video.video_id)
        return dna

    def _parse_dna_json(self, raw_output: str, video_id: str) -> dict:
        """Parse the model's JSON output, falling back to a safe skeleton on failure."""
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]

        try:
            parsed = json.loads(cleaned)
            parsed["video_id"] = video_id
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