"""
AI Service Models
Shared data models for AI components
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ResponseMode(Enum):
    """AI response modes"""

    EDUCATIONAL = "educational"
    PLAYFUL = "playful"
    STORYTELLING = "storytelling"
    SUPPORTIVE = "supportive"
    CREATIVE = "creative"
    CONVERSATIONAL = "conversational"


class EmotionalTone(Enum):
    """Voice emotional tones"""

    CHEERFUL = "cheerful"
    CALM = "calm"
    EXCITED = "excited"
    WARM = "warm"
    GENTLE = "gentle"
    ENCOURAGING = "encouraging"
    PLAYFUL = "playful"
    SOOTHING = "soothing"


@dataclass
class AIResponse:
    """AI response with full metadata"""

    content: str
    emotion: "EmotionAnalysis"
    confidence: float = 0.0
    response_mode: ResponseMode = ResponseMode.CONVERSATIONAL
    suggested_voice_tone: EmotionalTone = EmotionalTone.CALM
    follow_up_questions: List[str] = field(default_factory=list)
    educational_content: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    moderation_result: Optional[Dict] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    child_id: Optional[str] = None
