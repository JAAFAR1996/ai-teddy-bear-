"""
Data models for the distributed AI processing system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class ProcessingPriority(Enum):
    """Processing priority levels for conversation requests."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    EMERGENCY = 5


class AIServiceType(Enum):
    """Types of AI services in the distributed system."""

    TRANSCRIPTION = "transcription"
    EMOTION_ANALYSIS = "emotion_analysis"
    SAFETY_CHECK = "safety_check"
    AI_RESPONSE = "ai_response"
    TTS_SYNTHESIS = "tts_synthesis"
    PERSONALIZATION = "personalization"


@dataclass
class ChildContext:
    """Child context for personalized processing."""

    child_id: str
    name: str
    age: int
    language: str = "ar"
    voice_profile: str = "child_friendly"
    emotion_state: str = "neutral"
    conversation_history: List[str] = field(default_factory=list)
    safety_level: str = "standard"
    personalization_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationRequest:
    """Request for distributed conversation processing."""

    request_id: str
    audio_data: bytes
    child_context: ChildContext
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    max_processing_time_ms: int = 5000
    requested_services: List[AIServiceType] = field(
        default_factory=lambda: [
            AIServiceType.TRANSCRIPTION,
            AIServiceType.EMOTION_ANALYSIS,
            AIServiceType.SAFETY_CHECK,
            AIServiceType.AI_RESPONSE,
            AIServiceType.TTS_SYNTHESIS,
        ]
    )
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationResponse:
    """Response from distributed conversation processing."""

    request_id: str
    success: bool
    audio: bytes | None = None
    transcription: str = ""
    ai_text: str = ""
    emotion: str = "neutral"
    safety_status: str = "safe"
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    processing_source: str = "distributed"
    service_results: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    error_message: str = ""


@dataclass
class ProcessingMetrics:
    """Metrics for distributed processing performance."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_processing_time_ms: float = 0.0
    service_latencies: Dict[str, float] = field(default_factory=dict)
    throughput_per_second: float = 0.0
    active_workers: int = 0
    queue_length: int = 0
    last_updated: datetime | None = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
