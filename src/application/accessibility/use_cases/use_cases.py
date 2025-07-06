#!/usr/bin/env python3
"""
🏗️ Accessibility Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

# Original imports
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# This class is a placeholder. You should define it based on your actual data model.


@dataclass
class AccessibilityProfile:
    sensory_preferences: Dict[str, str]
    special_needs: List[str]


def _get_sensory_guidelines(self, profile: AccessibilityProfile) -> List[str]:
    """إرشادات حسية"""
    guidelines = []

    if profile.sensory_preferences.get("sound_level") == "quiet":
        guidelines.append("خفف الأصوات وتجنب الضوضاء العالية")

    if profile.sensory_preferences.get("visual_stimulation") == "minimal":
        guidelines.append("قلل من المثيرات البصرية والألوان الساطعة")

    if "sensory_processing" in profile.special_needs:
        guidelines.extend([
            "راقب علامات الحمل الحسي الزائد",
            "وفر بدائل حسية مهدئة",
            "احترم الحاجة للفواصل الحسية"
        ])

    return guidelines
