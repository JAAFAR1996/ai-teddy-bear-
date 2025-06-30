#!/usr/bin/env python3
"""
Accessibility DTOs
Generated from: accessibility_service.py
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AccessibilityProfileDTO:
    """DTO لملف الوصولية"""
    child_id: str
    special_needs: List[str]
    communication_level: str
    attention_span: int
    sensory_preferences: Dict[str, str]
    learning_adaptations: Dict[str, bool]
    behavioral_triggers: List[str]
    calming_strategies: List[str]
    support_level: str
    communication_aids: List[str]

@dataclass
class AdaptiveContentDTO:
    """DTO للمحتوى المتكيف"""
    content_id: str
    original_content: Dict
    adapted_content: Dict
    adaptation_type: str
    target_needs: List[str]
    effectiveness_score: float

@dataclass
class AccessibilityReportDTO:
    """DTO لتقرير الوصولية"""
    child_id: str
    assessment_date: str
    accessibility_score: float
    recommendations: List[str]
    progress_notes: List[str]
