from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any


class StoryLength(Enum):
    SHORT = "قصيرة"
    MEDIUM = "متوسطة"
    LONG = "طويلة"


class StoryTheme(Enum):
    ADVENTURE = "مغامرة"
    FRIENDSHIP = "صداقة"
    LEARNING = "تعليمية"
    BEDTIME = "نوم"
    FAMILY = "عائلة"
    ANIMALS = "حيوانات"
    SPACE = "فضاء"
    FANTASY = "خيال"
    HEROIC = "بطولة"
    PROBLEM_SOLVING = "حل_مشاكل"


class AgeGroup(Enum):
    TODDLER = "3-4"
    PRESCHOOL = "5-6"
    EARLY_SCHOOL = "7-9"
    MIDDLE_SCHOOL = "10-12"
    TEEN = "13-15"


@dataclass
class StoryContext:
    child_name: str
    age: int
    friends: List[str]
    family_members: List[str]
    interests: List[str]
    recent_experiences: List[str]
    emotional_state: str
    learning_goals: List[str]
    cultural_background: str
    preferred_characters: List[str]


@dataclass
class GeneratedStory:
    id: str
    title: str
    content: str
    theme: StoryTheme
    length: StoryLength
    age_group: AgeGroup
    characters: List[str]
    moral_lesson: str
    educational_elements: List[str]
    emotional_tags: List[str]
    personalization_score: float
    generated_at: datetime
    audio_cues: List[str]
