"""ESP32 domain models."""

from .device_models import (
    ESP32Device, DeviceStatus, HardwareState, PowerState
)
from .audio_models import (
    AudioSettings, MicrophoneSettings, AudioVisualization, SpeechRecognition, AudioQuality
)
from .network_models import (
    NetworkConnection, WiFiStatus, ServerConnection, CommunicationProtocol
)
from .child_models import (
    ChildProfile, ConversationEntry, LearningProgress, SessionData
)

__all__ = [
    'ESP32Device',
    'DeviceStatus', 
    'HardwareState',
    'PowerState',
    'AudioSettings',
    'MicrophoneSettings',
    'AudioVisualization',
    'SpeechRecognition',
    'AudioQuality',
    'NetworkConnection',
    'WiFiStatus',
    'ServerConnection',
    'CommunicationProtocol',
    'ChildProfile',
    'ConversationEntry',
    'LearningProgress',
    'SessionData'
]
