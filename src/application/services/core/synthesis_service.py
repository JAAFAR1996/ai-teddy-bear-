#!/usr/bin/env python3
"""
🔊 Synthesis Service - Refactored for High Cohesion
خدمة تركيب الصوت - مُعاد هيكلتها لتحسين التماسك

⚠️ REFACTORING NOTICE: 
This file has been refactored to resolve low cohesion issues.
The monolithic 943-line service has been split into specialized services.

New Architecture:
- ModernSynthesisService: Main facade service
- StreamingAudioBuffer: Audio buffer management
- VoiceCharacterManager: Character management
- AudioProcessor: Audio processing
- PerformanceMonitor: Performance tracking  
- Providers: ElevenLabs, OpenAI, Azure, Fallback implementations

Benefits:
✅ High Cohesion - Each service has a single responsibility
✅ Maintainability - Easier to test and modify
✅ Extensibility - Easy to add new providers
✅ Testability - Each component can be tested independently
"""

import warnings

# Import the new refactored services
from ..synthesis import (
    # Main Service
    ModernSynthesisService,
    
    # Models
    VoiceProvider,
    SynthesisConfig, 
    VoiceCharacter,
    SynthesisContext,
    SynthesisServiceCredentials,
    
    # Specialized Services
    StreamingAudioBuffer,
    VoiceCharacterManager,
    AudioProcessor,
    PerformanceMonitor,
    
    # Providers
    ElevenLabsProvider,
    OpenAIProvider,
    AzureProvider,
    FallbackProvider,
    
    # Factory Functions
    create_synthesis_service,
    create_synthesis_service_legacy,
    create_synthesis_service_old
)

# Legacy compatibility aliases
SynthesisService = ModernSynthesisService

# Re-export all components for backward compatibility
__all__ = [
    # Main Service (New Architecture)
    'ModernSynthesisService',
    'SynthesisService',  # Legacy alias
    
    # Models
    'VoiceProvider',
    'SynthesisConfig',
    'VoiceCharacter', 
    'SynthesisContext',
    'SynthesisServiceCredentials',
    
    # Specialized Services (High Cohesion)
    'StreamingAudioBuffer',
    'VoiceCharacterManager', 
    'AudioProcessor',
    'PerformanceMonitor',
    
    # Provider Implementations
    'ElevenLabsProvider',
    'OpenAIProvider', 
    'AzureProvider',
    'FallbackProvider',
    
    # Factory Functions
    'create_synthesis_service',
    'create_synthesis_service_legacy', 
    'create_synthesis_service_old'
]

warnings.warn("Service refactored for better cohesion", FutureWarning) 