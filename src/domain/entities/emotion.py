"""
🎭 Emotion Entity - Domain Layer
Core emotion domain entity
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from .base import Entity


class EmotionEntity(Entity):
    """Domain entity representing an emotion analysis"""
    
    def __init__(
        self,
        child_id: UUID,
        child_name: str,
        dominant_emotion: str,
        confidence: float,
        all_emotions: Dict[str, float],
        behavioral_indicators: List[str],
        transcription: str = "",
        response_text: str = "",
        session_context: Optional[Dict[str, Any]] = None,
        entity_id: Optional[UUID] = None
    ):
        super().__init__(str(entity_id) if entity_id else None)
        self.child_id = child_id
        self.child_name = child_name
        self.dominant_emotion = dominant_emotion
        self.confidence = confidence
        self.all_emotions = all_emotions or {}
        self.behavioral_indicators = behavioral_indicators or []
        self.transcription = transcription
        self.response_text = response_text
        self.session_context = session_context or {}
        self.analysis_timestamp = datetime.utcnow()
    
    def is_positive_emotion(self) -> bool:
        """Check if the dominant emotion is positive"""
        positive_emotions = ['joy', 'happiness', 'excitement', 'curiosity', 'playfulness']
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
            self.behavioral_indicators.append(indicator)
            self.update_timestamp()
    
    def update_context(self, new_context: Dict[str, Any]) -> None:
        """Update session context"""
        self.session_context.update(new_context)
        self.update_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'child_id': str(self.child_id),
            'child_name': self.child_name,
            'dominant_emotion': self.dominant_emotion,
            'confidence': self.confidence,
            'all_emotions': self.all_emotions,
            'behavioral_indicators': self.behavioral_indicators,
            'transcription': self.transcription,
            'response_text': self.response_text,
            'session_context': self.session_context,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionEntity':
        """Create instance from dictionary"""
        return cls(
            child_id=UUID(data['child_id']),
            child_name=data['child_name'],
            dominant_emotion=data['dominant_emotion'],
            confidence=data['confidence'],
            all_emotions=data.get('all_emotions', {}),
            behavioral_indicators=data.get('behavioral_indicators', []),
            transcription=data.get('transcription', ''),
            response_text=data.get('response_text', ''),
            session_context=data.get('session_context', {}),
            entity_id=UUID(data['id']) if data.get('id') else None
        ) 