"""
🎭 Emotion Repository Interface - Domain Layer
Domain interface for emotion data operations
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from ..entities.emotion import EmotionEntity
from ..value_objects.emotion_analysis import EmotionAnalysis


class IEmotionRepository(ABC):
    """Repository interface for emotion data operations"""

    @abstractmethod
    async def save_emotion_analysis(self, emotion: EmotionEntity) -> str:
        """Save emotion analysis result"""
        pass

    @abstractmethod
    async def get_emotion_history(
        self, child_id: UUID, days: int = 7
    ) -> List[EmotionEntity]:
        """Get emotion history for a child"""
        pass

    @abstractmethod
    async def get_child_emotion_stats(
            self, child_id: UUID) -> Optional[Dict[str, Any]]:
        """Get emotion statistics for a child"""
        pass

    @abstractmethod
    async def save_parent_feedback(
            self,
            child_id: UUID,
            interaction_id: str,
            feedback: str,
            accuracy_rating: int) -> None:
        """Save parent feedback"""
        pass

    @abstractmethod
    async def update_child_stats(
            self,
            child_id: UUID,
            emotion: EmotionEntity) -> None:
        """Update child emotion statistics"""
        pass
