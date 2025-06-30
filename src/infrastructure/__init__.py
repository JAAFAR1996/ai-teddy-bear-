"""Infrastructure Layer - External Services and Databases"""

# Export emotion infrastructure components
from .emotion import (
    TextEmotionAnalyzer, AudioEmotionAnalyzer, EmotionRepository
)

# Export ESP32 infrastructure components  
from .esp32 import (
    HardwareSimulator, AudioDriver, NetworkAdapter, GUIComponents
)

# Export memory infrastructure
from .memory import (
    VectorMemoryStore, MemoryRepository
)

# Audio Infrastructure Clients
from .audio.clients import (
    ElevenLabsClient,
    AzureSpeechClient,
    WhisperClient,
    OpenAISpeechClient
)

# Add reporting infrastructure
from .reporting import (
    ChartGenerator,
    PDFGenerator,
    ReportRepository
)

# Add Parent Dashboard infrastructure services  
from . import parentdashboard

# Child Infrastructure Components
from .child import (
    ChildSQLiteRepositoryRefactored,
    ChildBackupService
)
