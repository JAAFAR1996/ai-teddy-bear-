from typing import Any, Dict, List, Optional

"""
🎭 Unified Emotion Analyzer - Complete Implementation 2025
Combines text analysis, audio analysis (Hume AI), and multi-modal emotion detection
Merged from 3 different emotion analyzer implementations for maximum capability
"""

import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests
import structlog
from opentelemetry import trace

# Optional imports for advanced features
try:
    from hume import StreamDataModels
    from hume.client import AsyncHumeClient

    HUME_AVAILABLE = True
except ImportError:
    HUME_AVAILABLE = False

try:
    # from src.application.services.core.service_registry import ServiceBase
    from src.infrastructure.observability import trace_async

    SERVICE_REGISTRY_AVAILABLE = True
except ImportError:
    SERVICE_REGISTRY_AVAILABLE = False

logger = structlog.get_logger() if "structlog" in globals() else None


class EmotionCategory(Enum):
    """Enhanced emotion categories for comprehensive analysis"""

    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SCARED = "scared"
    EXCITED = "excited"
    CURIOUS = "curious"
    CONFUSED = "confused"
    TIRED = "tired"
    NEUTRAL = "neutral"
    JOY = "joy"
    FEAR = "fear"
    LOVE = "love"
    SURPRISE = "surprise"


@dataclass
class EmotionAnalysis:
    """Comprehensive emotion analysis result"""

    primary_emotion: EmotionCategory
    confidence: float
    secondary_emotions: Dict[EmotionCategory,
                             float] = field(default_factory=dict)
    sentiment_score: float = 0.0  # -1 to 1
    arousal_level: float = 0.5  # 0 to 1
    keywords: List[str] = field(default_factory=list)
    language: str = "ar"
    analysis_method: str = "text"  # text, audio, or hybrid
    processing_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ================== UNIFIED EMOTION ANALYZER ==================


