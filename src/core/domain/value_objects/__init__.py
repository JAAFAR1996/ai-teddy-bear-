"""
💎 Domain Value Objects - AI Teddy Bear Core
===========================================

Value objects are immutable objects that represent concepts through their attributes.
They have no identity, only value equality, and encapsulate business logic.

Following DDD principles:
- Immutable by design
- Equality based on value, not identity
- Self-validating
- Expressive business concepts
"""

from .identities import ChildId, ParentId, ConversationId, AudioSessionId
from .emotion import EmotionScore, EmotionType, EmotionIntensity
from .learning import LearningLevel, LearningGoal, ProgressMetric
from .preferences import InteractionPreferences, VoicePreferences, ContentPreferences
from .safety import SafetySettings, ContentFilter, TimeRestriction
from .audio import AudioMetadata, AudioQuality, SpeechCharacteristics
from .interaction import InteractionContext, ResponseTone, DifficultyLevel
from .voice_profile import VoiceProfile, VoiceGender, EmotionBaseline
from .safety_settings import (
    SafetySettings, ContentFilterLevel, TimeRestriction, TimeRestrictionType
)

__all__ = [
    # Identity Value Objects
    'ChildId',
    'ParentId', 
    'ConversationId',
    'AudioSessionId',
    
    # Emotion Value Objects
    'EmotionScore',
    'EmotionType',
    'EmotionIntensity',
    
    # Learning Value Objects
    'LearningLevel',
    'LearningGoal',
    'ProgressMetric',
    
    # Preference Value Objects
    'InteractionPreferences',
    'VoicePreferences',
    'ContentPreferences',
    
    # Safety Value Objects
    'SafetySettings',
    'ContentFilter',
    'TimeRestriction',
    
    # Audio Value Objects
    'AudioMetadata',
    'AudioQuality',
    'SpeechCharacteristics',
    
    # Interaction Value Objects
    'InteractionContext',
    'ResponseTone',
    'DifficultyLevel',

    # Voice Profile Value Objects
    'VoiceProfile',
    'VoiceGender',
    'EmotionBaseline',

    # Safety Settings Value Objects
    'SafetySettings',
    'ContentFilterLevel',
    'TimeRestriction',
    'TimeRestrictionType'
] 