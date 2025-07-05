# audio_stream.py - Enhanced audio stream entity with complete features

import hashlib
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from pydantic import BaseModel, Field, validator


class AudioFormat(str, Enum):
    """Supported audio formats"""

    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    PCM = "pcm"
    OPUS = "opus"
    WEBM = "webm"


class StreamState(str, Enum):
    """Audio stream states"""

    IDLE = "idle"
    BUFFERING = "buffering"
    STREAMING = "streaming"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class StreamDirection(str, Enum):
    """Stream direction"""

    INPUT = "input"  # From user (microphone)
    OUTPUT = "output"  # To user (speaker)
    BIDIRECTIONAL = "bidirectional"


class AudioQuality(str, Enum):
    """Audio quality presets"""

    LOW = "low"  # 8kHz, 64kbps
    MEDIUM = "medium"  # 16kHz, 128kbps
    HIGH = "high"  # 24kHz, 192kbps
    ULTRA = "ultra"  # 48kHz, 320kbps


class VoiceSettings(BaseModel):
    """Voice configuration settings"""

    voice_id: str = Field(..., description="Voice identifier")
    voice_name: str = Field(..., description="Human-readable voice name")
    language: str = Field(default="en", description="Language code")

    # Voice characteristics
    stability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Voice stability")
    similarity_boost: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Voice similarity boost"
    )
    style: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Voice style strength"
    )
    use_speaker_boost: bool = Field(
        default=True, description="Enable speaker boost")

    # Additional settings
    pitch_adjustment: float = Field(
        default=0.0,
        ge=-12.0,
        le=12.0,
        description="Pitch adjustment in semitones")
    speed_adjustment: float = Field(
        default=1.0, ge=0.5, le=2.0, description="Speed multiplier"
    )
    volume_adjustment: float = Field(
        default=1.0, ge=0.0, le=2.0, description="Volume multiplier"
    )

    # Emotional tone
    emotional_tone: Optional[str] = Field(
        None, description="Emotional tone preset")

    def to_elevenlabs_format(self) -> Dict[str, Any]:
        """Convert to ElevenLabs API format"""
        return {
            "stability": self.stability,
            "similarity_boost": self.similarity_boost,
            "style": self.style,
            "use_speaker_boost": self.use_speaker_boost,
        }


class AudioMetrics(BaseModel):
    """Audio stream metrics"""

    sample_rate: int = Field(default=24000, description="Sample rate in Hz")
    bit_rate: int = Field(default=128000, description="Bit rate in bps")
    channels: int = Field(default=1, description="Number of audio channels")
    bit_depth: int = Field(default=16, description="Bit depth")

    # Quality metrics
    signal_to_noise_ratio: Optional[float] = Field(
        None, description="SNR in dB")
    peak_amplitude: Optional[float] = Field(
        None, description="Peak amplitude (0-1)")
    rms_level: Optional[float] = Field(None, description="RMS level")

    # Performance metrics
    latency_ms: Optional[float] = Field(None, description="End-to-end latency")
    jitter_ms: Optional[float] = Field(
        None, description="Jitter in milliseconds")
    packet_loss_rate: Optional[float] = Field(
        None, description="Packet loss rate (0-1)"
    )


class AudioChunk(BaseModel):
    """Individual audio chunk in a stream"""

    id: str = Field(
        default_factory=lambda: str(
            uuid.uuid4()),
        description="Chunk ID")
    sequence_number: int = Field(..., description="Sequence number in stream")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Chunk timestamp"
    )
    duration_ms: float = Field(...,
                               description="Chunk duration in milliseconds")

    # Audio data
    data: bytes = Field(..., description="Raw audio data")
    format: AudioFormat = Field(..., description="Audio format")

    # Metadata
    is_speech: bool = Field(default=False, description="Contains speech")
    energy_level: float = Field(default=0.0, description="Audio energy level")

    @validator("data")
    def validate_data_size(cls, v) -> Any:
        """Validate chunk size"""
        max_size = 1024 * 1024  # 1MB max per chunk
        if len(v) > max_size:
            raise ValueError(f"Chunk size {len(v)} exceeds maximum {max_size}")
        return v

    def get_size_bytes(self) -> int:
        """Get chunk size in bytes"""
        return len(self.data)


