"""
Voice Service — Ultra-low latency Speech-to-Text powered by Groq Whisper API.
Incorporates whisper-large-v3-turbo / whisper-large-v3 from the localflow/yolo-wisper project.
Zero-cost, fast (~200-300ms) transcription for mobile, tablet, and desktop agency users.
"""

import io
import os
import time
import logging
from typing import Optional, Dict, Any, Union
from groq import Groq
from src.config import GROQ_API_KEY, get_groq_api_key
from src.services.security import redact_secrets

logger = logging.getLogger("LeadFinder.VoiceService")

# Phrases that Whisper occasionally hallucinates during dead silence or low background noise
SILENCE_HALLUCINATIONS = {
    "thank you.",
    "thank you",
    "thanks for watching.",
    "thanks for watching!",
    "subscribe to my channel",
    "you",
    "bye.",
    "subtitles by",
    "subtitles created by",
    "amara.org",
}

class VoiceService:
    """
    Autonomous voice transcription engine utilizing Groq Whisper API.
    Provides sub-second audio-to-text conversion for voice-driven lead searches and agency chat commands.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or "").strip()
        self.client: Optional[Groq] = None
        self._active_key: Optional[str] = None
        self._ensure_client()

    def _ensure_client(self) -> None:
        """Dynamically ensures the Groq client is initialized with the latest key."""
        current_key = (self.api_key or get_groq_api_key() or "").strip()
        if current_key and (self.client is None or self._active_key != current_key):
            try:
                self.client = Groq(api_key=current_key)
                self._active_key = current_key
            except Exception as e:
                logger.error(f"Failed to initialize Groq client for VoiceService: {redact_secrets(str(e))}")
                self.client = None

    def is_available(self) -> bool:
        """Checks if the Groq Whisper service is available and configured."""
        self._ensure_client()
        return self.client is not None and bool(self._active_key)

    def transcribe_audio(
        self,
        audio_data: Union[bytes, io.BytesIO, str],
        filename: str = "audio.wav",
        language: Optional[str] = None,
        model: str = "whisper-large-v3-turbo"
    ) -> Dict[str, Any]:
        """
        Transcribes audio data (bytes, BytesIO stream, or file path) using Groq Whisper.
        """
        self._ensure_client()
        if not self.is_available():
            return {
                "text": "",
                "duration_ms": 0,
                "success": False,
                "error": "Groq API key not configured. Please add GROQ_API_KEY in Streamlit Cloud Secrets."
            }

        start_time = time.time()

        try:
            # Prepare file tuple for Groq SDK
            file_payload = None
            if isinstance(audio_data, bytes):
                file_payload = (filename, audio_data)
            elif isinstance(audio_data, io.BytesIO):
                audio_data.seek(0)
                file_payload = (filename, audio_data.read())
            elif isinstance(audio_data, str) and os.path.exists(audio_data):
                with open(audio_data, "rb") as f:
                    file_payload = (filename, f.read())
            elif hasattr(audio_data, "read"):
                # Streamlit UploadedFile or generic file-like object
                raw_bytes = audio_data.read()
                # Reset pointer if possible
                if hasattr(audio_data, "seek"):
                    try:
                        audio_data.seek(0)
                    except Exception:
                        pass
                file_payload = (filename, raw_bytes)
            else:
                return {
                    "text": "",
                    "duration_ms": 0,
                    "success": False,
                    "error": "Unsupported audio data format provided."
                }

            # Prepare optional transcription arguments
            kwargs: Dict[str, Any] = {
                "file": file_payload,
                "model": model,
                "response_format": "json"
            }
            if language and language != "auto":
                kwargs["language"] = language

            # Execute transcription request
            try:
                response = self.client.audio.transcriptions.create(**kwargs)
            except Exception as first_err:
                # If turbo model encounters a transient error, fallback to whisper-large-v3
                if model == "whisper-large-v3-turbo":
                    logger.warning(f"Groq whisper-large-v3-turbo retry with whisper-large-v3: {redact_secrets(str(first_err))}")
                    kwargs["model"] = "whisper-large-v3"
                    response = self.client.audio.transcriptions.create(**kwargs)
                else:
                    raise first_err

            raw_text = (response.text or "").strip()
            duration_ms = int((time.time() - start_time) * 1000)

            # Filter hallucinations on silent / low-volume recordings
            clean_text = raw_text
            if clean_text.lower().strip() in SILENCE_HALLUCINATIONS:
                clean_text = ""

            logger.info(f"Audio transcribed in {duration_ms}ms: '{clean_text}'")

            return {
                "text": clean_text,
                "duration_ms": duration_ms,
                "success": True,
                "error": None
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            err_msg = redact_secrets(str(e))
            logger.error(f"Groq Whisper transcription failed ({duration_ms}ms): {err_msg}")
            if "401" in err_msg or "invalid_api_key" in err_msg.lower():
                user_friendly = "Invalid Groq API key (401). Please verify that GROQ_API_KEY is correctly set in Streamlit Cloud Secrets (App Settings -> Secrets)."
            else:
                user_friendly = f"Transcription error: {err_msg}"
            return {
                "text": "",
                "duration_ms": duration_ms,
                "success": False,
                "error": user_friendly
            }

# Singleton instance
voice_service = VoiceService()
