"""
🎭 Unified Emotion Analyzer - Complete Implementation 2025
Combines text analysis, audio analysis (Hume AI), and multi-modal emotion detection
Merged from 3 different emotion analyzer implementations for maximum capability
"""

import re
import asyncio
import json
import requests
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import structlog
from opentelemetry import trace

# Optional imports for advanced features
try:
    from hume.client import AsyncHumeClient
    from hume import StreamDataModels
    HUME_AVAILABLE = True
except ImportError:
    HUME_AVAILABLE = False

try:
    from src.application.services.service_registry import ServiceBase
    from src.infrastructure.observability import trace_async
    SERVICE_REGISTRY_AVAILABLE = True
except ImportError:
    SERVICE_REGISTRY_AVAILABLE = False

logger = structlog.get_logger() if 'structlog' in globals() else None


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
    secondary_emotions: Dict[EmotionCategory, float] = field(default_factory=dict)
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
    
    def __init__(self, registry=None, config: Dict = None, api_key: str = None):
        # Configuration
        self.config = config or {}
        self.api_key = api_key or self.config.get('hume_api_key')
        
        # Service registry integration (if available)
        if SERVICE_REGISTRY_AVAILABLE and registry:
            self.registry = registry
            self._state = getattr(self, 'ServiceState', type('ServiceState', (), {'READY': 'ready'})).READY
        else:
            self.registry = None
            self._state = 'ready'
        
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
        self._state = 'ready'
    
    async def shutdown(self) -> None:
        """Shutdown the analyzer"""
        self._state = 'stopped'
    
    async def health_check(self) -> Dict:
        """Health check for service monitoring"""
        return {
            "healthy": self._state == 'ready',
            "service": "unified_emotion_analyzer",
            "features": {
                "text_analysis": True,
                "audio_analysis": HUME_AVAILABLE and self.hume_client is not None,
                "hume_integration": HUME_AVAILABLE,
                "cultural_awareness": True
            },
            "analysis_count": self._analysis_count,
            "avg_processing_time_ms": self._total_processing_time / max(self._analysis_count, 1)
        }
    
    # ================== MAIN ANALYSIS METHODS ==================
    
    async def analyze(self, text: str, language: str = "ar") -> EmotionAnalysis:
        """
        🎯 Main analysis method with Service Registry compatibility
        Enhanced text analysis with cultural awareness
        """
        return await self.analyze_text_emotion(text, language)
    
    async def analyze_text_emotion(self, text: str, language: str = "ar") -> EmotionAnalysis:
        """
        🔤 Comprehensive text-based emotion analysis
        Supports Arabic and English with cultural context
        """
        start_time = datetime.now()
        self._analysis_count += 1
        
        try:
            # Clean and prepare text
            text_clean = text.strip().lower()
            
            # Multi-method analysis
            keyword_emotions = self._analyze_keywords(text_clean, language)
            emoji_emotions = self._analyze_emojis(text)
            cultural_emotions = self._analyze_cultural_patterns(text_clean, language)
            intensity_score = self._analyze_intensity(text)
            
            # Combine all emotion scores with weights
            all_emotions = self._combine_emotion_scores(
                (keyword_emotions, 0.4),
                (emoji_emotions, 0.3), 
                (cultural_emotions, 0.3)
            )
            
            # Determine primary emotion
            primary_emotion = self._get_primary_emotion(all_emotions)
            confidence = self._calculate_confidence(all_emotions, primary_emotion, intensity_score)
            
            # Calculate sentiment and arousal
            sentiment_score = self._calculate_sentiment(all_emotions)
            arousal_level = self._calculate_arousal(primary_emotion, text, intensity_score)
            
            # Extract emotional keywords
            keywords = self._extract_emotional_keywords(text_clean, language)
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._total_processing_time += processing_time
            
            result = EmotionAnalysis(
                primary_emotion=primary_emotion,
                confidence=confidence,
                secondary_emotions={k: v for k, v in all_emotions.items() if k != primary_emotion},
                sentiment_score=sentiment_score,
                arousal_level=arousal_level,
                keywords=keywords,
                language=language,
                analysis_method="text",
                processing_time_ms=processing_time,
                metadata={
                    "text_length": len(text),
                    "intensity_score": intensity_score,
                    "methods_used": ["keywords", "emojis", "cultural_patterns"]
                }
            )
            
            if logger:
                logger.info(f"🎭 Text emotion analysis completed", 
                          emotion=primary_emotion.value, 
                          confidence=confidence,
                          processing_time_ms=processing_time)
            
            return result
            
        except Exception as e:
            if logger:
                logger.error(f"❌ Text emotion analysis failed: {str(e)}")
            
            # Return neutral fallback
            return EmotionAnalysis(
                primary_emotion=EmotionCategory.NEUTRAL,
                confidence=0.5,
                language=language,
                analysis_method="text_fallback",
                metadata={"error": str(e)}
            )
    
    async def analyze_audio_emotion(self, audio_file_path: str, language: str = "ar") -> EmotionAnalysis:
        """
        🎤 Audio-based emotion analysis using Hume AI
        Advanced audio emotion detection with streaming support
        """
        if not HUME_AVAILABLE or not self.hume_client:
            if logger:
                logger.warning("⚠️ Hume AI not available for audio analysis")
            return await self._fallback_audio_analysis(audio_file_path, language)
        
        start_time = datetime.now()
        
        try:
            # Setup audio data model
            config = StreamDataModels.voice()
            
            # Read audio file
            with open(audio_file_path, "rb") as f:
                audio_bytes = f.read()
            
            # Process with Hume AI
            async with self.hume_client.connect([config]) as socket:
                await socket.send_bytes(audio_bytes)
                result = await socket.recv()
            
            # Extract emotion data
            emotion_data = result.get("voice", {})
            dominant_emotion = self._get_dominant_emotion(emotion_data)
            confidence = self._extract_confidence(emotion_data)
            
            # Convert to our emotion categories
            emotion_category = self._map_hume_emotion(dominant_emotion)
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Store in history
            emotion_result = {
                'timestamp': datetime.now().isoformat(),
                'emotions': emotion_data,
                'dominant_emotion': dominant_emotion,
                'audio_file': audio_file_path,
                'confidence': confidence
            }
            self.emotion_history.append(emotion_result)
            
            analysis = EmotionAnalysis(
                primary_emotion=emotion_category,
                confidence=confidence,
                language=language,
                analysis_method="audio_hume",
                processing_time_ms=processing_time,
                metadata={
                    "hume_emotion": dominant_emotion,
                    "hume_data": emotion_data,
                    "audio_file": audio_file_path
                }
            )
            
            if logger:
                logger.info(f"🎤 Audio emotion analysis completed",
                          emotion=emotion_category.value,
                          hume_emotion=dominant_emotion,
                          confidence=confidence)
            
            return analysis
            
        except Exception as e:
            if logger:
                logger.error(f"❌ Audio emotion analysis failed: {str(e)}")
            return await self._fallback_audio_analysis(audio_file_path, language)
    
    async def analyze_hybrid(
        self, 
        text: str = None, 
        audio_file_path: str = None, 
        language: str = "ar"
    ) -> EmotionAnalysis:
        """
        🔄 Hybrid analysis combining text and audio
        Provides the most accurate emotion detection
        """
        start_time = datetime.now()
        
        analyses = []
        methods_used = []
        
        # Text analysis
        if text:
            text_analysis = await self.analyze_text_emotion(text, language)
            analyses.append((text_analysis, 0.6))  # Higher weight for text
            methods_used.append("text")
        
        # Audio analysis  
        if audio_file_path:
            audio_analysis = await self.analyze_audio_emotion(audio_file_path, language)
            analyses.append((audio_analysis, 0.4))
            methods_used.append("audio")
        
        if not analyses:
            raise ValueError("At least text or audio must be provided")
        
        # Combine analyses
        combined_emotions = {}
        total_weight = 0
        combined_confidence = 0
        combined_sentiment = 0
        combined_arousal = 0
        
        for analysis, weight in analyses:
            total_weight += weight
            combined_confidence += analysis.confidence * weight
            combined_sentiment += analysis.sentiment_score * weight
            combined_arousal += analysis.arousal_level * weight
            
            # Combine emotions
            combined_emotions[analysis.primary_emotion] = \
                combined_emotions.get(analysis.primary_emotion, 0) + weight
            
            for emotion, score in analysis.secondary_emotions.items():
                combined_emotions[emotion] = \
                    combined_emotions.get(emotion, 0) + (score * weight * 0.5)
        
        # Normalize
        combined_confidence /= total_weight
        combined_sentiment /= total_weight
        combined_arousal /= total_weight
        
        # Get primary emotion
        primary_emotion = max(combined_emotions.items(), key=lambda x: x[1])[0]
        
        # Calculate processing time
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        result = EmotionAnalysis(
            primary_emotion=primary_emotion,
            confidence=combined_confidence,
            secondary_emotions={k: v for k, v in combined_emotions.items() if k != primary_emotion},
            sentiment_score=combined_sentiment,
            arousal_level=combined_arousal,
            language=language,
            analysis_method="hybrid",
            processing_time_ms=processing_time,
            metadata={
                "methods_used": methods_used,
                "text_provided": text is not None,
                "audio_provided": audio_file_path is not None,
                "individual_analyses": len(analyses)
            }
        )
        
        if logger:
            logger.info(f"🔄 Hybrid emotion analysis completed",
                      emotion=primary_emotion.value,
                      confidence=combined_confidence,
                      methods=methods_used)
        
        return result
    
    # ================== PATTERN LOADING METHODS ==================
    
    def _load_emotion_keywords(self) -> Dict[EmotionCategory, List[str]]:
        """Enhanced emotion keywords with Arabic and English support"""
        return {
            EmotionCategory.HAPPY: [
                # English
                'happy', 'joy', 'glad', 'cheerful', 'delighted', 'excited', 'pleased',
                'joyful', 'thrilled', 'elated', 'content', 'satisfied', 'upbeat',
                # Arabic
                'سعيد', 'فرح', 'مبتهج', 'مسرور', 'فرحان', 'مبسوط', 'مستبشر',
                'مرح', 'منشرح', 'متفائل', 'راض', 'مطمئن'
            ],
            EmotionCategory.SAD: [
                # English  
                'sad', 'unhappy', 'depressed', 'down', 'blue', 'crying', 'upset',
                'melancholy', 'gloomy', 'sorrowful', 'dejected', 'heartbroken',
                # Arabic
                'حزين', 'مكتئب', 'يبكي', 'منزعج', 'مهموم', 'كئيب', 'محبط',
                'منكسر', 'متألم', 'حسير', 'متوجع'
            ],
            EmotionCategory.ANGRY: [
                # English
                'angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated',
                'enraged', 'livid', 'outraged', 'irate', 'vexed',
                # Arabic  
                'غاضب', 'منزعج', 'محبط', 'مستاء', 'متذمر', 'ثائر',
                'منفعل', 'مستشيط', 'متضايق', 'عصبي'
            ],
            EmotionCategory.SCARED: [
                # English
                'scared', 'afraid', 'frightened', 'worried', 'anxious', 'fearful',
                'terrified', 'nervous', 'panicked', 'alarmed', 'apprehensive',
                # Arabic
                'خائف', 'قلق', 'مرعوب', 'متوتر', 'فزع', 'مذعور',
                'مضطرب', 'متوجس', 'مهموم', 'متردد'
            ],
            EmotionCategory.EXCITED: [
                # English
                'excited', 'thrilled', 'enthusiastic', 'eager', 'pumped',
                'energetic', 'animated', 'exhilarated', 'electrified',
                # Arabic
                'متحمس', 'متشوق', 'منتشٍ', 'متوقد', 'متفعل',
                'متحرك', 'نشط', 'متيقظ'
            ],
            EmotionCategory.CURIOUS: [
                # English
                'curious', 'wondering', 'interested', 'question', 'why', 'how',
                'intrigued', 'inquisitive', 'puzzled about',
                # Arabic
                'فضولي', 'متسائل', 'مهتم', 'مستطلع', 'متتبع',
                'ليش', 'لماذا', 'كيف', 'متى', 'أين', 'ماذا'
            ],
            EmotionCategory.CONFUSED: [
                # English
                'confused', 'puzzled', 'unsure', 'don\'t understand', 'lost',
                'bewildered', 'perplexed', 'baffled',
                # Arabic
                'محتار', 'مشوش', 'لا أفهم', 'ضائع', 'متردد',
                'محيرني', 'غير واضح', 'مختلط'
            ],
            EmotionCategory.TIRED: [
                # English
                'tired', 'sleepy', 'exhausted', 'worn out', 'weary',
                'fatigued', 'drained', 'lethargic',
                # Arabic
                'متعب', 'نعسان', 'مرهق', 'منهك', 'مستنزف',
                'خامل', 'كسول', 'مجهد'
            ],
            EmotionCategory.LOVE: [
                # English
                'love', 'adore', 'cherish', 'treasure', 'care', 'affection',
                # Arabic
                'حب', 'أحب', 'عشق', 'أعشق', 'أهتم', 'أقدر'
            ],
            EmotionCategory.SURPRISE: [
                # English
                'surprised', 'amazed', 'astonished', 'shocked', 'wow',
                # Arabic
                'مفاجأة', 'مندهش', 'متعجب', 'مصدوم', 'واو'
            ]
        }
    
    def _load_emoji_emotions(self) -> Dict[str, EmotionCategory]:
        """Enhanced emoji to emotion mapping"""
        return {
            # Happy emotions
            '😊': EmotionCategory.HAPPY, '😁': EmotionCategory.HAPPY,
            '😄': EmotionCategory.HAPPY, '😃': EmotionCategory.HAPPY,
            '🙂': EmotionCategory.HAPPY, '😌': EmotionCategory.HAPPY,
            '😆': EmotionCategory.HAPPY, '🤗': EmotionCategory.HAPPY,
            
            # Love emotions
            '❤️': EmotionCategory.LOVE, '💕': EmotionCategory.LOVE,
            '😍': EmotionCategory.LOVE, '🥰': EmotionCategory.LOVE,
            '💖': EmotionCategory.LOVE, '💝': EmotionCategory.LOVE,
            
            # Sad emotions
            '😢': EmotionCategory.SAD, '😭': EmotionCategory.SAD,
            '😞': EmotionCategory.SAD, '☹️': EmotionCategory.SAD,
            '😔': EmotionCategory.SAD, '😿': EmotionCategory.SAD,
            '💔': EmotionCategory.SAD,
            
            # Angry emotions  
            '😠': EmotionCategory.ANGRY, '😡': EmotionCategory.ANGRY,
            '🤬': EmotionCategory.ANGRY, '😤': EmotionCategory.ANGRY,
            '💢': EmotionCategory.ANGRY, '🔥': EmotionCategory.ANGRY,
            
            # Scared emotions
            '😨': EmotionCategory.SCARED, '😰': EmotionCategory.SCARED,
            '😱': EmotionCategory.SCARED, '😟': EmotionCategory.SCARED,
            '😦': EmotionCategory.SCARED, '😧': EmotionCategory.SCARED,
            
            # Excited emotions
            '🤩': EmotionCategory.EXCITED, '🎉': EmotionCategory.EXCITED,
            '✨': EmotionCategory.EXCITED, '🚀': EmotionCategory.EXCITED,
            '⚡': EmotionCategory.EXCITED, '🎊': EmotionCategory.EXCITED,
            
            # Curious emotions
            '🤔': EmotionCategory.CURIOUS, '🧐': EmotionCategory.CURIOUS,
            '❓': EmotionCategory.CURIOUS, '❔': EmotionCategory.CURIOUS,
            
            # Confused emotions
            '😕': EmotionCategory.CONFUSED, '🤷': EmotionCategory.CONFUSED,
            '😵': EmotionCategory.CONFUSED, '🤯': EmotionCategory.CONFUSED,
            
            # Tired emotions
            '😴': EmotionCategory.TIRED, '🥱': EmotionCategory.TIRED,
            '😪': EmotionCategory.TIRED, '💤': EmotionCategory.TIRED,
            
            # Surprise emotions
            '😲': EmotionCategory.SURPRISE, '😮': EmotionCategory.SURPRISE,
            '🤭': EmotionCategory.SURPRISE, '😯': EmotionCategory.SURPRISE
        }
    
    def _load_cultural_patterns(self) -> Dict[str, Dict[EmotionCategory, float]]:
        """Cultural-specific emotional expressions"""
        return {
            # Arabic cultural expressions
            'الحمد لله': {EmotionCategory.HAPPY: 0.7, EmotionCategory.NEUTRAL: 0.3},
            'ما شاء الله': {EmotionCategory.HAPPY: 0.6, EmotionCategory.SURPRISE: 0.4},
            'يا ربي': {EmotionCategory.SURPRISED: 0.5, EmotionCategory.SCARED: 0.3},
            'وحشتني': {EmotionCategory.LOVE: 0.8, EmotionCategory.SAD: 0.2},
            'إن شاء الله': {EmotionCategory.NEUTRAL: 0.6, EmotionCategory.HAPPY: 0.4},
            'لا حول ولا قوة إلا بالله': {EmotionCategory.SAD: 0.5, EmotionCategory.SCARED: 0.3},
            
            # English cultural expressions
            'oh my god': {EmotionCategory.SURPRISE: 0.8, EmotionCategory.SCARED: 0.2},
            'no way': {EmotionCategory.SURPRISE: 0.7, EmotionCategory.CONFUSED: 0.3},
            'awesome': {EmotionCategory.EXCITED: 0.9, EmotionCategory.HAPPY: 0.1},
            'whatever': {EmotionCategory.NEUTRAL: 0.6, EmotionCategory.ANGRY: 0.4},
        }
    
    # ================== ANALYSIS HELPER METHODS ==================
    
    def _analyze_keywords(self, text: str, language: str) -> Dict[EmotionCategory, float]:
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
                normalized_score = min(score / (len(text_words) + len(keywords)), 1.0)
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
    
    def _analyze_cultural_patterns(self, text: str, language: str) -> Dict[EmotionCategory, float]:
        """Analyze cultural-specific emotional expressions"""
        scores = {}
        
        for pattern, emotions in self._cultural_patterns.items():
            if pattern in text:
                for emotion, weight in emotions.items():
                    scores[emotion] = scores.get(emotion, 0) + weight
        
        # Language-specific boosts
        if language == "ar":
            # Boost Arabic emotional expressions
            arabic_indicators = ['يا', 'آه', 'أوه', 'الله']
            for indicator in arabic_indicators:
                if indicator in text:
                    for emotion in scores:
                        scores[emotion] *= 1.1
        
        return {k: min(v, 1.0) for k, v in scores.items()}
    
    def _analyze_intensity(self, text: str) -> float:
        """Analyze emotional intensity markers"""
        intensity_markers = {
            'very': 0.3, 'really': 0.3, 'so': 0.2, 'extremely': 0.5,
            'incredibly': 0.4, 'absolutely': 0.4, 'totally': 0.3,
            'جداً': 0.4, 'كثير': 0.3, 'جداً جداً': 0.6, 'كتير': 0.3
        }
        
        intensity = 0.5  # Base intensity
        
        for marker, boost in intensity_markers.items():
            if marker in text.lower():
                intensity += boost
        
        # Punctuation intensity
        intensity += min(text.count('!') * 0.1, 0.3)
        intensity += min(text.count('?') * 0.05, 0.1)
        
        # Capital letters (shouting)
        if text.isupper() and len(text) > 3:
            intensity += 0.2
        
        return min(intensity, 1.0)
    
    def _combine_emotion_scores(self, *weighted_scores) -> Dict[EmotionCategory, float]:
        """Combine multiple emotion score dictionaries with weights"""
        combined = {}
        total_weight = sum(weight for scores, weight in weighted_scores)
        
        for scores, weight in weighted_scores:
            normalized_weight = weight / total_weight
            for emotion, score in scores.items():
                combined[emotion] = combined.get(emotion, 0) + (score * normalized_weight)
        
        return combined
    
    def _get_primary_emotion(self, emotions: Dict[EmotionCategory, float]) -> EmotionCategory:
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
        intensity: float
    ) -> float:
        """Calculate confidence score for the emotion detection"""
        if not emotions or primary_emotion not in emotions:
            return 0.5
        
        primary_score = emotions[primary_emotion]
        
        # Calculate score separation (how much primary dominates)
        other_scores = [score for emotion, score in emotions.items() if emotion != primary_emotion]
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
    
    def _calculate_sentiment(self, emotions: Dict[EmotionCategory, float]) -> float:
        """Calculate overall sentiment score (-1 to 1)"""
        positive_emotions = [
            EmotionCategory.HAPPY, EmotionCategory.EXCITED, 
            EmotionCategory.LOVE, EmotionCategory.JOY
        ]
        negative_emotions = [
            EmotionCategory.SAD, EmotionCategory.ANGRY, 
            EmotionCategory.SCARED, EmotionCategory.CONFUSED
        ]
        
        positive_score = sum(emotions.get(e, 0) for e in positive_emotions)
        negative_score = sum(emotions.get(e, 0) for e in negative_emotions)
        
        if positive_score + negative_score == 0:
            return 0.0
        
        return (positive_score - negative_score) / (positive_score + negative_score)
    
    def _calculate_arousal(
        self, 
        emotion: EmotionCategory, 
        text: str, 
        intensity: float
    ) -> float:
        """Calculate emotional arousal level (0 to 1)"""
        high_arousal = [
            EmotionCategory.EXCITED, EmotionCategory.ANGRY, 
            EmotionCategory.SCARED, EmotionCategory.SURPRISE
        ]
        low_arousal = [
            EmotionCategory.TIRED, EmotionCategory.SAD, 
            EmotionCategory.CONFUSED
        ]
        
        base_arousal = 0.5
        
        if emotion in high_arousal:
            base_arousal = 0.8
        elif emotion in low_arousal:
            base_arousal = 0.3
        
        # Apply intensity multiplier
        arousal = base_arousal * (0.5 + intensity * 0.5)
        
        return min(arousal, 1.0)
    
    def _extract_emotional_keywords(self, text: str, language: str) -> List[str]:
        """Extract keywords that indicate emotion"""
        keywords = []
        
        # Extract from emotion keywords
        for emotion_keywords in self._emotion_keywords.values():
            for keyword in emotion_keywords:
                if keyword in text and keyword not in keywords:
                    keywords.append(keyword)
        
        # Extract emotional punctuation patterns
        if '!' in text:
            keywords.append('exclamation')
        if '?' in text:
            keywords.append('question')
        if '...' in text:
            keywords.append('hesitation')
        
        return keywords[:5]  # Return top 5 keywords
    
    # ================== HUME AI HELPER METHODS ==================
    
    def _get_dominant_emotion(self, emotion_data: Dict) -> str:
        """Extract dominant emotion from Hume AI response"""
        try:
            predictions = emotion_data.get('predictions', [])
            if predictions:
                emotions = predictions[0].get('emotions', {})
                if emotions:
                    dominant = max(emotions.items(), key=lambda x: x[1])
                    return dominant[0]
        except Exception:
            pass
        return 'neutral'
    
    def _extract_confidence(self, emotion_data: Dict) -> float:
        """Extract confidence score from Hume AI response"""
        try:
            predictions = emotion_data.get('predictions', [])
            if predictions:
                emotions = predictions[0].get('emotions', {})
                if emotions:
                    max_score = max(emotions.values())
                    return min(max_score, 1.0)
        except Exception:
            pass
        return 0.5
    
    def _map_hume_emotion(self, hume_emotion: str) -> EmotionCategory:
        """Map Hume AI emotion to our emotion categories"""
        emotion_mapping = {
            'joy': EmotionCategory.HAPPY,
            'sadness': EmotionCategory.SAD,
            'anger': EmotionCategory.ANGRY,
            'fear': EmotionCategory.SCARED,
            'surprise': EmotionCategory.SURPRISE,
            'excitement': EmotionCategory.EXCITED,
            'confusion': EmotionCategory.CONFUSED,
            'neutral': EmotionCategory.NEUTRAL,
            'love': EmotionCategory.LOVE,
            'curiosity': EmotionCategory.CURIOUS
        }
        
        return emotion_mapping.get(hume_emotion.lower(), EmotionCategory.NEUTRAL)
    
    async def _fallback_audio_analysis(self, audio_file_path: str, language: str) -> EmotionAnalysis:
        """Fallback audio analysis when Hume AI is not available"""
        return EmotionAnalysis(
            primary_emotion=EmotionCategory.NEUTRAL,
            confidence=0.4,
            language=language,
            analysis_method="audio_fallback",
            metadata={
                "error": "Hume AI not available",
                "audio_file": audio_file_path,
                "fallback_used": True
            }
        )
    
    # ================== REPORTING AND HISTORY METHODS ==================
    
    def get_emotion_report(self, days: int = 7) -> pd.DataFrame:
        """Generate emotion report for parents (from audio history)"""
        try:
            df = pd.DataFrame(self.emotion_history)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                # Filter by days
                cutoff_date = datetime.now() - pd.Timedelta(days=days)
                df = df[df['timestamp'] >= cutoff_date]
            return df
        except Exception:
            # Return empty DataFrame if pandas not available
            return None
    
    def save_history(self, filepath: str):
        """Save emotion history to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.emotion_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            if logger:
                logger.error(f"Failed to save emotion history: {str(e)}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        return {
            "total_analyses": self._analysis_count,
            "average_processing_time_ms": self._total_processing_time / max(self._analysis_count, 1),
            "audio_history_entries": len(self.emotion_history),
            "hume_available": HUME_AVAILABLE and self.hume_client is not None,
            "service_registry_integration": SERVICE_REGISTRY_AVAILABLE,
            "supported_languages": ["ar", "en"],
            "analysis_methods": ["text", "audio", "hybrid"]
        }
    
    # ================== BACKWARD COMPATIBILITY ==================
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Simple backward compatibility method"""
        # Simple synchronous analysis for backward compatibility
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['happy', 'سعيد', 'فرح']):
            return {'emotion': 'happy', 'score': 0.9}
        elif any(word in text_lower for word in ['sad', 'حزين']):
            return {'emotion': 'sad', 'score': 0.8}
        elif any(word in text_lower for word in ['angry', 'غاضب']):
            return {'emotion': 'angry', 'score': 0.8}
        elif any(word in text_lower for word in ['scared', 'خائف']):
            return {'emotion': 'scared', 'score': 0.8}
        else:
            return {'emotion': 'neutral', 'score': 0.5}


# ================== EXPORT FOR COMPATIBILITY ==================

# For backward compatibility with different import patterns
EmotionAnalyzer = EmotionAnalyzer
EmotionResult = EmotionAnalysis  # Alias for older code 