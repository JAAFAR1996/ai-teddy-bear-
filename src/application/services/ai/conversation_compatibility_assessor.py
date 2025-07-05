from datetime import datetime
from typing import Dict, List

from ....domain.entities import Child, Conversation
from ....domain.value_objects import VoiceProfile


@dataclass
class ConversationCompatibilityResult:
    """Result of conversation compatibility check"""

    is_compatible: bool
    compatibility_score: float  # 0.0 to 1.0
    recommendations: List[str]
    blocking_issues: List[str]


class ConversationCompatibilityAssessor:
    """Assesses conversation compatibility for a child."""

    def assess(
        self,
        child: Child,
        proposed_topic: str,
        conversation_history: List[Conversation],
    ) -> ConversationCompatibilityResult:
        """
        Assess if a proposed conversation topic is compatible with
        the child's profile, history, and current state.
        """
        compatibility_score = 1.0
        recommendations = []
        blocking_issues = []

        compatibility_score, blocking_issues = self._check_safety_compatibility(
            child, proposed_topic, compatibility_score, blocking_issues
        )
        compatibility_score, recommendations = self._check_age_and_history_compatibility(
            child, proposed_topic, conversation_history, compatibility_score, recommendations
        )
        compatibility_score, recommendations = self._check_emotional_and_time_compatibility(
            child, proposed_topic, compatibility_score, recommendations
        )

        return ConversationCompatibilityResult(
            is_compatible=compatibility_score >= 0.6 and not blocking_issues,
            compatibility_score=compatibility_score,
            recommendations=recommendations,
            blocking_issues=blocking_issues,
        )

    def _check_safety_compatibility(
        self, child: Child, proposed_topic: str, compatibility_score: float, blocking_issues: List[str]
    ) -> tuple[float, List[str]]:
        """Check safety settings compatibility."""
        if not child.safety_settings.is_topic_allowed(proposed_topic):
            blocking_issues.append(
                f"Topic '{proposed_topic}' is blocked by safety settings")
            compatibility_score = 0.0
        return compatibility_score, blocking_issues

    def _check_age_and_history_compatibility(
        self,
        child: Child,
        proposed_topic: str,
        conversation_history: List[Conversation],
        compatibility_score: float,
        recommendations: List[str],
    ) -> tuple[float, List[str]]:
        """Check age appropriateness and conversation history compatibility."""
        age_appropriate_score = self._assess_topic_age_appropriateness(
            proposed_topic, child.age)
        compatibility_score *= age_appropriate_score
        if age_appropriate_score < 0.7:
            recommendations.append(
                f"Consider simplifying topic for age {child.age}")

        history_score = self._analyze_conversation_history_compatibility(
            proposed_topic, conversation_history)
        compatibility_score *= history_score
        if history_score < 0.8:
            recommendations.append(
                "Topic may be repetitive based on recent conversations")
        return compatibility_score, recommendations

    def _check_emotional_and_time_compatibility(
        self, child: Child, proposed_topic: str, compatibility_score: float, recommendations: List[str]
    ) -> tuple[float, List[str]]:
        """Check emotional state and time appropriateness."""
        if child.emotional_state_history:
            recent_emotion = child.emotional_state_history[-1]
            emotion_compatibility = self._assess_emotional_compatibility(
                proposed_topic, recent_emotion["emotion"])
            compatibility_score *= emotion_compatibility
            if emotion_compatibility < 0.6:
                recommendations.append(
                    f"Consider child's current emotional state: {recent_emotion['emotion']}")

        current_time = datetime.utcnow()
        time_score = self._assess_time_appropriateness(
            proposed_topic, current_time)
        compatibility_score *= time_score
        if time_score < 0.8:
            recommendations.append(
                "Topic may not be appropriate for current time")
        return compatibility_score, recommendations

    def _assess_topic_age_appropriateness(self, topic: str, age: int) -> float:
        """Assess how age-appropriate a topic is (0.0 to 1.0)"""
        topic_lower = topic.lower()
        age_keywords = self._find_age_keywords(age)
        if not age_keywords:
            return 0.5
        return self._score_topic_by_keywords(topic_lower, age_keywords)

    def _get_age_appropriateness_map(self) -> Dict[tuple, Dict[str, List[str]]]:
        """Define age-appropriate keywords mapping."""
        return {
            (3, 4): {"high": ["animals", "colors", "shapes", "toys", "family", "food"], "medium": ["games", "friends", "school"], "low": ["science", "history", "technology"], "blocked": ["violence", "scary", "complex"]},
            (5, 6): {"high": ["animals", "colors", "games", "school", "friends", "toys"], "medium": ["science", "art", "music", "sports"], "low": ["history", "technology", "emotions"], "blocked": ["violence", "scary", "complex relationships"]},
            (7, 10): {"high": ["science", "animals", "school", "games", "friends", "art", "music"], "medium": ["history", "technology", "emotions", "relationships"], "low": ["politics", "complex science"], "blocked": ["violence", "inappropriate content"]},
            (11, 12): {"high": ["science", "technology", "history", "friends", "school", "hobbies"], "medium": ["emotions", "relationships", "current events"], "low": ["politics", "advanced topics"], "blocked": ["inappropriate content", "violence"]},
        }

    def _find_age_keywords(self, age: int) -> Optional[Dict[str, List[str]]]:
        """Find appropriate keywords for the given age."""
        age_map = self._get_age_appropriateness_map()
        for age_range, keywords in age_map.items():
            if age_range[0] <= age <= age_range[1]:
                return keywords
        return None

    def _score_topic_by_keywords(self, topic_lower: str, age_keywords: Dict[str, List[str]]) -> float:
        """Score topic based on age-appropriate keywords."""
        if any(blocked in topic_lower for blocked in age_keywords["blocked"]):
            return 0.0
        if any(high in topic_lower for high in age_keywords["high"]):
            return 1.0
        if any(medium in topic_lower for medium in age_keywords["medium"]):
            return 0.8
        if any(low in topic_lower for low in age_keywords["low"]):
            return 0.6
        return 0.7

    def _analyze_conversation_history_compatibility(self, topic: str, conversations: List[Conversation]) -> float:
        """Analyze if topic is compatible with recent conversation history."""
        if not conversations:
            return 1.0
        recent_topics = [conv.current_topic.lower()
                         for conv in conversations[-5:] if conv.current_topic]
        topic_lower = topic.lower()
        similarity_count = sum(
            1 for t in recent_topics if topic_lower in t or t in topic_lower)
        if similarity_count == 0:
            return 1.0
        elif similarity_count == 1:
            return 0.8
        elif similarity_count == 2:
            return 0.6
        else:
            return 0.4

    def _assess_emotional_compatibility(self, topic: str, current_emotion: str) -> float:
        """Assess if topic is compatible with child's current emotional state."""
        topic_lower = topic.lower()
        emotion_lower = current_emotion.lower()
        compatibility_map = {
            "happy": {"high": ["games", "fun", "adventure", "friends", "celebration"], "medium": ["learning", "animals", "art", "music"], "low": ["serious", "sad", "problem"]},
            "sad": {"high": ["comfort", "animals", "family", "gentle"], "medium": ["art", "music", "nature"], "low": ["exciting", "adventure", "games"]},
            "excited": {"high": ["adventure", "games", "fun", "exploration"], "medium": ["learning", "discovery", "creativity"], "low": ["calm", "quiet", "slow"]},
            "frustrated": {"high": ["calm", "simple", "gentle", "easy"], "medium": ["art", "music", "nature"], "low": ["complex", "challenging", "difficult"]},
            "tired": {"high": ["calm", "gentle", "story", "quiet"], "medium": ["art", "music", "simple"], "low": ["exciting", "energetic", "complex"]},
        }
        emotion_compatibility = compatibility_map.get(emotion_lower, {})
        if any(high in topic_lower for high in emotion_compatibility.get("high", [])):
            return 1.0
        if any(medium in topic_lower for medium in emotion_compatibility.get("medium", [])):
            return 0.8
        if any(low in topic_lower for low in emotion_compatibility.get("low", [])):
            return 0.4
        return 0.7

    def _assess_time_appropriateness(self, topic: str, current_time: datetime) -> float:
        """Assess if topic is appropriate for current time of day."""
        hour = current_time.hour
        topic_lower = topic.lower()
        if 6 <= hour <= 11:
            if any(word in topic_lower for word in ["wake up", "breakfast", "morning", "school"]):
                return 1.0
            if any(word in topic_lower for word in ["bedtime", "sleep", "tired"]):
                return 0.5
        elif 12 <= hour <= 17:
            if any(word in topic_lower for word in ["play", "games", "adventure", "learning"]):
                return 1.0
            if any(word in topic_lower for word in ["bedtime", "sleep"]):
                return 0.6
        elif 18 <= hour <= 20:
            if any(word in topic_lower for word in ["family", "dinner", "calm", "story"]):
                return 1.0
            if any(word in topic_lower for word in ["exciting", "energetic"]):
                return 0.7
        else:
            if any(word in topic_lower for word in ["bedtime", "sleep", "calm", "gentle"]):
                return 1.0
            if any(word in topic_lower for word in ["exciting", "energetic", "loud"]):
                return 0.3
        return 0.8
