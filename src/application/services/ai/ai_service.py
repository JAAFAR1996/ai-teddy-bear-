"""
🤖 AI Service - Enterprise 2025 Implementation
Refactored to use modular components and clean architecture
"""

import logging
from typing import Dict, Any, Optional

# Import refactored components
from src.application.services.ai.refactored_ai_service import RefactoredAIService, AIService as CompatibilityAIService
from src.application.services.ai.models.ai_response_models import AIResponseModel
from src.application.services.ai.interfaces.ai_service_interface import IAIService
from src.application.services.ai.ai_service_factory import EnhancedAIServiceFactory
from src.domain.entities.child import Child
from src.infrastructure.config import Settings
from src.infrastructure.caching.simple_cache_service import CacheService

logger = logging.getLogger(__name__)

# ================== MAIN AI SERVICE (Delegation Pattern) ==================

class AIService:
    """
    🎯 Main AI Service that delegates to refactored components
    
    This service maintains backward compatibility while using the new modular architecture.
    All heavy logic has been moved to specialized services.
    """
    
    def __init__(
        self,
        settings: Settings,
        cache_service: CacheService,
        provider: str = "openai_modern"
    ):
        """Initialize AI Service with refactored components"""
        self.settings = settings
        self.cache_service = cache_service
        self.provider = provider
        
        # Delegate to refactored service
        self._refactored_service = RefactoredAIService(
            settings=settings,
            cache_service=cache_service,
            provider=provider
        )
        
        logger.info(f"✅ AI Service initialized (delegating to refactored service)")
    
    async def generate_response(
        self,
        message: str,
        child: Child,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponseModel:
        """Generate AI response (delegated)"""
        return await self._refactored_service.generate_response(
            message=message,
            child=child,
            session_id=session_id,
            context=context
        )
    
    async def analyze_emotion(self, message: str) -> str:
        """Analyze emotion (delegated)"""
        return await self._refactored_service.analyze_emotion(message)
    
    async def categorize_message(self, message: str) -> str:
        """Categorize message (delegated)"""
        return await self._refactored_service.categorize_message(message)
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics (delegated)"""
        return await self._refactored_service.get_performance_metrics()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check (delegated)"""
        return await self._refactored_service.health_check()
    
    def is_initialized(self) -> bool:
        """Check initialization status (delegated)"""
        return self._refactored_service.is_initialized()
    
    async def initialize(self) -> None:
        """Initialize service (delegated)"""
        await self._refactored_service.initialize()


# ================== FACTORY DELEGATION ==================

class AIServiceFactory:
    """
    🏭 Factory for creating AI service instances (delegated to enhanced factory)
    """
    
    @staticmethod
    def create(
        provider: str,
        settings: Settings,
        cache_service: CacheService,
        **kwargs
    ) -> IAIService:
        """Create AI service using enhanced factory"""
        return EnhancedAIServiceFactory.create_service(
            provider=provider,
            settings=settings,
            cache_service=cache_service,
            **kwargs
        )
    
    @staticmethod
    def get_available_providers() -> list:
        """Get available providers"""
        return EnhancedAIServiceFactory.get_available_providers()


# ================== BACKWARD COMPATIBILITY ==================

# Legacy aliases for existing code
ModernOpenAIService = AIService
EnhancedAIServiceFactory_Legacy = AIServiceFactory

# Export main interfaces
__all__ = [
    "AIService",
    "AIServiceFactory", 
    "AIResponseModel",
    "IAIService",
    "RefactoredAIService"
]

logger.info("🔄 AI Service module loaded with refactored architecture") 