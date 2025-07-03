"""
📊 Core AI Service Models - Enterprise 2025
Unified data models combining all features from existing implementations
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .enums import AIProvider, ResponseSafety, EmotionType, MessageCategory


@dataclass
class AIRequest:
    """Enhanced AI request with all features"""
    message: str
    child_id: str
    session_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Advanced options from modern service
    max_tokens: int = 150
    temperature: float = 0.7
    require_safety_check: bool = True
    timeout: float = 30.0
    
    # Child-specific context
    child_age: Optional[int] = None
    child_name: Optional[str] = None
    learning_level: Optional[str] = None
    emotional_state: Optional[str] = None
    
    # Conversation context
    conversation_history: List[Dict] = field(default_factory=list)
    previous_emotions: List[str] = field(default_factory=list)
    
    # Metadata
    device_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "message": self.message,
            "child_id": self.child_id,
            "session_id": self.session_id,
            "context": self.context,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "require_safety_check": self.require_safety_check,
            "timeout": self.timeout,
            "child_age": self.child_age,
            "child_name": self.child_name,
            "learning_level": self.learning_level,
            "emotional_state": self.emotional_state,
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AIResponse:
    """Enhanced AI response with all features"""
    text: str
    child_id: str
    session_id: str
    
    # Quality metrics
    confidence: float = 0.0
    safety_score: float = 1.0
    safety_level: ResponseSafety = ResponseSafety.SAFE
    
    # Processing info
    provider: AIProvider = AIProvider.OPENAI
    model: str = "gpt-4"
    tokens_used: int = 0
    processing_time_ms: float = 0.0
    
    # Content analysis
    emotion: str = "neutral"
    category: MessageCategory = MessageCategory.GENERAL_CONVERSATION
    learning_points: List[str] = field(default_factory=list)
    
    # Metadata
    cached: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    usage_metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    # Advanced features
    conversation_context: Dict[str, Any] = field(default_factory=dict)
    personalization_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "text": self.text,
            "child_id": self.child_id,
            "session_id": self.session_id,
            "confidence": self.confidence,
            "safety_score": self.safety_score,
            "safety_level": self.safety_level.value if isinstance(self.safety_level, ResponseSafety) else self.safety_level,
            "provider": self.provider.value if isinstance(self.provider, AIProvider) else self.provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "processing_time_ms": self.processing_time_ms,
            "emotion": self.emotion,
            "category": self.category.value if isinstance(self.category, MessageCategory) else self.category,
            "learning_points": self.learning_points,
            "cached": self.cached,
            "created_at": self.created_at.isoformat(),
            "usage_metadata": self.usage_metadata,
            "error": self.error
        }


@dataclass
class EmotionResult:
    """Enhanced emotion analysis result"""
    primary_emotion: EmotionType
    confidence: float
    
    # Detailed emotion analysis
    emotions_detected: Dict[str, float] = field(default_factory=dict)
    valence: float = 0.0  # Positive/negative scale (-1 to 1)
    arousal: float = 0.0  # Energy level (0 to 1)
    intensity: float = 0.0  # Emotion intensity (0 to 1)
    
    # Context
    child_id: Optional[str] = None
    text_analyzed: Optional[str] = None
    analysis_method: str = "text"  # text, audio, multimodal
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    analyzer_version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "primary_emotion": self.primary_emotion.value if isinstance(self.primary_emotion, EmotionType) else self.primary_emotion,
            "confidence": self.confidence,
            "emotions_detected": self.emotions_detected,
            "valence": self.valence,
            "arousal": self.arousal,
            "intensity": self.intensity,
            "child_id": self.child_id,
            "text_analyzed": self.text_analyzed,
            "analysis_method": self.analysis_method,
            "timestamp": self.timestamp.isoformat(),
            "analyzer_version": self.analyzer_version
        }


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    # Request statistics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0
    
    # Timing metrics
    average_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    total_processing_time_ms: float = 0.0
    
    # Provider metrics
    provider_usage: Dict[str, int] = field(default_factory=dict)
    provider_errors: Dict[str, int] = field(default_factory=dict)
    
    # Token usage
    total_tokens_used: int = 0
    average_tokens_per_request: float = 0.0
    
    # Cache metrics
    cache_hit_rate: float = 0.0
    cache_size: int = 0
    
    # Safety metrics
    safety_checks_performed: int = 0
    unsafe_content_blocked: int = 0
    
    # Error details
    error_breakdown: Dict[str, int] = field(default_factory=dict)
    rate_limit_incidents: int = 0
    
    # Time period
    start_time: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "cached_requests": self.cached_requests,
            "average_response_time_ms": self.average_response_time_ms,
            "min_response_time_ms": self.min_response_time_ms,
            "max_response_time_ms": self.max_response_time_ms,
            "total_processing_time_ms": self.total_processing_time_ms,
            "provider_usage": self.provider_usage,
            "provider_errors": self.provider_errors,
            "total_tokens_used": self.total_tokens_used,
            "average_tokens_per_request": self.average_tokens_per_request,
            "cache_hit_rate": self.cache_hit_rate,
            "cache_size": self.cache_size,
            "safety_checks_performed": self.safety_checks_performed,
            "unsafe_content_blocked": self.unsafe_content_blocked,
            "error_breakdown": self.error_breakdown,
            "rate_limit_incidents": self.rate_limit_incidents,
            "success_rate": self.success_rate,
            "error_rate": self.error_rate,
            "start_time": self.start_time.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class SafetyCheck:
    """Safety check result"""
    is_safe: bool
    safety_score: float
    flagged_categories: List[str] = field(default_factory=list)
    risk_level: str = "low"  # low, medium, high
    explanation: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_safe": self.is_safe,
            "safety_score": self.safety_score,
            "flagged_categories": self.flagged_categories,
            "risk_level": self.risk_level,
            "explanation": self.explanation,
            "recommendations": self.recommendations
        }


@dataclass
class ConversationSession:
    """Conversation session data"""
    session_id: str
    child_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    
    # Messages in session
    messages: List[Dict[str, Any]] = field(default_factory=list)
    
    # Session analytics
    total_messages: int = 0
    emotions_detected: List[str] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    learning_objectives_met: List[str] = field(default_factory=list)
    
    # Session metadata
    device_id: Optional[str] = None
    session_quality_score: float = 0.0
    
    def add_message(self, message: str, response: str, emotion: str, metadata: Optional[Dict] = None):
        """Add message to session"""
        self.messages.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "response": response,
            "emotion": emotion,
            "metadata": metadata or {}
        })
        self.total_messages += 1
        if emotion not in self.emotions_detected:
            self.emotions_detected.append(emotion)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "child_id": self.child_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "messages": self.messages,
            "total_messages": self.total_messages,
            "emotions_detected": self.emotions_detected,
            "topics_discussed": self.topics_discussed,
            "learning_objectives_met": self.learning_objectives_met,
            "device_id": self.device_id,
            "session_quality_score": self.session_quality_score
        } 