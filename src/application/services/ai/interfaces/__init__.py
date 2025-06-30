"""
🤖 AI Interfaces Module
Abstract interfaces and contracts for AI services
"""

from .ai_service_interface import (
    IAIService,
    IEmotionAnalyzer,
    IResponseGenerator,
    ICacheService,
    IConversationManager
)

__all__ = [
    "IAIService",
    "IEmotionAnalyzer",
    "IResponseGenerator",
    "ICacheService",
    "IConversationManager"
] 