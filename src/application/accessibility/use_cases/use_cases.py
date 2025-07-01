#!/usr/bin/env python3
"""
🏗️ Accessibility Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

# Original imports
import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

    def _get_sensory_guidelines(self, profile: AccessibilityProfile) -> List[str]:
        """إرشادات حسية"""
        guidelines = []
        
        if profile.sensory_preferences["sound_level"] == "quiet":
            guidelines.append("خفف الأصوات وتجنب الضوضاء العالية")
        
        if profile.sensory_preferences["visual_stimulation"] == "minimal":
            guidelines.append("قلل من المثيرات البصرية والألوان الساطعة")
        
        if "sensory_processing" in profile.special_needs:
            guidelines.extend([
                "راقب علامات الحمل الحسي الزائد",
                "وفر بدائل حسية مهدئة",
                "احترم الحاجة للفواصل الحسية"
            ])
        
        return guidelines
    