"""
Voice Provider Manager
Centralizes provider initialization and management
Fixes bumpy road pattern with simplified logic
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from elevenlabs.client import AsyncElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

from src.domain.audio.models import ProviderType, ProviderConfig, ProviderOperation

logger = logging.getLogger(__name__)


@dataclass
class ProviderResources:
    """Container for provider-specific resources"""
    whisper_model: Optional[Any] = None
    azure_speech_config: Optional[Any] = None
    elevenlabs_client: Optional[Any] = None


class ProviderManager:
    """Manages voice providers with simplified initialization"""
    
    def __init__(self, settings: Optional[Any] = None):
        self.settings = settings or MockSettings()
        self.resources = ProviderResources()
        self.providers: Dict[ProviderType, ProviderConfig] = {}
        
        # Initialize all providers
        self._initialize_providers()


class MockSettings:
    """Mock settings class for testing"""
    def __init__(self):
        self.azure_speech_key = None
        self.azure_speech_region = None
        self.elevenlabs_api_key = None
    
    def _initialize_providers(self):
        """Initialize all providers with their configurations"""
        # Initialize Whisper
        whisper_available = self._init_whisper()
        self.providers[ProviderType.WHISPER] = ProviderConfig(
            provider_type=ProviderType.WHISPER,
            is_available=whisper_available,
            priority=10,
            name="Whisper",
            supported_operations=[ProviderOperation.TRANSCRIPTION]
        )
        
        # Initialize Azure
        azure_available = self._init_azure()
        self.providers[ProviderType.AZURE] = ProviderConfig(
            provider_type=ProviderType.AZURE,
            is_available=azure_available,
            priority=8,
            name="Azure Speech",
            supported_operations=[
                ProviderOperation.TRANSCRIPTION,
                ProviderOperation.SYNTHESIS
            ]
        )
        
        # Initialize ElevenLabs
        elevenlabs_available = self._init_elevenlabs()
        self.providers[ProviderType.ELEVENLABS] = ProviderConfig(
            provider_type=ProviderType.ELEVENLABS,
            is_available=elevenlabs_available,
            priority=10,
            name="ElevenLabs",
            supported_operations=[ProviderOperation.SYNTHESIS]
        )
        
        # Initialize GTTS (always available)
        self.providers[ProviderType.GTTS] = ProviderConfig(
            provider_type=ProviderType.GTTS,
            is_available=True,
            priority=5,
            name="Google TTS",
            supported_operations=[ProviderOperation.SYNTHESIS]
        )
        
        # Initialize Fallback (always available)
        self.providers[ProviderType.FALLBACK] = ProviderConfig(
            provider_type=ProviderType.FALLBACK,
            is_available=True,
            priority=5,
            name="Fallback Recognition",
            supported_operations=[ProviderOperation.TRANSCRIPTION]
        )
    
    def _init_whisper(self) -> bool:
        """Initialize Whisper model"""
        if not WHISPER_AVAILABLE:
            logger.warning("Whisper library not available")
            return False
        
        try:
            self.resources.whisper_model = whisper.load_model("base")
            logger.info("✅ Whisper model loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load Whisper: {str(e)}")
            return False
    
    def _init_azure(self) -> bool:
        """Initialize Azure Speech services"""
        if not AZURE_AVAILABLE:
            logger.warning("Azure Speech library not available")
            return False
        
        try:
            if self.settings.azure_speech_key and self.settings.azure_speech_region:
                self.resources.azure_speech_config = speechsdk.SpeechConfig(
                    subscription=self.settings.azure_speech_key,
                    region=self.settings.azure_speech_region,
                )
                logger.info("✅ Azure Speech initialized")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Azure Speech: {str(e)}")
            return False
    
    def _init_elevenlabs(self) -> bool:
        """Initialize ElevenLabs client"""
        if not ELEVENLABS_AVAILABLE:
            logger.warning("ElevenLabs library not available")
            return False
        
        try:
            if self.settings.elevenlabs_api_key:
                self.resources.elevenlabs_client = AsyncElevenLabs(
                    api_key=self.settings.elevenlabs_api_key
                )
                logger.info("✅ ElevenLabs initialized")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs: {str(e)}")
            return False
    
    def get_providers_for_operation(
        self, operation: ProviderOperation
    ) -> List[ProviderConfig]:
        """Get all providers that support a specific operation"""
        return [
            provider for provider in self.providers.values()
            if operation in provider.supported_operations and provider.is_available
        ]
    
    def get_all_providers(self) -> List[ProviderConfig]:
        """Get all configured providers"""
        return list(self.providers.values())
    
    def get_provider(self, provider_type: ProviderType) -> Optional[ProviderConfig]:
        """Get specific provider by type"""
        return self.providers.get(provider_type)
    
    def update_availability(self, provider_type: str, is_available: bool):
        """
        Update provider availability - FIXED BUMPY ROAD
        Simplified logic without nested conditionals
        """
        # Convert string to enum safely
        try:
            provider_enum = ProviderType(provider_type)
        except ValueError:
            logger.error(f"Unknown provider type: {provider_type}")
            return
        
        # Update provider if it exists
        provider = self.providers.get(provider_enum)
        if provider:
            provider.is_available = is_available
            logger.info(f"Updated {provider.name} availability to {is_available}")
        else:
            logger.warning(f"Provider {provider_type} not found in registry")
    
    def get_all_providers_status(self) -> dict:
        """Get comprehensive status of all providers"""
        status = {
            "transcription": [],
            "synthesis": []
        }
        
        for provider in self.providers.values():
            provider_info = {
                "name": provider.name,
                "type": provider.provider_type.value,
                "available": provider.is_available,
                "priority": provider.priority
            }
            
            if ProviderOperation.TRANSCRIPTION in provider.supported_operations:
                status["transcription"].append(provider_info)
            
            if ProviderOperation.SYNTHESIS in provider.supported_operations:
                status["synthesis"].append(provider_info)
        
        return status
    
    def get_resources(self) -> ProviderResources:
        """Get provider resources for use in executors"""
        return self.resources 