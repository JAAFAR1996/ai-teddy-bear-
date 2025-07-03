"""
Unified AI Service - Application Layer
Coordinates all AI operations without duplication
"""

from typing import Protocol


class IAIService(Protocol):
    """AI Service Interface"""
    async def process_text(self, text: str) -> str: ...
    async def analyze_emotion(self, audio: bytes) -> dict: ...


class UnifiedAIService:
    """Single AI service replacing 6+ duplicate services"""
    
    def __init__(self, openai_adapter, emotion_analyzer):
        self.openai_adapter = openai_adapter
        self.emotion_analyzer = emotion_analyzer
        
    async def process_child_message(self, message: str, child_id: str) -> str:
        """Main AI processing workflow"""
        # 1. Safety check
        # 2. Emotion analysis  
        # 3. Response generation
        # 4. Content moderation
        return "Safe AI response"
        
    async def analyze_child_emotion(self, audio_data: bytes) -> dict:
        """Unified emotion analysis"""
        return await self.emotion_analyzer.analyze(audio_data)
