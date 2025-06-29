"""
🧠 Advanced Emotion Analyzer for AI Teddy Bear
Analyzes emotions from text and audio using modern AI techniques
"""

from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from dataclasses import dataclass
import json
import asyncio
from datetime import datetime

# For text emotion analysis
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not installed. Install with: pip install transformers")

# For audio emotion analysis  
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️ Librosa not installed. Install with: pip install librosa")


@dataclass
class EmotionResult:
    """Emotion analysis result with confidence scores"""
    primary_emotion: str
    confidence: float
    all_emotions: Dict[str, float]
    source: str  # 'text', 'audio', or 'combined'
    timestamp: str
    behavioral_indicators: List[str]
    recommendations: List[str]


class AdvancedEmotionAnalyzer:
    """
    Advanced emotion analyzer using state-of-the-art AI models
    for both text and audio analysis
    """
    
    def __init__(self):
        self.text_analyzer = None
        self.audio_features_extractor = None
        self._initialize_models()
        
        # Emotion categories relevant for children
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
    
    def _initialize_models(self):
        """Initialize AI models for emotion analysis"""
        if TRANSFORMERS_AVAILABLE:
            try:
                # Use a model specifically good for emotion detection
                self.text_analyzer = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    return_all_scores=True
                )
                print("✅ Text emotion analyzer initialized")
            except Exception as e:
                print(f"❌ Failed to load text emotion model: {e}")
                self.text_analyzer = None
    
    async def analyze_comprehensive(
        self, 
        text: Optional[str] = None,
        audio_data: Optional[np.ndarray] = None,
        audio_sr: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EmotionResult:
        """
        Comprehensive emotion analysis from text and/or audio
        
        Args:
            text: Text to analyze
            audio_data: Audio waveform as numpy array
            audio_sr: Audio sample rate
            context: Additional context (child age, recent activities, etc.)
        
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
            # Fallback if no analysis available
            final_emotion = self._get_default_emotion()
        
        # Generate recommendations based on emotion
        recommendations = self._generate_recommendations(
            final_emotion.primary_emotion,
            context
        )
        final_emotion.recommendations = recommendations
        
        return final_emotion
    
    async def _analyze_text(self, text: str) -> Optional[EmotionResult]:
        """Analyze emotions from text using transformer model"""
        if not text.strip():
            return None
        
        if self.text_analyzer:
            try:
                # Get predictions from model
                predictions = self.text_analyzer(text)
                
                # Convert to our format
                emotion_scores = {}
                for pred in predictions[0]:
                    emotion = pred['label'].lower()
                    score = pred['score']
                    emotion_scores[emotion] = score
                
                # Map to child-friendly emotions
                mapped_scores = self._map_to_child_emotions(emotion_scores)
                
                # Get primary emotion
                primary = max(mapped_scores.items(), key=lambda x: x[1])
                
                # Identify behavioral indicators from text
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
                print(f"❌ Text analysis error: {e}")
        
        # Fallback to rule-based analysis
        return self._analyze_text_rules(text)
    
    def _analyze_text_rules(self, text: str) -> EmotionResult:
        """Rule-based text emotion analysis as fallback"""
        text_lower = text.lower()
        scores = {emotion: 0.0 for emotion in self.child_emotions.keys()}
        indicators = []
        
        # Happy indicators
        happy_words = ['يضحك', 'سعيد', 'مرح', 'رائع', 'أحب', 'ممتاز', 'جميل', 
                      'happy', 'laugh', 'fun', 'love', 'great', 'awesome']
        for word in happy_words:
            if word in text_lower:
                scores['happy'] += 0.3
                indicators.append(f"positive word: {word}")
        
        # Sad indicators
        sad_words = ['حزين', 'بكي', 'وحيد', 'متضايق', 'مكتئب',
                    'sad', 'cry', 'lonely', 'upset', 'hurt']
        for word in sad_words:
            if word in text_lower:
                scores['sad'] += 0.3
                indicators.append(f"sad word: {word}")
        
        # Angry indicators
        angry_words = ['غاضب', 'زعلان', 'عصبي', 'مستاء',
                      'angry', 'mad', 'annoyed', 'frustrated']
        for word in angry_words:
            if word in text_lower:
                scores['angry'] += 0.3
                indicators.append(f"angry word: {word}")
        
        # Scared indicators
        scared_words = ['خائف', 'قلق', 'مرعوب', 'خوف',
                       'scared', 'afraid', 'worried', 'nervous']
        for word in scared_words:
            if word in text_lower:
                scores['scared'] += 0.3
                indicators.append(f"fear word: {word}")
        
        # Questions indicate curiosity
        if '?' in text or '؟' in text:
            scores['curious'] += 0.2
            indicators.append("questioning")
        
        # Exclamations can indicate excitement or anger
        if '!' in text:
            if scores['happy'] > 0:
                scores['happy'] += 0.1
            else:
                scores['angry'] += 0.1
            indicators.append("exclamation")
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        else:
            scores['calm'] = 0.5  # Default to calm
        
        # Get primary emotion
        primary = max(scores.items(), key=lambda x: x[1])
        
        return EmotionResult(
            primary_emotion=primary[0],
            confidence=min(primary[1], 0.8),  # Cap confidence for rule-based
            all_emotions=scores,
            source='text',
            timestamp=datetime.now().isoformat(),
            behavioral_indicators=indicators,
            recommendations=[]
        )
    
    async def _analyze_audio(
        self, 
        audio_data: np.ndarray, 
        sr: int
    ) -> Optional[EmotionResult]:
        """Analyze emotions from audio features"""
        if not LIBROSA_AVAILABLE:
            return None
        
        try:
            # Extract audio features
            features = self._extract_audio_features(audio_data, sr)
            
            # Analyze features for emotion indicators
            emotion_scores = self._analyze_audio_features(features)
            
            # Get behavioral indicators
            indicators = self._extract_audio_indicators(features)
            
            # Get primary emotion
            primary = max(emotion_scores.items(), key=lambda x: x[1])
            
            return EmotionResult(
                primary_emotion=primary[0],
                confidence=primary[1],
                all_emotions=emotion_scores,
                source='audio',
                timestamp=datetime.now().isoformat(),
                behavioral_indicators=indicators,
                recommendations=[]
            )
        except Exception as e:
            print(f"❌ Audio analysis error: {e}")
            return None
    
    def _extract_audio_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract relevant audio features for emotion analysis"""
        features = {}
        
        # Pitch/frequency features
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        features['pitch_mean'] = np.mean(pitches[pitches > 0]) if len(pitches[pitches > 0]) > 0 else 0
        features['pitch_std'] = np.std(pitches[pitches > 0]) if len(pitches[pitches > 0]) > 0 else 0
        
        # Energy/loudness
        features['rms_mean'] = np.mean(librosa.feature.rms(y=audio))
        features['rms_std'] = np.std(librosa.feature.rms(y=audio))
        
        # Spectral features
        features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
        features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr))
        
        # Tempo/rhythm
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        features['tempo'] = tempo
        
        # Zero crossing rate (voice quality)
        features['zcr_mean'] = np.mean(librosa.feature.zero_crossing_rate(audio))
        
        return features
    
    def _analyze_audio_features(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Map audio features to emotion scores"""
        scores = {emotion: 0.0 for emotion in self.child_emotions.keys()}
        
        # High pitch + high energy = happy/excited
        if features['pitch_mean'] > 300 and features['rms_mean'] > 0.1:
            scores['happy'] += 0.4
        
        # Low pitch + low energy = sad
        if features['pitch_mean'] < 200 and features['rms_mean'] < 0.05:
            scores['sad'] += 0.4
        
        # High energy + high pitch variance = angry
        if features['rms_mean'] > 0.15 and features['pitch_std'] > 50:
            scores['angry'] += 0.4
        
        # Low energy + high ZCR = scared/nervous
        if features['rms_mean'] < 0.05 and features['zcr_mean'] > 0.05:
            scores['scared'] += 0.3
        
        # Steady features = calm
        if features['pitch_std'] < 30 and features['rms_std'] < 0.05:
            scores['calm'] += 0.3
        
        # Fast tempo can indicate excitement or anxiety
        if features['tempo'] > 120:
            if scores['happy'] > scores['scared']:
                scores['happy'] += 0.1
            else:
                scores['scared'] += 0.1
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        else:
            scores['calm'] = 0.5
        
        return scores
    
    def _extract_audio_indicators(self, features: Dict[str, Any]) -> List[str]:
        """Extract behavioral indicators from audio features"""
        indicators = []
        
        if features['pitch_mean'] > 300:
            indicators.append("high pitch")
        elif features['pitch_mean'] < 200:
            indicators.append("low pitch")
        
        if features['rms_mean'] > 0.1:
            indicators.append("loud voice")
        elif features['rms_mean'] < 0.05:
            indicators.append("quiet voice")
        
        if features['pitch_std'] > 50:
            indicators.append("variable pitch")
        
        if features['tempo'] > 120:
            indicators.append("fast speech")
        elif features['tempo'] < 80:
            indicators.append("slow speech")
        
        return indicators
    
    def _extract_text_indicators(self, text: str, emotion: str) -> List[str]:
        """Extract behavioral indicators from text"""
        indicators = []
        
        # Length of response
        word_count = len(text.split())
        if word_count < 5:
            indicators.append("short response")
        elif word_count > 20:
            indicators.append("long response")
        
        # Punctuation patterns
        if text.count('!') > 1:
            indicators.append("multiple exclamations")
        if text.count('?') > 1:
            indicators.append("multiple questions")
        if '...' in text:
            indicators.append("hesitation")
        
        # All caps
        if any(word.isupper() and len(word) > 1 for word in text.split()):
            indicators.append("emphasis/shouting")
        
        return indicators
    
    def _map_to_child_emotions(self, emotion_scores: Dict[str, float]) -> Dict[str, float]:
        """Map general emotions to child-friendly categories"""
        child_scores = {emotion: 0.0 for emotion in self.child_emotions.keys()}
        
        mapping = {
            'joy': 'happy',
            'happiness': 'happy',
            'love': 'happy',
            'sadness': 'sad',
            'grief': 'sad',
            'anger': 'angry',
            'rage': 'angry',
            'fear': 'scared',
            'anxiety': 'scared',
            'worry': 'scared',
            'neutral': 'calm',
            'surprise': 'curious'
        }
        
        for emotion, score in emotion_scores.items():
            emotion_lower = emotion.lower()
            if emotion_lower in mapping:
                child_scores[mapping[emotion_lower]] += score
            else:
                # Default mapping
                child_scores['calm'] += score * 0.5
        
        # Normalize
        total = sum(child_scores.values())
        if total > 0:
            child_scores = {k: v/total for k, v in child_scores.items()}
        
        return child_scores
    
    def _combine_results(
        self, 
        results: List[Tuple[str, EmotionResult]], 
        context: Optional[Dict[str, Any]]
    ) -> EmotionResult:
        """Combine results from multiple sources"""
        if len(results) == 1:
            return results[0][1]
        
        # Weight different sources
        weights = {'text': 0.5, 'audio': 0.7}  # Audio often more reliable for emotion
        
        combined_emotions = {}
        all_indicators = []
        total_weight = 0
        
        for source, result in results:
            weight = weights.get(source, 0.5)
            total_weight += weight
            
            for emotion, score in result.all_emotions.items():
                if emotion not in combined_emotions:
                    combined_emotions[emotion] = 0
                combined_emotions[emotion] += score * weight
            
            all_indicators.extend(result.behavioral_indicators)
        
        # Normalize by total weight
        if total_weight > 0:
            combined_emotions = {k: v/total_weight for k, v in combined_emotions.items()}
        
        # Context adjustments
        if context:
            combined_emotions = self._apply_context_adjustments(combined_emotions, context)
        
        # Get primary emotion
        primary = max(combined_emotions.items(), key=lambda x: x[1])
        
        return EmotionResult(
            primary_emotion=primary[0],
            confidence=min(primary[1], 0.95),
            all_emotions=combined_emotions,
            source='combined',
            timestamp=datetime.now().isoformat(),
            behavioral_indicators=list(set(all_indicators)),
            recommendations=[]
        )
    
    def _apply_context_adjustments(
        self, 
        emotions: Dict[str, float], 
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Adjust emotion scores based on context"""
        adjusted = emotions.copy()
        
        # Time of day adjustments
        current_hour = datetime.now().hour
        if current_hour >= 20 or current_hour <= 6:  # Late night
            # Children might be tired
            adjusted['sad'] *= 0.8  # Less likely actually sad
            adjusted['calm'] *= 1.2  # More likely just tired
        
        # Age adjustments
        age = context.get('age', 7)
        if age < 5:
            # Younger children have more volatile emotions
            primary = max(adjusted.items(), key=lambda x: x[1])
            if primary[1] < 0.6:
                # If no strong emotion, more likely to be curious
                adjusted['curious'] *= 1.3
        
        # Recent activity adjustments
        recent_activity = context.get('recent_activity', '')
        if 'game' in recent_activity and 'lost' in recent_activity:
            # Might be frustrated from losing
            adjusted['angry'] *= 0.7  # Less likely truly angry
            adjusted['sad'] *= 1.2  # More likely disappointed
        
        # Normalize
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: v/total for k, v in adjusted.items()}
        
        return adjusted
    
    def _generate_recommendations(
        self, 
        emotion: str, 
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on detected emotion"""
        recommendations = []
        
        if emotion == 'happy':
            recommendations.extend([
                "Continue engaging with fun activities",
                "This is a good time for learning new things",
                "Consider playing collaborative games"
            ])
        
        elif emotion == 'sad':
            recommendations.extend([
                "Offer comforting stories or calming music",
                "Engage in gentle conversation about feelings",
                "Suggest a favorite activity to lift mood",
                "Consider a virtual hug from teddy"
            ])
        
        elif emotion == 'angry':
            recommendations.extend([
                "Guide through calming breathing exercises",
                "Suggest a break or quiet time",
                "Play soothing background sounds",
                "Redirect to physical activity if possible"
            ])
        
        elif emotion == 'scared':
            recommendations.extend([
                "Provide reassurance and comfort",
                "Tell a brave character story",
                "Use night light feature if bedtime",
                "Engage in distraction with favorite topic"
            ])
        
        elif emotion == 'curious':
            recommendations.extend([
                "Perfect time for educational content",
                "Engage with discovery games",
                "Answer questions with detailed explanations",
                "Encourage exploration activities"
            ])
        
        elif emotion == 'calm':
            recommendations.extend([
                "Good time for focused activities",
                "Consider mindfulness exercises",
                "Engage in creative storytelling"
            ])
        
        # Age-specific recommendations
        if context and 'age' in context:
            age = context['age']
            if age < 5 and emotion in ['sad', 'angry', 'scared']:
                recommendations.append("Use simple words and soothing voice")
            elif age > 8:
                recommendations.append("Encourage verbal expression of feelings")
        
        return recommendations
    
    def _get_default_emotion(self) -> EmotionResult:
        """Return default emotion when no analysis is possible"""
        return EmotionResult(
            primary_emotion='calm',
            confidence=0.3,
            all_emotions={'calm': 0.3, 'curious': 0.2, 'happy': 0.2, 
                         'sad': 0.1, 'angry': 0.1, 'scared': 0.1},
            source='default',
            timestamp=datetime.now().isoformat(),
            behavioral_indicators=['no clear indicators'],
            recommendations=['Engage in general conversation to assess mood']
        )
    
    async def get_emotion_history(
        self, 
        child_id: str, 
        hours: int = 24
    ) -> List[EmotionResult]:
        """Get emotion history for a child (placeholder for database integration)"""
        # TODO: Integrate with database to fetch historical emotion data
        return []
    
    def generate_emotion_report(
        self, 
        emotions: List[EmotionResult], 
        child_name: str
    ) -> str:
        """Generate a summary report of emotions over time"""
        if not emotions:
            return f"No emotion data available for {child_name}"
        
        # Count emotions
        emotion_counts = {}
        for result in emotions:
            emotion = result.primary_emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Generate report
        report = f"Emotion Summary for {child_name}\n"
        report += "=" * 40 + "\n\n"
        
        total = len(emotions)
        report += f"Total interactions analyzed: {total}\n\n"
        
        report += "Emotion Distribution:\n"
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            report += f"- {emotion.capitalize()}: {count} times ({percentage:.1f}%)\n"
        
        # Most common emotion
        most_common = max(emotion_counts.items(), key=lambda x: x[1])
        report += f"\nMost common emotion: {most_common[0].capitalize()}\n"
        
        # Recommendations based on overall pattern
        report += "\nGeneral Recommendations:\n"
        if most_common[0] in ['sad', 'angry', 'scared']:
            report += "- Child shows signs of distress. Consider consulting with a specialist.\n"
            report += "- Increase positive reinforcement and comforting activities.\n"
        elif most_common[0] == 'happy':
            report += "- Child shows positive emotional state. Continue current approach.\n"
            report += "- Good time to introduce new learning challenges.\n"
        
        return report


# ================================================================
# DATABASE INTEGRATION FOR EMOTION ANALYSIS
# Advanced SQLAlchemy integration with intelligent storage
# ================================================================

# Additional imports for database integration
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, and_, desc, func, text
from sqlalchemy.exc import SQLAlchemyError
import json
from contextlib import contextmanager
from typing import Generator
import uuid
from dataclasses import asdict

# Import our SQLAlchemy models
try:
    from ...infrastructure.persistence.sqlalchemy_models import (
        Child, Conversation, Message, EmotionalState, Parent
    )
    from ...infrastructure.persistence.models import Base
    DATABASE_MODELS_AVAILABLE = True
except ImportError:
    DATABASE_MODELS_AVAILABLE = False
    print("⚠️ Database models not available. Running in standalone mode.")
    
    # Create dummy classes for type hints when models are not available
    class Child:
        pass
    
    class Conversation:
        pass
    
    class Message:
        pass
    
    class EmotionalState:
        pass
    
    class Parent:
        pass
    
    class Base:
        metadata = None


class DatabaseEmotionService:
    """
    Advanced database service for emotion analysis integration
    
    Features:
    - Automatic emotion storage with session linking
    - Intelligent data aggregation and analysis
    - Parental report generation
    - Emotion trend analysis
    - Data privacy and retention management
    """
    
    def __init__(
        self, 
        database_url: str = "sqlite:///teddy_emotions.db",
        enable_analytics: bool = True,
        retention_days: int = 365
    ):
        self.database_url = database_url
        self.enable_analytics = enable_analytics
        self.retention_days = retention_days
        
        # Initialize database
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables if they don't exist
        if DATABASE_MODELS_AVAILABLE:
            Base.metadata.create_all(bind=self.engine)
        
        # Analytics cache
        self._analytics_cache = {}
        self._cache_timeout = 300  # 5 minutes
    
    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    async def analyze_and_save_emotion(
        self,
        audio_file: Optional[bytes] = None,
        text_input: Optional[str] = None,
        session_id: str = None,
        child_id: str = None,
        device_id: str = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[EmotionResult, str]:
        """
        Main function: Analyze emotion and save to database
        
        Returns:
            Tuple of (EmotionResult, emotion_record_id)
        """
        if not DATABASE_MODELS_AVAILABLE:
            raise RuntimeError("Database models not available")
        
        try:
            # Initialize emotion analyzer
            analyzer = AdvancedEmotionAnalyzer()
            
            # Analyze emotion
            if audio_file:
                # Convert audio bytes to numpy array if needed
                audio_data = self._process_audio_bytes(audio_file)
                emotion_result = await analyzer.analyze_comprehensive(
                    text=text_input,
                    audio_data=audio_data,
                    context=context
                )
            else:
                emotion_result = await analyzer.analyze_comprehensive(
                    text=text_input,
                    context=context
                )
            
            # Save to database
            emotion_record_id = await self.save_emotion_to_db(
                emotion_result=emotion_result,
                session_id=session_id,
                child_id=child_id,
                device_id=device_id,
                context=context,
                audio_data=audio_file,
                text_input=text_input
            )
            
            # Update analytics cache
            if self.enable_analytics:
                await self._update_analytics_cache(child_id, emotion_result)
            
            return emotion_result, emotion_record_id
            
        except Exception as e:
            print(f"❌ Error in analyze_and_save_emotion: {e}")
            raise e
    
    async def save_emotion_to_db(
        self,
        emotion_result: EmotionResult,
        session_id: str = None,
        child_id: str = None,
        device_id: str = None,
        context: Optional[Dict[str, Any]] = None,
        audio_data: Optional[bytes] = None,
        text_input: Optional[str] = None
    ) -> str:
        """Save emotion analysis result to database"""
        
        with self.get_db_session() as session:
            try:
                # Ensure child exists
                child = await self._get_or_create_child(session, child_id, device_id)
                
                # Get or create conversation session
                conversation = await self._get_or_create_conversation(
                    session, session_id, child.id, context
                )
                
                # Create message record if text provided
                message_id = None
                if text_input:
                    message = Message(
                        id=str(uuid.uuid4()),
                        conversation_id=conversation.id,
                        sender='child',
                        content=text_input,
                        message_type='text',
                        metadata_=json.dumps(context or {}),
                        created_at=datetime.utcnow()
                    )
                    session.add(message)
                    session.flush()
                    message_id = message.id
                
                # Create emotional state record
                emotional_state = EmotionalState(
                    id=str(uuid.uuid4()),
                    child_id=child.id,
                    conversation_id=conversation.id,
                    message_id=message_id,
                    primary_emotion=emotion_result.primary_emotion,
                    confidence_score=emotion_result.confidence,
                    all_emotions=json.dumps(emotion_result.all_emotions),
                    source=emotion_result.source,
                    behavioral_indicators=json.dumps(emotion_result.behavioral_indicators),
                    recommendations=json.dumps(emotion_result.recommendations),
                    context_data=json.dumps(context or {}),
                    audio_features=json.dumps(self._extract_audio_metadata(audio_data)) if audio_data else None,
                    analysis_timestamp=datetime.utcnow(),
                    device_id=device_id
                )
                
                session.add(emotional_state)
                session.flush()
                
                # Update conversation metadata
                conversation.total_messages = conversation.total_messages + 1
                conversation.last_emotion = emotion_result.primary_emotion
                conversation.updated_at = datetime.utcnow()
                
                # Update child's last interaction
                child.last_interaction = datetime.utcnow()
                child.total_interactions = child.total_interactions + 1
                
                session.commit()
                
                print(f"✅ Emotion saved to database: {emotion_result.primary_emotion} "
                      f"(confidence: {emotion_result.confidence:.2f})")
                
                return emotional_state.id
                
            except SQLAlchemyError as e:
                session.rollback()
                print(f"❌ Database error saving emotion: {e}")
                raise e
    
    async def get_emotion_history(
        self,
        child_id: str,
        hours: int = 24,
        limit: int = 100,
        emotion_filter: Optional[str] = None
    ) -> List[EmotionResult]:
        """Get emotion history for a child"""
        
        with self.get_db_session() as session:
            try:
                # Calculate time threshold
                time_threshold = datetime.utcnow() - timedelta(hours=hours)
                
                # Build query
                query = session.query(EmotionalState).filter(
                    and_(
                        EmotionalState.child_id == child_id,
                        EmotionalState.analysis_timestamp >= time_threshold
                    )
                ).order_by(desc(EmotionalState.analysis_timestamp))
                
                # Apply emotion filter if provided
                if emotion_filter:
                    query = query.filter(EmotionalState.primary_emotion == emotion_filter)
                
                # Apply limit
                emotional_states = query.limit(limit).all()
                
                # Convert to EmotionResult objects
                emotion_results = []
                for state in emotional_states:
                    emotion_result = EmotionResult(
                        primary_emotion=state.primary_emotion,
                        confidence=state.confidence_score,
                        all_emotions=json.loads(state.all_emotions) if state.all_emotions else {},
                        source=state.source,
                        timestamp=state.analysis_timestamp.isoformat(),
                        behavioral_indicators=json.loads(state.behavioral_indicators) if state.behavioral_indicators else [],
                        recommendations=json.loads(state.recommendations) if state.recommendations else []
                    )
                    emotion_results.append(emotion_result)
                
                return emotion_results
                
            except SQLAlchemyError as e:
                print(f"❌ Database error getting emotion history: {e}")
                return []
    
    async def get_emotion_analytics(
        self,
        child_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get comprehensive emotion analytics for a child"""
        
        with self.get_db_session() as session:
            try:
                # Calculate time threshold
                time_threshold = datetime.utcnow() - timedelta(days=days)
                
                # Get all emotions in period
                emotions_query = session.query(EmotionalState).filter(
                    and_(
                        EmotionalState.child_id == child_id,
                        EmotionalState.analysis_timestamp >= time_threshold
                    )
                ).order_by(EmotionalState.analysis_timestamp)
                
                emotions = emotions_query.all()
                
                if not emotions:
                    return {"message": "No emotion data available", "child_id": child_id}
                
                # Basic statistics
                total_interactions = len(emotions)
                emotion_counts = {}
                confidence_scores = []
                daily_patterns = {}
                
                for emotion in emotions:
                    # Count emotions
                    primary = emotion.primary_emotion
                    emotion_counts[primary] = emotion_counts.get(primary, 0) + 1
                    
                    # Collect confidence scores
                    confidence_scores.append(emotion.confidence_score)
                    
                    # Daily patterns
                    day_key = emotion.analysis_timestamp.strftime('%Y-%m-%d')
                    if day_key not in daily_patterns:
                        daily_patterns[day_key] = {}
                    daily_patterns[day_key][primary] = daily_patterns[day_key].get(primary, 0) + 1
                
                # Calculate percentages
                emotion_percentages = {
                    emotion: (count / total_interactions) * 100
                    for emotion, count in emotion_counts.items()
                }
                
                # Most common emotion
                most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])
                
                # Average confidence
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                
                # Trend analysis (compare first half vs second half)
                midpoint = len(emotions) // 2
                first_half = emotions[:midpoint]
                second_half = emotions[midpoint:]
                
                first_half_emotions = {}
                second_half_emotions = {}
                
                for emotion in first_half:
                    first_half_emotions[emotion.primary_emotion] = first_half_emotions.get(emotion.primary_emotion, 0) + 1
                
                for emotion in second_half:
                    second_half_emotions[emotion.primary_emotion] = second_half_emotions.get(emotion.primary_emotion, 0) + 1
                
                # Calculate trends
                trends = {}
                for emotion in set(list(first_half_emotions.keys()) + list(second_half_emotions.keys())):
                    first_count = first_half_emotions.get(emotion, 0)
                    second_count = second_half_emotions.get(emotion, 0)
                    
                    if first_count > 0:
                        change = ((second_count - first_count) / first_count) * 100
                        trends[emotion] = change
                    elif second_count > 0:
                        trends[emotion] = 100  # New emotion appeared
                    else:
                        trends[emotion] = 0
                
                # Risk assessment
                risk_indicators = self._assess_emotional_risk(emotion_counts, total_interactions)
                
                # Recommendations
                recommendations = self._generate_parental_recommendations(
                    emotion_counts, total_interactions, trends
                )
                
                return {
                    "child_id": child_id,
                    "analysis_period_days": days,
                    "total_interactions": total_interactions,
                    "emotion_distribution": emotion_percentages,
                    "emotion_counts": emotion_counts,
                    "most_common_emotion": {
                        "emotion": most_common_emotion[0],
                        "count": most_common_emotion[1],
                        "percentage": emotion_percentages[most_common_emotion[0]]
                    },
                    "average_confidence": round(avg_confidence, 3),
                    "daily_patterns": daily_patterns,
                    "trends": trends,
                    "risk_indicators": risk_indicators,
                    "recommendations": recommendations,
                    "generated_at": datetime.utcnow().isoformat()
                }
                
            except SQLAlchemyError as e:
                print(f"❌ Database error getting analytics: {e}")
                return {"error": str(e)}
    
    async def generate_parental_report(
        self,
        child_id: str,
        report_type: str = "weekly",
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive parental report"""
        
        # Determine time period
        days_map = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "quarterly": 90
        }
        days = days_map.get(report_type, 7)
        
        try:
            # Get child information
            with self.get_db_session() as session:
                child = session.query(Child).filter(Child.id == child_id).first()
                if not child:
                    return {"error": "Child not found"}
            
            # Get analytics
            analytics = await self.get_emotion_analytics(child_id, days)
            
            if "error" in analytics:
                return analytics
            
            # Get recent conversations
            recent_conversations = await self._get_recent_conversations_summary(child_id, days)
            
            # Get emotion trends
            emotion_trends = await self._get_emotion_trends(child_id, days)
            
            # Behavioral insights
            behavioral_insights = await self._generate_behavioral_insights(child_id, days)
            
            # Create comprehensive report
            report = {
                "report_header": {
                    "child_name": child.name,
                    "child_age": child.age,
                    "report_type": report_type.capitalize(),
                    "period_days": days,
                    "generated_at": datetime.utcnow().isoformat(),
                    "report_id": str(uuid.uuid4())
                },
                "emotion_summary": analytics,
                "conversation_insights": recent_conversations,
                "behavioral_patterns": behavioral_insights,
                "trend_analysis": emotion_trends,
                "parental_recommendations": [],
                "action_items": [],
                "next_report_date": (datetime.utcnow() + timedelta(days=days)).isoformat()
            }
            
            # Add recommendations if requested
            if include_recommendations:
                recommendations = self._generate_detailed_parental_recommendations(analytics, behavioral_insights)
                report["parental_recommendations"] = recommendations["recommendations"]
                report["action_items"] = recommendations["action_items"]
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating parental report: {e}")
            return {"error": str(e)}
    
    async def get_emotion_trends(
        self,
        child_id: str,
        days: int = 30,
        granularity: str = "daily"
    ) -> Dict[str, Any]:
        """Get detailed emotion trends over time"""
        
        with self.get_db_session() as session:
            try:
                time_threshold = datetime.utcnow() - timedelta(days=days)
                
                # Group by time period
                if granularity == "daily":
                    time_format = '%Y-%m-%d'
                elif granularity == "weekly":
                    time_format = '%Y-W%W'
                elif granularity == "monthly":
                    time_format = '%Y-%m'
                else:
                    time_format = '%Y-%m-%d'
                
                # Get emotions grouped by time
                emotions = session.query(EmotionalState).filter(
                    and_(
                        EmotionalState.child_id == child_id,
                        EmotionalState.analysis_timestamp >= time_threshold
                    )
                ).order_by(EmotionalState.analysis_timestamp).all()
                
                # Group data
                trends = {}
                for emotion in emotions:
                    time_key = emotion.analysis_timestamp.strftime(time_format)
                    
                    if time_key not in trends:
                        trends[time_key] = {
                            "total_interactions": 0,
                            "emotions": {},
                            "avg_confidence": 0,
                            "confidence_scores": []
                        }
                    
                    trends[time_key]["total_interactions"] += 1
                    
                    primary = emotion.primary_emotion
                    trends[time_key]["emotions"][primary] = trends[time_key]["emotions"].get(primary, 0) + 1
                    trends[time_key]["confidence_scores"].append(emotion.confidence_score)
                
                # Calculate averages
                for time_key in trends:
                    confidence_scores = trends[time_key]["confidence_scores"]
                    trends[time_key]["avg_confidence"] = sum(confidence_scores) / len(confidence_scores)
                    del trends[time_key]["confidence_scores"]  # Remove raw scores
                
                return {
                    "child_id": child_id,
                    "granularity": granularity,
                    "period_days": days,
                    "trends": trends,
                    "generated_at": datetime.utcnow().isoformat()
                }
                
            except SQLAlchemyError as e:
                print(f"❌ Database error getting trends: {e}")
                return {"error": str(e)}
    
    def _process_audio_bytes(self, audio_bytes: bytes) -> Optional[np.ndarray]:
        """Process audio bytes to numpy array"""
        try:
            # This is a placeholder - implement actual audio processing
            # You would use librosa.load or similar to convert bytes to numpy array
            return np.random.random(16000)  # Mock 1-second audio at 16kHz
        except Exception as e:
            print(f"❌ Error processing audio bytes: {e}")
            return None
    
    def _extract_audio_metadata(self, audio_data: bytes) -> Dict[str, Any]:
        """Extract metadata from audio data"""
        if not audio_data:
            return {}
        
        return {
            "size_bytes": len(audio_data),
            "format": "unknown",  # Could be detected
            "duration_estimate": len(audio_data) / 16000,  # Rough estimate
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _get_or_create_child(
        self, 
        session: Session, 
        child_id: str, 
        device_id: str
    ) -> Child:
        """Get existing child or create new one"""
        
        child = session.query(Child).filter(Child.id == child_id).first()
        
        if not child:
            # Create new child
            child = Child(
                id=child_id or str(uuid.uuid4()),
                name=f"Child_{child_id[:8] if child_id else 'Unknown'}",
                age=7,  # Default age
                device_id=device_id,
                total_interactions=0,
                created_at=datetime.utcnow(),
                last_interaction=datetime.utcnow()
            )
            session.add(child)
            session.flush()
        
        return child
    
    async def _get_or_create_conversation(
        self,
        session: Session,
        session_id: str,
        child_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Conversation:
        """Get existing conversation or create new one"""
        
        conversation = session.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                id=str(uuid.uuid4()),
                child_id=child_id,
                session_id=session_id or str(uuid.uuid4()),
                total_messages=0,
                context_data=json.dumps(context or {}),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conversation)
            session.flush()
        
        return conversation
    
    async def _update_analytics_cache(
        self, 
        child_id: str, 
        emotion_result: EmotionResult
    ):
        """Update analytics cache for real-time insights"""
        cache_key = f"analytics_{child_id}"
        
        if cache_key not in self._analytics_cache:
            self._analytics_cache[cache_key] = {
                "total_interactions": 0,
                "emotions": {},
                "last_updated": datetime.utcnow()
            }
        
        cache = self._analytics_cache[cache_key]
        cache["total_interactions"] += 1
        emotion = emotion_result.primary_emotion
        cache["emotions"][emotion] = cache["emotions"].get(emotion, 0) + 1
        cache["last_updated"] = datetime.utcnow()
    
    async def _get_recent_conversations_summary(
        self, 
        child_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """Get summary of recent conversations"""
        
        with self.get_db_session() as session:
            time_threshold = datetime.utcnow() - timedelta(days=days)
            
            conversations = session.query(Conversation).filter(
                and_(
                    Conversation.child_id == child_id,
                    Conversation.created_at >= time_threshold
                )
            ).order_by(desc(Conversation.created_at)).all()
            
            total_conversations = len(conversations)
            total_messages = sum(conv.total_messages for conv in conversations)
            
            # Most common emotions in conversations
            emotion_summary = {}
            for conv in conversations:
                if conv.last_emotion:
                    emotion_summary[conv.last_emotion] = emotion_summary.get(conv.last_emotion, 0) + 1
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "avg_messages_per_conversation": round(total_messages / max(total_conversations, 1), 2),
                "conversation_emotions": emotion_summary
            }
    
    async def _get_emotion_trends(
        self, 
        child_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """Get emotion trends analysis"""
        
        # Get current period
        current_analytics = await self.get_emotion_analytics(child_id, days)
        
        # Get previous period for comparison
        previous_analytics = await self.get_emotion_analytics(child_id, days * 2)
        
        if "error" in current_analytics or "error" in previous_analytics:
            return {"message": "Insufficient data for trend analysis"}
        
        # Calculate trends
        trends = {}
        current_emotions = current_analytics.get("emotion_counts", {})
        
        # This is a simplified trend calculation
        for emotion, count in current_emotions.items():
            if count > 0:
                trends[emotion] = "stable"  # Could implement more sophisticated trend analysis
        
        return {
            "trend_summary": "Overall emotional state appears stable",
            "detailed_trends": trends,
            "analysis_confidence": "medium"
        }
    
    async def _generate_behavioral_insights(
        self, 
        child_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """Generate behavioral insights from emotion data"""
        
        with self.get_db_session() as session:
            time_threshold = datetime.utcnow() - timedelta(days=days)
            
            emotions = session.query(EmotionalState).filter(
                and_(
                    EmotionalState.child_id == child_id,
                    EmotionalState.analysis_timestamp >= time_threshold
                )
            ).all()
            
            if not emotions:
                return {"message": "No data available for behavioral analysis"}
            
            # Analyze behavioral indicators
            all_indicators = []
            for emotion in emotions:
                if emotion.behavioral_indicators:
                    indicators = json.loads(emotion.behavioral_indicators)
                    all_indicators.extend(indicators)
            
            # Count indicator frequency
            indicator_counts = {}
            for indicator in all_indicators:
                indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1
            
            # Top behavioral patterns
            top_indicators = sorted(indicator_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "total_indicators_analyzed": len(all_indicators),
                "unique_behavioral_patterns": len(indicator_counts),
                "top_behavioral_indicators": top_indicators,
                "behavioral_summary": f"Child shows {len(indicator_counts)} distinct behavioral patterns"
            }
    
    def _assess_emotional_risk(
        self, 
        emotion_counts: Dict[str, int], 
        total_interactions: int
    ) -> List[str]:
        """Assess emotional risk indicators"""
        risk_indicators = []
        
        # High negative emotion percentage
        negative_emotions = ['sad', 'angry', 'scared']
        negative_count = sum(emotion_counts.get(emotion, 0) for emotion in negative_emotions)
        negative_percentage = (negative_count / total_interactions) * 100
        
        if negative_percentage > 40:
            risk_indicators.append(f"High negative emotions: {negative_percentage:.1f}%")
        
        # Consistent single emotion (lack of emotional range)
        if len(emotion_counts) < 3:
            risk_indicators.append("Limited emotional range observed")
        
        # Specific emotion concerns
        if emotion_counts.get('sad', 0) / total_interactions > 0.3:
            risk_indicators.append("Frequent sadness detected")
        
        if emotion_counts.get('angry', 0) / total_interactions > 0.25:
            risk_indicators.append("Frequent anger detected")
        
        if emotion_counts.get('scared', 0) / total_interactions > 0.2:
            risk_indicators.append("Frequent fear detected")
        
        return risk_indicators
    
    def _generate_parental_recommendations(
        self, 
        emotion_counts: Dict[str, int], 
        total_interactions: int, 
        trends: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations for parents"""
        recommendations = []
        
        # Most common emotion
        most_common = max(emotion_counts.items(), key=lambda x: x[1])
        primary_emotion = most_common[0]
        
        if primary_emotion == 'happy':
            recommendations.append("Child shows positive emotional state. Continue current activities.")
            recommendations.append("Good time to introduce new learning challenges.")
        
        elif primary_emotion in ['sad', 'angry', 'scared']:
            recommendations.append("Child showing signs of distress. Consider:")
            recommendations.append("- More comforting activities and one-on-one time")
            recommendations.append("- Consulting with child development specialist if pattern continues")
        
        elif primary_emotion == 'curious':
            recommendations.append("Child shows high curiosity. Excellent for learning!")
            recommendations.append("Engage with educational content and discovery activities.")
        
        # Trend-based recommendations
        for emotion, trend in trends.items():
            if trend > 20 and emotion in ['sad', 'angry', 'scared']:
                recommendations.append(f"Increasing {emotion} trend detected. Monitor closely.")
        
        return recommendations
    
    def _generate_detailed_parental_recommendations(
        self, 
        analytics: Dict[str, Any], 
        behavioral_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed recommendations with action items"""
        
        recommendations = []
        action_items = []
        
        # Based on emotion distribution
        emotion_dist = analytics.get("emotion_distribution", {})
        
        if emotion_dist.get("happy", 0) > 50:
            recommendations.append("Your child shows predominantly positive emotions. This is excellent!")
            action_items.append("Continue current interaction patterns")
        
        if emotion_dist.get("sad", 0) > 20:
            recommendations.append("Elevated sadness levels detected.")
            action_items.append("Schedule extra comfort time and favorite activities")
            action_items.append("Consider discussing feelings with your child")
        
        if emotion_dist.get("curious", 0) > 30:
            recommendations.append("High curiosity levels - great for learning!")
            action_items.append("Introduce new educational content")
            action_items.append("Encourage exploration and questions")
        
        # Based on behavioral patterns
        if behavioral_insights.get("unique_behavioral_patterns", 0) < 3:
            recommendations.append("Limited behavioral variety observed.")
            action_items.append("Try varying interaction types and activities")
        
        return {
            "recommendations": recommendations,
            "action_items": action_items
        }
    
    async def cleanup_old_data(self, days_to_keep: int = None):
        """Clean up old emotion data based on retention policy"""
        if not days_to_keep:
            days_to_keep = self.retention_days
        
        with self.get_db_session() as session:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
                
                # Delete old emotional states
                deleted_count = session.query(EmotionalState).filter(
                    EmotionalState.analysis_timestamp < cutoff_date
                ).delete()
                
                session.commit()
                
                print(f"✅ Cleaned up {deleted_count} old emotion records")
                return deleted_count
                
            except SQLAlchemyError as e:
                session.rollback()
                print(f"❌ Error cleaning up data: {e}")
                return 0


class EnhancedEmotionAnalyzer(AdvancedEmotionAnalyzer):
    """
    Enhanced emotion analyzer with integrated database functionality
    """
    
    def __init__(
        self, 
        database_url: str = "sqlite:///teddy_emotions.db",
        enable_db_integration: bool = True
    ):
        super().__init__()
        
        self.enable_db_integration = enable_db_integration
        
        if enable_db_integration and DATABASE_MODELS_AVAILABLE:
            self.db_service = DatabaseEmotionService(database_url)
        else:
            self.db_service = None
            print("⚠️ Database integration disabled")
    
    async def analyze_and_save(
        self,
        text: Optional[str] = None,
        audio_data: Optional[bytes] = None,
        session_id: str = None,
        child_id: str = None,
        device_id: str = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[EmotionResult, Optional[str]]:
        """
        Analyze emotions and automatically save to database
        
        Returns:
            Tuple of (EmotionResult, emotion_record_id or None)
        """
        
        # Perform emotion analysis
        emotion_result = await self.analyze_comprehensive(
            text=text,
            audio_data=self._convert_bytes_to_numpy(audio_data) if audio_data else None,
            context=context
        )
        
        # Save to database if enabled
        emotion_record_id = None
        if self.db_service:
            try:
                emotion_record_id = await self.db_service.save_emotion_to_db(
                    emotion_result=emotion_result,
                    session_id=session_id,
                    child_id=child_id,
                    device_id=device_id,
                    context=context,
                    audio_data=audio_data,
                    text_input=text
                )
            except Exception as e:
                print(f"❌ Failed to save to database: {e}")
        
        return emotion_result, emotion_record_id
    
    async def get_child_emotion_history(
        self,
        child_id: str,
        hours: int = 24
    ) -> List[EmotionResult]:
        """Get emotion history for a child from database"""
        if not self.db_service:
            return []
        
        return await self.db_service.get_emotion_history(child_id, hours)
    
    async def generate_parental_insights(
        self,
        child_id: str,
        report_type: str = "weekly"
    ) -> Dict[str, Any]:
        """Generate comprehensive parental insights"""
        if not self.db_service:
            return {"error": "Database not available"}
        
        return await self.db_service.generate_parental_report(child_id, report_type)
    
    def _convert_bytes_to_numpy(self, audio_bytes: bytes) -> Optional[np.ndarray]:
        """Convert audio bytes to numpy array"""
        if not audio_bytes:
            return None
        
        try:
            # This is a placeholder implementation
            # In real implementation, you would use librosa or similar
            import struct
            
            # Assume 16-bit PCM audio
            audio_data = struct.unpack(f'{len(audio_bytes)//2}h', audio_bytes)
            return np.array(audio_data, dtype=np.float32) / 32768.0
            
        except Exception as e:
            print(f"❌ Error converting audio bytes: {e}")
            return None


# Convenience functions
async def analyze_and_save_emotion(
    audio_file: Optional[bytes] = None,
    text_input: Optional[str] = None,
    session_id: str = None,
    child_id: str = None,
    device_id: str = None,
    context: Optional[Dict[str, Any]] = None,
    database_url: str = "sqlite:///teddy_emotions.db"
) -> Tuple[EmotionResult, str]:
    """
    Main convenience function for emotion analysis and storage
    
    Usage:
        emotion_result, record_id = await analyze_and_save_emotion(
            text_input="I'm happy today!",
            child_id="child_123",
            session_id="session_456"
        )
    """
    
    db_service = DatabaseEmotionService(database_url)
    
    return await db_service.analyze_and_save_emotion(
        audio_file=audio_file,
        text_input=text_input,
        session_id=session_id,
        child_id=child_id,
        device_id=device_id,
        context=context
    )


async def get_emotion_analytics_report(
    child_id: str,
    days: int = 7,
    database_url: str = "sqlite:///teddy_emotions.db"
) -> Dict[str, Any]:
    """
    Get comprehensive emotion analytics report
    
    Usage:
        report = await get_emotion_analytics_report("child_123", days=7)
    """
    
    db_service = DatabaseEmotionService(database_url)
    return await db_service.get_emotion_analytics(child_id, days)


# Example usage function
async def test_analyzer():
    """Test the emotion analyzer with sample data"""
    analyzer = AdvancedEmotionAnalyzer()
    
    # Test text analysis
    test_texts = [
        "أنا سعيد جداً اليوم! أحب اللعب مع دبدوبي",
        "أشعر بالحزن لأن صديقي لم يأت",
        "لماذا السماء زرقاء؟ أريد أن أعرف!",
        "أنا خائف من الظلام",
        "I'm so happy today! I love my teddy!",
        "I feel sad and lonely",
        "Why is the sky blue? Tell me!"
    ]
    
    print("Testing Emotion Analyzer:\n" + "="*50)
    
    for text in test_texts:
        result = await analyzer.analyze_comprehensive(text=text)
        print(f"\nText: {text}")
        print(f"Emotion: {result.primary_emotion} (confidence: {result.confidence:.2f})")
        print(f"All emotions: {result.all_emotions}")
        print(f"Indicators: {result.behavioral_indicators}")
        print(f"Recommendations: {result.recommendations[:2]}")  # Show first 2
    
    # Generate sample report
    print("\n" + "="*50)
    print("Sample Emotion Report:")
    print(analyzer.generate_emotion_report([], "أحمد"))


if __name__ == "__main__":
    # Run test
    asyncio.run(test_analyzer()) 