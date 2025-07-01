#!/usr/bin/env python3
"""
Accessibility Domain - Entities
Generated from: accessibility_service.py
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..value_objects.special_need_type import LearningAdaptations, SensoryPreferences, SpecialNeedType


@dataclass
class AccessibilityProfile:
    """ملف الوصولية للطفل - كيان رئيسي"""

    child_id: str
    special_needs: List[str] = field(default_factory=list)
    communication_level: str = "verbal"
    attention_span: int = 5
    sensory_preferences: Optional[SensoryPreferences] = None
    learning_adaptations: Optional[LearningAdaptations] = None
    behavioral_triggers: List[str] = field(default_factory=list)
    calming_strategies: List[str] = field(default_factory=list)
    support_level: str = "minimal"
    communication_aids: List[str] = field(default_factory=list)
    created_at: str = ""
    last_updated: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()
        if self.sensory_preferences is None:
            self.sensory_preferences = SensoryPreferences()
        if self.learning_adaptations is None:
            self.learning_adaptations = LearningAdaptations()

    def update_last_modified(self):
        """تحديث تاريخ آخر تعديل"""
        self.last_updated = datetime.now().isoformat()

    def add_special_need(self, need_type: str):
        """إضافة احتياج خاص جديد"""
        if need_type not in self.special_needs:
            self.special_needs.append(need_type)
            self.update_last_modified()

    def remove_special_need(self, need_type: str):
        """إزالة احتياج خاص"""
        if need_type in self.special_needs:
            self.special_needs.remove(need_type)
            self.update_last_modified()


@dataclass
class AdaptiveContent:
    """محتوى متكيف للاحتياجات الخاصة"""

    content_id: str
    original_content: Dict
    adapted_content: Dict
    adaptation_type: str
    target_needs: List[str]
    effectiveness_score: float = 0.0
    usage_count: int = 0
    created_at: str = ""

    def __post_init__(self):
        if not self.content_id:
            self.content_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def increment_usage(self):
        """زيادة عداد الاستخدام"""
        self.usage_count += 1

    def update_effectiveness(self, score: float):
        """تحديث نتيجة الفعالية"""
        if 0.0 <= score <= 1.0:
            self.effectiveness_score = score
