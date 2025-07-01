#!/usr/bin/env python3
"""
Accessibility Application Service
Generated from: accessibility_service.py
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from .dto.accessibility_dto import AccessibilityProfileDTO
from .use_cases.adapt_content_use_case import AdaptContentUseCase
from .use_cases.create_profile_use_case import CreateAccessibilityProfileUseCase

logger = logging.getLogger(__name__)


class AccessibilityApplicationService:
    """خدمة تطبيق الوصولية"""

    def __init__(self, repository, adaptation_service):
        self.repository = repository
        self.adaptation_service = adaptation_service
        self.create_profile_use_case = CreateAccessibilityProfileUseCase(repository)
        self.adapt_content_use_case = AdaptContentUseCase(repository, adaptation_service)

    def create_accessibility_profile(self, child_id: str, special_needs: List[str]) -> AccessibilityProfileDTO:
        """إنشاء ملف وصولية جديد"""
        try:
            profile = self.create_profile_use_case.execute(child_id, special_needs)
            return self._profile_to_dto(profile)
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف الوصولية: {e}")
            raise

    def adapt_content_for_child(self, child_id: str, content: Dict) -> Dict:
        """تكييف المحتوى للطفل"""
        try:
            return self.adapt_content_use_case.execute(child_id, content)
        except Exception as e:
            logger.error(f"خطأ في تكييف المحتوى: {e}")
            return content

    def get_accessibility_profile(self, child_id: str) -> Optional[AccessibilityProfileDTO]:
        """الحصول على ملف الوصولية"""
        try:
            profile = self.repository.get_by_child_id(child_id)
            return self._profile_to_dto(profile) if profile else None
        except Exception as e:
            logger.error(f"خطأ في الحصول على ملف الوصولية: {e}")
            return None

    def _profile_to_dto(self, profile) -> AccessibilityProfileDTO:
        """تحويل Profile إلى DTO"""
        return AccessibilityProfileDTO(
            child_id=profile.child_id,
            special_needs=profile.special_needs,
            communication_level=profile.communication_level,
            attention_span=profile.attention_span,
            sensory_preferences=profile.sensory_preferences.__dict__,
            learning_adaptations=profile.learning_adaptations.__dict__,
            behavioral_triggers=profile.behavioral_triggers,
            calming_strategies=profile.calming_strategies,
            support_level=profile.support_level,
            communication_aids=profile.communication_aids,
        )
