#!/usr/bin/env python3
"""
📊 Moderation Result Processor
معالجة وتجميع نتائج الفحص

المسؤوليات:
- تجميع نتائج من مصادر متعددة
- تنسيق الاستجابة النهائية
- توليد البدائل الآمنة
- حساب الثقة والخطورة
"""

import logging
from typing import Any, Dict, List, Optional

from .moderation import ContentCategory, ModerationResult, ModerationSeverity
from .moderation_helpers import ModerationRequest, ModerationLookupTables


class ModerationResultProcessor:
    """📊 معالج نتائج الفحص"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def aggregate_results(self, results: List[ModerationResult]) -> ModerationResult:
        """📋 تجميع نتائج متعددة"""
        if not results:
            return self._create_safe_result("No results to aggregate")
        
        # تصفية النتائج الصالحة
        valid_results = [r for r in results if isinstance(r, ModerationResult)]
        if not valid_results:
            return self._create_safe_result("No valid results")
        
        # تجميع باستخدام دوال مبسطة
        safety_status = self._determine_overall_safety(valid_results)
        severity = self._determine_max_severity(valid_results)
        categories_and_scores = self._merge_categories_and_scores(valid_results)
        
        return ModerationResult(
            is_safe=safety_status,
            severity=severity,
            flagged_categories=categories_and_scores["categories"],
            confidence_scores=categories_and_scores["scores"],
            matched_rules=self._merge_rules(valid_results),
            context_notes=self._merge_notes(valid_results),
        )
    
    def format_response(self, result: ModerationResult, request: ModerationRequest) -> Dict[str, Any]:
        """📝 تنسيق الاستجابة النهائية"""
        allowed = result.is_safe and result.severity in [
            ModerationSeverity.SAFE, 
            ModerationSeverity.LOW
        ]
        
        response = {
            "allowed": allowed,
            "severity": result.severity.value,
            "categories": [cat.value for cat in result.flagged_categories],
            "confidence": self._calculate_confidence(result),
            "reason": self._get_rejection_reason(result) if not allowed else None,
            "alternative_response": self._get_alternative_response(result) if not allowed else None,
            "timestamp": result.timestamp.isoformat() if hasattr(result, 'timestamp') else None,
        }
        
        return response
    
    def _determine_overall_safety(self, results: List[ModerationResult]) -> bool:
        """🛡️ تحديد الأمان العام"""
        return all(result.is_safe for result in results)
    
    def _determine_max_severity(self, results: List[ModerationResult]) -> ModerationSeverity:
        """⚠️ تحديد أقصى خطورة"""
        max_severity = ModerationSeverity.SAFE
        for result in results:
            if result.severity.value > max_severity.value:
                max_severity = result.severity
        return max_severity
    
    def _merge_categories_and_scores(self, results: List[ModerationResult]) -> Dict[str, Any]:
        """🔗 دمج التصنيفات والنقاط"""
        all_categories = []
        all_scores = {}
        
        for result in results:
            all_categories.extend(result.flagged_categories)
            
            # دمج النقاط - أخذ أعلى نقاط لكل تصنيف
            for category, score in result.confidence_scores.items():
                all_scores[category] = max(all_scores.get(category, 0), score)
        
        return {
            "categories": list(set(all_categories)),
            "scores": all_scores
        }
    
    def _merge_rules(self, results: List[ModerationResult]) -> List[str]:
        """📋 دمج القواعد المطابقة"""
        all_rules = []
        for result in results:
            all_rules.extend(result.matched_rules)
        return list(set(all_rules))[:5]  # حد أقصى 5 قواعد
    
    def _merge_notes(self, results: List[ModerationResult]) -> List[str]:
        """📝 دمج الملاحظات"""
        all_notes = []
        for result in results:
            all_notes.extend(result.context_notes)
        return list(set(all_notes))
    
    def _calculate_confidence(self, result: ModerationResult) -> float:
        """🎯 حساب الثقة"""
        if hasattr(result, 'overall_score') and result.overall_score:
            return result.overall_score
        
        if result.confidence_scores:
            return max(result.confidence_scores.values())
        
        return 1.0 if result.is_safe else 0.0
    
    def _get_rejection_reason(self, result: ModerationResult) -> str:
        """📝 الحصول على سبب الرفض"""
        try:
            return ModerationLookupTables.get_rejection_reason(result.flagged_categories)
        except Exception as e:
            self.logger.error(f"Error getting rejection reason: {e}")
            return "المحتوى قد يحتوي على مواد غير مناسبة"
    
    def _get_alternative_response(self, result: ModerationResult) -> str:
        """💬 الحصول على رد بديل"""
        try:
            return ModerationLookupTables.get_alternative_response(result.flagged_categories)
        except Exception as e:
            self.logger.error(f"Error getting alternative response: {e}")
            return "دعنا نتحدث عن شيء آخر! ✨"
    
    def _create_safe_result(self, note: str) -> ModerationResult:
        """✅ إنشاء نتيجة آمنة"""
        return ModerationResult(
            is_safe=True,
            severity=ModerationSeverity.SAFE,
            flagged_categories=[],
            confidence_scores={},
            matched_rules=[],
            context_notes=[note]
        )
    
    def create_unsafe_response(self, reason: str, categories: List[ContentCategory]) -> Dict[str, Any]:
        """❌ إنشاء رد غير آمن"""
        return {
            "allowed": False,
            "severity": ModerationSeverity.HIGH.value,
            "categories": [cat.value for cat in categories],
            "confidence": 0.9,
            "reason": reason,
            "alternative_response": ModerationLookupTables.get_alternative_response(categories),
        }
    
    def create_safe_response(self, reason: str) -> Dict[str, Any]:
        """✅ إنشاء رد آمن"""
        return {
            "allowed": True,
            "severity": ModerationSeverity.SAFE.value,
            "categories": [],
            "confidence": 1.0,
            "reason": reason,
            "alternative_response": None,
        }


def create_result_processor() -> ModerationResultProcessor:
    """🏭 Factory function"""
    return ModerationResultProcessor() 