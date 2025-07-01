from typing import Any, Dict, List, Optional

"""
🧸 Enhanced Child Interaction Service - 2025 Edition
خدمة تفاعل الطفل المحسنة مع التحسينات الجديدة

Lead Architect: جعفر أديب (Jaafar Adeeb)
Senior Backend Developer & Professor
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional

import numpy as np
import structlog

from src.infrastructure.external_services.advanced_ai_orchestrator import (
    AdvancedAIOrchestrator,
    ChildRequest,
    ModelComplexity,
)

# Import enhanced components
from src.infrastructure.external_services.enhanced_audio_processor import (
    AudioConfig,
    AudioProcessingResult,
    EnhancedAudioProcessor,
)
from src.infrastructure.security.advanced_content_filter import AdvancedContentFilter, ContentAnalysisResult

logger = structlog.get_logger(__name__)


@dataclass
class ChildSession:
    """جلسة تفاعل الطفل"""

    child_id: str
    child_name: str
    child_age: int
    session_start: float
    interaction_count: int = 0
    total_processing_time: float = 0.0
    mood_history: List[str] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    safety_violations: List[Dict[str, Any]] = field(default_factory=list)
    educational_progress: Dict[str, float] = field(default_factory=dict)


@dataclass
class InteractionResponse:
    """استجابة التفاعل الشاملة"""

    audio_processing_result: AudioProcessingResult
    content_analysis_result: ContentAnalysisResult
    ai_response: Dict[str, Any]
    safety_check_passed: bool
    processing_time_ms: float
    session_updated: bool
    parent_notification_sent: bool
    recommendations: List[str]


class EnhancedChildInteractionService:
    """
    خدمة تفاعل الطفل المحسنة - 2025

    تجمع جميع التحسينات:
    - معالجة صوت متطورة
    - ذكاء اصطناعي ذكي
    - فلترة أمان شاملة
    - تتبع تقدم تعليمي
    """

    def __init__(
        self,
        audio_processor: EnhancedAudioProcessor,
        ai_orchestrator: AdvancedAIOrchestrator,
        content_filter: AdvancedContentFilter,
    ):
        self.audio_processor = audio_processor
        self.ai_orchestrator = ai_orchestrator
        self.content_filter = content_filter
        self.logger = structlog.get_logger(__name__)

        # إدارة الجلسات
        self.active_sessions: Dict[str, ChildSession] = {}

        # إحصائيات الخدمة
        self.service_stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "blocked_interactions": 0,
            "average_response_time": 0.0,
            "unique_children": 0,
            "safety_violations": 0,
            "educational_interactions": 0,
        }

        self.logger.info("✅ Enhanced Child Interaction Service initialized")

    async def process_child_interaction(
        self,
        audio_stream: AsyncIterator[bytes],
        child_id: str,
        child_profile: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        session_context: Optional[Dict[str, Any]] = None,
    ) -> InteractionResponse:
        """
        معالجة تفاعل الطفل الشاملة مع جميع التحسينات
        """

        start_time = time.time()
        self.service_stats["total_interactions"] += 1

        try:
            # 1. إنشاء أو تحديث الجلسة
            session = await self._get_or_create_session(child_id, child_profile)

            # 2. معالجة الصوت المتطورة
            audio_result = await self.audio_processor.process_audio_stream(
                audio_stream=audio_stream,
                child_context={
                    "child_id": child_id,
                    "age": child_profile.get("age", 7),
                    "mood_history": session.mood_history[-5:],  # آخر 5 حالات مزاجية
                    "session_context": session_context,
                },
            )

            self.logger.info(
                "🎵 Audio processing completed",
                child_id=child_id,
                quality_score=audio_result.quality_score,
                voice_activity=audio_result.voice_activity_score,
                processing_time=f"{audio_result.processing_time_ms:.1f}ms",
            )

            # 3. استخراج النص من الصوت (محاكاة)
            transcribed_text = await self._transcribe_audio(audio_result)

            # 4. فحص الأمان الشامل
            content_analysis = await self.content_filter.comprehensive_safety_check(
                content=transcribed_text,
                child_age=child_profile.get("age", 7),
                context={
                    "child_id": child_id,
                    "session_history": conversation_history,
                    "safety_level": child_profile.get("safety_level", 5),
                },
            )

            self.logger.info(
                "🛡️ Content safety check completed",
                child_id=child_id,
                is_safe=content_analysis.is_safe,
                risk_level=content_analysis.risk_level.value,
                confidence=f"{content_analysis.confidence_score:.2f}",
            )

            # 5. إذا لم يكن المحتوى آمناً، استخدم البديل الآمن
            final_text = transcribed_text
            if not content_analysis.is_safe and content_analysis.safe_alternative:
                final_text = content_analysis.safe_alternative
                self.logger.warning(
                    "⚠️ Using safe alternative content",
                    child_id=child_id,
                    original_length=len(transcribed_text),
                    safe_length=len(final_text),
                )

            # 6. توليد الاستجابة الذكية
            if content_analysis.is_safe or content_analysis.safe_alternative:
                child_request = ChildRequest(
                    text=final_text,
                    child_id=child_id,
                    child_age=child_profile.get("age", 7),
                    child_profile=child_profile,
                    emotion_state=self._extract_emotion_from_audio(audio_result),
                    conversation_history=conversation_history,
                    complexity=self._determine_complexity_level(child_profile),
                    safety_level=child_profile.get("safety_level", 5),
                    session_context=session_context or {},
                )

                ai_response = await self.ai_orchestrator.generate_intelligent_response(child_request)

                self.logger.info(
                    "🧠 AI response generated",
                    child_id=child_id,
                    model_used=ai_response.get("model_used", "unknown"),
                    quality_score=ai_response.get("quality_score", 0),
                    response_length=len(ai_response.get("content", "")),
                )
            else:
                # استجابة احتياطية آمنة
                ai_response = {
                    "content": "عذراً، لم أفهم جيداً. هل يمكنك المحاولة مرة أخرى؟",
                    "model_used": "safety_fallback",
                    "quality_score": 0.5,
                    "response_metadata": {"is_fallback": True},
                }

            # 7. فحص أمان الاستجابة أيضاً
            response_safety = await self.content_filter.comprehensive_safety_check(
                content=ai_response.get("content", ""), child_age=child_profile.get("age", 7)
            )

            if not response_safety.is_safe:
                ai_response["content"] = response_safety.safe_alternative or "دعنا نتحدث عن شيء آخر جميل!"
                self.logger.warning("⚠️ AI response was filtered for safety", child_id=child_id)

            # 8. تحديث الجلسة
            session_updated = await self._update_session(session, audio_result, content_analysis, ai_response)

            # 9. تحديد ما إذا كان يتطلب إشعار الوالدين
            parent_notification_sent = await self._handle_parent_notification(child_id, content_analysis, session)

            # 10. توليد التوصيات
            recommendations = await self._generate_interaction_recommendations(
                session, audio_result, content_analysis, ai_response
            )

            # 11. تحديث الإحصائيات
            processing_time = (time.time() - start_time) * 1000
            await self._update_service_stats(processing_time, content_analysis, ai_response)

            # 12. إنشاء الاستجابة النهائية
            interaction_response = InteractionResponse(
                audio_processing_result=audio_result,
                content_analysis_result=content_analysis,
                ai_response=ai_response,
                safety_check_passed=content_analysis.is_safe,
                processing_time_ms=processing_time,
                session_updated=session_updated,
                parent_notification_sent=parent_notification_sent,
                recommendations=recommendations,
            )

            self.logger.info(
                "✅ Child interaction completed successfully",
                child_id=child_id,
                total_time=f"{processing_time:.1f}ms",
                safety_passed=content_analysis.is_safe,
                interaction_count=session.interaction_count,
            )

            return interaction_response

        except Exception as e:
            self.logger.error(
                "❌ Child interaction failed",
                child_id=child_id,
                error=str(e),
                processing_time=f"{(time.time() - start_time) * 1000:.1f}ms",
            )

            # إرجاع استجابة احتياطية آمنة
            return await self._generate_emergency_response(child_id, child_profile)

    async def _get_or_create_session(self, child_id: str, child_profile: Dict[str, Any]) -> ChildSession:
        """إنشاء أو استرجاع جلسة الطفل"""

        if child_id not in self.active_sessions:
            session = ChildSession(
                child_id=child_id,
                child_name=child_profile.get("name", f"طفل_{child_id[:8]}"),
                child_age=child_profile.get("age", 7),
                session_start=time.time(),
            )
            self.active_sessions[child_id] = session
            self.service_stats["unique_children"] = len(self.active_sessions)

            self.logger.info(
                "👶 New child session created",
                child_id=child_id,
                child_name=session.child_name,
                child_age=session.child_age,
            )

        return self.active_sessions[child_id]

    async def _transcribe_audio(self, audio_result: AudioProcessingResult) -> str:
        """تحويل الصوت إلى نص (محاكاة)"""

        # في التطبيق الحقيقي، هنا سيتم استخدام Whisper أو خدمة STT
        await asyncio.sleep(0.1)  # محاكاة زمن المعالجة

        # استجابة تجريبية بناءً على خصائص الصوت
        if audio_result.voice_activity_score < 0.3:
            return "..."  # صمت أو صوت غير واضح
        elif audio_result.emotion_features.get("energy", 0) > 0.8:
            return "أريد أن ألعب!"
        elif "pitch_mean" in audio_result.emotion_features:
            return "مرحبا دبدوب، كيف حالك؟"
        else:
            return "أريد أن أتعلم شيئاً جديداً"

    def _extract_emotion_from_audio(self, audio_result: AudioProcessingResult) -> str:
        """استخراج الحالة العاطفية من نتيجة الصوت"""

        features = audio_result.emotion_features

        if not features:
            return "neutral"

        energy = features.get("energy", 0.5)
        zcr = features.get("zero_crossing_rate", 0.1)

        if energy > 0.8 and zcr > 0.15:
            return "excited"
        elif energy < 0.3:
            return "sad"
        elif energy > 0.6:
            return "happy"
        elif zcr > 0.2:
            return "nervous"
        else:
            return "calm"

    def _determine_complexity_level(self, child_profile: Dict[str, Any]) -> ModelComplexity:
        """تحديد مستوى تعقيد المودل المناسب"""

        age = child_profile.get("age", 7)
        interests = child_profile.get("interests", [])

        if age < 6:
            return ModelComplexity.SIMPLE
        elif age < 10 and "science" not in interests:
            return ModelComplexity.MEDIUM
        else:
            return ModelComplexity.COMPLEX

    async def _update_session(
        self,
        session: ChildSession,
        audio_result: AudioProcessingResult,
        content_analysis: ContentAnalysisResult,
        ai_response: Dict[str, Any],
    ) -> bool:
        """تحديث بيانات الجلسة"""

        try:
            session.interaction_count += 1
            session.total_processing_time += audio_result.processing_time_ms

            # تحديث تاريخ المزاج
            emotion = self._extract_emotion_from_audio(audio_result)
            session.mood_history.append(emotion)
            if len(session.mood_history) > 20:  # الاحتفاظ بآخر 20 حالة فقط
                session.mood_history = session.mood_history[-20:]

            # تحديث المواضيع المناقشة
            if content_analysis.content_category:
                category = content_analysis.content_category.value
                if category not in session.topics_discussed:
                    session.topics_discussed.append(category)

            # تسجيل انتهاكات الأمان
            if content_analysis.violations:
                for violation in content_analysis.violations:
                    session.safety_violations.append(
                        {
                            "type": violation.violation_type,
                            "severity": violation.severity.value,
                            "timestamp": violation.timestamp,
                            "description": violation.description,
                        }
                    )

            # تحديث التقدم التعليمي
            if content_analysis.content_category.value == "educational":
                request_type = ai_response.get("response_metadata", {}).get("request_type")
                if request_type:
                    if request_type.value not in session.educational_progress:
                        session.educational_progress[request_type.value] = 0
                    session.educational_progress[request_type.value] += 1

            return True

        except Exception as e:
            self.logger.error(f"❌ Session update failed: {e}")
            return False

    async def _handle_parent_notification(
        self, child_id: str, content_analysis: ContentAnalysisResult, session: ChildSession
    ) -> bool:
        """التعامل مع إشعارات الوالدين"""

        try:
            if content_analysis.parent_notification_required:
                # في التطبيق الحقيقي، هنا سيتم إرسال إشعار فعلي
                notification_data = {
                    "child_id": child_id,
                    "child_name": session.child_name,
                    "risk_level": content_analysis.risk_level.value,
                    "violations": [v.description for v in content_analysis.violations],
                    "timestamp": time.time(),
                    "recommendations": content_analysis.safety_recommendations,
                }

                self.logger.warning(
                    "📧 Parent notification required", child_id=child_id, notification_data=notification_data
                )

                # محاكاة إرسال الإشعار
                await asyncio.sleep(0.05)
                return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Parent notification failed: {e}")
            return False

    async def _generate_interaction_recommendations(
        self,
        session: ChildSession,
        audio_result: AudioProcessingResult,
        content_analysis: ContentAnalysisResult,
        ai_response: Dict[str, Any],
    ) -> List[str]:
        """توليد توصيات للتفاعل"""

        recommendations = []

        # توصيات بناءً على جودة الصوت
        if audio_result.quality_score < 0.5:
            recommendations.append("تحسين جودة الصوت - قرّب المايك أو قلّل الضوضاء")

        # توصيات بناءً على النشاط الصوتي
        if audio_result.voice_activity_score < 0.3:
            recommendations.append("شجّع الطفل على التحدث بوضوح أكبر")

        # توصيات بناءً على الأمان
        if content_analysis.safety_recommendations:
            recommendations.extend(content_analysis.safety_recommendations)

        # توصيات بناءً على التقدم التعليمي
        if session.educational_progress:
            total_educational = sum(session.educational_progress.values())
            if total_educational < session.interaction_count * 0.3:
                recommendations.append("اقترح أنشطة تعليمية أكثر")

        # توصيات بناءً على المزاج
        if session.mood_history:
            recent_moods = session.mood_history[-5:]
            if recent_moods.count("sad") >= 3:
                recommendations.append("الطفل يبدو حزيناً - فكر في أنشطة مرحة")
            elif recent_moods.count("excited") >= 4:
                recommendations.append("الطفل متحمس جداً - ساعده على التهدئة")

        # توصيات بناءً على مدة الجلسة
        session_duration = time.time() - session.session_start
        if session_duration > 1800:  # 30 دقيقة
            recommendations.append("استراحة مقترحة - الجلسة طويلة")

        return recommendations

    async def _update_service_stats(
        self, processing_time: float, content_analysis: ContentAnalysisResult, ai_response: Dict[str, Any]
    ):
        """تحديث إحصائيات الخدمة"""

        if content_analysis.is_safe:
            self.service_stats["successful_interactions"] += 1
        else:
            self.service_stats["blocked_interactions"] += 1

        if content_analysis.violations:
            self.service_stats["safety_violations"] += len(content_analysis.violations)

        if content_analysis.content_category.value == "educational":
            self.service_stats["educational_interactions"] += 1

        # تحديث متوسط زمن الاستجابة
        total_interactions = self.service_stats["total_interactions"]
        current_avg = self.service_stats["average_response_time"]
        new_avg = ((current_avg * (total_interactions - 1)) + processing_time) / total_interactions
        self.service_stats["average_response_time"] = new_avg

    async def _generate_emergency_response(self, child_id: str, child_profile: Dict[str, Any]) -> InteractionResponse:
        """توليد استجابة طوارئ آمنة"""

        # استجابة طوارئ آمنة
        emergency_audio_result = AudioProcessingResult(
            processed_audio=np.array([]),
            original_audio=np.array([]),
            noise_level=1.0,
            voice_activity_score=0.0,
            emotion_features={},
            processing_time_ms=0.0,
            quality_score=0.0,
            confidence=0.0,
        )

        from src.infrastructure.security.advanced_content_filter import (
            ContentAnalysisResult,
            ContentCategory,
            RiskLevel,
            SafetyViolation,
        )

        emergency_content_analysis = ContentAnalysisResult(
            is_safe=False,
            risk_level=RiskLevel.CRITICAL,
            confidence_score=1.0,
            content_category=ContentCategory.INAPPROPRIATE,
            violations=[
                SafetyViolation(
                    violation_type="system_error",
                    severity=RiskLevel.CRITICAL,
                    description="خطأ في النظام - تفعيل الوضع الآمن",
                    content_excerpt="emergency",
                )
            ],
            modifications=["تفعيل وضع الطوارئ"],
            safe_alternative="عذراً، أواجه مشكلة تقنية. هل يمكنك المحاولة مرة أخرى؟",
            safety_recommendations=["إعادة تشغيل النظام", "فحص الاتصال"],
            parent_notification_required=True,
            processing_time_ms=1.0,
        )

        emergency_ai_response = {
            "content": "عذراً، أواجه مشكلة تقنية صغيرة. دعني أعيد المحاولة!",
            "model_used": "emergency_fallback",
            "quality_score": 0.7,
            "response_metadata": {"is_emergency": True, "timestamp": time.time()},
        }

        return InteractionResponse(
            audio_processing_result=emergency_audio_result,
            content_analysis_result=emergency_content_analysis,
            ai_response=emergency_ai_response,
            safety_check_passed=False,
            processing_time_ms=1.0,
            session_updated=False,
            parent_notification_sent=True,
            recommendations=["إعادة تشغيل التطبيق", "فحص الاتصال بالإنترنت"],
        )

    def get_session_summary(self, child_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على ملخص الجلسة"""

        if child_id not in self.active_sessions:
            return None

        session = self.active_sessions[child_id]

        return {
            "child_info": {"id": session.child_id, "name": session.child_name, "age": session.child_age},
            "session_stats": {
                "duration_minutes": (time.time() - session.session_start) / 60,
                "interaction_count": session.interaction_count,
                "average_processing_time": (session.total_processing_time / max(1, session.interaction_count)),
                "topics_discussed": session.topics_discussed,
                "educational_progress": session.educational_progress,
            },
            "mood_analysis": {
                "mood_history": session.mood_history,
                "current_mood": session.mood_history[-1] if session.mood_history else "unknown",
                "mood_stability": self._calculate_mood_stability(session.mood_history),
            },
            "safety_summary": {
                "total_violations": len(session.safety_violations),
                "violation_types": list(set(v["type"] for v in session.safety_violations)),
                "last_violation": session.safety_violations[-1] if session.safety_violations else None,
            },
        }

    def _calculate_mood_stability(self, mood_history: List[str]) -> float:
        """حساب استقرار المزاج"""

        if len(mood_history) < 2:
            return 1.0

        changes = 0
        for i in range(1, len(mood_history)):
            if mood_history[i] != mood_history[i - 1]:
                changes += 1

        stability = 1.0 - (changes / (len(mood_history) - 1))
        return stability

    def get_service_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الخدمة الشاملة"""

        # إحصائيات من المكونات الفرعية
        audio_stats = self.audio_processor.get_performance_stats()
        ai_stats = asyncio.create_task(self.ai_orchestrator.get_performance_report())
        filter_stats = self.content_filter.get_filter_statistics()

        return {
            "service_stats": self.service_stats,
            "component_stats": {
                "audio_processor": audio_stats,
                "content_filter": filter_stats,
                "active_sessions": len(self.active_sessions),
            },
            "performance_metrics": {
                "success_rate": (
                    self.service_stats["successful_interactions"] / max(1, self.service_stats["total_interactions"])
                )
                * 100,
                "safety_rate": (
                    (self.service_stats["total_interactions"] - self.service_stats["safety_violations"])
                    / max(1, self.service_stats["total_interactions"])
                )
                * 100,
                "educational_rate": (
                    self.service_stats["educational_interactions"] / max(1, self.service_stats["total_interactions"])
                )
                * 100,
            },
        }

    async def cleanup(self):
        """تنظيف موارد الخدمة"""
        try:
            # حفظ بيانات الجلسات إذا لزم الأمر
            for child_id, session in self.active_sessions.items():
                self.logger.info(
                    "💾 Saving session data",
                    child_id=child_id,
                    interaction_count=session.interaction_count,
                    duration_minutes=(time.time() - session.session_start) / 60,
                )

            # مسح الجلسات النشطة
            self.active_sessions.clear()

            self.logger.info("✅ Enhanced Child Interaction Service cleanup completed")

        except Exception as e:
            self.logger.error(f"❌ Service cleanup failed: {e}")


def create_enhanced_child_interaction_service(
    audio_processor: EnhancedAudioProcessor,
    ai_orchestrator: AdvancedAIOrchestrator,
    content_filter: AdvancedContentFilter,
) -> EnhancedChildInteractionService:
    """إنشاء خدمة تفاعل طفل محسنة"""
    return EnhancedChildInteractionService(
        audio_processor=audio_processor, ai_orchestrator=ai_orchestrator, content_filter=content_filter
    )
