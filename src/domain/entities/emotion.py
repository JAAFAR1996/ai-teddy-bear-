"""
🎭 Emotion Entity - Domain Layer
Core emotion domain entity
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from .base import Entity


class EmotionData(BaseModel):
    """Data container for emotion analysis"""
    child_id: UUID
    child_name: str
    dominant_emotion: str
    confidence: float
    all_emotions: Dict[str, float] = Field(default_factory=dict)
    behavioral_indicators: List[str] = Field(default_factory=list)
    transcription: str = ""
    response_text: str = ""
    session_context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EmotionEntity(Entity):
    """Domain entity representing an emotion analysis"""

    def __init__(
        self,
        data: EmotionData,
        entity_id: Optional[UUID] = None
    ):
        super().__init__(str(entity_id) if entity_id else None)
        self.data = data
        self.analysis_timestamp = datetime.utcnow()

    @property
    def child_id(self) -> UUID:
        return self.data.child_id

    @property
    def dominant_emotion(self) -> str:
        return self.data.dominant_emotion

    @property
    def confidence(self) -> float:
        return self.data.confidence

    @property
    def all_emotions(self) -> Dict[str, float]:
        return self.data.all_emotions

    @property
    def behavioral_indicators(self) -> List[str]:
        return self.data.behavioral_indicators

    def is_positive_emotion(self) -> bool:
        """Check if the dominant emotion is positive"""
        positive_emotions = ['joy', 'happiness',
                             'excitement', 'curiosity', 'playfulness']
        return self.dominant_emotion.lower() in positive_emotions

    def get_emotional_intensity(self) -> float:
        """Calculate overall emotional intensity"""
        if not self.all_emotions:
            return self.confidence

        # Calculate weighted average of all emotions
        total_intensity = sum(self.all_emotions.values())
        return min(total_intensity, 1.0)

    def has_concerning_pattern(self) -> bool:
        """Check if emotion shows concerning patterns"""
        concerning_emotions = ['sadness', 'anger', 'fear', 'anxiety']

        # High confidence in negative emotion
        if (self.dominant_emotion.lower() in concerning_emotions and
                self.confidence > 0.7):
            return True

        # Multiple negative emotions with significant scores
        negative_count = sum(1 for emotion, score in self.all_emotions.items()
                             if emotion.lower() in concerning_emotions and score > 0.3)

        return negative_count >= 2

    def add_behavioral_indicator(self, indicator: str) -> None:
        """Add a behavioral indicator"""
        if indicator and indicator not in self.behavioral_indicators:
            self.data.behavioral_indicators.append(indicator)
            self.update_timestamp()

    def update_context(self, new_context: Dict[str, Any]) -> None:
        """Update session context"""
        self.data.session_context.update(new_context)
        self.update_timestamp()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        entity_dict = {
            'id': self.id,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        entity_dict.update(self.data.dict())
        entity_dict['child_id'] = str(entity_dict['child_id'])
        return entity_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionEntity':
        """Create instance from dictionary"""
        emotion_data = EmotionData(
            child_id=UUID(data['child_id']),
            child_name=data['child_name'],
            dominant_emotion=data['dominant_emotion'],
            confidence=data['confidence'],
            all_emotions=data.get('all_emotions', {}),
            behavioral_indicators=data.get('behavioral_indicators', []),
            transcription=data.get('transcription', ''),
            response_text=data.get('response_text', ''),
            session_context=data.get('session_context', {}),
        )
        return cls(
            data=emotion_data,
            entity_id=UUID(data['id']) if data.get('id') else None
        )