class StreamBuffer(BaseModel):
    """Audio stream buffer management"""

    chunks: List[AudioChunk] = Field(
        default_factory=list, description="Buffered chunks"
    )
    max_chunks: int = Field(
        default=100,
        description="Maximum chunks to buffer")
    target_duration_ms: float = Field(
        default=1000.0, description="Target buffer duration"
    )

    # Buffer metrics
    total_duration_ms: float = Field(
        default=0.0, description="Total buffered duration")
    total_size_bytes: int = Field(default=0, description="Total buffer size")
    underrun_count: int = Field(default=0, description="Buffer underrun count")
    overrun_count: int = Field(default=0, description="Buffer overrun count")

    def add_chunk(self, chunk: AudioChunk) -> bool:
        """Add chunk to buffer"""
        if len(self.chunks) >= self.max_chunks:
            self.overrun_count += 1
            return False

        self.chunks.append(chunk)
        self.total_duration_ms += chunk.duration_ms
        self.total_size_bytes += chunk.get_size_bytes()
        return True

    def get_chunk(self) -> Optional[AudioChunk]:
        """Get next chunk from buffer"""
        if not self.chunks:
            self.underrun_count += 1
            return None

        chunk = self.chunks.pop(0)
        self.total_duration_ms -= chunk.duration_ms
        self.total_size_bytes -= chunk.get_size_bytes()
        return chunk

    def clear(self) -> Any:
        """Clear buffer"""
        self.chunks.clear()
        self.total_duration_ms = 0.0
        self.total_size_bytes = 0

    def get_fill_level(self) -> float:
        """Get buffer fill level (0-1)"""
        if self.target_duration_ms <= 0:
            return 0.0
        return min(1.0, self.total_duration_ms / self.target_duration_ms)


class AudioTranscript(BaseModel):
    """Transcription result for audio"""

    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Transcription confidence"
    )

    # Word-level timing
    words: List[Dict[str, Any]] = Field(
        default_factory=list, description="Word timings"
    )

    # Alternative transcriptions
    alternatives: List[Dict[str, Any]] = Field(
        default_factory=list, description="Alternative transcriptions"
    )

    # Metadata
    duration_ms: float = Field(..., description="Audio duration")
    processing_time_ms: Optional[float] = Field(
        None, description="Processing time")


