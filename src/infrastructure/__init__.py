"""Infrastructure Layer - External Services and Databases"""

# Export emotion infrastructure components
from .emotion import (
    TextEmotionAnalyzer, AudioEmotionAnalyzer, EmotionRepository
)

# Export ESP32 infrastructure components  
from .esp32 import (
    HardwareSimulator, AudioDriver, NetworkAdapter, GUIComponents
)
