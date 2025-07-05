#!/usr/bin/env python3

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .moderation import ContentCategory, ModerationResult, ModerationSeverity

# ================== PARAMETER OBJECTS ==================


@dataclass
class ModerationRequest:
    """📦 Parameter Object - حل مشكلة كثرة المعاملات"""

    content: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    age: int = 10
    language: str = "en"
    context: Optional[List] = None

    def __post_init__(self):
        """تنظيف وتحقق من صحة البيانات"""
        if self.content:
            self.content = self.content.strip()
        if self.age < 1:
            self.age = 10
        if not self.language:
            self.language = "en"


@dataclass
class ModerationContext:
    """📦 Parameter Object - سياق الفحص"""

    enable_openai: bool = True
    enable_azure: bool = True
    enable_google: bool = True
    enable_local: bool = True
    use_cache: bool = True
    generate_alternatives: bool = True


# ================== STATE MACHINE ==================


class ModerationState(Enum):
    """🔄 حالات آلة الفحص"""

    STARTING = "starting"
    VALIDATING = "validating"
    CHECKING_CACHE = "checking_cache"
    LOCAL_CHECK = "local_check"
    AI_CHECK = "ai_check"
    AGGREGATING = "aggregating"
    GENERATING_RESPONSE = "generating_response"
    COMPLETED = "completed"
    FAILED = "failed"


class ModerationEvent(Enum):
    """📨 أحداث آلة الفحص"""

    START = "start"
    VALIDATE = "validate"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    LOCAL_SAFE = "local_safe"
    LOCAL_UNSAFE = "local_unsafe"
    AI_SAFE = "ai_safe"
    AI_UNSAFE = "ai_unsafe"
    AI_FAILED = "ai_failed"
    AGGREGATE = "aggregate"
    GENERATE = "generate"
    COMPLETE = "complete"
    FAIL = "fail"