class AudioStream(BaseModel):
    """
    Enhanced audio stream entity with complete features
    """

    # Identification
    id: str = Field(
        default_factory=lambda: str(
            uuid.uuid4()),
        description="Stream ID")
    session_id: str = Field(..., description="Associated session ID")
    child_id: Optional[str] = Field(None, description="Associated child ID")

    # Stream properties
    direction: StreamDirection = Field(..., description="Stream direction")
    state: StreamState = Field(
        default=StreamState.IDLE,
        description="Current state")
    format: AudioFormat = Field(
        default=AudioFormat.OPUS,
        description="Audio format")
    quality: AudioQuality = Field(
        default=AudioQuality.HIGH, description="Quality preset"
    )

    # Content
    text: Optional[str] = Field(None, description="Text for TTS streams")
    transcript: Optional[AudioTranscript] = Field(
        None, description="Transcription for STT"
    )

    # Voice configuration
    voice_settings: Optional[VoiceSettings] = Field(
        None, description="Voice settings for TTS"
    )

    # Audio metrics
    metrics: AudioMetrics = Field(
        default_factory=AudioMetrics, description="Stream metrics"
    )

    # Buffering
    buffer: StreamBuffer = Field(
        default_factory=StreamBuffer, description="Stream buffer"
    )

    # Timing
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation time"
    )
    started_at: Optional[datetime] = Field(
        None, description="Stream start time")
    ended_at: Optional[datetime] = Field(None, description="Stream end time")
    duration: Optional[timedelta] = Field(None, description="Total duration")

    # Statistics
    total_chunks: int = Field(default=0, description="Total chunks processed")
    total_bytes: int = Field(default=0, description="Total bytes processed")
    error_count: int = Field(default=0, description="Error count")

    # WebSocket connection
    websocket_url: Optional[str] = Field(None, description="WebSocket URL")
    connection_id: Optional[str] = Field(
        None, description="Connection identifier")

    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    # Methods

    def start(self) -> Any:
        """Start the stream"""
        if self.state not in [StreamState.IDLE, StreamState.ERROR]:
            raise ValueError(f"Cannot start stream in state {self.state}")

        self.state = StreamState.BUFFERING
        self.started_at = datetime.now()
        self.buffer.clear()

    def stop(self) -> Any:
        """Stop the stream"""
        if self.state in [
            StreamState.STREAMING,
            StreamState.PAUSED,
            StreamState.BUFFERING,
        ]:
            self.state = StreamState.COMPLETED
            self.ended_at = datetime.now()
            if self.started_at:
                self.duration = self.ended_at - self.started_at

    def pause(self) -> Any:
        """Pause the stream"""
        if self.state == StreamState.STREAMING:
            self.state = StreamState.PAUSED

    def resume(self) -> Any:
        """Resume the stream"""
        if self.state == StreamState.PAUSED:
            self.state = StreamState.STREAMING

    def add_audio_chunk(
        self,
        data: bytes,
        sequence_number: int,
        duration_ms: float,
        is_speech: bool = False,
    ) -> bool:
        """Add audio chunk to stream"""
        chunk = AudioChunk(
            sequence_number=sequence_number,
            duration_ms=duration_ms,
            data=data,
            format=self.format,
            is_speech=is_speech,
        )

        success = self.buffer.add_chunk(chunk)
        if success:
            self.total_chunks += 1
            self.total_bytes += len(data)

            # Auto-transition to streaming state
            if (
                self.state == StreamState.BUFFERING
                and self.buffer.get_fill_level() > 0.5
            ):
                self.state = StreamState.STREAMING

        return success

    def get_next_chunk(self) -> Optional[AudioChunk]:
        """Get next audio chunk"""
        if self.state not in [StreamState.STREAMING, StreamState.BUFFERING]:
            return None

        chunk = self.buffer.get_chunk()

        # Check for buffer underrun
        if chunk is None and self.state == StreamState.STREAMING:
            self.state = StreamState.BUFFERING

        return chunk

    def set_error(str) -> None:
        """Set stream to error state"""
        self.state = StreamState.ERROR
        self.error_count += 1
        self.metadata["last_error"] = error_message
        self.metadata["error_time"] = datetime.now().isoformat()

    def get_statistics(self) -> Dict[str, Any]:
        """Get stream statistics"""
        stats = {
            "id": self.id,
            "state": self.state.value,
            "direction": self.direction.value,
            "total_chunks": self.total_chunks,
            "total_bytes": self.total_bytes,
            "total_mb": round(self.total_bytes / (1024 * 1024), 2),
            "error_count": self.error_count,
            "buffer_fill_level": self.buffer.get_fill_level(),
            "buffer_underruns": self.buffer.underrun_count,
            "buffer_overruns": self.buffer.overrun_count,
        }

        if self.started_at:
            if self.ended_at:
                stats["duration_seconds"] = (
                    self.ended_at - self.started_at
                ).total_seconds()
            else:
                stats["duration_seconds"] = (
                    datetime.now() - self.started_at
                ).total_seconds()

            stats["average_bitrate_kbps"] = round(
                (
                    (self.total_bytes * 8 / stats["duration_seconds"] / 1000)
                    if stats["duration_seconds"] > 0
                    else 0
                ),
                2,
            )

        if self.metrics.latency_ms:
            stats["average_latency_ms"] = self.metrics.latency_ms

        return stats

    def calculate_quality_score(self) -> float:
        """Calculate stream quality score (0-1)"""
        factors = []

        # Buffer health
        buffer_health = 1.0 - \
            (self.buffer.underrun_count / max(self.total_chunks, 1))
        factors.append(max(0, buffer_health))

        # Error rate
        error_rate = 1.0 - (self.error_count / max(self.total_chunks, 1))
        factors.append(max(0, error_rate))

        # Latency (if available)
        if self.metrics.latency_ms:
            # Good: <150ms, Acceptable: <300ms, Poor: >300ms
            latency_score = max(0, 1.0 - (self.metrics.latency_ms / 300))
            factors.append(latency_score)

        # Packet loss (if available)
        if self.metrics.packet_loss_rate is not None:
            loss_score = 1.0 - self.metrics.packet_loss_rate
            factors.append(loss_score)

        return sum(factors) / len(factors) if factors else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "child_id": self.child_id,
            "direction": self.direction.value,
            "state": self.state.value,
            "format": self.format.value,
            "quality": self.quality.value,
            "text": self.text,
            "transcript": self.transcript.dict() if self.transcript else None,
            "voice_settings": (
                self.voice_settings.dict() if self.voice_settings else None),
            "metrics": self.metrics.dict(),
            "statistics": self.get_statistics(),
            "quality_score": self.calculate_quality_score(),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration": str(
                self.duration) if self.duration else None,
            "metadata": self.metadata,
        }

    def generate_stream_key(self) -> str:
        """Generate unique stream key for caching/routing"""
        key_parts = [
            self.session_id,
            self.direction.value,
            self.format.value,
            str(self.metrics.sample_rate),
        ]

        if self.voice_settings:
            key_parts.append(self.voice_settings.voice_id)

        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    class Config:
        """Pydantic configuration"""

        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            timedelta: lambda v: str(v),
            bytes: lambda v: f"<{len(v)} bytes>",
        }


# Helper functions for audio processing


def calculate_audio_metrics(
    audio_data: np.ndarray, sample_rate: int
) -> Dict[str, float]:
    """Calculate audio metrics from raw data"""
    # RMS level
    rms = np.sqrt(np.mean(audio_data**2))

    # Peak amplitude
    peak = np.max(np.abs(audio_data))

    # Simple SNR estimation (would need noise profile for accurate SNR)
    signal_power = np.mean(audio_data**2)
    noise_power = np.mean(
        audio_data[: int(0.1 * len(audio_data))] ** 2
    )  # First 10% as "noise"

    if noise_power > 0:
        snr_db = 10 * np.log10(signal_power / noise_power)
    else:
        snr_db = float("inf")

    return {
        "rms_level": float(rms),
        "peak_amplitude": float(peak),
        "signal_to_noise_ratio": float(snr_db) if not np.isinf(snr_db) else None,
    }


def detect_voice_activity(audio_chunk: bytes, threshold: float = 0.01) -> bool:
    """Simple voice activity detection"""
    # Convert bytes to numpy array
    audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32)
    audio_array = audio_array / 32768.0  # Normalize

    # Calculate energy
    energy = np.mean(audio_array**2)

    return energy > threshold
