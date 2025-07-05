"""
📋 Shared Streaming Models
Common data structures used across streaming components
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class TTSProvider(Enum):
    """Text-to-Speech provider options"""

    ELEVENLABS = "elevenlabs"
    GTTS = "gtts"
    AZURE = "azure"


class AudioFormat(Enum):
    """Audio format options"""

    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"


class ProcessingStatus(Enum):
    """Processing status options"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AudioProcessingRequest:
    """Parameter object for audio processing requests"""

    audio_data: bytes
    session_id: str
    websocket: Optional[Any] = None
    format: AudioFormat = AudioFormat.WAV
    sample_rate: int = 16000

    def __post_init__(self):
        """Validate audio processing request"""
        if not self.audio_data:
            raise ValueError("audio_data cannot be empty")
        if not self.session_id:
            raise ValueError("session_id cannot be empty")
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")


@dataclass
class TextToSpeechRequest:
    """Parameter object for text-to-speech requests"""

    text: str
    voice: Optional[str] = None
    provider: TTSProvider = TTSProvider.ELEVENLABS
    format: AudioFormat = AudioFormat.MP3
    language: str = "ar"

    def __post_init__(self):
        """Validate TTS request"""
        if not self.text or not self.text.strip():
            raise ValueError("text cannot be empty")
        if len(self.text) > 5000:
            raise ValueError("text cannot exceed 5000 characters")


@dataclass
class LLMRequest:
    """Parameter object for LLM processing requests"""

    text: str
    session_id: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    retry_count: int = 0

    def __post_init__(self):
        """Validate LLM request"""
        if not self.text or not self.text.strip():
            raise ValueError("text cannot be empty")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        if self.retry_count < 0:
            raise ValueError("retry_count cannot be negative")


@dataclass
class StreamingStatus:
    """Streaming status information"""

    session_id: str
    is_active: bool
    status: ProcessingStatus
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate streaming status"""
        if not self.session_id:
            raise ValueError("session_id cannot be empty")


@dataclass
class WebSocketMessage:
    """WebSocket message structure"""

    type: str
    data: Dict[str, Any]
    session_id: str
    timestamp: datetime = None

    def __post_init__(self):
        """Set default timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        return {
            "type": self.type,
            "data": self.data,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class AudioBuffer:
    """Audio buffer configuration"""

    max_size: int = 8192
    chunk_size: int = 1024

    def __post_init__(self):
        """Validate buffer configuration"""
        if self.max_size <= 0:
            raise ValueError("max_size must be positive")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.chunk_size > self.max_size:
            raise ValueError("chunk_size cannot exceed max_size")


@dataclass
class ConnectionConfig:
    """Connection configuration for external services"""

    host: str
    port: int
    api_key: Optional[str] = None
    timeout: int = 30
    max_reconnect_attempts: int = 5
    reconnect_delay: float = 1.0

    def __post_init__(self):
        """Validate connection configuration"""
        if not self.host:
            raise ValueError("host cannot be empty")
        if not 1 <= self.port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_reconnect_attempts < 0:
            raise ValueError("max_reconnect_attempts cannot be negative")
        if self.reconnect_delay < 0:
            raise ValueError("reconnect_delay cannot be negative")


@dataclass
class ProcessingResult:
    """Generic processing result"""

    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def success_result(
        cls,
        data: Any,
        processing_time_ms: float = None,
        metadata: Dict[str, Any] = None,
    ):
        """Create successful result"""
        return cls(
            success=True,
            data=data,
            processing_time_ms=processing_time_ms,
            metadata=metadata or {},
        )

    @classmethod
    def error_result(cls, error_message: str, metadata: Dict[str, Any] = None):
        """Create error result"""
        return cls(
            success=False,
            error_message=error_message,
            metadata=metadata or {})
