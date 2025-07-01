"""Infrastructure Layer - External Services and Databases"""

# Export emotion infrastructure components
# Add Parent Dashboard infrastructure services
from . import parentdashboard
# Audio Infrastructure Clients
from .audio.clients import (AzureSpeechClient, ElevenLabsClient,
                            OpenAISpeechClient, WhisperClient)
# Child Infrastructure Components
from .child import ChildBackupService, ChildSQLiteRepositoryRefactored
from .emotion import (AudioEmotionAnalyzer, EmotionRepository,
                      TextEmotionAnalyzer)
# Export ESP32 infrastructure components
from .esp32 import (AudioDriver, GUIComponents, HardwareSimulator,
                    NetworkAdapter)
# Export memory infrastructure
from .memory import MemoryRepository, VectorMemoryStore
# Add reporting infrastructure
from .reporting import ChartGenerator, PDFGenerator, ReportRepository
