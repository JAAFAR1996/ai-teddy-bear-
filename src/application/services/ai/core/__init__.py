"""
🏗️ Core AI Service Package - Enterprise 2025
Unified core components for the AI service architecture
"""

from .enums import (
    AIProvider,
    ResponseSafety,
    EmotionType,
    MessageCategory,
    CacheLevel,
    ProcessingPriority,
    ContentType,
    SafetyRiskLevel,
    ResponseType,
    SessionStatus,
    LearningLevel,
    DeviceType,
    ErrorType,
    HealthStatus,
    MetricType,
    NotificationLevel,
    ConversationPhase,
    PersonalizationLevel,
    DataRetentionPolicy,
    ComplianceLevel,
)

from .models import (
    AIRequest,
    AIResponse,
    EmotionResult,
    PerformanceMetrics,
    SafetyCheck,
    ConversationSession,
)

from .interfaces import (
    IAIProvider,
    IAIService,
    IEmotionAnalyzer,
    ISafetyChecker,
    ICacheService,
    IConversationManager,
    IFallbackHandler,
    IAIServiceFactory,
)

__all__ = [
    # Enums
    "AIProvider",
    "ResponseSafety",
    "EmotionType",
    "MessageCategory",
    "CacheLevel",
    "ProcessingPriority",
    "ContentType",
    "SafetyRiskLevel",
    "ResponseType",
    "SessionStatus",
    "LearningLevel",
    "DeviceType",
    "ErrorType",
    "HealthStatus",
    "MetricType",
    "NotificationLevel",
    "ConversationPhase",
    "PersonalizationLevel",
    "DataRetentionPolicy",
    "ComplianceLevel",
    # Models
    "AIRequest",
    "AIResponse",
    "EmotionResult",
    "PerformanceMetrics",
    "SafetyCheck",
    "ConversationSession",
    # Interfaces
    "IAIProvider",
    "IAIService",
    "IEmotionAnalyzer",
    "ISafetyChecker",
    "ICacheService",
    "IConversationManager",
    "IFallbackHandler",
    "IAIServiceFactory",
]
