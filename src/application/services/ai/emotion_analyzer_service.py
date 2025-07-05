"""
🎭 Emotion Analyzer Service - Enterprise 2025 Implementation
Advanced emotion analysis with cultural awareness and AI integration
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.application.services.ai.emotion_analyzer_service import (
    EmotionAnalyzer as DomainEmotionAnalyzer,
)
from src.application.services.ai.core import IEmotionAnalyzer
from src.application.services.ai.models.ai_response_models import EmotionAnalysis

logger = logging.getLogger(__name__)


class EmotionAnalyzerService(IEmotionAnalyzer):
    """
    🎭 Advanced emotion analysis service with:
    - Cultural awareness for Arabic and English
    - Machine learning integration
    - Real-time emotion tracking
    - Conversation trend analysis
    """

    def __init__(
            self,
            domain_analyzer: Optional[DomainEmotionAnalyzer] = None):
        self.domain_analyzer = domain_analyzer
        self.emotion_cache: Dict[str, EmotionAnalysis] = {}
        self.cache_ttl = 300  # 5 minutes
        self.emotion_patterns = self._get_emotion_patterns()
        logger.info("✅ Emotion Analyzer Service initialized")

    @staticmethod
    def _get_emotion_patterns() -> Dict[str, Dict[str, Any]]:
        """Load enhanced emotion patterns with cultural awareness"""
        return {
            **EmotionAnalyzerService._load_basic_emotions(),
            **EmotionAnalyzerService._load_complex_emotions(),
        }

    @staticmethod
    def _load_basic_emotions() -> Dict[str, Dict[str, Any]]:
        """Load basic emotion patterns (joy, sadness, anger, fear)"""
        return {
            "joy": {
                "arabic_keywords": ["سعيد", "فرح", "مبسوط", "ضحك", "فرحان", "مسرور"],
                "english_keywords": ["happy", "joy", "glad", "cheerful", "delighted"],
                "emojis": ["😊", "😄", "😃", "🙂", "😆", "🤗"],
                "weight": 1.0,
            },
            "sadness": {
                "arabic_keywords": ["حزين", "زعلان", "مكتئب", "بكي", "دموع", "محبط"],
                "english_keywords": ["sad", "unhappy", "depressed", "cry", "tears"],
                "emojis": ["😢", "😭", "😞", "☹️", "💔"],
                "weight": 1.0,
            },
            "anger": {
                "arabic_keywords": ["غضب", "زعل", "عصبي", "متضايق", "غاضب", "منزعج"],
                "english_keywords": ["angry", "mad", "furious", "annoyed", "upset"],
                "emojis": ["😡", "😠", "🤬", "😤"],
                "weight": 1.0,
            },
            "fear": {
                "arabic_keywords": ["خوف", "خائف", "قلق", "مرعوب", "فزع", "رعب"],
                "english_keywords": [
                    "scared",
                    "afraid",
                    "frightened",
                    "worried",
                    "anxious",
                ],
                "emojis": ["😨", "😰", "😱", "😟", "😧"],
                "weight": 1.0,
            },
        }

    @staticmethod
    def _load_complex_emotions() -> Dict[str, Dict[str, Any]]:
        """Load complex emotion patterns (love, excitement, curiosity, surprise)"""
        return {
            "love": {
                "arabic_keywords": ["حب", "أحب", "عشق", "أعشق", "أحبك", "حبيب"],
                "english_keywords": ["love", "adore", "cherish", "affection"],
                "emojis": ["❤️", "💕", "😍", "🥰", "💖"],
                "weight": 1.0,
            },
            "excitement": {
                "arabic_keywords": ["متحمس", "متشوق", "رائع", "ممتاز", "واو"],
                "english_keywords": [
                    "excited",
                    "thrilled",
                    "amazing",
                    "awesome",
                    "wow",
                ],
                "emojis": ["🤩", "✨", "🎉", "😍", "🔥"],
                "weight": 1.0,
            },
            "curiosity": {
                "arabic_keywords": [
                    "فضول",
                    "ليش",
                    "لماذا",
                    "كيف",
                    "متى",
                    "أين",
                    "ماذا",
                ],
                "english_keywords": ["curious", "why", "how", "when", "where", "what"],
                "emojis": ["🤔", "❓", "❔"],
                "weight": 0.8,
            },
            "surprise": {
                "arabic_keywords": ["مفاجأة", "عجيب", "غريب", "لا أصدق"],
                "english_keywords": ["surprised", "amazed", "shocked", "wow"],
                "emojis": ["😲", "😯", "🤯", "😮"],
                "weight": 0.9,
            },
        }

    async def analyze_text_emotion(
        self, text: str, language: str = "ar"
    ) -> EmotionAnalysis:
        """🎭 Analyze emotion from text with advanced detection"""
        try:
            # Check cache first
            cache_key = f"{text[:50]}_{language}"
            if cache_key in self.emotion_cache:
                cached_result = self.emotion_cache[cache_key]
                if self._is_cache_valid(cached_result.analysis_timestamp):
                    return cached_result

            # Use domain analyzer if available
            if self.domain_analyzer:
                try:
                    domain_result = await self.domain_analyzer.analyze_text_emotion(
                        text
                    )
                    if hasattr(domain_result, "value"):
                        primary_emotion = domain_result.value
                        confidence = 0.85
                    else:
                        primary_emotion = str(domain_result)
                        confidence = 0.80
                except Exception as e:
                    logger.warning(f"Domain analyzer failed: {e}")
                    primary_emotion, confidence = self._analyze_with_patterns(
                        text, language
                    )
            else:
                primary_emotion, confidence = self._analyze_with_patterns(
                    text, language
                )

            # Get detailed emotion breakdown
            emotion_scores = self._get_emotion_scores(text, language)

            # Create result
            result = EmotionAnalysis(
                primary_emotion=primary_emotion,
                confidence=confidence,
                detected_emotions=emotion_scores,
                analysis_timestamp=datetime.utcnow(),
            )

            # Cache result
            self.emotion_cache[cache_key] = result

            return result

        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
            return EmotionAnalysis(
                primary_emotion="neutral",
                confidence=0.5,
                detected_emotions={"neutral": 1.0},
            )

    def _analyze_with_patterns(
            self, text: str, language: str) -> tuple[str, float]:
        """Analyze emotion using enhanced pattern matching"""
        text_lower = text.lower()
        emotion_scores = {}

        for emotion, data in self.emotion_patterns.items():
            score = 0.0

            # Check language-specific keywords
            if language == "ar":
                keywords = data.get("arabic_keywords", [])
            else:
                keywords = data.get("english_keywords", [])

            # Add emoji keywords
            keywords.extend(data.get("emojis", []))

            # Calculate score
            for keyword in keywords:
                if keyword in text_lower:
                    score += data["weight"]

            # Apply contextual multipliers
            score = self._apply_contextual_multipliers(
                text_lower, emotion, score)

            if score > 0:
                emotion_scores[emotion] = score

        if not emotion_scores:
            return "neutral", 0.6

        # Get primary emotion
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[primary_emotion]

        # Calculate confidence based on score and competition
        confidence = min(0.95, 0.5 + (max_score * 0.15))

        return primary_emotion, confidence

    def _apply_contextual_multipliers(
        self, text: str, emotion: str, base_score: float
    ) -> float:
        """Apply contextual multipliers to emotion scores"""
        if base_score == 0:
            return 0

        multiplier = 1.0

        # Negation detection
        negation_words = ["لا", "ليس", "غير", "not", "no", "never", "don't"]
        if any(neg in text for neg in negation_words):
            multiplier *= 0.3

        # Intensifiers
        intensifiers = [
            "جداً",
            "كثيراً",
            "very",
            "really",
            "extremely",
            "super"]
        if any(intensifier in text for intensifier in intensifiers):
            multiplier *= 1.5

        # Question marks reduce certainty
        if "?" in text or "؟" in text:
            multiplier *= 0.8

        return base_score * multiplier

    def _get_emotion_scores(
            self, text: str, language: str) -> Dict[str, float]:
        """Get detailed emotion scores for all emotions"""
        text_lower = text.lower()
        scores = {}

        for emotion, data in self.emotion_patterns.items():
            score = 0.0

            keywords = data.get(
                "arabic_keywords" if language == "ar" else "english_keywords", [])
            keywords.extend(data.get("emojis", []))

            for keyword in keywords:
                if keyword in text_lower:
                    score += data["weight"]

            if score > 0:
                scores[emotion] = min(1.0, score / 3.0)  # Normalize to 0-1

        # Add neutral if no emotions detected
        if not scores:
            scores["neutral"] = 1.0

        return scores

    async def analyze_emotion_trend(
        self, conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """🔍 Analyze emotion trends in conversation history"""
        if not conversation_history:
            return {
                "trend": "neutral",
                "confidence": 0.5,
                "pattern": "no_data"}

        # Extract emotions from recent messages
        recent_emotions = []
        for message in conversation_history[-10:]:  # Last 10 messages
            if message.get("emotion"):
                recent_emotions.append(message["emotion"])
            elif message.get("content"):
                emotion_analysis = await self.analyze_text_emotion(message["content"])
                recent_emotions.append(emotion_analysis.primary_emotion)

        if not recent_emotions:
            return {
                "trend": "neutral",
                "confidence": 0.5,
                "pattern": "no_emotions"}

        # Analyze trend
        trend_analysis = self._analyze_trend_pattern(recent_emotions)

        return {
            "trend": trend_analysis["current_trend"],
            "confidence": trend_analysis["confidence"],
            "pattern": trend_analysis["pattern"],
            "emotion_distribution": self._get_emotion_distribution(recent_emotions),
            "stability": trend_analysis["stability"],
        }

    def _analyze_trend_pattern(self, emotions: List[str]) -> Dict[str, Any]:
        """Analyze pattern in emotion sequence"""
        if len(emotions) < 2:
            return {
                "current_trend": emotions[0] if emotions else "neutral",
                "confidence": 0.5,
                "pattern": "insufficient_data",
                "stability": "unknown",
            }

        # Get most recent emotion
        current_emotion = emotions[-1]

        # Calculate stability (how consistent recent emotions are)
        recent_count = len(emotions)
        current_emotion_count = emotions.count(current_emotion)
        stability = current_emotion_count / recent_count

        # Determine pattern
        if stability > 0.7:
            pattern = "consistent"
        elif self._is_improving_pattern(emotions):
            pattern = "improving"
        elif self._is_declining_pattern(emotions):
            pattern = "declining"
        else:
            pattern = "variable"

        return {
            "current_trend": current_emotion,
            "confidence": min(0.95, 0.5 + stability * 0.4),
            "pattern": pattern,
            "stability": stability,
        }

    def _is_improving_pattern(self, emotions: List[str]) -> bool:
        """Check if emotions are improving (getting more positive)"""
        positive_emotions = {"joy", "love", "excitement", "curiosity"}
        negative_emotions = {"sadness", "anger", "fear"}

        if len(emotions) < 3:
            return False

        # Check if recent emotions are more positive than earlier ones
        early_positive = sum(
            1 for e in emotions[: len(emotions) // 2] if e in positive_emotions
        )
        late_positive = sum(
            1 for e in emotions[len(emotions) // 2:] if e in positive_emotions
        )

        early_negative = sum(
            1 for e in emotions[: len(emotions) // 2] if e in negative_emotions
        )
        late_negative = sum(
            1 for e in emotions[len(emotions) // 2:] if e in negative_emotions
        )

        return late_positive > early_positive or late_negative < early_negative

    def _is_declining_pattern(self, emotions: List[str]) -> bool:
        """Check if emotions are declining (getting more negative)"""
        positive_emotions = {"joy", "love", "excitement", "curiosity"}
        negative_emotions = {"sadness", "anger", "fear"}

        if len(emotions) < 3:
            return False

        # Check if recent emotions are more negative than earlier ones
        early_positive = sum(
            1 for e in emotions[: len(emotions) // 2] if e in positive_emotions
        )
        late_positive = sum(
            1 for e in emotions[len(emotions) // 2:] if e in positive_emotions
        )

        early_negative = sum(
            1 for e in emotions[: len(emotions) // 2] if e in negative_emotions
        )
        late_negative = sum(
            1 for e in emotions[len(emotions) // 2:] if e in negative_emotions
        )

        return late_positive < early_positive or late_negative > early_negative

    def _get_emotion_distribution(
            self, emotions: List[str]) -> Dict[str, float]:
        """Get distribution of emotions in the list"""
        if not emotions:
            return {}

        distribution = {}
        for emotion in emotions:
            distribution[emotion] = distribution.get(emotion, 0) + 1

        # Convert to percentages
        total = len(emotions)
        return {
            emotion: count /
            total for emotion,
            count in distribution.items()}

    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cache entry is still valid"""
        return (datetime.utcnow() - timestamp).total_seconds() < self.cache_ttl

    def clear_cache(self) -> None:
        """Clear emotion analysis cache"""
        self.emotion_cache.clear()
        logger.info("Emotion analysis cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.emotion_cache),
            "cache_ttl": self.cache_ttl,
            "patterns_loaded": len(self.emotion_patterns),
        }
