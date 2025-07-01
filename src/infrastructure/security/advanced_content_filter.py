from typing import Any, Dict, List, Optional

"""
🛡️ Advanced Content Filter - 2025 Edition
نظام فلترة محتوى متطور مع أمان شامل متعدد الطبقات

Lead Architect: جعفر أديب (Jaafar Adeeb)
Senior Backend Developer & Professor
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog
from cachetools import TTLCache

logger = structlog.get_logger(__name__)


class RiskLevel(Enum):
    """مستويات الخطر"""

    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"


class ContentCategory(Enum):
    """فئات المحتوى"""

    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    PERSONAL = "personal"
    INAPPROPRIATE = "inappropriate"
    HARMFUL = "harmful"


@dataclass
class SafetyViolation:
    """انتهاك أمني"""

    violation_type: str
    severity: RiskLevel
    description: str
    content_excerpt: str
    timestamp: float = field(default_factory=time.time)
    requires_parent_notification: bool = False


@dataclass
class ContentAnalysisResult:
    """نتيجة تحليل المحتوى"""

    is_safe: bool
    risk_level: RiskLevel
    confidence_score: float
    content_category: ContentCategory
    violations: List[SafetyViolation]
    modifications: List[str]
    safe_alternative: Optional[str]
    safety_recommendations: List[str]
    parent_notification_required: bool
    processing_time_ms: float


class ToxicityDetector:
    """كاشف السموم والمحتوى الضار"""

    def __init__(self):
        self.toxic_patterns = self._load_toxic_patterns()
        self.severity_weights = {"violence": 0.9, "hate_speech": 0.8, "sexual": 1.0, "drugs": 0.7, "profanity": 0.5}

    def _load_toxic_patterns(self) -> Dict[str, List[str]]:
        """تحميل أنماط المحتوى الضار"""
        return {
            "violence": ["عنف", "ضرب", "قتل", "إيذاء", "عدوان"],
            "hate_speech": ["كراهية", "تمييز", "عنصرية", "طائفية"],
            "sexual": ["جنس", "عري", "إثارة"],
            "drugs": ["مخدرات", "سجائر", "كحول", "مسكرات"],
            "profanity": ["سب", "شتم", "لعن", "كلام سيء"],
            "personal_info": ["رقم هاتف", "عنوان", "اسم عائلة", "مدرسة"],
        }

    async def analyze_toxicity(self, content: str, child_age: int) -> Dict[str, Any]:
        """تحليل السمية في المحتوى"""

        content_lower = content.lower()
        detected_categories = {}
        total_score = 0.0
        violations = []

        for category, patterns in self.toxic_patterns.items():
            category_score = 0.0
            detected_patterns = []

            for pattern in patterns:
                if pattern in content_lower:
                    detected_patterns.append(pattern)
                    age_multiplier = self._get_age_sensitivity_multiplier(child_age, category)
                    category_score += self.severity_weights.get(category, 0.5) * age_multiplier

            if detected_patterns:
                detected_categories[category] = {"score": min(1.0, category_score), "patterns": detected_patterns}

                violation = SafetyViolation(
                    violation_type=category,
                    severity=self._calculate_severity(category_score),
                    description=f"تم اكتشاف محتوى {category}",
                    content_excerpt=content[:100],
                    requires_parent_notification=category_score > 0.7,
                )
                violations.append(violation)

        if detected_categories:
            total_score = max(cat["score"] for cat in detected_categories.values())

        return {
            "toxicity_score": total_score,
            "detected_categories": detected_categories,
            "violations": violations,
            "is_toxic": total_score > 0.3,
        }

    def _get_age_sensitivity_multiplier(self, age: int, category: str) -> float:
        """حساب مضاعف الحساسية حسب العمر"""

        base_multipliers = {
            "violence": {(3, 6): 2.0, (7, 10): 1.5, (11, 12): 1.0},
            "hate_speech": {(3, 6): 2.0, (7, 10): 1.8, (11, 12): 1.2},
            "sexual": {(3, 6): 3.0, (7, 10): 2.5, (11, 12): 2.0},
            "drugs": {(3, 6): 2.0, (7, 10): 1.5, (11, 12): 1.0},
            "profanity": {(3, 6): 1.5, (7, 10): 1.2, (11, 12): 1.0},
        }

        category_multipliers = base_multipliers.get(category, {})

        for age_range, multiplier in category_multipliers.items():
            if age_range[0] <= age <= age_range[1]:
                return multiplier

        return 1.0

    def _calculate_severity(self, score: float) -> RiskLevel:
        """حساب مستوى الخطر"""

        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH_RISK
        elif score >= 0.4:
            return RiskLevel.MEDIUM_RISK
        elif score >= 0.2:
            return RiskLevel.LOW_RISK
        else:
            return RiskLevel.SAFE


class AgeAppropriatenessChecker:
    """فاحص ملاءمة العمر"""

    async def check_age_appropriateness(self, content: str, child_age: int) -> Dict[str, Any]:
        """فحص ملاءمة المحتوى للعمر"""

        vocabulary_score = self._analyze_vocabulary_complexity(content, child_age)
        concept_score = self._analyze_concept_appropriateness(content, child_age)
        emotional_score = self._analyze_emotional_complexity(content, child_age)

        overall_score = (vocabulary_score + concept_score + emotional_score) / 3

        return {
            "is_age_appropriate": overall_score > 0.6,
            "appropriateness_score": overall_score,
            "vocabulary_score": vocabulary_score,
            "concept_score": concept_score,
            "emotional_score": emotional_score,
            "recommendations": self._generate_age_recommendations(
                vocabulary_score, concept_score, emotional_score, child_age
            ),
        }

    def _analyze_vocabulary_complexity(self, content: str, age: int) -> float:
        """تحليل تعقيد المفردات"""

        words = content.split()
        if not words:
            return 1.0

        avg_word_length = sum(len(word) for word in words) / len(words)

        age_limits = {(3, 5): 4, (6, 8): 6, (9, 12): 8}

        appropriate_limit = 6
        for age_range, limit in age_limits.items():
            if age_range[0] <= age <= age_range[1]:
                appropriate_limit = limit
                break

        if avg_word_length <= appropriate_limit:
            return 1.0
        elif avg_word_length <= appropriate_limit + 2:
            return 0.7
        else:
            return 0.3

    def _analyze_concept_appropriateness(self, content: str, age: int) -> float:
        """تحليل ملاءمة المفاهيم"""

        content_lower = content.lower()

        inappropriate_concepts = ["موت", "مرض خطير", "حادث", "طلاق", "فقر", "حروب", "سياسة", "اقتصاد معقد"]

        inappropriate_count = sum(1 for concept in inappropriate_concepts if concept in content_lower)

        if inappropriate_count == 0:
            return 1.0
        elif inappropriate_count <= 2:
            return 0.6
        else:
            return 0.2

    def _analyze_emotional_complexity(self, content: str, age: int) -> float:
        """تحليل التعقيد العاطفي"""

        content_lower = content.lower()

        complex_emotions = ["اكتئاب", "قلق شديد", "خوف مرضي", "غضب شديد", "يأس", "إحباط عميق", "صدمة نفسية"]

        complex_emotion_count = sum(1 for emotion in complex_emotions if emotion in content_lower)

        if age < 6:
            tolerance = 0
        elif age < 10:
            tolerance = 1
        else:
            tolerance = 2

        if complex_emotion_count <= tolerance:
            return 1.0
        else:
            return max(0.2, 1.0 - (complex_emotion_count - tolerance) * 0.3)

    def _generate_age_recommendations(
        self, vocab_score: float, concept_score: float, emotional_score: float, age: int
    ) -> List[str]:
        """توليد توصيات للتحسين"""

        recommendations = []

        if vocab_score < 0.7:
            recommendations.append("استخدم كلمات أبسط وأقصر")

        if concept_score < 0.7:
            recommendations.append("تجنب المواضيع المعقدة أو الحساسة")

        if emotional_score < 0.7:
            recommendations.append("استخدم مشاعر أساسية وإيجابية")

        if age < 6:
            recommendations.append("ركز على الأشياء الملموسة والبسيطة")

        return recommendations


class AdvancedContentFilter:
    """نظام فلترة المحتوى المتطور"""

    def __init__(self):
        self.logger = structlog.get_logger(__name__)

        # مكونات التحليل
        self.toxicity_detector = ToxicityDetector()
        self.age_checker = AgeAppropriatenessChecker()

        # كاش للنتائج
        self.analysis_cache = TTLCache(maxsize=1000, ttl=1800)

        # إحصائيات
        self.filter_stats = {
            "total_requests": 0,
            "blocked_content": 0,
            "modified_content": 0,
            "safe_content": 0,
            "cache_hits": 0,
        }

    async def comprehensive_safety_check(
        self, content: str, child_age: int, context: Optional[Dict[str, Any]] = None
    ) -> ContentAnalysisResult:
        """فحص أمان شامل متعدد الطبقات"""

        start_time = time.time()
        self.filter_stats["total_requests"] += 1

        try:
            # فحص الكاش
            cache_key = self._generate_cache_key(content, child_age, context)
            if cached_result := self.analysis_cache.get(cache_key):
                self.filter_stats["cache_hits"] += 1
                self.logger.info("🎯 Cache hit for content analysis")
                return cached_result

            # تشغيل التحليلات بالتوازي
            toxicity_result, age_result = await asyncio.gather(
                self.toxicity_detector.analyze_toxicity(content, child_age),
                self.age_checker.check_age_appropriateness(content, child_age),
            )

            # دمج النتائج وتحليلها
            analysis_result = await self._combine_analysis_results(content, child_age, toxicity_result, age_result)

            # حفظ في الكاش
            self.analysis_cache[cache_key] = analysis_result

            # تحديث الإحصائيات
            self._update_filter_stats(analysis_result)

            return analysis_result

        except Exception as e:
            self.logger.error(f"❌ Content analysis failed: {e}")
            return self._generate_safe_fallback_result(content)

    async def _combine_analysis_results(
        self, content: str, child_age: int, toxicity_result: Dict[str, Any], age_result: Dict[str, Any]
    ) -> ContentAnalysisResult:
        """دمج جميع نتائج التحليل"""

        # تحديد الأمان العام
        is_safe = all([not toxicity_result.get("is_toxic", False), age_result.get("is_age_appropriate", False)])

        # حساب مستوى الخطر
        risk_level = self._calculate_overall_risk(toxicity_result, age_result)

        # حساب نقاط الثقة
        confidence_score = self._calculate_confidence(toxicity_result, age_result)

        # تحديد فئة المحتوى
        content_category = ContentCategory.EDUCATIONAL if "تعلم" in content else ContentCategory.ENTERTAINMENT

        # جمع الانتهاكات
        violations = toxicity_result.get("violations", [])

        # توليد التعديلات إذا لزم الأمر
        modifications = []
        safe_alternative = None

        if not is_safe:
            modifications, safe_alternative = await self._generate_safe_modifications(
                content, toxicity_result, age_result, child_age
            )

        # توليد توصيات الأمان
        safety_recommendations = self._generate_safety_recommendations(toxicity_result, age_result, child_age)

        # تحديد ما إذا كان يتطلب إشعار الوالدين
        parent_notification = self._requires_parent_notification(risk_level, child_age)

        processing_time = (time.time() - start_time) * 1000

        return ContentAnalysisResult(
            is_safe=is_safe,
            risk_level=risk_level,
            confidence_score=confidence_score,
            content_category=content_category,
            violations=violations,
            modifications=modifications,
            safe_alternative=safe_alternative,
            safety_recommendations=safety_recommendations,
            parent_notification_required=parent_notification,
            processing_time_ms=processing_time,
        )

    def _calculate_overall_risk(self, toxicity_result: Dict[str, Any], age_result: Dict[str, Any]) -> RiskLevel:
        """حساب مستوى الخطر الإجمالي"""

        risk_scores = []

        # نقاط السمية
        if toxicity_result.get("is_toxic", False):
            toxicity_score = toxicity_result.get("toxicity_score", 0)
            if toxicity_score >= 0.8:
                risk_scores.append(4)  # CRITICAL
            elif toxicity_score >= 0.6:
                risk_scores.append(3)  # HIGH_RISK
            elif toxicity_score >= 0.4:
                risk_scores.append(2)  # MEDIUM_RISK
            else:
                risk_scores.append(1)  # LOW_RISK
        else:
            risk_scores.append(0)  # SAFE

        # نقاط ملاءمة العمر
        if not age_result.get("is_age_appropriate", True):
            appropriateness_score = age_result.get("appropriateness_score", 1.0)
            if appropriateness_score < 0.3:
                risk_scores.append(3)
            elif appropriateness_score < 0.5:
                risk_scores.append(2)
            else:
                risk_scores.append(1)
        else:
            risk_scores.append(0)

        max_risk_score = max(risk_scores)

        risk_levels = [
            RiskLevel.SAFE,
            RiskLevel.LOW_RISK,
            RiskLevel.MEDIUM_RISK,
            RiskLevel.HIGH_RISK,
            RiskLevel.CRITICAL,
        ]

        return risk_levels[min(max_risk_score, len(risk_levels) - 1)]

    def _calculate_confidence(self, toxicity_result: Dict[str, Any], age_result: Dict[str, Any]) -> float:
        """حساب نقاط الثقة"""

        confidence_factors = []

        # ثقة كشف السمية
        if toxicity_result.get("detected_categories"):
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.8)

        # ثقة فحص العمر
        age_score = age_result.get("appropriateness_score", 0.5)
        confidence_factors.append(min(1.0, age_score + 0.3))

        return sum(confidence_factors) / len(confidence_factors)

    async def _generate_safe_modifications(
        self, content: str, toxicity_result: Dict[str, Any], age_result: Dict[str, Any], child_age: int
    ) -> Tuple[List[str], Optional[str]]:
        """توليد تعديلات آمنة للمحتوى"""

        modifications = []
        safe_alternative = content

        # تعديل السمية
        if toxicity_result.get("is_toxic", False):
            safe_alternative = await self._remove_toxic_content(safe_alternative, toxicity_result)
            modifications.append("تم إزالة المحتوى الضار")

        # تعديل ملاءمة العمر
        if not age_result.get("is_age_appropriate", True):
            safe_alternative = await self._simplify_for_age(safe_alternative, child_age)
            modifications.append("تم تبسيط المحتوى ليناسب العمر")

        # إذا أصبح المحتوى فارغاً أو قصيراً جداً
        if len(safe_alternative.strip()) < 10:
            safe_alternative = self._generate_safe_replacement_content(child_age)
            modifications.append("تم استبدال المحتوى بمحتوى آمن")

        return modifications, safe_alternative

    async def _remove_toxic_content(self, content: str, toxicity_result: Dict[str, Any]) -> str:
        """إزالة المحتوى الضار"""

        safe_content = content

        detected_categories = toxicity_result.get("detected_categories", {})

        for category, info in detected_categories.items():
            patterns = info.get("patterns", [])
            for pattern in patterns:
                safe_replacements = {"عنف": "لعب", "ضرب": "لمس بلطف", "قتل": "نوم", "غضب": "انزعاج خفيف"}

                replacement = safe_replacements.get(pattern, "***")
                safe_content = safe_content.replace(pattern, replacement)

        return safe_content

    async def _simplify_for_age(self, content: str, age: int) -> str:
        """تبسيط المحتوى ليناسب العمر"""

        simplifications = {"تكنولوجيا": "آلات ذكية", "اقتصاد": "تجارة", "سياسة": "قوانين", "فلسفة": "أفكار"}

        simplified_content = content
        for complex_word, simple_word in simplifications.items():
            simplified_content = simplified_content.replace(complex_word, simple_word)

        return simplified_content

    def _generate_safe_replacement_content(self, age: int) -> str:
        """توليد محتوى بديل آمن"""

        age_appropriate_responses = {
            (3, 5): "دعنا نتحدث عن شيء جميل! هل تحب الألوان؟",
            (6, 8): "هذا موضوع مثير للاهتمام! دعني أحكي لك قصة لطيفة.",
            (9, 12): "أعتذر، دعني أجيب بطريقة أخرى. ما رأيك أن نتعلم شيئاً جديداً؟",
        }

        for age_range, response in age_appropriate_responses.items():
            if age_range[0] <= age <= age_range[1]:
                return response

        return "دعنا نتحدث عن شيء آخر أكثر متعة!"

    def _generate_safety_recommendations(
        self, toxicity_result: Dict[str, Any], age_result: Dict[str, Any], child_age: int
    ) -> List[str]:
        """توليد توصيات الأمان"""

        recommendations = []

        if toxicity_result.get("is_toxic", False):
            recommendations.append("تجنب المحتوى العنيف أو المؤذي")

        if not age_result.get("is_age_appropriate", True):
            recommendations.append("استخدم لغة ومفاهيم مناسبة للعمر")

        if child_age < 6:
            recommendations.append("ركز على المواضيع الإيجابية والبسيطة")

        if not recommendations:
            recommendations.append("المحتوى آمن ومناسب")

        return recommendations

    def _requires_parent_notification(self, risk_level: RiskLevel, child_age: int) -> bool:
        """تحديد ما إذا كان يتطلب إشعار الوالدين"""

        if risk_level in [RiskLevel.HIGH_RISK, RiskLevel.CRITICAL]:
            return True

        if child_age <= 5 and risk_level == RiskLevel.MEDIUM_RISK:
            return True

        return False

    def _generate_cache_key(self, content: str, child_age: int, context: Optional[Dict[str, Any]]) -> str:
        """توليد مفتاح كاش"""

        cache_components = [content[:100], str(child_age), str(context.get("safety_level", 5) if context else 5)]

        cache_string = "_".join(cache_components)
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _update_filter_stats(ContentAnalysisResult) -> None:
        """تحديث إحصائيات الفلتر"""

        if not result.is_safe:
            self.filter_stats["blocked_content"] += 1
        elif result.modifications:
            self.filter_stats["modified_content"] += 1
        else:
            self.filter_stats["safe_content"] += 1

    def _generate_safe_fallback_result(self, content: str) -> ContentAnalysisResult:
        """توليد نتيجة احتياطية آمنة"""

        return ContentAnalysisResult(
            is_safe=False,
            risk_level=RiskLevel.MEDIUM_RISK,
            confidence_score=0.5,
            content_category=ContentCategory.INAPPROPRIATE,
            violations=[
                SafetyViolation(
                    violation_type="processing_error",
                    severity=RiskLevel.MEDIUM_RISK,
                    description="خطأ في معالجة المحتوى",
                    content_excerpt=content[:50],
                )
            ],
            modifications=["فشل التحليل - تم الرفض احتياطاً"],
            safe_alternative="عذراً، لا يمكنني معالجة هذا المحتوى الآن.",
            safety_recommendations=["راجع المحتوى مع الوالدين"],
            parent_notification_required=True,
            processing_time_ms=0.0,
        )

    def get_filter_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الفلتر"""

        total = self.filter_stats["total_requests"]

        return {
            **self.filter_stats,
            "safety_rate": (self.filter_stats["safe_content"] / max(1, total)) * 100,
            "modification_rate": (self.filter_stats["modified_content"] / max(1, total)) * 100,
            "block_rate": (self.filter_stats["blocked_content"] / max(1, total)) * 100,
            "cache_hit_rate": (self.filter_stats["cache_hits"] / max(1, total)) * 100,
            "cache_size": len(self.analysis_cache),
        }

    async def cleanup(self):
        """تنظيف الموارد"""
        try:
            self.analysis_cache.clear()
            self.logger.info("✅ Content filter cleanup completed")
        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")


def create_advanced_content_filter() -> AdvancedContentFilter:
    """إنشاء فلتر محتوى متطور"""
    return AdvancedContentFilter()
