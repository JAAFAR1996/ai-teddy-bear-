"""Domain Layer - Pure Business Logic"""

# Export emotion domain models
from .emotion.models import (
    EmotionResult, EmotionType, BehavioralIndicator,
    EmotionContext, ChildEmotionProfile, EmotionAnalytics,
    EmotionTrend, ParentalReport, EmotionInsight, RiskAssessment, RiskLevel
)

# Export ESP32 domain models
from .esp32.models import (
    ESP32Device, DeviceStatus, HardwareState, PowerState,
    AudioSettings, MicrophoneSettings, AudioVisualization, SpeechRecognition,
    NetworkConnection, WiFiStatus, ServerConnection, CommunicationProtocol,
    ChildProfile, ConversationEntry, LearningProgress, SessionData
)

# Export memory domain models
from .memory.models import (
    Memory, MemoryType, MemoryImportance, ChildMemoryProfile, ConversationSummary
)

# Audio Domain Models
from .audio.models import (
    EmotionalTone,
    Language,
    AudioConfig,
    VoiceProfile
)

# Audio Domain Services
from .audio.services import (
    VoiceActivityDetector,
    AudioProcessor
)
