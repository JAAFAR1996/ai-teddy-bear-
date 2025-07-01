"""AI Service Interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class AIRequest:
    message: str
    child_id: str = None
    context: Dict[str, Any] = None

@dataclass
class AIResponse:
    text: str
    confidence: float
    safety_score: float

@dataclass
class EmotionResult:
    emotion: str
    confidence: float
    valence: float = 0.0
    arousal: float = 0.0

class IAIService(ABC):
    @abstractmethod
    async def generate_response(self, request: AIRequest) -> AIResponse:
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        pass

class IEmotionAnalyzer(ABC):
    @abstractmethod
    async def analyze_emotion(self, text: str) -> EmotionResult:
        pass
    
    @abstractmethod
    def get_emotion_history(self, child_id: str) -> List[EmotionResult]:
        pass

class BaseAIService(IAIService):
    async def generate_response(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            text="مرحبا! كيف يمكنني مساعدتك؟",
            confidence=0.9,
            safety_score=0.95
        )
    
    def get_available_models(self) -> List[str]:
        return ["gpt-3.5-turbo", "gpt-4"]

class IResponseGenerator(ABC):
    @abstractmethod
    async def generate_text_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        pass
    
    @abstractmethod
    async def generate_audio_response(self, text: str, voice_config: Dict[str, Any] = None) -> bytes:
        pass

class BaseResponseGenerator(IResponseGenerator):
    async def generate_text_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        return "مرحبا! كيف يمكنني مساعدتك؟"
    
    async def generate_audio_response(self, text: str, voice_config: Dict[str, Any] = None) -> bytes:
        return b"mock_audio_response"

class ICacheService(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

class BaseCacheService(ICacheService):
    def __init__(self):
        self.cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        self.cache[key] = value
        return True
    
    async def delete(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            return True
        return False

class BaseEmotionAnalyzer(IEmotionAnalyzer):
    async def analyze_emotion(self, text: str) -> EmotionResult:
        # Simple mock emotion analysis
        if "سعيد" in text or "happy" in text.lower():
            return EmotionResult(emotion="happy", confidence=0.8, valence=0.7)
        elif "حزين" in text or "sad" in text.lower():
            return EmotionResult(emotion="sad", confidence=0.8, valence=-0.6)
        else:
            return EmotionResult(emotion="neutral", confidence=0.7, valence=0.0)
    
    def get_emotion_history(self, child_id: str) -> List[EmotionResult]:
        return []
class IConversationManager(ABC):
    @abstractmethod
    async def start_conversation(self, child_id: str) -> str:
        pass
    
    @abstractmethod
    async def end_conversation(self, session_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_conversation_history(self, child_id: str) -> List[Dict[str, Any]]:
        pass

class BaseConversationManager(IConversationManager):
    def __init__(self):
        self.conversations = {}
    
    async def start_conversation(self, child_id: str) -> str:
        import uuid
        session_id = str(uuid.uuid4())
        self.conversations[session_id] = {
            "child_id": child_id,
            "started_at": "2024-01-01T00:00:00",
            "messages": []
        }
        return session_id
    
    async def end_conversation(self, session_id: str) -> bool:
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False
    
    async def get_conversation_history(self, child_id: str) -> List[Dict[str, Any]]:
        return []

