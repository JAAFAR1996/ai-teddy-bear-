"""
🔊 Synthesis Services Package - Refactored for High Cohesion
خدمات تركيب الصوت - مُعاد هيكلتها لتحسين التماسك
"""

from .models import (
    VoiceProvider,
    SynthesisConfig,
    VoiceCharacter,
    SynthesisContext,
    SynthesisServiceCredentials
)
from .audio_buffer import StreamingAudioBuffer
from .character_manager import VoiceCharacterManager
from src.domain.audio.services import AudioProcessor
from .performance_monitor import PerformanceMonitor
from .providers import (
    BaseSynthesisProvider,
    ElevenLabsProvider,
    OpenAIProvider,
    AzureProvider,
    FallbackProvider
)
from .synthesis_service import ModernSynthesisService
from .factory import (
    create_synthesis_service,
    create_synthesis_service_legacy,
    create_synthesis_service_old
)

# Legacy compatibility
SynthesisService = ModernSynthesisService

__all__ = [
    # Models
    'VoiceProvider',
    'SynthesisConfig', 
    'VoiceCharacter',
    'SynthesisContext',
    'SynthesisServiceCredentials',
    
    # Core Services
    'StreamingAudioBuffer',
    'VoiceCharacterManager',
    'AudioProcessor', 
    'PerformanceMonitor',
    
    # Providers
    'BaseSynthesisProvider',
    'ElevenLabsProvider',
    'OpenAIProvider',
    'AzureProvider',
    'FallbackProvider',
    
    # Main Service
    'ModernSynthesisService',
    'SynthesisService',  # Legacy alias
    
    # Factory Functions
    'create_synthesis_service',
    'create_synthesis_service_legacy',
    'create_synthesis_service_old'
] 