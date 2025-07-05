#!/usr/bin/env python3
"""
📊 Synthesis Service Data Models
نماذج البيانات لخدمات تركيب الصوت
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

# Import voice settings from external dependencies
try:
    from elevenlabs import VoiceSettings
except ImportError:
    # Mock VoiceSettings for environments without ElevenLabs
    @dataclass
    class VoiceSettings:
        stability: float = 0.5
        similarity_boost: float = 0.8
        style: float = 0.4
        use_speaker_boost: bool = True

from src.domain.value_objects import EmotionalTone


class VoiceProvider(Enum):
    """Supported voice synthesis providers"""
    ELEVENLABS = "elevenlabs"
    OPENAI = "openai"
    AZURE = "azure"
    SYSTEM = "system"  # OS built-in TTS


@dataclass
class SynthesisConfig:
    """Configuration for synthesis service"""
    # Audio settings
    sample_rate: int = 24000
    channels: int = 1
    bit_depth: int = 16
    
    # Streaming settings
    chunk_size: int = 1024
    buffer_size: int = 4096
    streaming_enabled: bool = True
    
    # Quality settings
    voice_stability: float = 0.5
    voice_similarity: float = 0.8
    voice_style: float = 0.4
    voice_boost: bool = True
    
    # Performance settings
    timeout_seconds: float = 30.0
    max_retries: int = 3
    fallback_provider: VoiceProvider = VoiceProvider.SYSTEM
    
    # Language settings
    default_language: str = "en"
    auto_detect_language: bool = True


@dataclass
class VoiceCharacter:
    """Voice character profile with emotional settings"""
    id: str
    name: str
    provider: VoiceProvider
    voice_id: str
    language: str
    description: str
    
    # Emotional voice settings
    emotional_settings: Dict[EmotionalTone, VoiceSettings]
    
    # Voice adjustments
    pitch_adjustment: float = 0.0  # semitones
    speed_adjustment: float = 1.0  # multiplier
    volume_adjustment: float = 1.0  # multiplier


@dataclass
class SynthesisContext:
    """Context for synthesis operations"""
    text: str
    emotion: EmotionalTone
    character: VoiceCharacter
    voice_settings: VoiceSettings


@dataclass
class SynthesisServiceCredentials:
    """Credentials and settings for synthesis service providers"""
    # API Keys
    elevenlabs_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    azure_speech_key: Optional[str] = None
    
    # Provider-specific settings
    azure_speech_region: str = "eastus"
    
    def has_elevenlabs(self) -> bool:
        """Check if ElevenLabs credentials are available"""
        return self.elevenlabs_api_key is not None
    
    def has_openai(self) -> bool:
        """Check if OpenAI credentials are available"""
        return self.openai_api_key is not None
    
    def has_azure(self) -> bool:
        """Check if Azure Speech credentials are available"""
        return self.azure_speech_key is not None
    
    def get_available_providers(self) -> List[VoiceProvider]:
        """Get list of available providers based on credentials"""
        providers = []
        if self.has_elevenlabs():
            providers.append(VoiceProvider.ELEVENLABS)
        if self.has_openai():
            providers.append(VoiceProvider.OPENAI)
        if self.has_azure():
            providers.append(VoiceProvider.AZURE)
        providers.append(VoiceProvider.SYSTEM)  # Always available as fallback
        return providers 