import asyncio
import logging
from typing import Any, Dict, Optional

from .models import EmotionAnalysis
from .pattern_loader import load_cultural_patterns, load_emoji_emotions, load_emotion_keywords
from .text_analyzer import TextEmotionAnalyzer
from .audio_analyzer import AudioEmotionAnalyzer, HUME_AVAILABLE

# Optional Hume client for audio analysis
if HUME_AVAILABLE:
    from hume.client import AsyncHumeClient

logger = logging.getLogger(__name__)


class UnifiedEmotionAnalyzer:
    """
    Orchestrates emotion analysis by combining results from specialized
    text and audio analyzers.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.api_key = self.config.get("hume_api_key")

        # Load patterns and initialize analyzers
        emotion_keywords = load_emotion_keywords()
        emoji_emotions = load_emoji_emotions()
        cultural_patterns = load_cultural_patterns()

        self.text_analyzer = TextEmotionAnalyzer(
            emotion_keywords, emoji_emotions, cultural_patterns)

        hume_client = None
        if HUME_AVAILABLE and self.api_key:
            hume_client = AsyncHumeClient(self.api_key)
        self.audio_analyzer = AudioEmotionAnalyzer(hume_client)

        logger.info("✅ Unified Emotion Analyzer initialized")

    async def analyze(
        self, text: Optional[str] = None, audio_file_path: Optional[str] = None, language: str = "ar"
    ) -> EmotionAnalysis:
        """
        Performs hybrid emotion analysis by combining text and audio modalities.
        """
        if not text and not audio_file_path:
            raise ValueError(
                "Either text or audio_file_path must be provided.")

        tasks = {}
        if text:
            tasks["text"] = self.text_analyzer.analyze(text, language)
        if audio_file_path:
            tasks["audio"] = self.audio_analyzer.analyze(
                audio_file_path, language)

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        analysis_results = {key: res for key, res in zip(
            tasks.keys(), results) if not isinstance(res, Exception)}

        text_result = analysis_results.get("text")
        audio_result = analysis_results.get("audio")

        if text_result and audio_result:
            return self._combine_hybrid_results(text_result, audio_result, language)

        return text_result or audio_result or self._fallback_analysis(language)

    def _combine_hybrid_results(self, text_result: EmotionAnalysis, audio_result: EmotionAnalysis, language: str) -> EmotionAnalysis:
        """Combines results from text and audio analysis."""
        primary_emotion = text_result.primary_emotion if text_result.confidence >= audio_result.confidence else audio_result.primary_emotion
        combined_confidence = (text_result.confidence +
                               audio_result.confidence) / 2

        return EmotionAnalysis(
            primary_emotion=primary_emotion,
            confidence=combined_confidence,
            secondary_emotions={
                **text_result.secondary_emotions, **audio_result.secondary_emotions},
            sentiment_score=(text_result.sentiment_score +
                             audio_result.sentiment_score) / 2,
            arousal_level=(text_result.arousal_level +
                           audio_result.arousal_level) / 2,
            language=language,
            analysis_method="hybrid",
            metadata={"text_confidence": text_result.confidence,
                      "audio_confidence": audio_result.confidence}
        )

    def _fallback_analysis(self, language: str) -> EmotionAnalysis:
        return EmotionAnalysis(
            primary_emotion="neutral",
            confidence=0.0,
            language=language,
            analysis_method="fallback",
            metadata={"error": "All analysis methods failed."}
        )
