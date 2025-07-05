"""
🤖 AI Response Models - Enterprise 2025 Implementation
Data models and structures for AI service responses
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AIResponseModel:
    """Enhanced AI response with comprehensive metadata"""

    text: str
    emotion: str
    category: str
    learning_points: List[str]
    session_id: str
    confidence: float = 0.0
    processing_time_ms: int = 0
    cached: bool = False
    model_used: str = ""
    usage: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "text": self.text,
            "emotion": self.emotion,
            "category": self.category,
            "learning_points": self.learning_points,
            "session_id": self.session_id,
            "confidence": self.confidence,
            "processing_time_ms": self.processing_time_ms,
            "cached": self.cached,
            "model_used": self.model_used,
            "usage": self.usage,
            "error": self.error,
        }


@dataclass
class EmotionAnalysis:
    """Emotion analysis result"""

    primary_emotion: str
    confidence: float
    detected_emotions: Dict[str, float] = field(default_factory=dict)
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConversationContext:
    """Context for conversation management"""

    session_id: str
    child_id: str
    history: List[Dict[str, Any]] = field(default_factory=list)
    current_topic: Optional[str] = None
    emotion_trend: List[str] = field(default_factory=list)
    last_interaction: Optional[datetime] = None


@dataclass
class AIServiceMetrics:
    """Performance metrics for AI service"""

    total_requests: int = 0
    total_errors: int = 0
    rate_limit_hits: int = 0
    average_processing_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    active_conversations: int = 0

    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.total_errors / self.total_requests) * 100


@dataclass
class ResponseGenerationRequest:
    """Request model for response generation"""

    message: str
    child_id: str
    session_id: str
    context: Optional[Dict[str, Any]] = None
    emotion_context: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
