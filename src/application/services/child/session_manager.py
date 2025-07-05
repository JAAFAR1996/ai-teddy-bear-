from typing import Any, Dict
import time
import structlog

from .enhanced_child_interaction_service import ChildSession, AudioProcessingResult, ContentAnalysisResult

logger = structlog.get_logger(__name__)


class SessionManager:
    """Manages child interaction sessions."""

    def __init__(self):
        self.active_sessions: Dict[str, "ChildSession"] = {}
        self.service_stats = {"unique_children": 0}

    async def get_or_create(
        self, child_id: str, child_profile: Dict[str, Any]
    ) -> "ChildSession":
        """Get or create a session for a child."""
        if child_id not in self.active_sessions:
            session = ChildSession(
                child_id=child_id,
                child_name=child_profile.get("name", f"طفل_{child_id[:8]}"),
                child_age=child_profile.get("age", 7),
                session_start=time.time(),
            )
            self.active_sessions[child_id] = session
            self.service_stats["unique_children"] = len(self.active_sessions)
            logger.info("👶 New child session created",
                        child_id=child_id, child_name=session.child_name)
        return self.active_sessions[child_id]

    async def update(
        self,
        session: "ChildSession",
        audio_result: "AudioProcessingResult",
        content_analysis: "ContentAnalysisResult",
        ai_response: Dict[str, Any],
    ) -> bool:
        """Update the session with new interaction data."""
        try:
            session.interaction_count += 1
            session.total_processing_time += audio_result.processing_time_ms

            emotion = self._extract_emotion_from_audio(audio_result)
            session.mood_history.append(emotion)
            if len(session.mood_history) > 20:
                session.mood_history.pop(0)

            if content_analysis.content_category and content_analysis.content_category.value not in session.topics_discussed:
                session.topics_discussed.append(
                    content_analysis.content_category.value)

            if content_analysis.violations:
                for violation in content_analysis.violations:
                    session.safety_violations.append({
                        "type": violation.violation_type,
                        "severity": violation.severity.value,
                        "timestamp": violation.timestamp,
                        "description": violation.description,
                    })

            if content_analysis.content_category.value == "educational":
                request_type = ai_response.get(
                    "response_metadata", {}).get("request_type")
                if request_type:
                    session.educational_progress.setdefault(
                        request_type.value, 0)
                    session.educational_progress[request_type.value] += 1
            return True
        except Exception as e:
            logger.error(f"❌ Session update failed: {e}")
            return False

    def _extract_emotion_from_audio(self, audio_result: "AudioProcessingResult") -> str:
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

    def get_summary(self, child_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of the child's session."""
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

    def _calculate_mood_stability(self, mood_history: list[str]) -> float:
        """Calculate mood stability."""
        if len(mood_history) < 2:
            return 1.0
        changes = sum(1 for i in range(1, len(mood_history))
                      if mood_history[i] != mood_history[i - 1])
        return 1.0 - (changes / (len(mood_history) - 1))

    async def cleanup(self):
        """Cleanup session resources."""
        for child_id, session in self.active_sessions.items():
            logger.info("💾 Saving session data", child_id=child_id,
                        interaction_count=session.interaction_count)
        self.active_sessions.clear()
        logger.info("✅ Session Manager cleanup completed")
