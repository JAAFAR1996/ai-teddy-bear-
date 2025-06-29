"""
⚡ Domain Events - AI Teddy Bear Core
===================================

Domain events represent something significant that happened in the domain.
They enable loose coupling between bounded contexts and support
event-driven architecture patterns.

Following DDD principles:
- Named in past tense (what happened)
- Immutable once created
- Contain minimal but sufficient data
- Published after successful state changes
"""

from .child_events import (
    ChildRegistered,
    ChildProfileUpdated,
    ChildDeactivated,
    ChildReactivated,
    SafetyViolationDetected,
    SafetySettingsUpdated,
    VoiceProfileUpdated,
    DevelopmentMilestoneAchieved,
    UsageLimitReached,
    EmotionalStateTracked
)

from .conversation_events import (
    ConversationStarted,
    ConversationEnded,
    ConversationPaused,
    ConversationResumed,
    ConversationEscalated,
    MessageReceived,
    ResponseGenerated,
    EmotionDetected,
    SafetyViolationInConversation
)

__all__ = [
    # Child Events
    'ChildRegistered',
    'ChildProfileUpdated',
    'ChildDeactivated',
    'ChildReactivated',
    'SafetyViolationDetected',
    'SafetySettingsUpdated',
    'VoiceProfileUpdated',
    'DevelopmentMilestoneAchieved',
    'UsageLimitReached',
    'EmotionalStateTracked',
    
    # Conversation Events
    'ConversationStarted',
    'ConversationEnded',
    'ConversationPaused',
    'ConversationResumed',
    'ConversationEscalated',
    'MessageReceived',
    'ResponseGenerated',
    'EmotionDetected',
    'SafetyViolationInConversation'
] 