class ModerationStateMachine:
    """🔄 آلة الحالة للفحص - بدلاً من الشروط المتعددة"""

    def __init__(self):
        self.state = ModerationState.STARTING
        self.transitions = self._build_transition_table()
        self.handlers = self._build_handler_table()

    def _build_transition_table(
        self,
    ) -> Dict[Tuple[ModerationState, ModerationEvent], ModerationState]:
        """🗺️ جدول التحولات - Lookup Table بدلاً من الشروط"""
        return {
            # من البداية
            (
                ModerationState.STARTING,
                ModerationEvent.START,
            ): ModerationState.VALIDATING,
            # التحقق من صحة البيانات
            (
                ModerationState.VALIDATING,
                ModerationEvent.VALIDATE,
            ): ModerationState.CHECKING_CACHE,
            (ModerationState.VALIDATING, ModerationEvent.FAIL): ModerationState.FAILED,
            # فحص Cache
            (
                ModerationState.CHECKING_CACHE,
                ModerationEvent.CACHE_HIT,
            ): ModerationState.COMPLETED,
            (
                ModerationState.CHECKING_CACHE,
                ModerationEvent.CACHE_MISS,
            ): ModerationState.LOCAL_CHECK,
            # الفحص المحلي
            (
                ModerationState.LOCAL_CHECK,
                ModerationEvent.LOCAL_UNSAFE,
            ): ModerationState.GENERATING_RESPONSE,
            (
                ModerationState.LOCAL_CHECK,
                ModerationEvent.LOCAL_SAFE,
            ): ModerationState.AI_CHECK,
            # فحص AI
            (
                ModerationState.AI_CHECK,
                ModerationEvent.AI_UNSAFE,
            ): ModerationState.GENERATING_RESPONSE,
            (
                ModerationState.AI_CHECK,
                ModerationEvent.AI_SAFE,
            ): ModerationState.GENERATING_RESPONSE,
            (
                ModerationState.AI_CHECK,
                ModerationEvent.AI_FAILED,
            ): ModerationState.GENERATING_RESPONSE,
            # إنتاج النتيجة
            (
                ModerationState.GENERATING_RESPONSE,
                ModerationEvent.GENERATE,
            ): ModerationState.COMPLETED,
            # الإكمال
            (
                ModerationState.COMPLETED,
                ModerationEvent.COMPLETE,
            ): ModerationState.COMPLETED,
        }

    def _build_handler_table(self) -> Dict[ModerationState, Callable]:
        """🔧 جدول المعالجات - Lookup Table للدوال"""
        return {
            ModerationState.VALIDATING: self._handle_validation,
            ModerationState.CHECKING_CACHE: self._handle_cache_check,
            ModerationState.LOCAL_CHECK: self._handle_local_check,
            ModerationState.AI_CHECK: self._handle_ai_check,
            ModerationState.GENERATING_RESPONSE: self._handle_response_generation,
            ModerationState.COMPLETED: self._handle_completion,
            ModerationState.FAILED: self._handle_failure,
        }

    def transition(self, event: ModerationEvent) -> bool:
        """🔄 تنفيذ التحول بدلاً من if/else معقدة"""
        transition_key = (self.state, event)

        if transition_key in self.transitions:
            new_state = self.transitions[transition_key]
            self.state = new_state
            return True

        return False

    def handle_current_state(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 تنفيذ معالج الحالة الحالية"""
        if self.state in self.handlers:
            return self.handlers[self.state](context)
        return {"error": f"No handler for state: {self.state}"}

    # ================== STATE HANDLERS ==================

    def _handle_validation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """✅ معالج التحقق من صحة البيانات"""
        request: ModerationRequest = context.get("request")

        if not request or not request.content.strip():
            return {"valid": False, "error": "Empty content"}

        if len(request.content) > 10000:  # حد أقصى
            return {"valid": False, "error": "Content too long"}

        return {"valid": True}

    def _handle_cache_check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """📦 معالج فحص Cache"""
        # سيتم تنفيذه في الخدمة الرئيسية
        return {"cache_checked": True}

    def _handle_local_check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """🏠 معالج الفحص المحلي"""
        # سيتم تنفيذه في الخدمة الرئيسية
        return {"local_checked": True}

    def _handle_ai_check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """🤖 معالج فحص AI"""
        # سيتم تنفيذه في الخدمة الرئيسية
        return {"ai_checked": True}

    def _handle_response_generation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """📝 معالج إنتاج النتيجة"""
        # سيتم تنفيذه في الخدمة الرئيسية
        return {"response_generated": True}

    def _handle_completion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """✅ معالج الإكمال"""
        return {"completed": True, "timestamp": datetime.now().isoformat()}

    def _handle_failure(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """❌ معالج الفشل"""
        return {"failed": True, "error": context.get("error", "Unknown error")}


# ================== LOOKUP TABLES ==================


class ModerationLookupTables:
    """📋 جداول البحث - بدلاً من سلاسل المنطق الطويلة"""

    # جدول تحويل تصنيفات OpenAI
    OPENAI_CATEGORY_MAPPING = {
        "sexual": ContentCategory.SEXUAL,
        "hate": ContentCategory.HATE_SPEECH,
        "violence": ContentCategory.VIOLENCE,
        "self-harm": ContentCategory.VIOLENCE,
        "sexual/minors": ContentCategory.AGE_INAPPROPRIATE,
        "hate/threatening": ContentCategory.HATE_SPEECH,
        "violence/graphic": ContentCategory.VIOLENCE,
    }

    # جدول تحديد الخطورة حسب النقاط
    SEVERITY_SCORE_MAPPING = {
        (0.0, 0.3): ModerationSeverity.SAFE,
        (0.3, 0.5): ModerationSeverity.LOW,
        (0.5, 0.8): ModerationSeverity.MEDIUM,
        (0.8, 0.95): ModerationSeverity.HIGH,
        (0.95, 1.0): ModerationSeverity.CRITICAL,
    }

    # جدول الردود البديلة حسب التصنيف
    ALTERNATIVE_RESPONSES = {
        ContentCategory.VIOLENCE: "دعنا نتحدث عن شيء لطيف ومرح بدلاً من ذلك! 🌟",
        ContentCategory.SCARY_CONTENT: "هل تريد أن نتحدث عن شيء سعيد وممتع؟ 😊",
        ContentCategory.PERSONAL_INFO: "من المهم أن نحافظ على معلوماتنا الشخصية آمنة! 🔒",
        ContentCategory.PROFANITY: "لنستخدم كلمات لطيفة ومهذبة! 🌈",
        ContentCategory.HATE_SPEECH: "الكلمات اللطيفة تجعل الجميع سعداء! ✨",
        ContentCategory.BULLYING: "لنكن أصدقاء طيبين مع بعضنا البعض! 💝",
        ContentCategory.AGE_INAPPROPRIATE: "دعنا نتحدث عن أشياء مناسبة وممتعة! 🎈",
        ContentCategory.SEXUAL: "دعنا نغير الموضوع إلى شيء أكثر إيجابية! 🌈",
    }

    # جدول أسباب الرفض
    REJECTION_REASONS = {
        ContentCategory.VIOLENCE: "المحتوى يحتوي على عنف غير مناسب للأطفال",
        ContentCategory.SEXUAL: "المحتوى غير مناسب للأطفال",
        ContentCategory.PERSONAL_INFO: "المحتوى يحتوي على معلومات شخصية حساسة",
        ContentCategory.HATE_SPEECH: "المحتوى يحتوي على كلام مؤذي",
        ContentCategory.SCARY_CONTENT: "المحتوى قد يكون مخيفاً للأطفال",
        ContentCategory.PROFANITY: "المحتوى يحتوي على كلمات غير مناسبة",
        ContentCategory.BULLYING: "المحتوى قد يكون مؤذياً أو يحتوي على تنمر",
        ContentCategory.AGE_INAPPROPRIATE: "المحتوى غير مناسب لهذه الفئة العمرية",
    }

    # جدول حدود العمر للتصنيفات
    AGE_CATEGORY_LIMITS = {
        ContentCategory.SCARY_CONTENT: 10,  # تحت 10 سنوات
        ContentCategory.VIOLENCE: 13,  # تحت 13 سنة
        ContentCategory.AGE_INAPPROPRIATE: 16,  # تحت 16 سنة
    }

    @classmethod
    def get_severity_by_score(cls, score: float) -> ModerationSeverity:
        """🎯 تحديد الخطورة حسب النقاط - بدلاً من if/else متعددة"""
        for (min_score, max_score), severity in cls.SEVERITY_SCORE_MAPPING.items():
            if min_score <= score < max_score:
                return severity
        return ModerationSeverity.CRITICAL  # افتراضي للنقاط عالية

    @classmethod
    def get_alternative_response(cls, categories: List[ContentCategory]) -> str:
        """💬 الحصول على رد بديل - Lookup بدلاً من switch/case"""
        for category in categories:
            if category in cls.ALTERNATIVE_RESPONSES:
                return cls.ALTERNATIVE_RESPONSES[category]
        return "دعنا نغير الموضوع إلى شيء أكثر إيجابية! ✨"

    @classmethod
    def get_rejection_reason(cls, categories: List[ContentCategory]) -> str:
        """📝 الحصول على سبب الرفض - Lookup بدلاً من switch/case"""
        for category in categories:
            if category in cls.REJECTION_REASONS:
                return cls.REJECTION_REASONS[category]
        return "المحتوى قد يحتوي على مواد غير مناسبة"

    @classmethod
    def is_age_appropriate(cls, category: ContentCategory, age: int) -> bool:
        """👶 فحص مناسبة العمر - Lookup بدلاً من شروط معقدة"""
        if category in cls.AGE_CATEGORY_LIMITS:
            return age >= cls.AGE_CATEGORY_LIMITS[category]
        return True  # افتراضي: مناسب لجميع الأعمار


# ================== DECOMPOSED CONDITIONALS ==================


class ConditionalDecomposer:
    """🧩 تبسيط الشروط المعقدة - DECOMPOSE CONDITIONAL"""

    @staticmethod
    def is_content_empty_or_invalid(content: str) -> bool:
        """✅ شرط مبسط: هل المحتوى فارغ أم غير صالح؟"""
        return not content or not content.strip() or len(content.strip()) == 0

    @staticmethod
    def is_content_too_long(content: str, max_length: int = 10000) -> bool:
        """📏 شرط مبسط: هل المحتوى طويل جداً؟"""
        return len(content) > max_length

    @staticmethod
    def is_young_child(age: int, threshold: int = 10) -> bool:
        """👶 شرط مبسط: هل هو طفل صغير؟"""
        return age < threshold

    @staticmethod
    def is_cache_hit_valid(cache_timestamp: datetime, ttl_seconds: int) -> bool:
        """📦 شرط مبسط: هل Cache صالح؟"""
        if not cache_timestamp:
            return False
        elapsed = (datetime.now() - cache_timestamp).total_seconds()
        return elapsed < ttl_seconds

    @staticmethod
    def is_score_above_threshold(score: float, threshold: float) -> bool:
        """🎯 شرط مبسط: هل النقاط أعلى من الحد؟"""
        return score > threshold

    @staticmethod
    def has_risky_categories(
        categories: List[ContentCategory], risky_list: List[ContentCategory]
    ) -> bool:
        """⚠️ شرط مبسط: هل يحتوي على تصنيفات خطيرة؟"""
        return any(cat in risky_list for cat in categories)

    @staticmethod
    def should_use_ai_check(
        content_length: int, local_result_safe: bool, ai_enabled: bool
    ) -> bool:
        """🤖 شرط مبسط: هل نحتاج فحص AI؟"""
        return ai_enabled and local_result_safe and content_length > 20

    @staticmethod
    def should_alert_parent(
        severity: ModerationSeverity, user_violations_count: int
    ) -> bool:
        """👨‍👩‍👧‍👦 شرط مبسط: هل نحتاج تنبيه الوالدين؟"""
        return (
            severity in [ModerationSeverity.HIGH, ModerationSeverity.CRITICAL]
            or user_violations_count >= 3
        )


# ================== STRATEGY PATTERN FOR CHECKERS ==================


class ModerationChecker(ABC):
    """🎯 واجهة موحدة لجميع أنواع الفحص - Strategy Pattern"""

    @abstractmethod
    async def check(self, request: ModerationRequest) -> ModerationResult:
        """فحص المحتوى"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """هل الفاحص متوفر؟"""
        pass


class LocalChecker(ModerationChecker):
    """🏠 الفاحص المحلي"""

    def __init__(self, patterns: Dict[str, Any]):
        self.patterns = patterns

    async def check(self, request: ModerationRequest) -> ModerationResult:
        """فحص محلي سريع"""
        # سيتم تنفيذه في الخدمة الرئيسية
        pass

    def is_available(self) -> bool:
        return len(self.patterns) > 0


class OpenAIChecker(ModerationChecker):
    """🤖 فاحص OpenAI"""

    def __init__(self, client):
        self.client = client

    async def check(self, request: ModerationRequest) -> ModerationResult:
        """فحص OpenAI"""
        # سيتم تنفيذه في الخدمة الرئيسية
        pass

    def is_available(self) -> bool:
        return self.client is not None


# ================== EXPORTS ==================

__all__ = [
    "ModerationRequest",
    "ModerationContext",
    "ModerationStateMachine",
    "ModerationState",
    "ModerationEvent",
    "ModerationLookupTables",
    "ConditionalDecomposer",
    "ModerationChecker",
    "LocalChecker",
    "OpenAIChecker",
]
