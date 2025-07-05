"""
Infrastructure Audio Clients
External service integrations for audio processing
"""

from .azure_speech_client import AzureSpeechClient
from .elevenlabs_client import ElevenLabsClient
from .openai_speech_client import OpenAISpeechClient
from .whisper_client import WhisperClient

__all__ = [
    "ElevenLabsClient",
    "AzureSpeechClient",
    "WhisperClient",
    "OpenAISpeechClient",
]
