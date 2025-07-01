"""
🎤 Modern Transcription Service - 2025 Edition
Streaming Speech-to-Text with lazy model loading and async processing
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, Optional, Union

import numpy as np
import torch
# Audio processing
import whisper

try:
    import torchaudio
except ImportError:
    torchaudio = None
import librosa
from openai import AsyncOpenAI

# Value objects

logger = logging.getLogger(__name__)

# ================== CONFIGURATION ==================


@dataclass
class TranscriptionConfig:
    """Configuration for transcription service"""

    whisper_model: str = "base"  # tiny, base, small, medium, large
    chunk_duration: float = 3.0  # seconds
    overlap_duration: float = 0.5  # seconds
    min_silence_duration: float = 1.0  # seconds
    confidence_threshold: float = 0.7
    sample_rate: int = 16000
    use_gpu: bool = True
    language: Optional[str] = None  # Auto-detect if None

    @property
    def device(self) -> str:
        """Get computing device"""
        if self.use_gpu and torch.cuda.is_available():
            return "cuda"
        elif (
            self.use_gpu
            and hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        ):
            return "mps"  # Apple Silicon
        return "cpu"


# ================== AUDIO BUFFER ==================


class StreamingAudioBuffer:
    """Smart audio buffer for streaming transcription"""

    def __init__(self, config: TranscriptionConfig):
        self.config = config
        self.buffer = np.array([], dtype=np.float32)
        self.sample_rate = config.sample_rate
        self.chunk_samples = int(config.chunk_duration * self.sample_rate)
        self.overlap_samples = int(config.overlap_duration * self.sample_rate)
        self.min_silence_samples = int(config.min_silence_duration * self.sample_rate)

        # State tracking
        self.last_activity = time.time()
        self.is_speech_detected = False

    def add_chunk(self, audio_chunk: np.ndarray) -> None:
        """Add audio chunk to buffer"""
        # Ensure correct format
        if audio_chunk.dtype != np.float32:
            audio_chunk = audio_chunk.astype(np.float32)

        # Normalize if needed
        if np.max(np.abs(audio_chunk)) > 1.0:
            audio_chunk = audio_chunk / np.max(np.abs(audio_chunk))

        # Add to buffer
        self.buffer = np.concatenate([self.buffer, audio_chunk])

        # Update activity detection
        if self._detect_activity(audio_chunk):
            self.last_activity = time.time()
            self.is_speech_detected = True

    def _detect_activity(self, audio_chunk: np.ndarray) -> bool:
        """Simple voice activity detection"""
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_chunk**2))

        # Dynamic threshold based on recent history
        threshold = 0.01  # Base threshold
        return rms > threshold

    def get_ready_chunk(self) -> Optional[np.ndarray]:
        """Get audio chunk ready for transcription"""
        if len(self.buffer) < self.chunk_samples:
            return None

        # Check for silence gap
        silence_duration = time.time() - self.last_activity

        if (
            self.is_speech_detected
            and silence_duration >= self.config.min_silence_duration
        ):
            # Extract complete utterance
            chunk = self.buffer.copy()
            self.buffer = np.array([], dtype=np.float32)
            self.is_speech_detected = False
            return chunk

        # Extract chunk with overlap
        if len(self.buffer) >= self.chunk_samples:
            chunk = self.buffer[: self.chunk_samples]
            # Keep overlap for next chunk
            self.buffer = self.buffer[self.chunk_samples - self.overlap_samples :]
            return chunk

        return None

    @property
    def duration(self) -> float:
        """Current buffer duration in seconds"""
        return len(self.buffer) / self.sample_rate

    def clear(self) -> None:
        """Clear the buffer"""
        self.buffer = np.array([], dtype=np.float32)
        self.is_speech_detected = False


# ================== TRANSCRIPTION SERVICE ==================


class ModernTranscriptionService:
    """
    🎤 Modern Transcription Service with 2025 Features:
    - Lazy model loading with singleton pattern
    - Real-time streaming transcription
    - Multi-provider support (Whisper, OpenAI)
    - Smart buffering and voice activity detection
    - GPU acceleration support
    - Confidence scoring and language detection
    """

    _instance = None
    _model_cache = {}
    _model_lock = asyncio.Lock()

    def __init__(self, config: Optional[TranscriptionConfig] = None):
        self.config = config or TranscriptionConfig()
        self.model = None
        self.openai_client = None

        # Performance tracking
        self.stats = {
            "total_transcriptions": 0,
            "total_processing_time": 0.0,
            "average_confidence": 0.0,
            "error_count": 0,
        }

        logger.info(
            f"✅ Modern Transcription Service initialized (model: {self.config.whisper_model}, device: {self.config.device})"
        )

    @classmethod
    async def get_instance(
        cls, config: Optional[TranscriptionConfig] = None
    ) -> "ModernTranscriptionService":
        """Get singleton instance with lazy initialization"""
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance

    async def initialize(self, openai_api_key: Optional[str] = None) -> None:
        """Initialize services asynchronously"""
        try:
            # Initialize OpenAI client if API key provided
            if openai_api_key:
                self.openai_client = AsyncOpenAI(api_key=openai_api_key)
                logger.info("✅ OpenAI client initialized for transcription")

            # Pre-load model for faster first transcription
            await self._ensure_model_loaded()

            logger.info("🚀 Transcription service fully initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize transcription service: {e}")
            raise

    async def _ensure_model_loaded(self) -> None:
        """Ensure Whisper model is loaded (lazy loading with caching)"""
        model_key = f"{self.config.whisper_model}_{self.config.device}"

        if model_key in self._model_cache:
            self.model = self._model_cache[model_key]
            logger.debug(f"📦 Using cached Whisper model: {model_key}")
            return

        async with self._model_lock:
            # Double-check after acquiring lock
            if model_key in self._model_cache:
                self.model = self._model_cache[model_key]
                return

            logger.info(
                f"📥 Loading Whisper model: {self.config.whisper_model} on {self.config.device}"
            )
            start_time = time.time()

            try:
                # Load model in thread to avoid blocking
                model = await asyncio.to_thread(
                    whisper.load_model,
                    self.config.whisper_model,
                    device=self.config.device,
                )

                # Cache the model
                self._model_cache[model_key] = model
                self.model = model

                load_time = time.time() - start_time
                logger.info(f"✅ Whisper model loaded in {load_time:.2f}s")

            except Exception as e:
                logger.error(f"❌ Failed to load Whisper model: {e}")
                raise

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[np.ndarray]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        🌊 Stream transcription with real-time processing

        Args:
            audio_stream: Async iterator of audio chunks

        Yields:
            Transcription results with metadata
        """
        await self._ensure_model_loaded()

        buffer = StreamingAudioBuffer(self.config)

        try:
            async for audio_chunk in audio_stream:
                # Add chunk to buffer
                buffer.add_chunk(audio_chunk)

                # Check if we have a complete chunk ready
                ready_chunk = buffer.get_ready_chunk()
                if ready_chunk is not None:
                    # Transcribe the chunk
                    result = await self.transcribe_audio(ready_chunk)

                    # Only yield if confidence is high enough
                    if result["confidence"] >= self.config.confidence_threshold:
                        yield result

        except Exception as e:
            logger.error(f"❌ Stream transcription error: {e}")
            self.stats["error_count"] += 1

    async def transcribe_audio(
        self,
        audio_data: Union[np.ndarray, bytes, str],
        language: Optional[str] = None,
        provider: str = "whisper",
    ) -> Dict[str, Any]:
        """
        🎯 Transcribe audio with multiple provider support

        Args:
            audio_data: Audio data in various formats
            language: Language code (auto-detect if None)
            provider: "whisper" or "openai"

        Returns:
            Transcription result with confidence and metadata
        """
        start_time = time.time()

        try:
            # Prepare audio data
            audio_array = await self._prepare_audio(audio_data)

            # Choose transcription provider
            if provider == "openai" and self.openai_client:
                result = await self._transcribe_openai(audio_array, language)
            else:
                result = await self._transcribe_whisper(audio_array, language)

            # Calculate processing time
            processing_time = time.time() - start_time
            result["processing_time_ms"] = int(processing_time * 1000)

            # Update statistics
            self._update_stats(result, processing_time)

            logger.debug(
                f"🎯 Transcribed in {processing_time:.2f}s: '{result['text'][:50]}...'"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            self.stats["error_count"] += 1

            return {
                "text": "",
                "confidence": 0.0,
                "language": "unknown",
                "error": str(e),
                "processing_time_ms": int((time.time() - start_time) * 1000),
            }

    async def _transcribe_whisper(
        self, audio_array: np.ndarray, language: Optional[str]
    ) -> Dict[str, Any]:
        """Transcribe using Whisper model"""
        await self._ensure_model_loaded()

        # Prepare options
        options = {"language": language or self.config.language, "task": "transcribe"}

        # Run transcription in thread to avoid blocking
        result = await asyncio.to_thread(
            self.model.transcribe,
            audio_array,
            **{k: v for k, v in options.items() if v is not None},
        )

        # Extract confidence from segments
        confidence = self._calculate_confidence(result.get("segments", []))

        return {
            "text": result["text"].strip(),
            "confidence": confidence,
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "provider": "whisper",
        }

    async def _transcribe_openai(
        self, audio_array: np.ndarray, language: Optional[str]
    ) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        try:
            # Convert to wav bytes
            import io

            import soundfile as sf

            buffer = io.BytesIO()
            sf.write(buffer, audio_array, self.config.sample_rate, format="WAV")
            buffer.seek(0)

            # Call OpenAI API
            response = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=buffer,
                language=language,
                response_format="verbose_json",
            )

            return {
                "text": response.text.strip(),
                "confidence": 0.95,  # OpenAI doesn't provide confidence
                "language": response.language,
                "segments": getattr(response, "segments", []),
                "provider": "openai",
            }

        except Exception as e:
            logger.error(f"❌ OpenAI transcription failed: {e}")
            # Fallback to Whisper
            return await self._transcribe_whisper(audio_array, language)

    async def _prepare_audio(
        self, audio_data: Union[np.ndarray, bytes, str]
    ) -> np.ndarray:
        """Prepare audio data for transcription"""
        if isinstance(audio_data, str):
            # Load from file
            audio_array, sr = librosa.load(audio_data, sr=self.config.sample_rate)
        elif isinstance(audio_data, bytes):
            # Convert bytes to numpy array
            audio_array = (
                np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            )
        elif isinstance(audio_data, np.ndarray):
            audio_array = audio_data.astype(np.float32)
            # Resample if needed
            if len(audio_array.shape) > 1:
                audio_array = audio_array.mean(axis=1)  # Convert to mono
        else:
            raise ValueError(f"Unsupported audio data type: {type(audio_data)}")

        # Ensure correct sample rate
        if (
            hasattr(audio_data, "sample_rate")
            and audio_data.sample_rate != self.config.sample_rate
        ):
            audio_array = librosa.resample(
                audio_array,
                orig_sr=audio_data.sample_rate,
                target_sr=self.config.sample_rate,
            )

        return audio_array

    def _calculate_confidence(self, segments: list) -> float:
        """Calculate overall confidence from segments"""
        if not segments:
            return 0.5  # Default confidence

        # Average confidence from segments (if available)
        confidences = []
        for segment in segments:
            if "avg_logprob" in segment:
                # Convert log probability to confidence
                confidence = np.exp(segment["avg_logprob"])
                confidences.append(confidence)

        if confidences:
            return float(np.mean(confidences))

        return 0.8  # Default high confidence for Whisper

    def _update_stats(self, result: Dict[str, Any], processing_time: float) -> None:
        """Update performance statistics"""
        self.stats["total_transcriptions"] += 1
        self.stats["total_processing_time"] += processing_time

        # Update average confidence
        current_avg = self.stats["average_confidence"]
        count = self.stats["total_transcriptions"]
        new_confidence = result.get("confidence", 0.0)

        self.stats["average_confidence"] = (
            current_avg * (count - 1) + new_confidence
        ) / count

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        avg_processing_time = (
            self.stats["total_processing_time"] / self.stats["total_transcriptions"]
            if self.stats["total_transcriptions"] > 0
            else 0
        )

        return {
            "total_transcriptions": self.stats["total_transcriptions"],
            "average_processing_time_s": avg_processing_time,
            "average_confidence": self.stats["average_confidence"],
            "error_count": self.stats["error_count"],
            "error_rate": (
                self.stats["error_count"] / self.stats["total_transcriptions"]
                if self.stats["total_transcriptions"] > 0
                else 0
            ),
            "model": self.config.whisper_model,
            "device": self.config.device,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            # Test with a short audio sample
            test_audio = (
                np.random.randn(self.config.sample_rate).astype(np.float32) * 0.01
            )
            result = await self.transcribe_audio(test_audio)

            return {
                "status": "healthy",
                "model_loaded": self.model is not None,
                "device": self.config.device,
                "test_processing_time_ms": result.get("processing_time_ms", 0),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_loaded": self.model is not None,
            }


# ================== FACTORY FUNCTION ==================


async def create_transcription_service(
    config: Optional[TranscriptionConfig] = None, openai_api_key: Optional[str] = None
) -> ModernTranscriptionService:
    """Factory function to create and initialize transcription service"""
    service = await ModernTranscriptionService.get_instance(config)
    await service.initialize(openai_api_key)
    return service


# Re-export for compatibility
TranscriptionService = ModernTranscriptionService
