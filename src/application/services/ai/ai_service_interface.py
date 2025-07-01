"""
🤖 AI Service Interfaces - Enterprise 2025 Implementation
Abstract interfaces and contracts for AI services
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from src.application.services.ai.models.ai_response_models import (
    AIResponseModel, 
    EmotionAnalysis,
    ConversationContext,
    AIServiceMetrics,
    ResponseGenerationRequest
)
from src.core.domain.entities.child import Child

class IAIService(ABC):
    """Enhanced AI Service interface with modern capabilities"""
    
    @abstractmethod
    async def generate_response(
        self,
        message: str,
        child: Child,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponseModel:
        """Generate AI response with enhanced context handling"""
        pass
    
    @abstractmethod
    async def analyze_emotion(self, message: str) -> str:
        """Analyze emotion from message using advanced emotion analyzer"""
        pass
    
    @abstractmethod
    async def categorize_message(self, message: str) -> str:
        """Categorize the message type with enhanced detection"""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self) -> AIServiceMetrics:
        """Get comprehensive performance metrics"""
        pass

class IEmotionAnalyzer(ABC):
    """Interface for emotion analysis services"""
    
    @abstractmethod
    async def analyze_text_emotion(self, text: str, language: str = "ar") -> EmotionAnalysis:
        """Analyze emotion from text with language support"""
        pass
    
    @abstractmethod
    async def analyze_emotion_trend(
        self, 
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze emotion trends in conversation"""
        pass

class IResponseGenerator(ABC):
    """Interface for response generation services"""
    
    @abstractmethod
    async def generate_contextual_response(
        self,
        request: ResponseGenerationRequest
    ) -> AIResponseModel:
        """Generate contextual response based on request"""
        pass
    
    @abstractmethod
    async def generate_fallback_response(
        self,
        error_type: str,
        child: Child,
        session_id: str
    ) -> AIResponseModel:
        """Generate fallback response for errors"""
        pass

class ICacheService(ABC):
    """Interface for caching services"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value by key"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cached value with TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete cached value"""
        pass

class IConversationManager(ABC):
    """Interface for conversation management"""
    
    @abstractmethod
    async def get_conversation_context(
        self, 
        session_id: str, 
        child_id: str
    ) -> ConversationContext:
        """Get conversation context for session"""
        pass
    
    @abstractmethod
    async def update_conversation_history(
        self,
        session_id: str,
        child_id: str,
        user_message: str,
        ai_response: str,
        emotion: str
    ) -> None:
        """Update conversation history"""
        pass
    
    @abstractmethod
    async def clear_conversation_history(self, session_id: str) -> None:
        """Clear conversation history for session"""
        pass 