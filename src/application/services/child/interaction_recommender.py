from typing import Any, Dict, List
import time

from .enhanced_child_interaction_service import ChildSession, AudioProcessingResult, ContentAnalysisResult


class InteractionRecommender:
    """Generates recommendations for child interactions."""

    async def generate(
        self,
        session: "ChildSession",
        audio_result: "AudioProcessingResult",
        content_analysis: "ContentAnalysisResult",
        ai_response: Dict[str, Any],
    ) -> List[str]:
        """Generate recommendations for the interaction."""
        recommendations = []
        if audio_result.quality_score < 0.5:
            recommendations.append(
                "تحسين جودة الصوت - قرّب المايك أو قلّل الضوضاء")
        if audio_result.voice_activity_score < 0.3:
            recommendations.append("شجّع الطفل على التحدث بوضوح أكبر")
        if content_analysis.safety_recommendations:
            recommendations.extend(content_analysis.safety_recommendations)
        if session.educational_progress:
            total_educational = sum(session.educational_progress.values())
            if total_educational < session.interaction_count * 0.3:
                recommendations.append("اقترح أنشطة تعليمية أكثر")
        if session.mood_history:
            recent_moods = session.mood_history[-5:]
            if recent_moods.count("sad") >= 3:
                recommendations.append("الطفل يبدو حزيناً - فكر في أنشطة مرحة")
            elif recent_moods.count("excited") >= 4:
                recommendations.append("الطفل متحمس جداً - ساعده على التهدئة")
        session_duration = time.time() - session.session_start
        if session_duration > 1800:
            recommendations.append("استراحة مقترحة - الجلسة طويلة")
        return recommendations
