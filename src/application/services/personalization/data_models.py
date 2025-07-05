#!/usr/bin/env python3
"""
📊 Data Models for Personalization
نماذج البيانات المستخدمة في خدمات التخصيص
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ChildPersonality:
    """شخصية الطفل"""

    child_id: str
    openness: float = 0.5  # الانفتاح على التجارب الجديدة (0-1)
    conscientiousness: float = 0.5  # الضميرية/المثابرة (0-1)
    extraversion: float = 0.5  # الانبساطية (0-1)
    agreeableness: float = 0.5  # الوداعة/التعاون (0-1)
    neuroticism: float = 0.5  # العصابية/القلق (0-1)
    learning_style: str = "visual"  # visual, auditory, kinesthetic
    attention_span: int = 15  # بالدقائق
    preferred_difficulty: str = "medium"  # easy, medium, hard
    curiosity_level: float = 0.5  # مستوى الفضول (0-1)
    creativity_level: float = 0.5  # مستوى الإبداع (0-1)
    last_updated: str = ""


@dataclass
class InteractionPattern:
    """أنماط التفاعل"""

    child_id: str
    preferred_activities: List[str] = None
    favorite_topics: List[str] = None
    engagement_times: List[str] = None  # أوقات التفاعل النشط
    response_patterns: Dict[str, int] = None  # أنماط الردود
    mood_triggers: Dict[str, List[str]] = None  # محفزات المزاج
    learning_preferences: Dict[str, float] = None  # تفضيلات التعلم
    attention_patterns: Dict[str, int] = None  # أنماط الانتباه
    social_interaction_style: str = "moderate"  # shy, moderate, outgoing

    def __post_init__(self):
        if self.preferred_activities is None:
            self.preferred_activities = []
        if self.favorite_topics is None:
            self.favorite_topics = []
        if self.engagement_times is None:
            self.engagement_times = []
        if self.response_patterns is None:
            self.response_patterns = {}
        if self.mood_triggers is None:
            self.mood_triggers = {"positive": [], "negative": []}
        if self.learning_preferences is None:
            self.learning_preferences = {
                "storytelling": 0.5,
                "games": 0.5,
                "songs": 0.5,
                "questions": 0.5,
            }
        if self.attention_patterns is None:
            self.attention_patterns = {"morning": 0, "afternoon": 0, "evening": 0}


@dataclass
class AdaptiveContent:
    """محتوى متكيف"""

    content_type: str  # story, game, conversation, lesson
    difficulty_level: str
    topic: str
    duration: int  # بالدقائق
    engagement_score: float  # مدى الانخراط (0-1)
    success_rate: float  # معدل النجاح (0-1)
    child_feedback: str  # positive, neutral, negative
    usage_count: int = 0
    last_used: str = "" 