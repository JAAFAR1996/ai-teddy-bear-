#!/usr/bin/env python3
"""
🏗️ Accessibility Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

# Original imports
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

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
    