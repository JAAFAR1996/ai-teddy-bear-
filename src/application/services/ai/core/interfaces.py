"""
🔗 Core AI Service Interfaces - Enterprise 2025
Unified interfaces combining all features from existing implementations
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol

from .models import AIRequest, AIResponse, EmotionResult, PerformanceMetrics


class IAIProvider(Protocol):
    """Protocol for AI providers (OpenAI, Anthropic, etc.)"""

    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate AI response"""
        ...

    async def check_safety(self, content: str) -> str:
        """Check content safety"""
        ...

    async def health_check(self) -> bool:
        """Check provider health"""
        ...

    async def get_usage_metrics(self) -> Dict[str, Any]:
        """Get provider usage metrics"""
        ...


class IAIService(ABC):
    """Main AI Service interface with all enterprise features"""

    @abstractmethod
    async def generate_response(
        self,
        message: str,
        child_id: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AIResponse:
        """Generate AI response for child"""
        pass

    @abstractmethod
    async def analyze_emotion(self, text: str) -> EmotionResult:
        """Analyze emotion in text"""
        pass

    @abstractmethod
    async def categorize_message(self, message: str) -> str:
        """Categorize message type"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        pass

    @abstractmethod
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Get detailed performance metrics"""
        pass

    @abstractmethod
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        pass

    @abstractmethod
    async def switch_provider(self, provider: str) -> bool:
        """Switch to different provider"""
        pass


class IEmotionAnalyzer(ABC):
    """Enhanced emotion analysis interface"""

    @abstractmethod
    async def analyze_text_emotion(self, text: str) -> EmotionResult:
        """Analyze emotion in text"""
        pass

    @abstractmethod
    async def analyze_audio_emotion(self, audio_data: bytes) -> EmotionResult:
        """Analyze emotion in audio"""
        pass

    @abstractmethod
    async def get_emotion_history(self, child_id: str) -> List[EmotionResult]:
        """Get emotion history for child"""
        pass

    @abstractmethod
    async def detect_emotional_patterns(self, child_id: str) -> Dict[str, Any]:
        """Detect emotional patterns"""
        pass


class ISafetyChecker(ABC):
    """Content safety checking interface"""

    @abstractmethod
    async def check_content_safety(self, content: str) -> Dict[str, Any]:
        """Check if content is safe for children"""
        pass

    @abstractmethod
    async def check_conversation_safety(
            self, messages: List[Dict]) -> Dict[str, Any]:
        """Check entire conversation safety"""
        pass

    @abstractmethod
    async def get_safety_score(self, content: str) -> float:
        """Get safety score (0-1)"""
        pass


class ICacheService(ABC):
    """Enhanced caching interface"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cached value with TTL"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete cached value"""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern"""
        pass

    @abstractmethod
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass


class IConversationManager(ABC):
    """Conversation management interface"""

    @abstractmethod
    async def start_conversation(self, child_id: str) -> str:
        """Start new conversation session"""
        pass

    @abstractmethod
    async def end_conversation(self, session_id: str) -> bool:
        """End conversation session"""
        pass

    @abstractmethod
    async def add_message(
        self,
        session_id: str,
        message: str,
        response: str,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Add message to conversation"""
        pass

    @abstractmethod
    async def get_conversation_history(
        self, child_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get conversation history"""
        pass

    @abstractmethod
    async def get_conversation_analytics(
            self, child_id: str) -> Dict[str, Any]:
        """Get conversation analytics"""
        pass


class IFallbackHandler(ABC):
    """Fallback response handling interface"""

    @abstractmethod
    async def create_fallback_response(
        self,
        original_message: str,
        child_id: str,
        error_type: str,
        context: Optional[Dict] = None,
    ) -> AIResponse:
        """Create appropriate fallback response"""
        pass

    @abstractmethod
    async def create_safety_fallback(
        self, flagged_content: str, child_id: str, safety_issues: List[str]
    ) -> AIResponse:
        """Create safety-focused fallback"""
        pass

    @abstractmethod
    async def create_error_fallback(
        self, error_message: str, child_id: str, session_id: str
    ) -> AIResponse:
        """Create error fallback response"""
        pass


# Factory interface
class IAIServiceFactory(ABC):
    """AI Service factory interface"""

    @abstractmethod
    def create_service(
        self, provider: str, config: Dict[str, Any], **kwargs
    ) -> IAIService:
        """Create AI service instance"""
        pass

    @abstractmethod
    def get_available_providers(self) -> List[str]:
        """Get available providers"""
        pass

    @abstractmethod
    def register_provider(self, name: str, provider_class: type) -> None:
        """Register new provider"""
        pass
