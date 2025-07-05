# Transformers imports patched for development
from ....domain.emotion.models import (BehavioralIndicator, EmotionContext,
                                       EmotionResult)
import structlog
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import asyncio
"""Core emotion analysis service."""


logger = structlog.get_logger(__name__)

# For text emotion analysis
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    try:
        from src.infrastructure.external_services.mock.transformers import pipeline
        TRANSFORMERS_AVAILABLE = True
    except ImportError:
        TRANSFORMERS_AVAILABLE = False
        logger.warning(
            " Transformers not installed. Install with: pip install transformers")

# For audio emotion analysis
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning(" Librosa not installed. Install with: pip install librosa")


class EmotionAnalysisService:
    """Core emotion analysis service using AI models."""

    def __init__(self):
        self.text_analyzer = None
        self._initialize_models()

        # Child-friendly emotion mappings
        self.child_emotions = {
            'happy': ['joy', 'excitement', 'playful', 'content'],
            'sad': ['upset', 'disappointed', 'lonely', 'hurt'],
            'angry': ['frustrated', 'annoyed', 'mad'],
            'scared': ['anxious', 'worried', 'nervous', 'afraid'],
            'calm': ['relaxed', 'peaceful', 'comfortable'],
            'curious': ['interested', 'wondering', 'questioning']
        }

        # Behavioral indicators for each emotion
        self.behavioral_patterns = {
            'happy': ['increased speech rate', 'higher pitch', 'more words', 'laughter'],
            'sad': ['slower speech', 'lower pitch', 'shorter responses', 'sighs'],
            'angry': ['louder voice', 'sharp tone', 'interruptions'],
            'scared': ['trembling voice', 'hesitation', 'whispers'],
            'calm': ['steady speech', 'normal pace', 'clear articulation'],
            'curious': ['questions', 'rising intonation', 'engagement']
        }

    def _initialize_models(self) -> None:
        """Initialize AI models for emotion analysis."""
        if TRANSFORMERS_AVAILABLE:
            try:
                self.text_analyzer = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    return_all_scores=True
                )
                logger.info(" Text emotion analyzer initialized")
            except Exception as e:
                logger.error(f" Failed to load text emotion model: {e}")
                self.text_analyzer = None

    async def analyze_comprehensive(
        self,
        text: Optional[str] = None,
        audio_data: Optional[np.ndarray] = None,
        audio_sr: Optional[int] = None,
        context: Optional[EmotionContext] = None
    ) -> EmotionResult:
        """Comprehensive emotion analysis from text and/or audio.

        Args:
            text: Text to analyze
            audio_data: Audio waveform as numpy array
            audio_sr: Audio sample rate
            context: Additional context information

        Returns:
            EmotionResult with detailed analysis
        """
        results = []

        # Analyze text if provided
        if text:
            text_emotion = await self._analyze_text(text)
            if text_emotion:
                results.append(('text', text_emotion))

        # Analyze audio if provided
        if audio_data is not None and audio_sr:
            audio_emotion = await self._analyze_audio(audio_data, audio_sr)
            if audio_emotion:
                results.append(('audio', audio_emotion))

        # Combine results
        if results:
            final_emotion = self._combine_results(results, context)
        else:
            final_emotion = self._get_default_emotion()

        # Generate recommendations
        final_emotion.recommendations = self._generate_recommendations(
            final_emotion.primary_emotion, context
        )

        return final_emotion

    async def _analyze_text(self, text: str) -> Optional[EmotionResult]:
        """Analyze emotions from text using transformer model."""
        if not text.strip():
            return None

        if self.text_analyzer:
            try:
                predictions = self.text_analyzer(text)

                emotion_scores = {}
                for pred in predictions[0]:
                    emotion = pred['label'].lower()
                    score = pred['score']
                    emotion_scores[emotion] = score

                mapped_scores = self._map_to_child_emotions(emotion_scores)
                primary = max(mapped_scores.items(), key=lambda x: x[1])
                indicators = self._extract_text_indicators(text, primary[0])

                return EmotionResult(
                    primary_emotion=primary[0],
                    confidence=primary[1],
                    all_emotions=mapped_scores,
                    source='text',
                    timestamp=datetime.now().isoformat(),
                    behavioral_indicators=indicators,
                    recommendations=[]
                )
            except Exception as e:
                logger.error(f" Text analysis error: {e}")

        # Fallback to rule-based analysis
        return self._analyze_text_rules_refactored(text)

    def _get_emotion_score(self, text_lower: str, keywords: List[str], emotion: str) -> Tuple[float, List[str]]:
        """Calculates the score for a given emotion based on keywords."""
        score = 0.0
        indicators = []
        for word in keywords:
            if word in text_lower:
                score += 0.3
                indicators.append(f"{emotion} word: {word}")
        return score, indicators

    def _analyze_text_rules_refactored(self, text: str) -> EmotionResult:
        """Rule-based text emotion analysis as fallback."""
        text_lower = text.lower()
        scores = {emotion: 0.0 for emotion in self.child_emotions.keys()}
        indicators = []

        emotion_keywords = {
            "happy": ['يضحك', 'سعيد', 'مرح', 'رائع', 'أحب', 'happy', 'laugh', 'fun', 'love', 'great'],
            "sad": ['حزين', 'بكي', 'متضايق', 'sad', 'cry', 'upset', 'hurt'],
            "angry": ['غاضب', 'زعلان', 'angry', 'mad', 'frustrated'],
            "scared": ['خائف', 'قلق', 'scared', 'afraid', 'worried']
        }

        for emotion, keywords in emotion_keywords.items():
            score, new_indicators = self._get_emotion_score(
                text_lower, keywords, emotion)
            scores[emotion] += score
            indicators.extend(new_indicators)

        # Questions indicate curiosity
        if '?' in text or 'why' in text_lower or 'what' in text_lower or 'how' in text_lower:
            scores['curious'] += 0.2
            indicators.append("questioning")

        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        else:
            scores['calm'] = 0.5  # Default emotion if no indicators found

        primary = max(scores.items(), key=lambda x: x[1]) if scores else (
            'calm', 0.5)

        return EmotionResult(
            primary_emotion=primary[0],
            # Cap confidence for rule-based method
            confidence=min(primary[1], 0.8),
            all_emotions=scores,
            source='text_rules',
            timestamp=datetime.now().isoformat(),
            behavioral_indicators=indicators,
            recommendations=[]
        )

    def _map_to_child_emotions(
            self, emotion_scores: Dict[str, float]) -> Dict[str, float]:
        """Map general emotions to child-friendly categories."""
        child_scores = {emotion: 0.0 for emotion in self.child_emotions.keys()}

        mapping = {
            'joy': 'happy', 'happiness': 'happy', 'love': 'happy',
            'sadness': 'sad', 'grief': 'sad',
            'anger': 'angry', 'rage': 'angry',
            'fear': 'scared', 'anxiety': 'scared', 'worry': 'scared',
            'neutral': 'calm', 'surprise': 'curious'
        }

        for emotion, score in emotion_scores.items():
            emotion_lower = emotion.lower()
            if emotion_lower in mapping:
                child_scores[mapping[emotion_lower]] += score
            else:
                child_scores['calm'] += score * 0.5

        # Normalize
        total = sum(child_scores.values())
        if total > 0:
            child_scores = {k: v / total for k, v in child_scores.items()}

        return child_scores

    def _extract_text_indicators(self, text: str, emotion: str) -> List[str]:
        """Extract behavioral indicators from text."""
        indicators = []

        word_count = len(text.split())
        if word_count < 5:
            indicators.append("short response")
        elif word_count > 20:
            indicators.append("long response")

        if text.count('!') > 1:
            indicators.append("multiple exclamations")
        if text.count('?') > 1:
            indicators.append("multiple questions")
        if '...' in text:
            indicators.append("hesitation")

        if any(word.isupper() and len(word) > 1 for word in text.split()):
            indicators.append("emphasis/shouting")

        return indicators

    def _generate_recommendations(
        self,
        emotion: str,
        context: Optional[EmotionContext]
    ) -> List[str]:
        """Generate contextual recommendations based on emotion."""
        recommendations = []

        if emotion == 'happy':
            recommendations.extend([
                "Continue engaging in positive activities",
                "Share happy moments with family",
                "Encourage creative expression"
            ])
        elif emotion == 'sad':
            recommendations.extend([
                "Provide comfort and emotional support",
                "Engage in calming activities",
                "Consider professional help if persistent"
            ])
        elif emotion == 'angry':
            recommendations.extend([
                "Help child express feelings safely",
                "Practice deep breathing exercises",
                "Identify anger triggers"
            ])
        elif emotion == 'scared':
            recommendations.extend([
                "Provide reassurance and safety",
                "Talk through fears together",
                "Create positive bedtime routines"
            ])
        elif emotion == 'curious':
            recommendations.extend([
                "Encourage questions and exploration",
                "Provide educational activities",
                "Foster learning opportunities"
            ])

        return recommendations

    def _get_default_emotion(self) -> EmotionResult:
        """Return default emotion when analysis fails."""
        return EmotionResult(
            primary_emotion='calm',
            confidence=0.5,
            all_emotions={'calm': 0.5, 'happy': 0.3, 'curious': 0.2},
            source='default',
            timestamp=datetime.now().isoformat(),
            behavioral_indicators=[],
            recommendations=["Continue monitoring emotional state"]
        )
