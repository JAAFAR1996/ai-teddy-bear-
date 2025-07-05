#!/usr/bin/env python3
"""
Emotion Analyzer Module - Extracted from main_service.py
Handles emotion analysis for AI Teddy Bear interactions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import structlog


@dataclass
class EmotionResult:
    """Emotion analysis result"""

    primary_emotion: str
    confidence: float
    secondary_emotions: Dict[str, float] = field(default_factory=dict)
    valence: float = 0.0  # -1 to 1 (negative to positive)
    arousal: float = 0.0  # 0 to 1 (calm to excited)

    def to_dict(self) -> Dict:
        return {
            "primary": self.primary_emotion,
            "confidence": self.confidence,
            "secondary": self.secondary_emotions,
            "valence": self.valence,
            "arousal": self.arousal,
        }


class EmotionAnalyzer:
    """Analyzes emotions from text and audio inputs"""

    def __init__(self, ai_service=None):
        self.logger = structlog.get_logger()
        self.ai_service = ai_service

        # Emotion keywords mapping
        self.emotion_keywords = {
            "happy": [
                "happy",
                "glad",
                "excited",
                "joy",
                "fun",
                "great",
                "awesome",
                "love",
            ],
            "sad": ["sad", "cry", "upset", "miss", "lonely", "hurt", "bad"],
            "angry": ["angry", "mad", "hate", "annoying", "stupid", "mean"],
            "scared": ["scared", "afraid", "scary", "monster", "dark", "nightmare"],
            "surprised": ["wow", "amazing", "really", "oh", "surprised", "unexpected"],
            "neutral": ["okay", "fine", "alright", "yes", "no", "maybe"],
        }

    async def analyze_multimodal(
        self, text: str, audio_data: bytes, context: Optional[Dict] = None
    ) -> Dict:
        """Analyze emotions from both text and audio"""

        # Text-based emotion analysis
        text_emotion = await self.analyze_text(text)

        # Audio-based emotion analysis (if available)
        audio_emotion = await self.analyze_audio(audio_data) if audio_data else None

        # Combine results
        combined_result = self._combine_emotion_results(
            text_emotion, audio_emotion, context
        )

        return combined_result

    async def analyze_text(self, text: str) -> EmotionResult:
        """Analyze emotion from text"""

        # Simple keyword-based analysis first
        keyword_emotion = self._analyze_keywords(text)

        # Use AI service if available
        if self.ai_service:
            try:
                ai_result = await self.ai_service.analyze_emotion(text)
                return EmotionResult(
                    primary_emotion=ai_result.get("primary", keyword_emotion),
                    confidence=ai_result.get("confidence", 0.7),
                    secondary_emotions=ai_result.get("secondary", {}),
                    valence=ai_result.get("valence", 0.0),
                    arousal=ai_result.get("arousal", 0.5),
                )
            except Exception as e:
                self.logger.warning(f"AI emotion analysis failed: {e}")

        # Fallback to keyword analysis
        return EmotionResult(
            primary_emotion=keyword_emotion,
            confidence=0.6,
            secondary_emotions={},
            valence=self._calculate_valence(keyword_emotion),
            arousal=0.5,
        )

    async def analyze_audio(
            self,
            audio_data: bytes) -> Optional[EmotionResult]:
        """Analyze emotion from audio (voice tone, pitch, etc.)"""

        # This would integrate with audio analysis services
        # For now, return None as placeholder

        # Future implementation could use:
        # - Voice pitch analysis
        # - Speech rate analysis
        # - Voice energy/volume analysis
        # - Integration with services like Hume AI

        return None

    def _analyze_keywords(self, text: str) -> str:
        """Simple keyword-based emotion detection"""
        text_lower = text.lower()
        emotion_scores = {}

        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score

        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)

        return "neutral"

    def _calculate_valence(self, emotion: str) -> float:
        """Calculate emotional valence based on emotion type"""
        valence_map = {
            "happy": 0.8,
            "excited": 0.9,
            "surprised": 0.5,
            "neutral": 0.0,
            "sad": -0.7,
            "angry": -0.8,
            "scared": -0.6,
        }
        return valence_map.get(emotion, 0.0)

    def _combine_emotion_results(
        self,
        text_emotion: EmotionResult,
        audio_emotion: Optional[EmotionResult],
        context: Optional[Dict],
    ) -> Dict:
        """Combine text and audio emotion analysis results"""

        # If no audio analysis, return text result
        if not audio_emotion:
            return text_emotion.to_dict()

        # Weighted average of text and audio results
        # Text gets 60% weight, audio gets 40% weight
        combined_confidence = (
            text_emotion.confidence * 0.6 + audio_emotion.confidence * 0.4
        )

        combined_valence = text_emotion.valence * 0.6 + audio_emotion.valence * 0.4

        combined_arousal = text_emotion.arousal * 0.6 + audio_emotion.arousal * 0.4

        # Choose primary emotion based on higher confidence
        primary_emotion = (
            text_emotion.primary_emotion
            if text_emotion.confidence > audio_emotion.confidence
            else audio_emotion.primary_emotion
        )

        # Merge secondary emotions
        secondary_emotions = {
            **text_emotion.secondary_emotions,
            **audio_emotion.secondary_emotions,
        }

        return {
            "primary": primary_emotion,
            "confidence": combined_confidence,
            "secondary": secondary_emotions,
            "valence": combined_valence,
            "arousal": combined_arousal,
            "text_emotion": text_emotion.to_dict(),
            "audio_emotion": audio_emotion.to_dict() if audio_emotion else None,
        }

    def map_emotion_to_voice(self, emotion_result: EmotionResult) -> str:
        """Map emotion result to voice emotion parameter"""

        # Map based on primary emotion and arousal
        if emotion_result.primary_emotion == "happy":
            return "cheerful" if emotion_result.arousal > 0.7 else "friendly"
        elif emotion_result.primary_emotion == "sad":
            return "sympathetic"
        elif emotion_result.primary_emotion == "scared":
            return "comforting"
        elif emotion_result.primary_emotion == "angry":
            return "calm"  # Respond to anger with calmness
        elif emotion_result.primary_emotion == "excited":
            return "enthusiastic"
        else:
            return "warm"  # Default friendly tone
