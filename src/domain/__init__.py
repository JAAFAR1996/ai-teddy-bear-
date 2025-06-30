"""Domain Layer - Pure Business Logic"""

# Export emotion domain models
from .emotion.models import (
    EmotionResult, EmotionType, BehavioralIndicator,
    EmotionContext, ChildEmotionProfile, EmotionAnalytics,
    EmotionTrend, ParentalReport, EmotionInsight, RiskAssessment
)

# Export ESP32 domain models
from .esp32.models import (
    ESP32Device, DeviceStatus, HardwareState, PowerState,
    AudioSettings, MicrophoneSettings, AudioVisualization, SpeechRecognition,
    NetworkConnection, WiFiStatus, ServerConnection, CommunicationProtocol,
    ChildProfile, ConversationHistory, LearningProgress, SessionData
)
