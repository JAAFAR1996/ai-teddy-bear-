from datetime import datetime
from typing import Dict, List, Optional, Any

from ....domain.entities import Child, Conversation
from ....domain.value_objects import VoiceProfile


class VoiceProfileRecommender:
    """Recommends voice profile adjustments for a child."""

    def recommend_adjustments(
        self, child: Child, recent_conversations: List[Conversation]
    ) -> Optional[VoiceProfile]:
        """
        Analyze child's interaction patterns and recommend voice profile adjustments
        for better engagement and age-appropriate communication.
        """
        if not child.voice_profile:
            return VoiceProfile.create_default(child.age)

        current_profile = child.voice_profile
        avg_engagement, emotional_patterns = self._analyze_voice_adjustment_needs(
            child, recent_conversations
        )
        pitch_adjustment, speed_adjustment, emotion_sensitivity_adjustment = (
            self._calculate_voice_adjustments(
                avg_engagement, emotional_patterns)
        )
        return self._apply_voice_adjustments(
            current_profile, pitch_adjustment, speed_adjustment, emotion_sensitivity_adjustment
        )

    def _analyze_voice_adjustment_needs(
        self, child: Child, recent_conversations: List[Conversation]
    ) -> tuple[float, Dict[str, float]]:
        """Analyze engagement patterns and emotional responses for voice adjustments."""
        avg_engagement = self._calculate_average_engagement(
            recent_conversations)
        emotional_patterns = self._analyze_emotional_response_patterns(
            child.emotional_state_history)
        return avg_engagement, emotional_patterns

    def _calculate_voice_adjustments(
        self, avg_engagement: float, emotional_patterns: Dict[str, float]
    ) -> tuple[float, float, float]:
        """Calculate specific voice adjustments based on patterns."""
        pitch_adjustment = 0.0
        speed_adjustment = 0.0
        emotion_sensitivity_adjustment = 0.0

        if avg_engagement < 0.6:
            pitch_adjustment += 0.1
            speed_adjustment += 0.05
            emotion_sensitivity_adjustment += 0.1
        elif avg_engagement > 0.9:
            pitch_adjustment -= 0.05
            speed_adjustment -= 0.03

        if "frustrated" in emotional_patterns and emotional_patterns["frustrated"] > 0.3:
            pitch_adjustment -= 0.1
            speed_adjustment -= 0.1
            emotion_sensitivity_adjustment += 0.15
        if "excited" in emotional_patterns and emotional_patterns["excited"] > 0.7:
            pitch_adjustment -= 0.05
            speed_adjustment -= 0.05
        return pitch_adjustment, speed_adjustment, emotion_sensitivity_adjustment

    def _apply_voice_adjustments(
        self,
        current_profile: VoiceProfile,
        pitch_adjustment: float,
        speed_adjustment: float,
        emotion_sensitivity_adjustment: float,
    ) -> Optional[VoiceProfile]:
        """Apply adjustments and create new voice profile if changes are significant."""
        new_pitch = max(
            0.5, min(2.0, current_profile.pitch + pitch_adjustment))
        new_speed = max(
            0.5, min(2.0, current_profile.speed + speed_adjustment))
        new_emotion_sensitivity = max(
            0.1, min(1.0, current_profile.emotion_sensitivity +
                     emotion_sensitivity_adjustment)
        )

        if (
            abs(new_pitch - current_profile.pitch) > 0.05
            or abs(new_speed - current_profile.speed) > 0.03
            or abs(new_emotion_sensitivity - current_profile.emotion_sensitivity) > 0.05
        ):
            return current_profile.__class__(
                pitch=new_pitch,
                speed=new_speed,
                volume=current_profile.volume,
                emotion_baseline=current_profile.emotion_baseline,
                emotion_sensitivity=new_emotion_sensitivity,
                voice_gender=current_profile.voice_gender,
                language_accent=current_profile.language_accent,
                response_style=current_profile.response_style,
                complexity_level=current_profile.complexity_level,
                voice_model_version=current_profile.voice_model_version,
                last_calibrated=datetime.utcnow().isoformat(),
            )
        return None

    def _calculate_average_engagement(self, conversations: List[Conversation]) -> float:
        """Calculate average engagement score from conversations."""
        if not conversations:
            return 0.5
        engagement_scores = [
            conv.child_engagement_score for conv in conversations]
        return sum(engagement_scores) / len(engagement_scores)

    def _analyze_emotional_response_patterns(
        self, emotion_history: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Analyze patterns in emotional responses."""
        if not emotion_history:
            return {}
        emotion_counts = {}
        total_entries = len(emotion_history)
        for entry in emotion_history:
            emotion = entry["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        return {emotion: count / total_entries for emotion, count in emotion_counts.items()}
