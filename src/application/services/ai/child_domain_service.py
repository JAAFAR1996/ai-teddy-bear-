"""
🏗️ Child Domain Service
========================

Domain service for complex child-related business operations that don't
naturally belong to a single aggregate or entity.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..aggregates.child_aggregate import ConversationLimitExceeded, SafetyViolation
from ..entities import Child, Conversation
from ..value_objects import SafetySettings, VoiceProfile


@dataclass
class ConversationCompatibilityResult:
    """Result of conversation compatibility check"""

    is_compatible: bool
    compatibility_score: float  # 0.0 to 1.0
    recommendations: List[str]
    blocking_issues: List[str]


@dataclass
class SafetyAssessmentResult:
    """Result of comprehensive safety assessment"""

    overall_safety_score: float  # 0.0 to 1.0
    risk_factors: List[str]
    protective_factors: List[str]
    recommendations: List[str]
    requires_parent_review: bool


class ChildDomainService:
    """
    Domain service providing complex business operations for Child management.

    This service handles operations that involve multiple aggregates or
    complex domain logic that doesn't belong to a single entity.
    """

    def assess_conversation_compatibility(
        self, child: Child, proposed_topic: str, conversation_history: List[Conversation]
    ) -> ConversationCompatibilityResult:
        """
        Assess if a proposed conversation topic is compatible with
        the child's profile, history, and current state.
        """

        compatibility_score = 1.0
        recommendations = []
        blocking_issues = []

        # Check safety settings compatibility
        if not child.safety_settings.is_topic_allowed(proposed_topic):
            blocking_issues.append(f"Topic '{proposed_topic}' is blocked by safety settings")
            compatibility_score = 0.0

        # Check age appropriateness
        age_appropriate_score = self._assess_topic_age_appropriateness(proposed_topic, child.age)
        compatibility_score *= age_appropriate_score

        if age_appropriate_score < 0.7:
            recommendations.append(f"Consider simplifying topic for age {child.age}")

        # Check conversation history patterns
        history_score = self._analyze_conversation_history_compatibility(proposed_topic, conversation_history)
        compatibility_score *= history_score

        if history_score < 0.8:
            recommendations.append("Topic may be repetitive based on recent conversations")

        # Check current emotional state
        if child.emotional_state_history:
            recent_emotion = child.emotional_state_history[-1]
            emotion_compatibility = self._assess_emotional_compatibility(proposed_topic, recent_emotion["emotion"])
            compatibility_score *= emotion_compatibility

            if emotion_compatibility < 0.6:
                recommendations.append(f"Consider child's current emotional state: {recent_emotion['emotion']}")

        # Check time of day appropriateness
        current_time = datetime.utcnow()
        time_score = self._assess_time_appropriateness(proposed_topic, current_time)
        compatibility_score *= time_score

        if time_score < 0.8:
            recommendations.append("Topic may not be appropriate for current time")

        return ConversationCompatibilityResult(
            is_compatible=compatibility_score >= 0.6 and len(blocking_issues) == 0,
            compatibility_score=compatibility_score,
            recommendations=recommendations,
            blocking_issues=blocking_issues,
        )

    def conduct_comprehensive_safety_assessment(
        self, child: Child, recent_conversations: List[Conversation], parent_feedback: Optional[Dict[str, Any]] = None
    ) -> SafetyAssessmentResult:
        """
        Conduct a comprehensive safety assessment for a child based on
        their profile, recent activity, and parent feedback.
        """

        risk_factors = []
        protective_factors = []
        recommendations = []
        overall_safety_score = 1.0

        # Assess safety violations
        if child.safety_violations_count > 0:
            violation_impact = min(0.3, child.safety_violations_count * 0.1)
            overall_safety_score -= violation_impact
            risk_factors.append(f"{child.safety_violations_count} safety violations detected")

            if child.safety_violations_count >= 3:
                recommendations.append("Consider reviewing and updating safety settings")
        else:
            protective_factors.append("No safety violations in recent activity")

        # Assess conversation patterns
        conversation_safety_score = self._assess_conversation_patterns_safety(recent_conversations)
        overall_safety_score *= conversation_safety_score

        if conversation_safety_score < 0.8:
            risk_factors.append("Concerning patterns detected in recent conversations")
            recommendations.append("Review recent conversation transcripts")
        else:
            protective_factors.append("Healthy conversation patterns observed")

        # Assess emotional stability
        emotion_stability_score = self._assess_emotional_stability(child)
        overall_safety_score *= emotion_stability_score

        if emotion_stability_score < 0.7:
            risk_factors.append("Emotional instability indicators detected")
            recommendations.append("Consider emotional support or counseling")
        else:
            protective_factors.append("Stable emotional patterns observed")

        # Assess usage patterns
        usage_safety_score = self._assess_usage_patterns_safety(child)
        overall_safety_score *= usage_safety_score

        if usage_safety_score < 0.8:
            risk_factors.append("Potentially concerning usage patterns")
            recommendations.append("Review time limits and usage restrictions")
        else:
            protective_factors.append("Healthy usage patterns maintained")

        # Check parent involvement
        if parent_feedback:
            parent_involvement_score = self._assess_parent_involvement(parent_feedback)
            overall_safety_score *= parent_involvement_score

            if parent_involvement_score > 0.8:
                protective_factors.append("Strong parent involvement and oversight")
            else:
                recommendations.append("Encourage more parent involvement and oversight")

        # Determine if parent review is required
        requires_parent_review = (
            overall_safety_score < 0.7 or child.safety_violations_count >= 2 or child.escalation_count > 0
        )

        if requires_parent_review and "parent review" not in [r.lower() for r in recommendations]:
            recommendations.append("Parent review and approval required")

        return SafetyAssessmentResult(
            overall_safety_score=max(0.0, overall_safety_score),
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            recommendations=recommendations,
            requires_parent_review=requires_parent_review,
        )

    def recommend_voice_profile_adjustments(
        self, child: Child, recent_conversations: List[Conversation]
    ) -> Optional[VoiceProfile]:
        """
        Analyze child's interaction patterns and recommend voice profile adjustments
        for better engagement and age-appropriate communication.
        """

        if not child.voice_profile:
            return VoiceProfile.create_default(child.age)

        current_profile = child.voice_profile

        # Analyze engagement patterns
        avg_engagement = self._calculate_average_engagement(recent_conversations)

        # Analyze emotional responses
        emotional_patterns = self._analyze_emotional_response_patterns(child.emotional_state_history)

        # Determine adjustments needed
        pitch_adjustment = 0.0
        speed_adjustment = 0.0
        emotion_sensitivity_adjustment = 0.0

        # Adjust based on engagement
        if avg_engagement < 0.6:
            # Low engagement - make voice more engaging
            pitch_adjustment += 0.1
            speed_adjustment += 0.05
            emotion_sensitivity_adjustment += 0.1
        elif avg_engagement > 0.9:
            # High engagement - slightly calm down
            pitch_adjustment -= 0.05
            speed_adjustment -= 0.03

        # Adjust based on emotional patterns
        if "frustrated" in emotional_patterns and emotional_patterns["frustrated"] > 0.3:
            # Child shows frustration - make voice calmer
            pitch_adjustment -= 0.1
            speed_adjustment -= 0.1
            emotion_sensitivity_adjustment += 0.15

        if "excited" in emotional_patterns and emotional_patterns["excited"] > 0.7:
            # Child is often excited - balance with slightly calmer voice
            pitch_adjustment -= 0.05
            speed_adjustment -= 0.05

        # Apply adjustments within safe ranges
        new_pitch = max(0.5, min(2.0, current_profile.pitch + pitch_adjustment))
        new_speed = max(0.5, min(2.0, current_profile.speed + speed_adjustment))
        new_emotion_sensitivity = max(
            0.1, min(1.0, current_profile.emotion_sensitivity + emotion_sensitivity_adjustment)
        )

        # Only recommend changes if they're significant
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

        return None  # No significant adjustments needed

    def validate_child_aggregate_consistency(self, child: Child) -> List[str]:
        """
        Validate the consistency of a Child aggregate and return any
        business rule violations or inconsistencies.
        """

        violations = []

        # Check basic profile consistency
        if not child.name or not child.name.strip():
            violations.append("Child name cannot be empty")

        if not 3 <= child.age <= 12:
            violations.append("Child age must be between 3 and 12")

        # Check voice profile age appropriateness
        if child.voice_profile and not child.voice_profile.is_age_appropriate(child.age):
            violations.append("Voice profile complexity not appropriate for child's age")

        # Check safety settings consistency
        if child.safety_settings:
            if child.safety_settings.max_session_minutes > child.safety_settings.max_daily_minutes:
                violations.append("Session time limit cannot exceed daily time limit")

            if child.daily_usage_minutes > child.safety_settings.max_daily_minutes:
                violations.append("Daily usage exceeds allowed limit")

        # Check conversation consistency
        if len(child.active_conversations) > 1:
            violations.append("Child cannot have more than one active conversation")

        for conversation in child.active_conversations:
            if conversation.child_id != child.id:
                violations.append("Active conversation belongs to different child")

            if conversation.status not in ["active", "paused"]:
                violations.append("Active conversation list contains non-active conversation")

        # Check usage tracking consistency
        if child.total_conversations_today < 0:
            violations.append("Daily conversation count cannot be negative")

        if child.daily_usage_minutes < 0:
            violations.append("Daily usage minutes cannot be negative")

        return violations

    def _assess_topic_age_appropriateness(self, topic: str, age: int) -> float:
        """Assess how age-appropriate a topic is (0.0 to 1.0)"""

        topic_lower = topic.lower()

        # Define age-appropriate keywords
        age_appropriateness_map = {
            (3, 4): {
                "high": ["animals", "colors", "shapes", "toys", "family", "food"],
                "medium": ["games", "friends", "school"],
                "low": ["science", "history", "technology"],
                "blocked": ["violence", "scary", "complex"],
            },
            (5, 6): {
                "high": ["animals", "colors", "games", "school", "friends", "toys"],
                "medium": ["science", "art", "music", "sports"],
                "low": ["history", "technology", "emotions"],
                "blocked": ["violence", "scary", "complex relationships"],
            },
            (7, 10): {
                "high": ["science", "animals", "school", "games", "friends", "art", "music"],
                "medium": ["history", "technology", "emotions", "relationships"],
                "low": ["politics", "complex science"],
                "blocked": ["violence", "inappropriate content"],
            },
            (11, 12): {
                "high": ["science", "technology", "history", "friends", "school", "hobbies"],
                "medium": ["emotions", "relationships", "current events"],
                "low": ["politics", "advanced topics"],
                "blocked": ["inappropriate content", "violence"],
            },
        }

        # Find appropriate age range
        age_map = None
        for age_range, keywords in age_appropriateness_map.items():
            if age_range[0] <= age <= age_range[1]:
                age_map = keywords
                break

        if not age_map:
            return 0.5  # Default score

        # Check topic against age-appropriate keywords
        if any(blocked in topic_lower for blocked in age_map["blocked"]):
            return 0.0

        if any(high in topic_lower for high in age_map["high"]):
            return 1.0

        if any(medium in topic_lower for medium in age_map["medium"]):
            return 0.8

        if any(low in topic_lower for low in age_map["low"]):
            return 0.6

        return 0.7  # Default for neutral topics

    def _analyze_conversation_history_compatibility(self, topic: str, conversations: List[Conversation]) -> float:
        """Analyze if topic is compatible with recent conversation history"""

        if not conversations:
            return 1.0

        # Check for topic repetition in recent conversations
        recent_topics = []
        for conv in conversations[-5:]:  # Last 5 conversations
            if conv.current_topic:
                recent_topics.append(conv.current_topic.lower())

        topic_lower = topic.lower()

        # Calculate similarity to recent topics
        similarity_count = sum(1 for t in recent_topics if topic_lower in t or t in topic_lower)

        if similarity_count == 0:
            return 1.0  # New topic, good
        elif similarity_count == 1:
            return 0.8  # Some repetition, okay
        elif similarity_count == 2:
            return 0.6  # Notable repetition
        else:
            return 0.4  # Too much repetition

    def _assess_emotional_compatibility(self, topic: str, current_emotion: str) -> float:
        """Assess if topic is compatible with child's current emotional state"""

        topic_lower = topic.lower()
        emotion_lower = current_emotion.lower()

        # Define emotion-topic compatibility
        compatibility_map = {
            "happy": {
                "high": ["games", "fun", "adventure", "friends", "celebration"],
                "medium": ["learning", "animals", "art", "music"],
                "low": ["serious", "sad", "problem"],
            },
            "sad": {
                "high": ["comfort", "animals", "family", "gentle"],
                "medium": ["art", "music", "nature"],
                "low": ["exciting", "adventure", "games"],
            },
            "excited": {
                "high": ["adventure", "games", "fun", "exploration"],
                "medium": ["learning", "discovery", "creativity"],
                "low": ["calm", "quiet", "slow"],
            },
            "frustrated": {
                "high": ["calm", "simple", "gentle", "easy"],
                "medium": ["art", "music", "nature"],
                "low": ["complex", "challenging", "difficult"],
            },
            "tired": {
                "high": ["calm", "gentle", "story", "quiet"],
                "medium": ["art", "music", "simple"],
                "low": ["exciting", "energetic", "complex"],
            },
        }

        emotion_compatibility = compatibility_map.get(emotion_lower, {})

        if any(high in topic_lower for high in emotion_compatibility.get("high", [])):
            return 1.0

        if any(medium in topic_lower for medium in emotion_compatibility.get("medium", [])):
            return 0.8

        if any(low in topic_lower for low in emotion_compatibility.get("low", [])):
            return 0.4

        return 0.7  # Default neutral compatibility

    def _assess_time_appropriateness(self, topic: str, current_time: datetime) -> float:
        """Assess if topic is appropriate for current time of day"""

        hour = current_time.hour
        topic_lower = topic.lower()

        # Define time-sensitive topics
        if 6 <= hour <= 11:  # Morning
            if any(word in topic_lower for word in ["wake up", "breakfast", "morning", "school"]):
                return 1.0
            if any(word in topic_lower for word in ["bedtime", "sleep", "tired"]):
                return 0.5

        elif 12 <= hour <= 17:  # Afternoon
            if any(word in topic_lower for word in ["play", "games", "adventure", "learning"]):
                return 1.0
            if any(word in topic_lower for word in ["bedtime", "sleep"]):
                return 0.6

        elif 18 <= hour <= 20:  # Evening
            if any(word in topic_lower for word in ["family", "dinner", "calm", "story"]):
                return 1.0
            if any(word in topic_lower for word in ["exciting", "energetic"]):
                return 0.7

        else:  # Late evening/night
            if any(word in topic_lower for word in ["bedtime", "sleep", "calm", "gentle"]):
                return 1.0
            if any(word in topic_lower for word in ["exciting", "energetic", "loud"]):
                return 0.3

        return 0.8  # Default neutral score

    def _assess_conversation_patterns_safety(self, conversations: List[Conversation]) -> float:
        """Assess safety based on conversation patterns"""

        if not conversations:
            return 1.0

        safety_score = 1.0

        # Check for escalations
        escalation_count = sum(1 for conv in conversations if conv.status == "escalated")
        if escalation_count > 0:
            safety_score -= escalation_count * 0.2

        # Check for safety violations in conversations
        total_violations = sum(conv.safety_violations for conv in conversations)
        if total_violations > 0:
            safety_score -= total_violations * 0.15

        # Check for concerning engagement patterns
        low_engagement_count = sum(1 for conv in conversations if conv.child_engagement_score < 0.3)
        if low_engagement_count > len(conversations) * 0.5:
            safety_score -= 0.1  # Many low engagement conversations

        return max(0.0, safety_score)

    def _assess_emotional_stability(self, child: Child) -> float:
        """Assess emotional stability based on emotion history"""

        if not child.emotional_state_history:
            return 0.8  # Neutral score when no data

        recent_emotions = child.emotional_state_history[-10:]  # Last 10 entries

        # Count negative emotions
        negative_emotions = ["sad", "frustrated", "anxious", "angry"]
        negative_count = sum(1 for entry in recent_emotions if entry["emotion"] in negative_emotions)

        # Calculate stability score
        negative_ratio = negative_count / len(recent_emotions)

        if negative_ratio > 0.7:
            return 0.3  # High negative emotions
        elif negative_ratio > 0.5:
            return 0.6  # Moderate negative emotions
        elif negative_ratio > 0.3:
            return 0.8  # Some negative emotions
        else:
            return 1.0  # Stable emotional state

    def _assess_usage_patterns_safety(self, child: Child) -> float:
        """Assess safety based on usage patterns"""

        safety_score = 1.0

        # Check for excessive usage
        if child.safety_settings:
            usage_ratio = child.daily_usage_minutes / child.safety_settings.max_daily_minutes
            if usage_ratio > 0.9:
                safety_score -= 0.1
            elif usage_ratio > 1.0:
                safety_score -= 0.3

        # Check conversation frequency
        if child.total_conversations_today > 10:  # High frequency
            safety_score -= 0.1

        return max(0.0, safety_score)

    def _assess_parent_involvement(self, parent_feedback: Dict[str, Any]) -> float:
        """Assess parent involvement level"""

        involvement_score = 0.5  # Base score

        if parent_feedback.get("recent_review", False):
            involvement_score += 0.2

        if parent_feedback.get("settings_updated_recently", False):
            involvement_score += 0.1

        if parent_feedback.get("feedback_provided", False):
            involvement_score += 0.2

        return min(1.0, involvement_score)

    def _calculate_average_engagement(self, conversations: List[Conversation]) -> float:
        """Calculate average engagement score from conversations"""

        if not conversations:
            return 0.5

        engagement_scores = [conv.child_engagement_score for conv in conversations]
        return sum(engagement_scores) / len(engagement_scores)

    def _analyze_emotional_response_patterns(self, emotion_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze patterns in emotional responses"""

        if not emotion_history:
            return {}

        emotion_counts = {}
        total_entries = len(emotion_history)

        for entry in emotion_history:
            emotion = entry["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Convert to ratios
        emotion_patterns = {emotion: count / total_entries for emotion, count in emotion_counts.items()}

        return emotion_patterns
