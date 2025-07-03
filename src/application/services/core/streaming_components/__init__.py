"""
🎵 Streaming Service Components - High Cohesion Architecture
Refactored streaming service components following EXTRACT CLASS pattern
"""

from .websocket_manager import WebSocketManager
from .audio_processor import AudioProcessor
from .text_to_speech_service import TextToSpeechService
from .llm_processor import LLMProcessor
from .connection_manager import ConnectionManager
from .models import (
    AudioProcessingRequest,
    TextToSpeechRequest,
    LLMRequest,
    StreamingStatus
)

__all__ = [
    # Core Components
    "WebSocketManager",
    "AudioProcessor", 
    "TextToSpeechService",
    "LLMProcessor",
    "ConnectionManager",
    
    # Data Models
    "AudioProcessingRequest",
    "TextToSpeechRequest",
    "LLMRequest",
    "StreamingStatus"
]

# Version info
__version__ = "2.0.0"
__author__ = "AI Teddy Bear Team"
__description__ = "High-cohesion streaming components with EXTRACT CLASS refactoring" 