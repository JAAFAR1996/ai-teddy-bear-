"""ESP32 domain models."""

from .audio_models import AudioQuality, AudioSettings, AudioVisualization, MicrophoneSettings, SpeechRecognition
from .child_models import ChildProfile, ConversationEntry, LearningProgress, SessionData
from .device_models import DeviceStatus, ESP32Device, HardwareState, PowerState
from .network_models import CommunicationProtocol, NetworkConnection, ServerConnection, WiFiStatus

__all__ = [
    "ESP32Device",
    "DeviceStatus",
    "HardwareState",
    "PowerState",
    "AudioSettings",
    "MicrophoneSettings",
    "AudioVisualization",
    "SpeechRecognition",
    "AudioQuality",
    "NetworkConnection",
    "WiFiStatus",
    "ServerConnection",
    "CommunicationProtocol",
    "ChildProfile",
    "ConversationEntry",
    "LearningProgress",
    "SessionData",
]
