"""
🔧 Core AI Service Enums - Enterprise 2025
Unified constants and enums from all existing implementations
"""

from enum import Enum


class AIProvider(Enum):
    """AI Provider types"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    HUGGING_FACE = "hugging_face"
    LOCAL = "local"


class ResponseSafety(Enum):
    """Response safety levels"""

    SAFE = "safe"
    CAUTION = "caution"
    UNSAFE = "unsafe"
    BLOCKED = "blocked"


class EmotionType(Enum):
    """Emotion types from advanced emotion analyzer"""

    # Primary emotions
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    SURPRISED = "surprised"
    NEUTRAL = "neutral"

    # Secondary emotions
    EXCITED = "excited"
    ANXIOUS = "anxious"
    CONFUSED = "confused"
    CURIOUS = "curious"
    BORED = "bored"
    FRUSTRATED = "frustrated"
    PROUD = "proud"
    ASHAMED = "ashamed"

    # Complex emotions
    OVERWHELMED = "overwhelmed"
    CONTENT = "content"
    LONELY = "lonely"
    GRATEFUL = "grateful"
    HOPEFUL = "hopeful"
    WORRIED = "worried"


class MessageCategory(Enum):
    """Message categories for conversation analysis"""

    GENERAL_CONVERSATION = "general_conversation"
    EDUCATIONAL = "educational"
    EMOTIONAL_SUPPORT = "emotional_support"
    STORYTELLING = "storytelling"
    PLAY_ACTIVITY = "play_activity"
    SAFETY_CONCERN = "safety_concern"
    BEHAVIORAL_GUIDANCE = "behavioral_guidance"
    LEARNING_ASSESSMENT = "learning_assessment"
    SOCIAL_SKILLS = "social_skills"
    CREATIVE_EXPRESSION = "creative_expression"
    PROBLEM_SOLVING = "problem_solving"
    DAILY_ROUTINE = "daily_routine"


class CacheLevel(Enum):
    """Cache levels for different types of data"""

    MEMORY = "memory"
    REDIS = "redis"
    DATABASE = "database"
    PERSISTENT = "persistent"


class ProcessingPriority(Enum):
    """Processing priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class ContentType(Enum):
    """Content types for processing"""

    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class SafetyRiskLevel(Enum):
    """Safety risk levels"""

    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ResponseType(Enum):
    """Response types for different contexts"""

    DIRECT_ANSWER = "direct_answer"
    EDUCATIONAL = "educational"
    ENCOURAGING = "encouraging"
    REDIRECTING = "redirecting"
    STORY_BASED = "story_based"
    PLAY_BASED = "play_based"
    EMOTIONAL_SUPPORT = "emotional_support"
    SAFETY_GUIDANCE = "safety_guidance"


class SessionStatus(Enum):
    """Conversation session statuses"""

    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    INTERRUPTED = "interrupted"
    ERROR = "error"


class LearningLevel(Enum):
    """Child learning levels"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    GIFTED = "gifted"
    NEEDS_SUPPORT = "needs_support"


class DeviceType(Enum):
    """Device types for the teddy bear"""

    PHYSICAL_TEDDY = "physical_teddy"
    MOBILE_APP = "mobile_app"
    WEB_APP = "web_app"
    TABLET = "tablet"
    SMART_SPEAKER = "smart_speaker"


class ErrorType(Enum):
    """Error types for error handling"""

    NETWORK_ERROR = "network_error"
    API_ERROR = "api_error"
    RATE_LIMIT = "rate_limit"
    SAFETY_VIOLATION = "safety_violation"
    TIMEOUT = "timeout"
    INVALID_REQUEST = "invalid_request"
    AUTHENTICATION_ERROR = "authentication_error"
    PERMISSION_DENIED = "permission_denied"
    INTERNAL_ERROR = "internal_error"
    PROVIDER_ERROR = "provider_error"


class HealthStatus(Enum):
    """Health check statuses"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Metric types for monitoring"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class NotificationLevel(Enum):
    """Notification levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ConversationPhase(Enum):
    """Conversation phases"""

    GREETING = "greeting"
    MAIN_INTERACTION = "main_interaction"
    LEARNING_ACTIVITY = "learning_activity"
    EMOTIONAL_CHECK = "emotional_check"
    CLOSING = "closing"
    EMERGENCY = "emergency"


class PersonalizationLevel(Enum):
    """Personalization levels"""

    NONE = "none"
    BASIC = "basic"
    MODERATE = "moderate"
    HIGH = "high"
    FULL = "full"


class DataRetentionPolicy(Enum):
    """Data retention policies"""

    NONE = "none"  # No retention
    SESSION = "session"  # Keep for session only
    DAILY = "daily"  # Keep for 24 hours
    WEEKLY = "weekly"  # Keep for 7 days
    MONTHLY = "monthly"  # Keep for 30 days
    LONG_TERM = "long_term"  # Keep for legal/educational purposes


class ComplianceLevel(Enum):
    """Compliance levels"""

    COPPA = "coppa"  # Children's Online Privacy Protection Act
    GDPR = "gdpr"  # General Data Protection Regulation
    FERPA = "ferpa"  # Family Educational Rights and Privacy Act
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    CCPA = "ccpa"  # California Consumer Privacy Act
