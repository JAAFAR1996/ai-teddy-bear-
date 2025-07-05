"""Audio Transcription Service"""

from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import Any, Dict, List, Optional


class AudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"


@dataclass
class TranscriptionRequest:
    audio_data: bytes
    language: str = "ar"
    child_id: Optional[str] = None
    format: AudioFormat = AudioFormat.WAV


@dataclass
class TranscriptionResult:
    text: str
    confidence: float
    language: str
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass
class TranscriptionConfig:
    provider: str = "openai_whisper"
    language: str = "ar"
    model_size: str = "base"
    temperature: float = 0.0


class TranscriptionService:
    def __init__(self, config: Optional[TranscriptionConfig] = None):
        self.config = config or TranscriptionConfig()

    async def transcribe_audio(
        self, request: TranscriptionRequest
    ) -> TranscriptionResult:
        # Mock implementation
        mock_text = ("مرحبا، كيف حالك؟" if request.language ==
                     "ar" else "Hello, how are you?")

        return TranscriptionResult(
            text=mock_text,
            confidence=0.95,
            language=request.language,
            duration_seconds=2.5,
            metadata={"provider": self.config.provider},
        )

    def get_supported_languages(self) -> List[str]:
        return ["ar", "en", "fr", "es"]

    async def check_audio_quality(self, audio_data: bytes) -> Dict[str, Any]:
        return {
            "quality_score": 0.8,
            "noise_level": 0.2,
            "is_acceptable": True}


class ModernTranscriptionService(TranscriptionService):
    """Modern transcription service with advanced features"""

    def __init__(self, config: Optional[TranscriptionConfig] = None):
        super().__init__(config)
        self.advanced_mode = True

    async def transcribe_with_timestamps(
        self, request: TranscriptionRequest
    ) -> Dict[str, Any]:
        result = await self.transcribe_audio(request)
        return {
            "transcription": result,
            "timestamps": [
                {"word": "مرحبا", "start": 0.0, "end": 0.8},
                {"word": "كيف", "start": 1.0, "end": 1.3},
                {"word": "حالك", "start": 1.5, "end": 2.0},
            ],
        }


class StreamingAudioBuffer:
    """Buffer for streaming audio data"""

    def __init__(self, config: Optional[TranscriptionConfig] = None):
        self.config = config or TranscriptionConfig()
        self.buffer = Queue()
        self.is_recording = False
        self.max_buffer_size = 1024 * 1024  # 1MB

    def add_audio_chunk(self, audio_chunk: bytes):
        """Add audio chunk to buffer"""
        if not self.is_recording:
            return

        if self.buffer.qsize() < self.max_buffer_size:
            self.buffer.put(audio_chunk)

    def get_audio_data(self) -> bytes:
        """Get all buffered audio data"""
        audio_data = b""
        while not self.buffer.empty():
            audio_data += self.buffer.get()
        return audio_data

    def start_recording(self):
        """Start recording audio"""
        self.is_recording = True

    def stop_recording(self):
        """Stop recording audio"""
        self.is_recording = False

    def clear_buffer(self):
        """Clear the audio buffer"""
        while not self.buffer.empty():
            self.buffer.get()

    def get_buffer_size(self) -> int:
        """Get current buffer size in bytes"""
        return self.buffer.qsize()


# Factory for creating transcription services
def create_transcription_service(
        provider: str = "openai") -> TranscriptionService:
    config = TranscriptionConfig(provider=provider)
    if provider == "modern":
        return ModernTranscriptionService(config)
    return TranscriptionService(config)
