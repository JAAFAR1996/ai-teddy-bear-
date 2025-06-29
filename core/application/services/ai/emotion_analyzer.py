"""
Emotion Analysis Service
Modern cloud-based emotion detection for 2025
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import structlog
from opentelemetry import trace

from src.application.services.service_registry import ServiceBase
from src.infrastructure.observability import trace_async

logger = structlog.get_logger()


class EmotionCategory(Enum):
    """Emotion categories for analysis"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SCARED = "scared"
    EXCITED = "excited"
    CURIOUS = "curious"
    CONFUSED = "confused"
    TIRED = "tired"
    NEUTRAL = "neutral"


@dataclass
class EmotionAnalysis:
    """Detailed emotion analysis result"""
    primary_emotion: EmotionCategory
    confidence: float
    secondary_emotions: Dict[EmotionCategory, float] = field(default_factory=dict)
    sentiment_score: float = 0.0  # -1 to 1
    arousal_level: float = 0.5  # 0 to 1
    keywords: List[str] = field(default_factory=list)
    language: str = "en"


class EmotionAnalyzer(ServiceBase):
    """
    Cloud-based emotion analyzer using modern APIs
    """
    
    def __init__(self, registry, config: Dict):
        super().__init__(registry, config)
        self._emotion_keywords = self._load_emotion_keywords()
        self._emoji_emotions = self._load_emoji_emotions()
        self._tracer = trace.get_tracer(__name__)
    
    async def initialize(self) -> None:
        """Initialize the emotion analyzer"""
        self.logger.info("Initializing emotion analyzer")
        self._state = self.ServiceState.READY
    
    async def shutdown(self) -> None:
        """Shutdown the analyzer"""
        self._state = self.ServiceState.STOPPED
    
    async def health_check(self) -> Dict:
        """Health check"""
        return {
            "healthy": self._state == self.ServiceState.READY,
            "service": "emotion_analyzer"
        }
    
    @trace_async("analyze_emotion")
    async def analyze(self, text: str, language: str = "en") -> EmotionAnalysis:
        """
        Analyze emotion in text using multiple methods
        """
        # Clean text
        text_clean = text.strip().lower()
        
        # Keyword-based analysis
        keyword_emotions = self._analyze_keywords(text_clean)
        
        # Emoji-based analysis
        emoji_emotions = self._analyze_emojis(text)
        
        # Combine results
        all_emotions = self._combine_emotion_scores(keyword_emotions, emoji_emotions)
        
        # Calculate primary emotion
        primary_emotion = max(all_emotions.items(), key=lambda x: x[1])[0] if all_emotions else EmotionCategory.NEUTRAL
        confidence = all_emotions.get(primary_emotion, 0.5)
        
        # Calculate sentiment and arousal
        sentiment_score = self._calculate_sentiment(all_emotions)
        arousal_level = self._calculate_arousal(primary_emotion, text)
        
        # Extract keywords
        keywords = self._extract_emotional_keywords(text_clean)
        
        return EmotionAnalysis(
            primary_emotion=primary_emotion,
            confidence=confidence,
            secondary_emotions={k: v for k, v in all_emotions.items() if k != primary_emotion},
            sentiment_score=sentiment_score,
            arousal_level=arousal_level,
            keywords=keywords,
            language=language
        )
    
    def _load_emotion_keywords(self) -> Dict[EmotionCategory, List[str]]:
        """Load emotion keywords for multiple languages"""
        return {
            EmotionCategory.HAPPY: [
                'happy', 'joy', 'glad', 'cheerful', 'delighted', 'excited',
                'سعيد', 'فرح', 'مبتهج', 'مسرور'
            ],
            EmotionCategory.SAD: [
                'sad', 'unhappy', 'depressed', 'down', 'blue', 'crying',
                'حزين', 'مكتئب', 'يبكي'
            ],
            EmotionCategory.ANGRY: [
                'angry', 'mad', 'furious', 'annoyed', 'frustrated',
                'غاضب', 'منزعج', 'محبط'
            ],
            EmotionCategory.SCARED: [
                'scared', 'afraid', 'frightened', 'worried', 'anxious',
                'خائف', 'قلق', 'مرعوب'
            ],
            EmotionCategory.EXCITED: [
                'excited', 'thrilled', 'enthusiastic', 'eager',
                'متحمس', 'متشوق'
            ],
            EmotionCategory.CURIOUS: [
                'curious', 'wondering', 'interested', 'question',
                'فضولي', 'متسائل', 'مهتم'
            ],
            EmotionCategory.CONFUSED: [
                'confused', 'puzzled', 'unsure', 'don\'t understand',
                'محتار', 'مشوش', 'لا أفهم'
            ],
            EmotionCategory.TIRED: [
                'tired', 'sleepy', 'exhausted', 'worn out',
                'متعب', 'نعسان', 'مرهق'
            ]
        }
    
    def _load_emoji_emotions(self) -> Dict[str, EmotionCategory]:
        """Map emojis to emotions"""
        return {
            '😊': EmotionCategory.HAPPY, '😁': EmotionCategory.HAPPY,
            '😄': EmotionCategory.HAPPY, '😃': EmotionCategory.HAPPY,
            '😢': EmotionCategory.SAD, '😭': EmotionCategory.SAD,
            '😞': EmotionCategory.SAD, '☹️': EmotionCategory.SAD,
            '😠': EmotionCategory.ANGRY, '😡': EmotionCategory.ANGRY,
            '🤬': EmotionCategory.ANGRY, '😤': EmotionCategory.ANGRY,
            '😨': EmotionCategory.SCARED, '😰': EmotionCategory.SCARED,
            '😱': EmotionCategory.SCARED, '😟': EmotionCategory.SCARED,
            '🤗': EmotionCategory.EXCITED, '🎉': EmotionCategory.EXCITED,
            '🤔': EmotionCategory.CURIOUS, '🧐': EmotionCategory.CURIOUS,
            '😕': EmotionCategory.CONFUSED, '🤷': EmotionCategory.CONFUSED,
            '😴': EmotionCategory.TIRED, '🥱': EmotionCategory.TIRED,
        }
    
    def _analyze_keywords(self, text: str) -> Dict[EmotionCategory, float]:
        """Analyze emotions based on keywords"""
        scores = {}
        
        for emotion, keywords in self._emotion_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text:
                    score += 1.0
            
            if score > 0:
                scores[emotion] = min(score / len(keywords), 1.0)
        
        return scores
    
    def _analyze_emojis(self, text: str) -> Dict[EmotionCategory, float]:
        """Analyze emotions based on emojis"""
        scores = {}
        
        for emoji, emotion in self._emoji_emotions.items():
            count = text.count(emoji)
            if count > 0:
                scores[emotion] = scores.get(emotion, 0) + (count * 0.3)
        
        # Normalize scores
        return {k: min(v, 1.0) for k, v in scores.items()}
    
    def _combine_emotion_scores(self, *score_dicts) -> Dict[EmotionCategory, float]:
        """Combine multiple emotion score dictionaries"""
        combined = {}
        
        for scores in score_dicts:
            for emotion, score in scores.items():
                combined[emotion] = combined.get(emotion, 0) + score
        
        # Normalize
        if combined:
            max_score = max(combined.values())
            if max_score > 0:
                combined = {k: v / max_score for k, v in combined.items()}
        
        return combined
    
    def _calculate_sentiment(self, emotions: Dict[EmotionCategory, float]) -> float:
        """Calculate overall sentiment score"""
        positive_emotions = [EmotionCategory.HAPPY, EmotionCategory.EXCITED]
        negative_emotions = [EmotionCategory.SAD, EmotionCategory.ANGRY, EmotionCategory.SCARED]
        
        positive_score = sum(emotions.get(e, 0) for e in positive_emotions)
        negative_score = sum(emotions.get(e, 0) for e in negative_emotions)
        
        if positive_score + negative_score == 0:
            return 0.0
        
        return (positive_score - negative_score) / (positive_score + negative_score)
    
    def _calculate_arousal(self, emotion: EmotionCategory, text: str) -> float:
        """Calculate emotional arousal level"""
        high_arousal = [EmotionCategory.EXCITED, EmotionCategory.ANGRY, EmotionCategory.SCARED]
        low_arousal = [EmotionCategory.TIRED, EmotionCategory.SAD]
        
        base_arousal = 0.5
        
        if emotion in high_arousal:
            base_arousal = 0.8
        elif emotion in low_arousal:
            base_arousal = 0.3
        
        # Check for intensity markers
        if any(marker in text.lower() for marker in ['very', 'really', 'so', 'extremely', 'جداً', 'كثير']):
            base_arousal = min(base_arousal + 0.2, 1.0)
        
        # Check for exclamation marks
        exclamation_count = text.count('!')
        base_arousal = min(base_arousal + (exclamation_count * 0.1), 1.0)
        
        return base_arousal
    
    def _extract_emotional_keywords(self, text: str) -> List[str]:
        """Extract keywords that indicate emotion"""
        keywords = []
        
        # Extract from emotion keywords
        for emotion_keywords in self._emotion_keywords.values():
            for keyword in emotion_keywords:
                if keyword in text and keyword not in keywords:
                    keywords.append(keyword)
        
        # Extract emotion words using simple pattern
        emotion_patterns = [
            r'\bfeel\w*\b', r'\bemotion\w*\b', r'\bhappy\b', r'\bsad\b',
            r'\bangry\b', r'\bscared\b', r'\bexcited\b'
        ]
        
        for pattern in emotion_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend([m for m in matches if m not in keywords])
        
        return keywords[:5]  # Return top 5 keywords