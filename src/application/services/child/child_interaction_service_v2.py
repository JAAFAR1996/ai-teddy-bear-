"""
Child Interaction Service V2 - خدمة تفاعل الأطفال المحسنة
مثال كامل لاستخدام نظام Exception Handling المتقدم
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

import structlog

from src.domain.exceptions.base import (
    AgeInappropriateException,
    AuthenticationException,
    ErrorContext,
    ExternalServiceException,
    InappropriateContentException,
    ParentalConsentRequiredException,
    QuotaExceededException,
    ValidationException,
)
from src.infrastructure.decorators.exception_handler import (
    RetryConfig,
    authenticated,
    child_safe,
    handle_exceptions,
    validate_input,
    with_circuit_breaker,
    with_retry,
)
from src.infrastructure.exception_handling.global_handler import get_global_exception_handler
from src.infrastructure.monitoring.metrics import MetricsCollector, track_request_duration

logger = structlog.get_logger(__name__)


@dataclass
class SafetyCheckResult:
    """نتيجة فحص الأمان"""

    is_safe: bool
    violation_type: Optional[str] = None
    reason: Optional[str] = None
    confidence: float = 1.0


class ContentFilterService:
    """خدمة تصفية المحتوى"""

    async def check(self, content: str) -> SafetyCheckResult:
        """فحص المحتوى للتأكد من ملاءمته للأطفال"""
        # قائمة الكلمات الممنوعة (مثال بسيط)
        inappropriate_words = ["violence", "scary", "inappropriate"]

        content_lower = content.lower()
        for word in inappropriate_words:
            if word in content_lower:
                return SafetyCheckResult(
                    is_safe=False,
                    violation_type="inappropriate_language",
                    reason=f"Content contains inappropriate word: {word}",
                    confidence=0.95,
                )

        return SafetyCheckResult(is_safe=True, confidence=0.98)

    async def check_age_appropriateness(self, content: str, child_age: int) -> SafetyCheckResult:
        """فحص ملاءمة المحتوى لعمر الطفل"""
        # مثال: محتوى معقد للأطفال الصغار
        if child_age < 6 and len(content.split()) > 50:
            return SafetyCheckResult(
                is_safe=False,
                violation_type="age_inappropriate",
                reason="Content too complex for young children",
                confidence=0.85,
            )

        return SafetyCheckResult(is_safe=True)


class AIService:
    """خدمة الذكاء الاصطناعي"""

    @with_circuit_breaker(
        service_name="openai_api",
        failure_threshold=3,
        timeout_seconds=30,
        fallback=lambda: "مرحباً! كيف يمكنني مساعدتك اليوم؟",
    )
    @with_retry(
        config=RetryConfig(
            max_attempts=3, initial_delay=1.0, exponential_backoff=True, exceptions_to_retry=[ExternalServiceException]
        )
    )
    async def generate_response(self, message: str, context: Dict[str, Any]) -> str:
        """توليد رد من AI"""
        try:
            # محاكاة استدعاء OpenAI API
            await asyncio.sleep(0.5)  # محاكاة latency

            # محاكاة فشل عشوائي للاختبار
            import random

            if random.random() < 0.1:  # 10% failure rate
                raise ExternalServiceException(
                    service_name="OpenAI", status_code=503, response_body="Service temporarily unavailable"
                )

            # رد بسيط للمثال
            child_name = context.get("child_name", "صديقي")
            return f"مرحباً {child_name}! {message} هذا سؤال رائع!"

        except Exception as e:
            if not isinstance(e, ExternalServiceException):
                raise ExternalServiceException(service_name="OpenAI", status_code=500, response_body=str(e))
            raise


class QuotaService:
    """خدمة إدارة الحصص"""

    def __init__(self):
        self.usage = {}

    async def check_quota(self, child_id: str) -> Dict[str, Any]:
        """فحص حصة الاستخدام"""
        usage = self.usage.get(child_id, {"count": 0, "last_reset": datetime.utcnow()})

        # إعادة تعيين يومية
        if (datetime.utcnow() - usage["last_reset"]).days >= 1:
            usage = {"count": 0, "last_reset": datetime.utcnow()}

        return {"current_usage": usage["count"], "daily_limit": 100, "remaining": 100 - usage["count"]}

    async def increment_usage(self, child_id: str) -> None:
        """زيادة عداد الاستخدام"""
        if child_id not in self.usage:
            self.usage[child_id] = {"count": 0, "last_reset": datetime.utcnow()}
        self.usage[child_id]["count"] += 1


class ChildInteractionServiceV2:
    """خدمة تفاعل الأطفال المحسنة مع Exception Handling المتقدم"""

    def __init__(self):
        self.content_filter = ContentFilterService()
        self.ai_service = AIService()
        self.quota_service = QuotaService()

        # تسجيل recovery strategies
        self._register_recovery_strategies()

    def _register_recovery_strategies(self):
        """تسجيل استراتيجيات الاسترداد"""
        handler = get_global_exception_handler()

        # استراتيجية لمعالجة المحتوى غير المناسب
        handler.register_recovery_strategy(
            "INAPPROPRIATE_CONTENT",
            lambda e, ctx: {"response": "عذراً، لا أستطيع الإجابة على هذا السؤال. هل لديك سؤال آخر؟", "filtered": True},
        )

        # استراتيجية لتجاوز الحصة
        handler.register_recovery_strategy(
            "QUOTA_EXCEEDED",
            lambda e, ctx: {
                "response": "لقد وصلت لحد الأسئلة اليومي. حاول مرة أخرى غداً!",
                "retry_after": 86400,  # 24 ساعة
            },
        )

    @handle_exceptions(
        (
            InappropriateContentException,
            lambda e: {"error": "Content filtered", "safe": True, "message": "تم تصفية المحتوى لحماية الطفل"},
        ),
        (
            ParentalConsentRequiredException,
            lambda e: {
                "error": "Parent approval needed",
                "action": "notify_parent",
                "details": {"action": e.action, "reason": e.reason},
            },
        ),
        (ValidationException, lambda e: {"error": f"Invalid input: {str(e)}", "retry": True, "field": e.field_name}),
        (
            QuotaExceededException,
            lambda e: {
                "error": "Daily limit reached",
                "retry_after": e.retry_after,
                "quota_info": {"current": e.current_usage, "limit": e.quota_limit},
            },
        ),
    )
    @validate_input(
        validators={
            "message": lambda m: m and 0 < len(m) <= 1000,
            "child_id": lambda c: c and len(c) > 0,
            "child_age": lambda a: isinstance(a, int) and 3 <= a <= 12,
        },
        error_messages={
            "message": "الرسالة يجب أن تكون بين 1 و 1000 حرف",
            "child_id": "معرف الطفل مطلوب",
            "child_age": "العمر يجب أن يكون بين 3 و 12 سنة",
        },
    )
    @child_safe(notify_parent=True)
    @track_request_duration(endpoint="/api/v2/child/interact")
    async def process_interaction(
        self, child_id: str, child_age: int, message: str, auth_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        معالجة تفاعل الطفل مع جميع الحمايات

        Args:
            child_id: معرف الطفل
            child_age: عمر الطفل
            message: رسالة الطفل
            auth_context: سياق المصادقة

        Returns:
            استجابة آمنة للطفل
        """
        # إنشاء error context
        error_context = ErrorContext(
            child_id=child_id,
            user_id=auth_context.get("parent_id"),
            session_id=auth_context.get("session_id"),
            additional_data={"child_age": child_age, "message_length": len(message)},
        )

        try:
            # 1. فحص الحصة
            quota_info = await self.quota_service.check_quota(child_id)
            if quota_info["remaining"] <= 0:
                raise QuotaExceededException(
                    quota_type="daily_interactions",
                    current_usage=quota_info["current_usage"],
                    quota_limit=quota_info["daily_limit"],
                    reset_time=datetime.utcnow().replace(hour=0, minute=0, second=0),
                    context=error_context,
                )

            # 2. فحص أمان المحتوى
            safety_result = await self.content_filter.check(message)
            if not safety_result.is_safe:
                raise InappropriateContentException(
                    content_type=safety_result.violation_type,
                    violation_reason=safety_result.reason,
                    context=error_context,
                )

            # 3. فحص ملاءمة العمر
            age_result = await self.content_filter.check_age_appropriateness(message, child_age)
            if not age_result.is_safe:
                raise AgeInappropriateException(
                    child_age=child_age,
                    content_age_rating=child_age + 3,  # مثال
                    content_description="Complex content",
                    context=error_context,
                )

            # 4. فحص الصلاحيات الخاصة
            if "special_content" in message.lower():
                raise ParentalConsentRequiredException(
                    action="access_special_content",
                    reason="Child requested special content access",
                    context=error_context,
                )

            # 5. توليد الرد من AI
            ai_context = {
                "child_id": child_id,
                "child_age": child_age,
                "child_name": auth_context.get("child_name", "صديقي"),
                "language": "ar",
            }

            response = await self.ai_service.generate_response(message, ai_context)

            # 6. فحص أمان الرد
            response_safety = await self.content_filter.check(response)
            if not response_safety.is_safe:
                # استخدام رد آمن بديل
                response = self._get_safe_fallback_response(child_age)

            # 7. تحديث الحصة
            await self.quota_service.increment_usage(child_id)

            # 8. تسجيل metrics
            MetricsCollector.record_interaction(interaction_type="voice_chat", child_age=child_age)

            # 9. تسجيل النجاح
            logger.info(
                "Interaction processed successfully",
                child_id=child_id,
                message_length=len(message),
                response_length=len(response),
            )

            return {
                "success": True,
                "response": response,
                "metadata": {
                    "processed_at": datetime.utcnow().isoformat(),
                    "safety_checked": True,
                    "ai_generated": True,
                    "quota_remaining": quota_info["remaining"] - 1,
                    "child_id": child_id,
                },
            }

        except AITeddyBearException:
            # AITeddyBearException سيتم معالجتها بواسطة decorators
            raise
        except Exception as e:
            # أي خطأ غير متوقع
            logger.error("Unexpected error in process_interaction", error=str(e), exc_info=True)
            # سيتم معالجته بواسطة global handler
            raise

    def _get_safe_fallback_response(self, child_age: int) -> str:
        """الحصول على رد آمن بديل حسب العمر"""
        if child_age < 6:
            return "واو! هذا رائع! هل تريد أن نلعب لعبة؟"
        elif child_age < 9:
            return "سؤال ممتاز! دعنا نفكر في هذا معاً."
        else:
            return "هذا موضوع مثير للاهتمام! ما رأيك أنت؟"

    @authenticated(required_role="parent")
    @handle_exceptions(
        (AuthenticationException, lambda e: {"error": "Authentication required", "login_url": "/api/v2/auth/login"})
    )
    async def get_interaction_history(
        self, child_id: str, auth_context: Dict[str, Any], limit: int = 50
    ) -> Dict[str, Any]:
        """الحصول على تاريخ التفاعلات (للوالدين فقط)"""
        # التحقق من أن الوالد يملك صلاحية على هذا الطفل
        if child_id not in auth_context.get("children_ids", []):
            from src.domain.exceptions.base import AuthorizationException

            raise AuthorizationException(
                action="view_child_history", resource=f"child/{child_id}", required_role="parent_of_child"
            )

        # جلب التاريخ (مثال)
        return {
            "child_id": child_id,
            "interactions": [],  # سيتم ملؤها من قاعدة البيانات
            "total_count": 0,
            "limit": limit,
        }


# مثال للاستخدام
async def main():
    """مثال لاستخدام الخدمة"""
    service = ChildInteractionServiceV2()

    # سياق مصادقة وهمي
    auth_context = {
        "authenticated": True,
        "parent_id": "parent123",
        "child_name": "أحمد",
        "session_id": "session456",
        "children_ids": ["child789"],
    }

    try:
        # مثال 1: تفاعل ناجح
        result = await service.process_interaction(
            child_id="child789", child_age=7, message="ما هي الشمس؟", auth_context=auth_context
        )
        print("Success:", result)

        # مثال 2: محتوى غير مناسب
        result = await service.process_interaction(
            child_id="child789", child_age=7, message="أريد أن أشاهد محتوى violence", auth_context=auth_context
        )
        print("Filtered:", result)

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
