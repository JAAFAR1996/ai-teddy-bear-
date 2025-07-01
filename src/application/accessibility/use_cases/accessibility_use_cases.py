#!/usr/bin/env python3
"""
Accessibility Use Cases
Generated from: accessibility_service.py
"""

import logging
from typing import Dict, List

from ...domain.accessibility.entities.accessibility_profile import (
    AccessibilityProfile)

logger = logging.getLogger(__name__)


class CreateAccessibilityProfileUseCase:
    """حالة استخدام: إنشاء ملف وصولية"""

    def __init__(self, repository):
        self.repository = repository

    def execute(
        self,
        child_id: str,
        special_needs: List[str],
        communication_level: str = "verbal",
    ) -> AccessibilityProfile:
        """تنفيذ إنشاء ملف الوصولية"""
        try:
            # التحقق من صحة البيانات
            if not child_id:
                raise ValueError("معرف الطفل مطلوب")

            # التحقق من عدم وجود ملف سابق
            existing_profile = self.repository.get_by_child_id(child_id)
            if existing_profile:
                raise ValueError(f"ملف وصولية موجود بالفعل للطفل {child_id}")

            # إنشاء ملف الوصولية
            profile = AccessibilityProfile(
                child_id=child_id,
                special_needs=special_needs,
                communication_level=communication_level,
            )

            # حفظ في قاعدة البيانات
            saved_profile = self.repository.save(profile)

            logger.info(f"تم إنشاء ملف وصولية للطفل {child_id}")
            return saved_profile

        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف الوصولية: {e}")
            raise


class AdaptContentUseCase:
    """حالة استخدام: تكييف المحتوى"""

    def __init__(self, repository, adaptation_service):
        self.repository = repository
        self.adaptation_service = adaptation_service

    def execute(self, child_id: str, original_content: Dict) -> Dict:
        """تنفيذ تكييف المحتوى"""
        try:
            # الحصول على ملف الوصولية
            profile = self.repository.get_by_child_id(child_id)
            if not profile:
                logger.warning(f"لا يوجد ملف وصولية للطفل {child_id}")
                return original_content

            # تطبيق التكييفات
            adapted_content = self.adaptation_service.adapt_content(
                profile, original_content
            )

            logger.info(f"تم تكييف المحتوى للطفل {child_id}")
            return adapted_content

        except Exception as e:
            logger.error(f"خطأ في تكييف المحتوى: {e}")
            return original_content
