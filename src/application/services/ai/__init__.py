"""
AI Service Module
Split into smaller, focused components for better maintainability
"""

from .ai_service import AIService
from .emotion_analyzer import EmotionAnalyzer, EmotionCategory, EmotionAnalysis
from .personality_engine import PersonalityEngine
from .response_generator import ResponseGenerator, ResponseMode
from .conversation_manager import ConversationManager, ConversationContext
from .educational_content import EducationalContentProvider
from .models import AIResponse

__all__ = [
    'AIService',
    'EmotionAnalyzer',
    'EmotionCategory',
    'EmotionAnalysis',
    'PersonalityEngine',
    'ResponseGenerator',
    'ResponseMode',
    'ConversationManager',
    'ConversationContext',
    'EducationalContentProvider',
    'AIResponse'
] 