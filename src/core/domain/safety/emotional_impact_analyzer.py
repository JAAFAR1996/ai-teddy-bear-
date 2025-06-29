"""
Advanced Emotional Impact Analyzer for Child Safety
"""

import asyncio
from typing import List, Dict, Tuple
from dataclasses import dataclass
from .models import EmotionalImpactResult


class EmotionalImpactAnalyzer:
    """Advanced emotional impact analysis for child content"""
    
    def __init__(self):
        self.emotion_models = self._initialize_emotion_models()
        self.age_emotional_guidelines = self._load_age_guidelines()
        
    def _initialize_emotion_models(self) -> Dict:
        """Initialize emotion analysis models"""
        return {
            "sentiment_analyzer": self._create_sentiment_model(),
            "emotion_classifier": self._create_emotion_model(),
            "age_appropriateness": self._create_age_model()
        }
    
    def _create_sentiment_model(self):
        """Create sentiment analysis model"""
        # Simplified sentiment model
        positive_words = [
            "happy", "joy", "love", "good", "great", "wonderful",
            "amazing", "fun", "exciting", "beautiful", "nice"
        ]
        negative_words = [
            "sad", "angry", "hate", "bad", "terrible", "awful",
            "scary", "frightening", "hurt", "pain", "upset"
        ]
        
        return {
            "positive": positive_words,
            "negative": negative_words
        }
    
    def _create_emotion_model(self):
        """Create emotion classification model"""
        return {
            "joy": ["happy", "excited", "fun", "laughing", "cheerful"],
            "sadness": ["sad", "crying", "upset", "disappointed", "lonely"],
            "fear": ["scared", "afraid", "frightened", "worried", "anxious"],
            "anger": ["angry", "mad", "furious", "frustrated", "annoyed"],
            "surprise": ["surprised", "amazed", "wow", "unexpected"],
            "disgust": ["yucky", "gross", "eww", "disgusting"]
        }
    
    def _create_age_model(self):
        """Create age-appropriateness model"""
        return {
            3: {"max_complexity": 0.3, "avoid_emotions": ["anger", "fear"]},
            4: {"max_complexity": 0.4, "avoid_emotions": ["anger"]},
            5: {"max_complexity": 0.5, "avoid_emotions": []},
            6: {"max_complexity": 0.6, "avoid_emotions": []},
            7: {"max_complexity": 0.7, "avoid_emotions": []},
            8: {"max_complexity": 0.8, "avoid_emotions": []}
        }
    
    def _load_age_guidelines(self) -> Dict:
        """Load age-specific emotional guidelines"""
        return {
            3: {
                "positive_focus": 0.8,
                "max_negative_content": 0.1,
                "emotional_complexity": "simple",
                "preferred_emotions": ["joy", "surprise"]
            },
            4: {
                "positive_focus": 0.7,
                "max_negative_content": 0.2,
                "emotional_complexity": "simple",
                "preferred_emotions": ["joy", "surprise", "mild_sadness"]
            },
            5: {
                "positive_focus": 0.6,
                "max_negative_content": 0.3,
                "emotional_complexity": "moderate",
                "preferred_emotions": ["joy", "surprise", "curiosity"]
            },
            6: {
                "positive_focus": 0.6,
                "max_negative_content": 0.3,
                "emotional_complexity": "moderate",
                "preferred_emotions": ["all_appropriate"]
            }
        }
    
    async def analyze_emotional_impact(
        self, 
        text: str, 
        child_age: int,
        conversation_context: List[str] = None
    ) -> EmotionalImpactResult:
        """Analyze emotional impact of content"""
        
        # Analyze current text emotions
        emotion_scores = await self._analyze_emotions(text)
        
        # Calculate sentiment
        sentiment_score = await self._calculate_sentiment(text)
        
        # Check age appropriateness
        age_appropriate = self._check_age_appropriateness(
            emotion_scores, child_age
        )
        
        # Detect potential triggers
        triggers = self._detect_emotional_triggers(text, child_age)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            emotion_scores, age_appropriate, child_age
        )
        
        # Assess overall positivity
        is_positive = sentiment_score > 0.2 and age_appropriate > 0.7
        
        return EmotionalImpactResult(
            is_positive=is_positive,
            emotion_scores=emotion_scores,
            overall_sentiment=sentiment_score,
            age_appropriateness=age_appropriate,
            potential_triggers=triggers,
            recommendations=recommendations
        )
    
    async def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotions in text"""
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_models["emotion_classifier"].items():
            score = 0.0
            keyword_matches = 0
            
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1.0
                    keyword_matches += 1
            
            # Normalize score
            if keyword_matches > 0:
                emotion_scores[emotion] = min(1.0, score / len(keywords))
            else:
                emotion_scores[emotion] = 0.0
        
        return emotion_scores
    
    async def _calculate_sentiment(self, text: str) -> float:
        """Calculate overall sentiment score"""
        text_lower = text.lower()
        
        positive_count = sum(
            1 for word in self.emotion_models["sentiment_analyzer"]["positive"]
            if word in text_lower
        )
        
        negative_count = sum(
            1 for word in self.emotion_models["sentiment_analyzer"]["negative"]
            if word in text_lower
        )
        
        # Calculate sentiment score (-1 to 1)
        total_words = len(text_lower.split())
        if total_words == 0:
            return 0.0
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        sentiment = positive_ratio - negative_ratio
        return max(-1.0, min(1.0, sentiment * 5))  # Scale and clamp
    
    def _check_age_appropriateness(
        self, 
        emotion_scores: Dict[str, float], 
        child_age: int
    ) -> float:
        """Check if emotional content is age-appropriate"""
        
        age_config = self.age_emotional_guidelines.get(child_age, self.age_emotional_guidelines[6])
        avoid_emotions = self._create_age_model().get(child_age, {}).get("avoid_emotions", [])
        
        # Check for avoided emotions
        inappropriate_score = 0.0
        for emotion in avoid_emotions:
            if emotion in emotion_scores:
                inappropriate_score += emotion_scores[emotion]
        
        # Calculate appropriateness
        if inappropriate_score > 0.3:
            return 0.0
        elif inappropriate_score > 0.1:
            return 0.5
        else:
            return 1.0
    
    def _detect_emotional_triggers(self, text: str, child_age: int) -> List[str]:
        """Detect potential emotional triggers"""
        triggers = []
        text_lower = text.lower()
        
        # Age-specific triggers
        trigger_patterns = {
            "abandonment": ["alone", "left behind", "no one cares", "forgotten"],
            "fear_inducing": ["monster", "scary", "nightmare", "dark", "ghost"],
            "body_image": ["fat", "ugly", "skinny", "weird looking"],
            "performance_anxiety": ["stupid", "dumb", "can't do", "failure"],
            "social_rejection": ["no friends", "nobody likes", "outcast", "lonely"]
        }
        
        for trigger_type, keywords in trigger_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    triggers.append(trigger_type)
                    break
        
        return list(set(triggers))
    
    def _generate_recommendations(
        self, 
        emotion_scores: Dict[str, float],
        age_appropriateness: float,
        child_age: int
    ) -> List[str]:
        """Generate emotional safety recommendations"""
        recommendations = []
        
        # Check dominant emotions
        if emotion_scores:
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            if dominant_emotion[1] > 0.5:
                emotion_name = dominant_emotion[0]
                
                if emotion_name == "sadness" and dominant_emotion[1] > 0.7:
                    recommendations.append("Content contains high sadness - consider adding uplifting elements")
                
                elif emotion_name == "fear" and child_age < 6:
                    recommendations.append("Fear content detected - inappropriate for young children")
                
                elif emotion_name == "anger" and child_age < 5:
                    recommendations.append("Anger content detected - may overwhelm young children")
        
        # Age appropriateness recommendations
        if age_appropriateness < 0.5:
            recommendations.append(f"Content not suitable for age {child_age} - consider simplification")
        
        # Positive reinforcement recommendations
        if emotion_scores.get("joy", 0) < 0.2:
            recommendations.append("Consider adding more positive, joyful elements")
        
        return recommendations
    
    def analyze_conversation_emotional_journey(
        self, 
        conversation_history: List[str],
        child_age: int
    ) -> Dict[str, any]:
        """Analyze emotional journey through conversation"""
        
        emotional_timeline = []
        for i, text in enumerate(conversation_history):
            emotions = asyncio.run(self._analyze_emotions(text))
            sentiment = asyncio.run(self._calculate_sentiment(text))
            
            emotional_timeline.append({
                "turn": i,
                "emotions": emotions,
                "sentiment": sentiment,
                "timestamp": i  # Simplified timestamp
            })
        
        # Analyze trends
        sentiment_trend = self._calculate_sentiment_trend(emotional_timeline)
        emotional_stability = self._assess_emotional_stability(emotional_timeline)
        
        return {
            "emotional_timeline": emotional_timeline,
            "sentiment_trend": sentiment_trend,
            "emotional_stability": emotional_stability,
            "recommendations": self._generate_journey_recommendations(
                sentiment_trend, emotional_stability, child_age
            )
        }
    
    def _calculate_sentiment_trend(self, timeline: List[Dict]) -> str:
        """Calculate sentiment trend over conversation"""
        if len(timeline) < 3:
            return "insufficient_data"
        
        sentiments = [turn["sentiment"] for turn in timeline]
        
        # Simple trend analysis
        if sentiments[-1] > sentiments[0] + 0.2:
            return "improving"
        elif sentiments[-1] < sentiments[0] - 0.2:
            return "declining"
        else:
            return "stable"
    
    def _assess_emotional_stability(self, timeline: List[Dict]) -> float:
        """Assess emotional stability throughout conversation"""
        if len(timeline) < 2:
            return 1.0
        
        sentiment_changes = []
        for i in range(1, len(timeline)):
            change = abs(timeline[i]["sentiment"] - timeline[i-1]["sentiment"])
            sentiment_changes.append(change)
        
        # Calculate stability (lower changes = higher stability)
        avg_change = sum(sentiment_changes) / len(sentiment_changes)
        stability = max(0.0, 1.0 - avg_change)
        
        return stability
    
    def _generate_journey_recommendations(
        self, 
        sentiment_trend: str,
        emotional_stability: float,
        child_age: int
    ) -> List[str]:
        """Generate recommendations for emotional journey"""
        recommendations = []
        
        if sentiment_trend == "declining":
            recommendations.append("Conversation sentiment declining - introduce positive elements")
        
        if emotional_stability < 0.5:
            recommendations.append("High emotional volatility detected - maintain calm, stable tone")
        
        if child_age <= 5 and emotional_stability < 0.7:
            recommendations.append("Young child showing emotional instability - extra care needed")
        
        return recommendations 