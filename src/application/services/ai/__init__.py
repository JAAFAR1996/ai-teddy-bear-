"""
🤖 AI Services Module - Enterprise 2025 Implementation
Centralized AI services with clean architecture and dependency injection
"""

# Core models and interfaces
from .models.ai_response_models import (
    AIResponseModel,
    EmotionAnalysis,
    ConversationContext,
    AIServiceMetrics,
    ResponseGenerationRequest
)

from .interfaces.ai_service_interface import (
    IAIService,
    IEmotionAnalyzer,
    IResponseGenerator,
    ICacheService,
    IConversationManager
)

# Service implementations
from .analyzers.emotion_analyzer_service import EmotionAnalyzerService
from .fallback_response_service import FallbackResponseService
from .ai_service_factory import EnhancedAIServiceFactory, AIServiceFactory

# Re-exports for backward compatibility
__all__ = [
    # Models
    "AIResponseModel",
    "EmotionAnalysis", 
    "ConversationContext",
    "AIServiceMetrics",
    "ResponseGenerationRequest",
    
    # Interfaces
    "IAIService",
    "IEmotionAnalyzer",
    "IResponseGenerator",
    "ICacheService",
    "IConversationManager",
    
    # Services
    "EmotionAnalyzerService",
    "FallbackResponseService",
    
    # Factory
    "EnhancedAIServiceFactory",
    "AIServiceFactory"
] 