class EmotionAnalyzer:
    """
    🎭 Unified Emotion Analyzer with multiple capabilities:
    1. Text-based emotion detection (keywords, emojis, patterns)
    2. Audio-based emotion detection (Hume AI integration)
    3. Hybrid analysis combining multiple modalities
    4. Cultural awareness for Arabic and English
    5. Service registry integration for enterprise architecture
    """

    def __init__(
            self,
            registry=None,
            config: Dict = None,
            api_key: str = None):
        # Configuration
        self.config = config or {}
        self.api_key = api_key or self.config.get("hume_api_key")

        # Service registry integration (if available)
        if SERVICE_REGISTRY_AVAILABLE and registry:
            self.registry = registry
            self._state = getattr(
                self, "ServiceState", type(
                    "ServiceState", (), {
                        "READY": "ready"})).READY
        else:
            self.registry = None
            self._state = "ready"

        # Hume AI client for audio analysis
        self.hume_client = None
        if HUME_AVAILABLE and self.api_key:
            self.hume_client = AsyncHumeClient(self.api_key)

        # Emotion history for audio analysis
        self.emotion_history: List[Dict] = []

        # Load emotion detection patterns
        self._emotion_keywords = self._load_emotion_keywords()
        self._emoji_emotions = self._load_emoji_emotions()
        self._cultural_patterns = self._load_cultural_patterns()

        # Performance tracking
        self._analysis_count = 0
        self._total_processing_time = 0

        if logger:
            logger.info("✅ Unified Emotion Analyzer initialized")

    # ================== SERVICE REGISTRY METHODS ==================

    async def initialize(self) -> None:
        """Initialize the emotion analyzer (Service Registry compatibility)"""
        if logger:
            logger.info("Initializing unified emotion analyzer")
        self._state = "ready"

    async def shutdown(self) -> None:
        """Shutdown the analyzer"""
        self._state = "stopped"

    async def health_check(self) -> Dict:
        """Health check for service monitoring"""
        return {
            "healthy": self._state == "ready",
            "service": "unified_emotion_analyzer",
            "features": {
                "text_analysis": True,
                "audio_analysis": HUME_AVAILABLE and self.hume_client is not None,
                "hume_integration": HUME_AVAILABLE,
                "cultural_awareness": True,
            },
            "analysis_count": self._analysis_count,
            "avg_processing_time_ms": self._total_processing_time / max(
                self._analysis_count,
                1),
        }

    # ================== MAIN ANALYSIS METHODS ==================

    async def analyze(
            self,
            text: str,
            language: str = "ar") -> EmotionAnalysis:
        """
        🎯 Main analysis method with Service Registry compatibility
        Enhanced text analysis with cultural awareness
        """
        return await self.analyze_text_emotion(text, language)

    def _prepare_and_log_analysis(self):
        """Prepares for a new analysis and returns the start time."""
        start_time = datetime.now()
        self._analysis_count += 1
        return start_time

    def _run_text_analysis_pipeline(
            self, text: str, language: str) -> Dict[str, Any]:
        """Runs the full text analysis pipeline."""
        text_clean = text.strip().lower()
        return {
            "text_clean": text_clean,
            "keyword_emotions": self._analyze_keywords(
                text_clean,
                language),
            "emoji_emotions": self._analyze_emojis(text),
            "cultural_emotions": self._analyze_cultural_patterns(
                text_clean,
                language),
            "intensity_score": self._analyze_intensity(text),
        }

    def _synthesize_analysis_results(
        self, analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesizes the results from the analysis pipeline."""
        all_emotions = self._combine_emotion_scores(
            (analysis_data["keyword_emotions"], 0.4),
            (analysis_data["emoji_emotions"], 0.3),
            (analysis_data["cultural_emotions"], 0.3),
        )
        primary_emotion = self._get_primary_emotion(all_emotions)
        return {
            "all_emotions": all_emotions,
            "primary_emotion": primary_emotion,
            "confidence": self._calculate_confidence(
                all_emotions, primary_emotion, analysis_data["intensity_score"]
            ),
            "sentiment_score": self._calculate_sentiment(all_emotions),
            "arousal_level": self._calculate_arousal(
                primary_emotion,
                analysis_data["text_clean"],
                analysis_data["intensity_score"],
            ),
        }

    def _package_emotion_result(
        self,
        text: str,
        language: str,
        start_time: datetime,
        pipeline_data: Dict[str, Any],
        synthesis_data: Dict[str, Any],
    ) -> EmotionAnalysis:
        """Packages the final EmotionAnalysis object."""
        processing_time = int(
            (datetime.now() - start_time).total_seconds() * 1000)
        self._total_processing_time += processing_time

        result = EmotionAnalysis(
            primary_emotion=synthesis_data["primary_emotion"],
            confidence=synthesis_data["confidence"],
            secondary_emotions={
                k: v
                for k, v in synthesis_data["all_emotions"].items()
                if k != synthesis_data["primary_emotion"]
            },
            sentiment_score=synthesis_data["sentiment_score"],
            arousal_level=synthesis_data["arousal_level"],
            keywords=self._extract_emotional_keywords(
                pipeline_data["text_clean"], language
            ),
            language=language,
            analysis_method="text",
            processing_time_ms=processing_time,
            metadata={
                "text_length": len(text),
                "intensity_score": pipeline_data["intensity_score"],
                "methods_used": ["keywords", "emojis", "cultural_patterns"],
            },
        )
        if logger:
            logger.info(
                "🎭 Text emotion analysis completed",
                emotion=result.primary_emotion.value,
                confidence=result.confidence,
                processing_time_ms=processing_time,
            )
        return result

    async def analyze_text_emotion(
        self, text: str, language: str = "ar"
    ) -> EmotionAnalysis:
        """
        🔤 Comprehensive text-based emotion analysis
        Supports Arabic and English with cultural context
        """
        try:
            start_time = self._prepare_and_log_analysis()
            pipeline_data = self._run_text_analysis_pipeline(text, language)
            synthesis_data = self._synthesize_analysis_results(pipeline_data)
            return self._package_emotion_result(
                text, language, start_time, pipeline_data, synthesis_data
            )

        except Exception as e:
            if logger:
                logger.error(f"❌ Text emotion analysis failed: {str(e)}")

            # Return neutral fallback
            return EmotionAnalysis(
                primary_emotion=EmotionCategory.NEUTRAL,
                confidence=0.5,
                language=language,
                analysis_method="text_fallback",
                metadata={"error": str(e)},
            )

    async def _get_hume_results(self, audio_file_path: str) -> List[Dict]:
        """Gets emotion analysis results from the Hume AI API."""
        config = StreamDataModels.voice()
        with open(audio_file_path, "rb") as f:
            audio_bytes = f.read()

        results = []
        async with self.hume_client.connect_async([config]) as socket:
            response = await socket.send_bytes(audio_bytes)
            results.extend(response.get("voice", {}).get("predictions", []))
        return results

    def _process_hume_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Processes the raw results from Hume AI."""
        if not results:
            return {
                "primary": EmotionCategory.NEUTRAL,
                "confidence": 0.5,
                "secondary": {},
            }

        top_emotion_data = max(
            results[0]["emotions"],
            key=lambda x: x["score"])
        primary_emotion = self._map_hume_emotion(top_emotion_data["name"])
        confidence = self._extract_confidence(top_emotion_data)

        secondary_emotions = {
            self._map_hume_emotion(e["name"]): e["score"]
            for e in sorted(
                results[0]["emotions"], key=lambda x: x["score"], reverse=True
            )[1:4]
        }
        return {
            "primary": primary_emotion,
            "confidence": confidence,
            "secondary": secondary_emotions,
        }

    def _package_audio_emotion_result(
        self, processed_data: Dict, language: str, start_time: datetime
    ) -> EmotionAnalysis:
        """Packages the processed Hume AI data into an EmotionAnalysis object."""
        processing_time = int(
            (datetime.now() - start_time).total_seconds() * 1000)
        self._total_processing_time += processing_time

        return EmotionAnalysis(
            primary_emotion=processed_data["primary"],
            confidence=processed_data["confidence"],
            secondary_emotions=processed_data["secondary"],
            language=language,
            analysis_method="audio",
            processing_time_ms=processing_time,
            metadata={"source": "HumeAI"},
        )

    async def analyze_audio_emotion(
        self, audio_file_path: str, language: str = "ar"
    ) -> EmotionAnalysis:
        """
        🎤 Audio-based emotion analysis using Hume AI
        Advanced audio emotion detection with streaming support
        """
        if not HUME_AVAILABLE or not self.hume_client:
            if logger:
                logger.warning("⚠️ Hume AI not available for audio analysis")
            return await self._fallback_audio_analysis(audio_file_path, language)

        start_time = self._prepare_and_log_analysis()

        try:
            results = await self._get_hume_results(audio_file_path)
            processed_data = self._process_hume_results(results)
            return self._package_audio_emotion_result(
                processed_data, language, start_time
            )

        except Exception as e:
            if logger:
                logger.error(f"❌ Audio emotion analysis failed: {str(e)}")
            return await self._fallback_audio_analysis(
                audio_file_path, language, str(e)
            )

    async def _run_hybrid_analysis_pipeline(
        self, text: Optional[str], audio_file_path: Optional[str], language: str
    ) -> Dict[str, Optional[EmotionAnalysis]]:
        """Runs the text and audio analysis pipelines in parallel."""
        tasks = {}
        if text:
            tasks["text"] = self.analyze_text_emotion(text, language)
        if audio_file_path:
            tasks["audio"] = self.analyze_audio_emotion(
                audio_file_path, language)

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        analysis_results = {}
        for i, key in enumerate(tasks.keys()):
            analysis_results[key] = (
                results[i] if not isinstance(results[i], Exception) else None
            )
        return analysis_results

    def _combine_hybrid_results(
        self, text_result: EmotionAnalysis, audio_result: EmotionAnalysis
    ) -> Dict[str, Any]:
        """Combines the results from text and audio analysis."""
        # Weighted average for scores
        combined_confidence = (text_result.confidence * 0.5) + (
            audio_result.confidence * 0.5
        )
        combined_sentiment = (text_result.sentiment_score * 0.5) + (
            audio_result.sentiment_score * 0.5
        )
        combined_arousal = (text_result.arousal_level * 0.5) + (
            audio_result.arousal_level * 0.5
        )

        # Determine primary emotion
        primary_emotion = (
            text_result.primary_emotion
            if text_result.confidence >= audio_result.confidence
            else audio_result.primary_emotion
        )

        # Combine secondary emotions
        secondary_emotions = {
            **text_result.secondary_emotions,
            **audio_result.secondary_emotions,
        }

        return {
            "primary": primary_emotion,
            "confidence": combined_confidence,
            "sentiment": combined_sentiment,
            "arousal": combined_arousal,
            "secondary": secondary_emotions,
        }

    def _package_hybrid_result(
        self, combined_data: Dict, language: str, start_time: datetime
    ) -> EmotionAnalysis:
        """Packages the combined data into a final EmotionAnalysis object."""
        processing_time = int(
            (datetime.now() - start_time).total_seconds() * 1000)
        self._total_processing_time += processing_time

        return EmotionAnalysis(
            primary_emotion=combined_data["primary"],
            confidence=combined_data["confidence"],
            secondary_emotions=combined_data["secondary"],
            sentiment_score=combined_data["sentiment"],
            arousal_level=combined_data["arousal"],
            language=language,
            analysis_method="hybrid",
            processing_time_ms=processing_time,
            metadata={"source": "HybridAnalysis"},
        )

    async def analyze_hybrid(
            self,
            text: str = None,
            audio_file_path: str = None,
            language: str = "ar") -> EmotionAnalysis:
        """
        🎶 Hybrid multi-modal emotion analysis
        Combines text and audio for a more accurate result
        """
        if not text and not audio_file_path:
            raise ValueError(
                "Either text or audio_file_path must be provided for hybrid analysis."
            )

        start_time = self._prepare_and_log_analysis()

        try:
            analysis_results = await self._run_hybrid_analysis_pipeline(
                text, audio_file_path, language
            )
            text_result, audio_result = analysis_results.get(
                "text"
            ), analysis_results.get("audio")

            if text_result and audio_result:
                combined_data = self._combine_hybrid_results(
                    text_result, audio_result)
                return self._package_hybrid_result(
                    combined_data, language, start_time)
            elif text_result:
                return text_result
            elif audio_result:
                return audio_result
            else:
                raise Exception("Both text and audio analysis failed.")

        except Exception as e:
            if logger:
                logger.error(f"❌ Hybrid emotion analysis failed: {str(e)}")
            return EmotionAnalysis(
                primary_emotion=EmotionCategory.NEUTRAL,
                confidence=0.5,
                language=language,
                analysis_method="hybrid_fallback",
                metadata={"error": str(e)},
            )

    # ================== PATTERN LOADING METHODS ==================

    def _get_english_emotion_keywords(
            self) -> Dict[EmotionCategory, List[str]]:
        """Returns a dictionary of English emotion keywords."""
        return {
            EmotionCategory.HAPPY: [
                "happy",
                "glad",
                "joyful",
                "cheerful",
                "delighted",
                "ecstatic",
            ],
            EmotionCategory.SAD: [
                "sad",
                "unhappy",
                "miserable",
                "depressed",
                "sorrowful",
                "heartbroken",
            ],
            EmotionCategory.ANGRY: [
                "angry",
                "mad",
                "furious",
                "irate",
                "enraged",
                "livid",
            ],
            EmotionCategory.SCARED: [
                "scared",
                "afraid",
                "terrified",
                "frightened",
                "petrified",
            ],
            EmotionCategory.EXCITED: ["excited", "thrilled", "eager", "enthusiastic"],
            EmotionCategory.SURPRISE: ["surprised", "shocked", "astonished", "amazed"],
            EmotionCategory.LOVE: ["love", "adore", "cherish", "care"],
            EmotionCategory.NEUTRAL: ["neutral", "okay", "fine", "alright"],
        }

    def _get_arabic_emotion_keywords(self) -> Dict[EmotionCategory, List[str]]:
        """Returns a dictionary of Arabic emotion keywords."""
        return {
            EmotionCategory.HAPPY: ["سعيد", "فرحان", "مبسوط", "مسرور"],
            EmotionCategory.SAD: ["حزين", "زعلان", "متضايق", "مكتئب"],
            EmotionCategory.ANGRY: ["غاضب", "معصب", "منفعل", "مستاء"],
            EmotionCategory.SCARED: ["خايف", "مرعوب", "مذعور"],
            EmotionCategory.EXCITED: ["متحمس", "شغوف", "مندفع"],
            EmotionCategory.SURPRISE: ["متفاجئ", "مندهش", "مذهول"],
            EmotionCategory.LOVE: ["حب", "عشق", "غرام", "مودة"],
            EmotionCategory.NEUTRAL: ["عادي", "تمام", "ماشي"],
        }

    def _load_emotion_keywords(self) -> Dict[EmotionCategory, List[str]]:
        """
        Loads a comprehensive list of emotion keywords for multiple languages.
        This can be expanded to load from a file or database.
        """
        english_keywords = self._get_english_emotion_keywords()
        arabic_keywords = self._get_arabic_emotion_keywords()

        # Merge dictionaries
        all_keywords = {**english_keywords, **arabic_keywords}
        for emotion, keywords in arabic_keywords.items():
            if emotion in all_keywords:
                all_keywords[emotion].extend(keywords)

        if logger:
            logger.info(
                "Loaded emotion keywords",
                count=sum(len(v) for v in all_keywords.values()),
            )
        return all_keywords

    def _load_emoji_emotions(self) -> Dict[str, EmotionCategory]:
        """Enhanced emoji to emotion mapping"""
        return {
            # Happy emotions
            "😊": EmotionCategory.HAPPY,
            "😁": EmotionCategory.HAPPY,
            "😄": EmotionCategory.HAPPY,
            "😃": EmotionCategory.HAPPY,
            "🙂": EmotionCategory.HAPPY,
            "😌": EmotionCategory.HAPPY,
            "😆": EmotionCategory.HAPPY,
            "🤗": EmotionCategory.HAPPY,
            # Love emotions
            "❤️": EmotionCategory.LOVE,
            "💕": EmotionCategory.LOVE,
            "😍": EmotionCategory.LOVE,
            "🥰": EmotionCategory.LOVE,
            "💖": EmotionCategory.LOVE,
            "💝": EmotionCategory.LOVE,
            # Sad emotions
            "😢": EmotionCategory.SAD,
            "😭": EmotionCategory.SAD,
            "😞": EmotionCategory.SAD,
            "☹️": EmotionCategory.SAD,
            "😔": EmotionCategory.SAD,
            "😿": EmotionCategory.SAD,
            "💔": EmotionCategory.SAD,
            # Angry emotions
            "😠": EmotionCategory.ANGRY,
            "😡": EmotionCategory.ANGRY,
            "🤬": EmotionCategory.ANGRY,
            "😤": EmotionCategory.ANGRY,
            "💢": EmotionCategory.ANGRY,
            "🔥": EmotionCategory.ANGRY,
            # Scared emotions
            "😨": EmotionCategory.SCARED,
            "😰": EmotionCategory.SCARED,
            "😱": EmotionCategory.SCARED,
            "😟": EmotionCategory.SCARED,
            "😦": EmotionCategory.SCARED,
            "😧": EmotionCategory.SCARED,
            # Excited emotions
            "🤩": EmotionCategory.EXCITED,
            "🎉": EmotionCategory.EXCITED,
            "✨": EmotionCategory.EXCITED,
            "🚀": EmotionCategory.EXCITED,
            "⚡": EmotionCategory.EXCITED,
            "🎊": EmotionCategory.EXCITED,
            # Curious emotions
            "🤔": EmotionCategory.CURIOUS,
            "🧐": EmotionCategory.CURIOUS,
            "❓": EmotionCategory.CURIOUS,
            "❔": EmotionCategory.CURIOUS,
            # Confused emotions
            "😕": EmotionCategory.CONFUSED,
            "🤷": EmotionCategory.CONFUSED,
            "😵": EmotionCategory.CONFUSED,
            "🤯": EmotionCategory.CONFUSED,
            # Tired emotions
            "😴": EmotionCategory.TIRED,
            "🥱": EmotionCategory.TIRED,
            "😪": EmotionCategory.TIRED,
            "💤": EmotionCategory.TIRED,
            # Surprise emotions
            "😲": EmotionCategory.SURPRISE,
            "😮": EmotionCategory.SURPRISE,
            "🤭": EmotionCategory.SURPRISE,
            "😯": EmotionCategory.SURPRISE,
        }

    def _load_cultural_patterns(
            self) -> Dict[str, Dict[EmotionCategory, float]]:
        """Cultural-specific emotional expressions"""
        return {
            # Arabic cultural expressions
            "الحمد لله": {EmotionCategory.HAPPY: 0.7, EmotionCategory.NEUTRAL: 0.3},
            "ما شاء الله": {EmotionCategory.HAPPY: 0.6, EmotionCategory.SURPRISE: 0.4},
            "يا ربي": {EmotionCategory.SURPRISED: 0.5, EmotionCategory.SCARED: 0.3},
            "وحشتني": {EmotionCategory.LOVE: 0.8, EmotionCategory.SAD: 0.2},
            "إن شاء الله": {EmotionCategory.NEUTRAL: 0.6, EmotionCategory.HAPPY: 0.4},
            "لا حول ولا قوة إلا بالله": {
                EmotionCategory.SAD: 0.5,
                EmotionCategory.SCARED: 0.3,
            },
            # English cultural expressions
            "oh my god": {EmotionCategory.SURPRISE: 0.8, EmotionCategory.SCARED: 0.2},
            "no way": {EmotionCategory.SURPRISE: 0.7, EmotionCategory.CONFUSED: 0.3},
            "awesome": {EmotionCategory.EXCITED: 0.9, EmotionCategory.HAPPY: 0.1},
            "whatever": {EmotionCategory.NEUTRAL: 0.6, EmotionCategory.ANGRY: 0.4},
        }

    # ================== ANALYSIS HELPER METHODS ==================

    def _analyze_keywords(
        self, text: str, language: str
    ) -> Dict[EmotionCategory, float]:
        """Enhanced keyword analysis with language awareness"""
        scores = {}
        text_words = text.split()

        for emotion, keywords in self._emotion_keywords.items():
            score = 0.0
            matches = 0

            for keyword in keywords:
                if keyword in text:
                    # Weight based on keyword length and frequency
                    frequency = text.count(keyword)
                    keyword_weight = len(keyword.split()) * 0.1 + 1.0
                    score += frequency * keyword_weight
                    matches += frequency

            if score > 0:
                # Normalize by text length and keyword count
                normalized_score = min(
                    score / (len(text_words) + len(keywords)), 1.0)
                scores[emotion] = normalized_score

        return scores

    def _analyze_emojis(self, text: str) -> Dict[EmotionCategory, float]:
        """Enhanced emoji analysis with frequency weighting"""
        scores = {}

        for emoji, emotion in self._emoji_emotions.items():
            count = text.count(emoji)
            if count > 0:
                # Weight by frequency but with diminishing returns
                emoji_score = min(count * 0.4, 1.0)
                scores[emotion] = scores.get(emotion, 0) + emoji_score

        # Normalize scores
        return {k: min(v, 1.0) for k, v in scores.items()}

    def _analyze_cultural_patterns(
        self, text: str, language: str
    ) -> Dict[EmotionCategory, float]:
        """Analyzes text for cultural-specific emotional patterns."""
        emotion_scores: Dict[EmotionCategory, float] = {}
        patterns = self._cultural_patterns.get(language, {})

        for pattern, emotions in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                for emotion, score in emotions.items():
                    emotion_scores[emotion] = emotion_scores.get(
                        emotion, 0) + score

        return emotion_scores

    def _analyze_intensity(self, text: str) -> float:
        """Analyzes the intensity of emotion in the text."""
        intensity_markers = {
            "very": 0.3,
            "really": 0.3,
            "so": 0.2,
            "extremely": 0.5,
            "incredibly": 0.4,
            "absolutely": 0.4,
            "totally": 0.3,
            "جداً": 0.4,
            "كثير": 0.3,
            "جداً جداً": 0.6,
            "كتير": 0.3,
        }

        intensity = 0.5  # Base intensity

        for marker, boost in intensity_markers.items():
            if marker in text.lower():
                intensity += boost

        # Punctuation intensity
        intensity += min(text.count("!") * 0.1, 0.3)
        intensity += min(text.count("?") * 0.05, 0.1)

        # Capital letters (shouting)
        if text.isupper() and len(text) > 3:
            intensity += 0.2

        return min(intensity, 1.0)

    def _combine_emotion_scores(
            self, *weighted_scores) -> Dict[EmotionCategory, float]:
        """Combine multiple emotion score dictionaries with weights"""
        combined = {}
        total_weight = sum(weight for scores, weight in weighted_scores)

        for scores, weight in weighted_scores:
            normalized_weight = weight / total_weight
            for emotion, score in scores.items():
                combined[emotion] = combined.get(emotion, 0) + (
                    score * normalized_weight
                )

        return combined

    def _get_primary_emotion(
        self, emotions: Dict[EmotionCategory, float]
    ) -> EmotionCategory:
        """Get primary emotion with confidence thresholding"""
        if not emotions:
            return EmotionCategory.NEUTRAL

        max_emotion = max(emotions.items(), key=lambda x: x[1])

        # Require minimum confidence for non-neutral emotions
        if max_emotion[1] < 0.3:
            return EmotionCategory.NEUTRAL

        return max_emotion[0]

    def _calculate_confidence(
        self,
        emotions: Dict[EmotionCategory, float],
        primary_emotion: EmotionCategory,
        intensity: float,
    ) -> float:
        """Calculate confidence score for the emotion detection"""
        if not emotions or primary_emotion not in emotions:
            return 0.5

        primary_score = emotions[primary_emotion]

        # Calculate score separation (how much primary dominates)
        other_scores = [
            score for emotion,
            score in emotions.items() if emotion != primary_emotion]
        if other_scores:
            max_other = max(other_scores)
            separation = primary_score - max_other
        else:
            separation = primary_score

        # Base confidence from primary score
        confidence = primary_score

        # Boost confidence based on separation
        confidence += separation * 0.3

        # Boost confidence based on intensity
        confidence += intensity * 0.2

        return min(confidence, 1.0)

    def _calculate_sentiment(
            self, emotions: Dict[EmotionCategory, float]) -> float:
        """Calculate overall sentiment score (-1 to 1)"""
        positive_emotions = [
            EmotionCategory.HAPPY,
            EmotionCategory.EXCITED,
            EmotionCategory.LOVE,
            EmotionCategory.JOY,
        ]
        negative_emotions = [
            EmotionCategory.SAD,
            EmotionCategory.ANGRY,
            EmotionCategory.SCARED,
            EmotionCategory.CONFUSED,
        ]

        positive_score = sum(emotions.get(e, 0) for e in positive_emotions)
        negative_score = sum(emotions.get(e, 0) for e in negative_emotions)

        if positive_score + negative_score == 0:
            return 0.0

        return (positive_score - negative_score) / \
            (positive_score + negative_score)

    def _calculate_arousal(
        self, emotion: EmotionCategory, text: str, intensity: float
    ) -> float:
        """Calculate emotional arousal level (0 to 1)"""
        high_arousal = [
            EmotionCategory.EXCITED,
            EmotionCategory.ANGRY,
            EmotionCategory.SCARED,
            EmotionCategory.SURPRISE,
        ]
        low_arousal = [
            EmotionCategory.TIRED,
            EmotionCategory.SAD,
            EmotionCategory.CONFUSED,
        ]

        base_arousal = 0.5

        if emotion in high_arousal:
            base_arousal = 0.8
        elif emotion in low_arousal:
            base_arousal = 0.3

        # Apply intensity multiplier
        arousal = base_arousal * (0.5 + intensity * 0.5)

        return min(arousal, 1.0)

    def _extract_emotional_keywords(
            self, text: str, language: str) -> List[str]:
        """Extract keywords that indicate emotion"""
        keywords = []

        # Extract from emotion keywords
        for emotion_keywords in self._emotion_keywords.values():
            for keyword in emotion_keywords:
                if keyword in text and keyword not in keywords:
                    keywords.append(keyword)

        # Extract emotional punctuation patterns
        if "!" in text:
            keywords.append("exclamation")
        if "?" in text:
            keywords.append("question")
        if "..." in text:
            keywords.append("hesitation")

        return keywords[:5]  # Return top 5 keywords

    # ================== HUME AI HELPER METHODS ==================

    def _get_dominant_emotion(self, emotion_data: Dict) -> str:
        """Extract dominant emotion from Hume AI response"""
        try:
            predictions = emotion_data.get("predictions", [])
            if predictions:
                emotions = predictions[0].get("emotions", {})
                if emotions:
                    dominant = max(emotions.items(), key=lambda x: x[1])
                    return dominant[0]
        except Exception as e:
            logger.warning(f"Ignored exception: {e}")
        return "neutral"

    def _extract_confidence(self, emotion_data: Dict) -> float:
        """Extract confidence score from Hume AI response"""
        try:
            predictions = emotion_data.get("predictions", [])
            if predictions:
                emotions = predictions[0].get("emotions", {})
                if emotions:
                    max_score = max(emotions.values())
                    return min(max_score, 1.0)
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return 0.5

    def _map_hume_emotion(self, hume_emotion: str) -> EmotionCategory:
        """Map Hume AI emotion to our emotion categories"""
        emotion_mapping = {
            "joy": EmotionCategory.HAPPY,
            "sadness": EmotionCategory.SAD,
            "anger": EmotionCategory.ANGRY,
            "fear": EmotionCategory.SCARED,
            "surprise": EmotionCategory.SURPRISE,
            "excitement": EmotionCategory.EXCITED,
            "confusion": EmotionCategory.CONFUSED,
            "neutral": EmotionCategory.NEUTRAL,
            "love": EmotionCategory.LOVE,
            "curiosity": EmotionCategory.CURIOUS,
        }

        return emotion_mapping.get(
            hume_emotion.lower(),
            EmotionCategory.NEUTRAL)

    async def _fallback_audio_analysis(
        self, audio_file_path: str, language: str
    ) -> EmotionAnalysis:
        """Fallback audio analysis when Hume AI is not available"""
        return EmotionAnalysis(
            primary_emotion=EmotionCategory.NEUTRAL,
            confidence=0.4,
            language=language,
            analysis_method="audio_fallback",
            metadata={
                "error": "Hume AI not available",
                "audio_file": audio_file_path,
                "fallback_used": True,
            },
        )

    # ================== REPORTING AND HISTORY METHODS ==================

    def get_emotion_report(self, days: int = 7) -> pd.DataFrame:
        """Generate emotion report for parents (from audio history)"""
        try:
            df = pd.DataFrame(self.emotion_history)
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                # Filter by days
                cutoff_date = datetime.now() - pd.Timedelta(days=days)
                df = df[df["timestamp"] >= cutoff_date]
            return df
        except Exception as e:
            # Return empty DataFrame if pandas not available
            return None

    def save_history(self, filepath: str) -> None:
        """Save emotion history to file"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    self.emotion_history,
                    f,
                    ensure_ascii=False,
                    indent=2)
        except Exception as e:
            if logger:
                logger.error(f"Failed to save emotion history: {str(e)}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the analyzer."""
        return {
            "total_analyses": self._analysis_count,
            "avg_processing_time_ms": (
                self._total_processing_time / self._analysis_count
                if self._analysis_count > 0
                else 0
            ),
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Provides a simplified analysis, returning a dictionary.

        This method is kept for backwards compatibility or for use cases
        where a simple dictionary output is preferred over the full
        EmotionAnalysis object.
        """
        # Define a list of analysis functions (checkers)
        checkers = [
            self._analyze_keywords,
            self._analyze_emojis,
            self._analyze_cultural_patterns,
        ]

        # Run all checkers and collect scores
        emotion_scores: Dict[EmotionCategory, float] = {}
        for checker in checkers:
            # Defaulting to English for simplicity
            scores = checker(text, "en")
            for emotion, score in scores.items():
                emotion_scores[emotion] = emotion_scores.get(
                    emotion, 0) + score

        if not emotion_scores:
            return {
                "primary_emotion": "neutral",
                "confidence": 0.5,
                "details": {}}

        # Determine primary emotion
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[primary_emotion] / \
            sum(emotion_scores.values())

        return {
            "primary_emotion": primary_emotion.value,
            "confidence": round(
                confidence,
                2),
            "details": {
                e.value: round(
                    s,
                    2) for e,
                s in emotion_scores.items()},
        }


# ================== EXPORT FOR COMPATIBILITY ==================

# For backward compatibility with different import patterns
EmotionAnalyzer = EmotionAnalyzer
EmotionResult = EmotionAnalysis  # Alias for older code
