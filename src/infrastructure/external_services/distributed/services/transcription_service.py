"""
Distributed transcription service deployment.
"""

import logging
import time
from typing import Any, Dict

import numpy as np

try:
    from ray import serve
    import whisper
    from openai import AsyncOpenAI
    AI_SERVICES_AVAILABLE = True
except ImportError:
    AI_SERVICES_AVAILABLE = False
    serve = None

try:
    import soundfile as sf
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

from ..mocks import MockAIServices

logger = logging.getLogger(__name__)

if AI_SERVICES_AVAILABLE:
    @serve.deployment(
        name="transcription-service",
        num_replicas=2,
        ray_actor_options={"num_cpus": 1, "memory": 2000 * 1024 * 1024},  # 2GB
    )
    class TranscriptionService:
        """Distributed transcription service using Whisper."""

        def __init__(self):
            self.whisper_model = None
            self.openai_client = None
            self.service_stats = {"requests": 0, "total_time": 0.0}
            self._initialize_models()

        def _initialize_models(self) -> Any:
            """Initialize transcription models."""
            try:
                # Load Whisper model
                self.whisper_model = whisper.load_model("base")

                # Initialize OpenAI client
                self.openai_client = AsyncOpenAI()

                logger.info("✅ Transcription service models loaded")
            except Exception as e:
                logger.error(
                    f"❌ Failed to initialize transcription models: {e}")

        async def transcribe(self, audio_data: bytes) -> Dict[str, Any]:
            """Transcribe audio using best available method."""
            start_time = time.time()
            self.service_stats["requests"] += 1

            try:
                if self.whisper_model:
                    # Real Whisper transcription
                    result = await self._transcribe_with_whisper(audio_data)
                else:
                    # Mock transcription
                    result = await MockAIServices.transcribe_audio(audio_data)

                processing_time = (time.time() - start_time) * 1000
                result["processing_time_ms"] = processing_time
                self.service_stats["total_time"] += processing_time

                return result

            except Exception as e:
                logger.error(f"❌ Transcription failed: {e}")
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": "unknown",
                    "error": str(e),
                    "processing_time_ms": (time.time() - start_time) * 1000,
                }

        async def _transcribe_with_whisper(
                self, audio_data: bytes) -> Dict[str, Any]:
            """Transcribe using Whisper model."""
            try:
                # Convert bytes to audio array
                if AUDIO_PROCESSING_AVAILABLE:
                    audio_array = (
                        np.frombuffer(
                            audio_data,
                            dtype=np.int16).astype(
                            np.float32) /
                        32768.0)

                    # Transcribe with Whisper
                    result = self.whisper_model.transcribe(audio_array)

                    return {
                        "text": result["text"],
                        "confidence": 0.9,  # Whisper doesn't provide confidence scores
                        "language": result.get("language", "unknown"),
                    }
                else:
                    return await MockAIServices.transcribe_audio(audio_data)

            except Exception as e:
                logger.error(f"❌ Whisper transcription error: {e}")
                return await MockAIServices.transcribe_audio(audio_data)
else:
    TranscriptionService = MockAIServices
