#!/usr/bin/env python3
"""
Accessibility Domain - Value Objects
Generated from: accessibility_service.py
"""

from dataclasses import dataclass
from enum import Enum


class SpecialNeedType(Enum):
    """أنواع الاحتياجات الخاصة"""

    AUTISM = "autism"
    ADHD = "adhd"
    SPEECH_DELAY = "speech_delay"
    HEARING_IMPAIRED = "hearing_impaired"
    VISUAL_IMPAIRED = "visual_impaired"
    LEARNING_DISABILITY = "learning_disability"
    DYSLEXIA = "dyslexia"
    DOWN_SYNDROME = "down_syndrome"
    CEREBRAL_PALSY = "cerebral_palsy"
    SENSORY_PROCESSING = "sensory_processing"


@dataclass
class SensoryPreferences:
    """التفضيلات الحسية"""

    sound_level: str = "normal"
    visual_stimulation: str = "normal"
    interaction_pace: str = "normal"

    def __post_init__(self):
        valid_sound_levels = ["quiet", "normal", "loud"]
        valid_visual = ["minimal", "normal", "high"]
        valid_pace = ["slow", "normal", "fast"]

        if self.sound_level not in valid_sound_levels:
            self.sound_level = "normal"
        if self.visual_stimulation not in valid_visual:
            self.visual_stimulation = "normal"
        if self.interaction_pace not in valid_pace:
            self.interaction_pace = "normal"


@dataclass
class LearningAdaptations:
    """تكييفات التعلم"""

    repeat_instructions: bool = False
    visual_cues: bool = False
    simplified_language: bool = False
    extended_response_time: bool = False
    structured_routine: bool = False
