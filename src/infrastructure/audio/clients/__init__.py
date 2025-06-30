"""
Infrastructure Audio Clients
External service integrations for audio processing
"""

from .elevenlabs_client import ElevenLabsClient
from .azure_speech_client import AzureSpeechClient
from .whisper_client import WhisperClient
from .openai_speech_client import OpenAISpeechClient

__all__ = [
    'ElevenLabsClient',
    'AzureSpeechClient', 
    'WhisperClient',
    'OpenAISpeechClient'
] 