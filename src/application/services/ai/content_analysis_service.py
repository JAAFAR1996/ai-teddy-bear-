"""
Content Analysis Domain Service
==============================

Domain service for analyzing conversation content and detecting issues.
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Set

from ..models.alert_models import AlertSeverity, AlertType
from ..models.analytics_models import ConversationLog
from ..models.control_models import ParentalControl


class ContentAnalysisService:
    """Domain service for content analysis and moderation"""

    def __init__(self):
        self.emergency_keywords = {
            "help",
            "emergency",
            "hurt",
            "scared",
            "danger",
            "pain",
            "bleeding",
            "fire",
            "police",
            "ambulance",
            "hospital",
        }

        self.concerning_keywords = {
            "sad",
            "crying",
            "angry",
            "hate",
            "bullying",
            "mean",
            "alone",
            "nobody likes me",
            "want to die",
            "suicide",
        }

        self.inappropriate_keywords = {
            "violence",
            "weapon",
            "gun",
            "knife",
            "kill",
            "murder",
            "adult content",
            "sexual",
            "drugs",
            "alcohol",
            "smoking",
        }

    def analyze_conversation_content(
        self, conversation: ConversationLog, controls: ParentalControl
    ) -> Dict[str, Any]:
        """Analyze conversation content for moderation issues"""

        analysis = {
            "alerts_needed": [],
            "moderation_flags": [],
            "sentiment_concerns": [],
            "topic_violations": [],
            "emergency_detected": False,
            "requires_parent_attention": False,
        }

        # Extract text from conversation
        conversation_text = self._extract_conversation_text(conversation)

        # Check for emergency situations
        if self._detect_emergency(conversation_text):
            analysis["emergency_detected"] = True
            analysis["alerts_needed"].append(
                {
                    "type": AlertType.EMERGENCY,
                    "severity": AlertSeverity.CRITICAL,
                    "message": "Emergency keywords detected in conversation",
                }
            )

        # Check for concerning content
        concerning_flags = self._detect_concerning_content(conversation_text)
        if concerning_flags:
            analysis["moderation_flags"].extend(concerning_flags)
            analysis["requires_parent_attention"] = True

        # Check topic violations
        topic_violations = self._check_topic_violations(
            conversation.topics_discussed, controls
        )
        if topic_violations:
            analysis["topic_violations"] = topic_violations
            analysis["alerts_needed"].append(
                {
                    "type": AlertType.CONTENT_MODERATION,
                    "severity": AlertSeverity.HIGH,
                    "message": f'Blocked topics discussed: {", ".join(topic_violations)}',
                }
            )

        # Check sentiment concerns
        sentiment_issues = self._analyze_sentiment_concerns(
            conversation.sentiment_scores
        )
        if sentiment_issues:
            analysis["sentiment_concerns"] = sentiment_issues
            analysis["requires_parent_attention"] = True

        return analysis

    def extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from conversation text"""

        topic_keywords = {
            "education": ["learn", "study", "school", "math", "science", "homework"],
            "games": ["play", "game", "fun", "puzzle", "sport", "toy"],
            "stories": ["story", "tale", "book", "read", "character", "adventure"],
            "art": ["draw", "paint", "color", "create", "picture", "craft"],
            "music": ["song", "sing", "music", "instrument", "dance", "melody"],
            "science": ["experiment", "nature", "animal", "planet", "space"],
            "family": ["mom", "dad", "brother", "sister", "family", "grandma"],
            "friends": ["friend", "classmate", "buddy", "playmate"],
            "emotions": ["happy", "sad", "excited", "worried", "feeling"],
        }

        text_lower = text.lower()
        detected_topics = []

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)

        return detected_topics

    def calculate_interaction_quality(self, conversation: ConversationLog) -> float:
        """Calculate quality score for conversation (0-1)"""

        factors = {}

        # Duration factor (optimal 5-20 minutes)
        duration_minutes = conversation.get_duration_minutes()
        if 5 <= duration_minutes <= 20:
            factors["duration"] = 1.0
        elif duration_minutes < 5:
            factors["duration"] = duration_minutes / 5.0
        else:
            factors["duration"] = max(0.5, 1.0 - (duration_minutes - 20) / 30)

        # Engagement factor (message count)
        message_factor = min(conversation.message_count / 20, 1.0)
        factors["engagement"] = message_factor

        # Sentiment factor
        positive_sentiment = conversation.sentiment_scores.get("positive", 0)
        factors["sentiment"] = positive_sentiment

        # Topic diversity factor
        topic_diversity = min(len(conversation.topics_discussed) / 3, 1.0)
        factors["diversity"] = topic_diversity

        # Educational value factor
        factors["educational"] = 1.0 if conversation.has_educational_content() else 0.5

        # Weighted average
        weights = {
            "duration": 0.2,
            "engagement": 0.2,
            "sentiment": 0.3,
            "diversity": 0.15,
            "educational": 0.15,
        }

        return sum(factors[k] * weights[k] for k in factors)

    def detect_concerning_patterns(
        self, conversations: List[ConversationLog], days_window: int = 7
    ) -> List[Dict[str, Any]]:
        """Detect concerning patterns across multiple conversations"""

        patterns = []

        # Filter recent conversations
        cutoff_date = datetime.now() - timedelta(days=days_window)
        recent_conversations = [
            conv for conv in conversations if conv.timestamp >= cutoff_date
        ]

        if not recent_conversations:
            return patterns

        # Check for declining sentiment trend
        if self._detect_sentiment_decline(recent_conversations):
            patterns.append(
                {
                    "type": "sentiment_decline",
                    "severity": "medium",
                    "description": "Declining emotional state detected over recent conversations",
                }
            )

        # Check for repetitive concerning topics
        concerning_topics = self._detect_repetitive_concerns(recent_conversations)
        if concerning_topics:
            patterns.append(
                {
                    "type": "repetitive_concerns",
                    "severity": "high",
                    "description": f'Repeatedly discussing concerning topics: {", ".join(concerning_topics)}',
                    "topics": concerning_topics,
                }
            )

        # Check for social isolation indicators
        if self._detect_isolation_indicators(recent_conversations):
            patterns.append(
                {
                    "type": "social_isolation",
                    "severity": "medium",
                    "description": "Indicators of social isolation or loneliness detected",
                }
            )

        return patterns

    def _extract_conversation_text(self, conversation: ConversationLog) -> str:
        """Extract all text from conversation transcript"""

        text_parts = []
        for message in conversation.transcript:
            if isinstance(message, dict):
                if message.get("child"):
                    text_parts.append(message["child"])
                if message.get("assistant"):
                    text_parts.append(message["assistant"])

        return " ".join(text_parts).lower()

    def _detect_emergency(self, text: str) -> bool:
        """Detect emergency situations in text"""

        text_words = set(text.lower().split())
        return bool(text_words & self.emergency_keywords)

    def _detect_concerning_content(self, text: str) -> List[str]:
        """Detect concerning content flags"""

        flags = []
        text_words = set(text.lower().split())

        if text_words & self.concerning_keywords:
            flags.append("emotional_distress")

        if text_words & self.inappropriate_keywords:
            flags.append("inappropriate_content")

        # Check for bullying indicators
        bullying_patterns = [
            r"\b(bullying|bullied|mean kids|nobody likes me)\b",
            r"\b(alone|lonely|no friends)\b",
            r"\b(scared of|afraid of) .*(school|kids|children)\b",
        ]

        for pattern in bullying_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                flags.append("bullying_concern")
                break

        return flags

    def _check_topic_violations(
        self, topics: List[str], controls: ParentalControl
    ) -> List[str]:
        """Check for topic violations against parental controls"""

        violations = []
        for topic in topics:
            if not controls.is_topic_allowed(topic):
                violations.append(topic)

        return violations

    def _analyze_sentiment_concerns(
        self, sentiment_scores: Dict[str, float]
    ) -> List[str]:
        """Analyze sentiment for concerning patterns"""

        concerns = []

        negative_score = sentiment_scores.get("negative", 0)
        positive_score = sentiment_scores.get("positive", 0)

        if negative_score > 0.7:
            concerns.append("high_negative_sentiment")

        if positive_score < 0.2 and negative_score > 0.3:
            concerns.append("overall_negative_mood")

        return concerns

    def _detect_sentiment_decline(self, conversations: List[ConversationLog]) -> bool:
        """Detect declining sentiment trend"""

        if len(conversations) < 3:
            return False

        # Sort by timestamp
        sorted_convs = sorted(conversations, key=lambda x: x.timestamp)

        # Check if recent half has lower positive sentiment than earlier half
        mid_point = len(sorted_convs) // 2
        early_convs = sorted_convs[:mid_point]
        recent_convs = sorted_convs[mid_point:]

        early_avg = sum(
            conv.sentiment_scores.get("positive", 0) for conv in early_convs
        ) / len(early_convs)

        recent_avg = sum(
            conv.sentiment_scores.get("positive", 0) for conv in recent_convs
        ) / len(recent_convs)

        return recent_avg < early_avg - 0.2  # Significant decline

    def _detect_repetitive_concerns(
        self, conversations: List[ConversationLog]
    ) -> List[str]:
        """Detect repeatedly discussed concerning topics"""

        concerning_topics = {"sad", "scared", "bullying", "alone", "angry"}
        topic_counts = {}

        for conv in conversations:
            conv_text = self._extract_conversation_text(conv)
            for topic in concerning_topics:
                if topic in conv_text:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1

        # Return topics mentioned in more than half of conversations
        threshold = len(conversations) // 2
        return [
            topic
            for topic, count in topic_counts.items()
            if count >= threshold and count >= 2
        ]

    def _detect_isolation_indicators(
        self, conversations: List[ConversationLog]
    ) -> bool:
        """Detect indicators of social isolation"""

        isolation_keywords = {
            "lonely",
            "alone",
            "no friends",
            "nobody likes me",
            "by myself",
            "no one to play with",
        }

        isolation_mentions = 0
        for conv in conversations:
            conv_text = self._extract_conversation_text(conv)
            if any(keyword in conv_text for keyword in isolation_keywords):
                isolation_mentions += 1

        # If mentioned in more than 30% of conversations
        return isolation_mentions > len(conversations) * 0.3
