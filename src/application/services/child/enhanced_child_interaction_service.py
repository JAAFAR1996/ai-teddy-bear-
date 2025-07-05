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
    AudioProcessingResult,
    EnhancedAudioProcessor,
)
from src.infrastructure.security.advanced_content_filter import (
    AdvancedContentFilter,
    ContentAnalysisResult,
)
from .session_manager import SessionManager
from .parent_notifier import ParentNotifier
from .interaction_recommender import InteractionRecommender

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
    Orchestrates the child interaction process by delegating to specialized services.
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
        self.session_manager = SessionManager()
        self.parent_notifier = ParentNotifier()
        self.recommender = InteractionRecommender()
        self.logger = structlog.get_logger(__name__)
        self.service_stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "blocked_interactions": 0,
            "average_response_time": 0.0,
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
        """Process a comprehensive child interaction."""
        start_time = time.time()
        self.service_stats["total_interactions"] += 1

        try:
            session = await self.session_manager.get_or_create(child_id, child_profile)
            audio_result = await self.audio_processor.process_audio_stream(
                audio_stream=audio_stream,
                child_context={"child_id": child_id,
                               "age": child_profile.get("age", 7)},
            )
            transcribed_text = await self._transcribe_audio(audio_result)
            content_analysis = await self.content_filter.comprehensive_safety_check(
                content=transcribed_text,
                child_age=child_profile.get("age", 7),
                context={"child_id": child_id,
                         "session_history": conversation_history},
            )
            final_text = content_analysis.safe_alternative if not content_analysis.is_safe else transcribed_text

            ai_response = await self._get_ai_response(final_text, child_id, child_profile, audio_result, conversation_history, session_context, content_analysis)

            response_safety = await self.content_filter.comprehensive_safety_check(content=ai_response.get("content", ""), child_age=child_profile.get("age", 7))
            if not response_safety.is_safe:
                ai_response["content"] = response_safety.safe_alternative or "دعنا نتحدث عن شيء آخر جميل!"

            session_updated = await self.session_manager.update(session, audio_result, content_analysis, ai_response)
            parent_notification_sent = await self.parent_notifier.handle_notification(child_id, content_analysis, session)
            recommendations = await self.recommender.generate(session, audio_result, content_analysis, ai_response)

            processing_time = (time.time() - start_time) * 1000
            await self._update_service_stats(processing_time, content_analysis)

            return InteractionResponse(
                audio_processing_result=audio_result,
                content_analysis_result=content_analysis,
                ai_response=ai_response,
                safety_check_passed=content_analysis.is_safe,
                processing_time_ms=processing_time,
                session_updated=session_updated,
                parent_notification_sent=parent_notification_sent,
                recommendations=recommendations,
            )
        except Exception as e:
            self.logger.error("❌ Child interaction failed",
                              child_id=child_id, error=str(e))
            return await self._generate_emergency_response()

    async def _get_ai_response(
        self, text: str, child_id: str, child_profile: Dict[str, Any], audio_result: AudioProcessingResult,
        conversation_history: List[Dict[str, str]], session_context: Optional[Dict[str, Any]],
        content_analysis: ContentAnalysisResult
    ) -> Dict[str, Any]:
        if content_analysis.is_safe or content_analysis.safe_alternative:
            child_request = ChildRequest(
                text=text,
                child_id=child_id,
                child_age=child_profile.get("age", 7),
                child_profile=child_profile,
                emotion_state=self._extract_emotion_from_audio(audio_result),
                conversation_history=conversation_history,
                complexity=self._determine_complexity_level(child_profile),
                safety_level=child_profile.get("safety_level", 5),
                session_context=session_context or {},
            )
            return await self.ai_orchestrator.generate_intelligent_response(child_request)
        else:
            return {
                "content": "عذراً، لم أفهم جيداً. هل يمكنك المحاولة مرة أخرى؟",
                "model_used": "safety_fallback",
                "quality_score": 0.5,
                "response_metadata": {"is_fallback": True},
            }

    async def _transcribe_audio(self, audio_result: AudioProcessingResult) -> str:
        """Transcribe audio to text (mock implementation)."""
        await asyncio.sleep(0.1)
        if audio_result.voice_activity_score < 0.3:
            return "..."
        elif audio_result.emotion_features.get("energy", 0) > 0.8:
            return "أريد أن ألعب!"
        return "مرحبا دبدوب، كيف حالك؟"

    def _extract_emotion_from_audio(self, audio_result: AudioProcessingResult) -> str:
        """Extract emotion from audio processing result."""
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
        """Determine the appropriate model complexity level."""
        age = child_profile.get("age", 7)
        if age < 6:
            return ModelComplexity.SIMPLE
        elif age < 10 and "science" not in child_profile.get("interests", []):
            return ModelComplexity.MEDIUM
        else:
            return ModelComplexity.COMPLEX

    async def _update_service_stats(self, processing_time: float, content_analysis: ContentAnalysisResult):
        """Update the service's internal statistics."""
        if content_analysis.is_safe:
            self.service_stats["successful_interactions"] += 1
        else:
            self.service_stats["blocked_interactions"] += 1
        if content_analysis.violations:
            self.service_stats["safety_violations"] += len(
                content_analysis.violations)
        if content_analysis.content_category.value == "educational":
            self.service_stats["educational_interactions"] += 1

        total_interactions = self.service_stats["total_interactions"]
        current_avg = self.service_stats["average_response_time"]
        new_avg = ((current_avg * (total_interactions - 1)) +
                   processing_time) / total_interactions
        self.service_stats["average_response_time"] = new_avg

    async def _generate_emergency_response(self) -> InteractionResponse:
        """Generate a safe, emergency fallback response."""
        return InteractionResponse(
            audio_processing_result=AudioProcessingResult(processed_audio=np.array([]), original_audio=np.array(
                []), noise_level=1.0, voice_activity_score=0.0, emotion_features={}, processing_time_ms=0.0, quality_score=0.0, confidence=0.0),
            content_analysis_result=ContentAnalysisResult(is_safe=False, risk_level="critical", confidence_score=1.0, content_category="inappropriate", violations=[], modifications=[
            ], safe_alternative="عذراً، أواجه مشكلة تقنية. هل يمكنك المحاولة مرة أخرى؟", safety_recommendations=[], parent_notification_required=True, processing_time_ms=1.0),
            ai_response={"content": "عذراً، أواجه مشكلة تقنية صغيرة. دعني أعيد المحاولة!",
                         "model_used": "emergency_fallback", "quality_score": 0.7},
            safety_check_passed=False,
            processing_time_ms=1.0,
            session_updated=False,
            parent_notification_sent=True,
            recommendations=["إعادة تشغيل التطبيق", "فحص الاتصال بالإنترنت"],
        )

    def get_session_summary(self, child_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a child's session."""
        return self.session_manager.get_summary(child_id)

    def get_service_statistics(self) -> Dict[str, Any]:
        """Get overall service statistics."""
        return {
            "service_stats": self.service_stats,
            "component_stats": {
                "audio_processor": self.audio_processor.get_performance_stats(),
                "content_filter": self.content_filter.get_filter_statistics(),
                "active_sessions": len(self.session_manager.active_sessions),
            },
        }

    async def cleanup(self):
        """Clean up service resources."""
        await self.session_manager.cleanup()
        self.logger.info(
            "✅ Enhanced Child Interaction Service cleanup completed")


def create_enhanced_child_interaction_service(
    audio_processor: EnhancedAudioProcessor,
    ai_orchestrator: AdvancedAIOrchestrator,
    content_filter: AdvancedContentFilter,
) -> EnhancedChildInteractionService:
    """إنشاء خدمة تفاعل طفل محسنة"""
    return EnhancedChildInteractionService(
        audio_processor=audio_processor,
        ai_orchestrator=ai_orchestrator,
        content_filter=content_filter,
    )
