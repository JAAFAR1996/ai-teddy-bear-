"""
🧠 Domain Entities - AI Teddy Bear Core
======================================

Domain entities represent the core business objects with identity and lifecycle.
These are the heart of the business logic following DDD principles.

Entities included:
- Child: The main aggregate root representing a child using the system
- Conversation: Represents a conversation session between child and AI
- AudioSession: Represents an audio interaction session
- EmotionState: Tracks emotional state throughout interactions
- LearningProfile: Child's learning preferences and progress
"""

from .child import Child
from .conversation import Conversation, Message, ConversationStatus, MessageType, EmotionDetection
from .audio_session import AudioSession, AudioSessionId
from .emotion_state import EmotionState
from .learning_profile import LearningProfile

__all__ = [
    'Child',
    'Conversation',
    'Message',
    'ConversationStatus',
    'MessageType',
    'EmotionDetection',
    'AudioSession',
    'AudioSessionId',
    'EmotionState',
    'LearningProfile'
] 