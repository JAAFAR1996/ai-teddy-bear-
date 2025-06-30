"""Application Layer - Use Cases and Orchestration"""

# Export emotion application services
from .services.emotion import (
    EmotionAnalysisService, EmotionDatabaseService,
    EmotionAnalyticsService, EmotionHistoryService
)

# Export ESP32 application services
from .services.esp32 import (
    DeviceManagementService, AudioManagementService,
    NetworkCommunicationService, GUIManagementService,
    ChildProfileService
)

# Audio Application Services
from .services.audio.voice_synthesis_service import VoiceSynthesisService
from .services.audio.voice_recognition_service import VoiceRecognitionService
from .services.audio.voice_profile_service import VoiceProfileService

# Add reporting application services
from .services.reporting import (
    ReportGenerationService,
    AnalysisOrchestratorService,
    RecommendationService
)

# Add Parent Dashboard application services
from .services import parentdashboard
