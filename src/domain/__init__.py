"""Domain Layer - Pure Business Logic"""

# Export emotion domain models
# Add Parent Dashboard domain exports
from . import parentdashboard

# Audio Domain Models
from .audio.models import AudioConfig, EmotionalTone, Language, VoiceProfile

# Audio Domain Services
from .audio.services import AudioProcessor, VoiceActivityDetector

# Child Domain Components
from .child import (
    AgeRange,
    ChildAnalyticsDomainService,
    ChildEngagementInsight,
    ChildFamilyDomainService,
    ChildInteractionDomainService,
    ChildSearchCriteria,
    ChildStatistics,
    InteractionMetrics,
    SearchFilters,
)
from .emotion.models import (
    BehavioralIndicator,
    ChildEmotionProfile,
    EmotionAnalytics,
    EmotionContext,
    EmotionInsight,
    EmotionResult,
    EmotionTrend,
    EmotionType,
    ParentalReport,
    RiskAssessment,
    RiskLevel,
)

# Export ESP32 domain models
from .esp32.models import (
    AudioSettings,
    AudioVisualization,
    ChildProfile,
    CommunicationProtocol,
    ConversationEntry,
    DeviceStatus,
    ESP32Device,
    HardwareState,
    LearningProgress,
    MicrophoneSettings,
    NetworkConnection,
    PowerState,
    ServerConnection,
    SessionData,
    SpeechRecognition,
    WiFiStatus,
)

# Export memory domain models
from .memory.models import ChildMemoryProfile, ConversationSummary, Memory, MemoryImportance, MemoryType

# Add reporting domain exports
from .reporting.models import (
    ActivityRecommendation,
    ChildProgress,
    EmotionDistribution,
    InteractionAnalysis,
    InterventionRecommendation,
    LLMRecommendation,
    ProgressMetrics,
    RecommendationBundle,
    ReportPeriod,
    SkillAnalysis,
    UrgencyLevel,
)
from .reporting.services import BehaviorAnalyzer, EmotionAnalyzerService, ProgressAnalyzer, SkillAnalyzer
