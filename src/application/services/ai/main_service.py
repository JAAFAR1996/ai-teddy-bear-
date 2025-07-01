"""
AI Teddy Bear Main Service - Production Ready 2025
Handles core application logic with proper error handling and security
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog
from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

from src.infrastructure.config import get_settings
# from src.application.services.core.service_registry import ServiceBase
from src.infrastructure.observability import trace_async
from src.infrastructure.security.audit_logger import (AuditEventType,
                                                      AuditLogger)

# from src.application.services.core.circuit_breaker import CircuitBreaker


# Metrics
interaction_counter = Counter(
    "teddy_interactions_total",
    "Total number of voice interactions",
    ["session_type", "emotion", "success"],
)

response_time_histogram = Histogram(
    "teddy_response_duration_seconds", "Response time for voice interactions"
)

active_sessions_gauge = Gauge("teddy_active_sessions", "Number of active sessions")


class ActivityType(Enum):
    """Types of activities the teddy can engage in"""

    CONVERSATION = "conversation"
    STORY = "story"
    GAME = "game"
    LEARNING = "learning"
    COMFORT = "comfort"
    SLEEP_ROUTINE = "sleep_routine"


@dataclass
class TranscriptionResult:
    """Transcription result with metadata"""

    text: str
    confidence: float
    language: str = "en"
    audio_duration_ms: int = 0


@dataclass
class EmotionResult:
    """Emotion analysis result"""

    primary_emotion: str
    confidence: float
    secondary_emotions: Dict[str, float] = field(default_factory=dict)
    valence: float = 0.0  # -1 to 1
    arousal: float = 0.0  # 0 to 1

    def to_dict(self) -> Dict:
        return {
            "primary": self.primary_emotion,
            "confidence": self.confidence,
            "secondary": self.secondary_emotions,
            "valence": self.valence,
            "arousal": self.arousal,
        }


@dataclass
class ResponseContext:
    """Context for generating responses"""

    text: str
    emotion: str
    activity_type: ActivityType
    metadata: Dict = field(default_factory=dict)
    processing_time: int = 0


@dataclass
class SessionContext:
    """Enhanced session context with full tracking"""

    child_id: str
    session_id: str
    start_time: datetime
    interactions: List[Dict] = field(default_factory=list)
    emotions: List[EmotionResult] = field(default_factory=list)
    current_activity: Optional[ActivityType] = None
    language_preference: str = "en"
    voice_preference: str = "default"
    metadata: Dict = field(default_factory=dict)

    @property
    def duration(self) -> timedelta:
        return datetime.utcnow() - self.start_time

    @property
    def interaction_count(self) -> int:
        return len(self.interactions)

    def get_emotion_summary(self) -> Dict:
        """Get summary of emotions during session"""
        if not self.emotions:
            return {}

        emotion_counts = {}
        for emotion in self.emotions:
            emotion_counts[emotion.primary_emotion] = (
                emotion_counts.get(emotion.primary_emotion, 0) + 1
            )

        return {
            "dominant": max(emotion_counts, key=emotion_counts.get),
            "distribution": emotion_counts,
            "average_valence": sum(e.valence for e in self.emotions)
            / len(self.emotions),
            "average_arousal": sum(e.arousal for e in self.emotions)
            / len(self.emotions),
        }


class AITeddyBearService(ServiceBase):
    """
    Main AI Teddy Bear Service - Refactored for 2025
    Properly integrated with service registry and security
    """

    def __init__(self, registry, config: Dict):
        super().__init__(registry, config)
        self.settings = get_settings()
        self.logger = structlog.get_logger()
        self._tracer = trace.get_tracer(__name__)

        # Services will be injected from registry
        self.audit_logger: Optional[AuditLogger] = None
        self.session_manager = None
        self.ai_service = None
        self.voice_service = None
        self.game_engine = None
        self.story_generator = None
        self.health_service = None
        self.emotion_analyzer = None
        self.speech_analyzer = None

        # Session management
        self.active_sessions: Dict[str, SessionContext] = {}

        # Circuit breakers for external services
        self._transcription_breaker = CircuitBreaker(
            name="transcription", failure_threshold=3, recovery_timeout=30
        )

        self._ai_breaker = CircuitBreaker(
            name="ai_service", failure_threshold=5, recovery_timeout=60
        )

    async def initialize(self) -> None:
        """Initialize service with proper dependency injection"""
        self.logger.info("Initializing AI Teddy Bear Service")

        # Get services from registry with retry
        services_to_load = [
            ("audit_logger", True),
            ("session_manager", True),
            ("ai", True),
            ("voice", True),
            ("game_engine", False),
            ("story_generator", False),
            ("health", True),
            ("emotion_analyzer", True),
            ("speech_analyzer", False),
        ]

        for service_name, required in services_to_load:
            try:
                service = await self.wait_for_service(service_name, timeout=30)
                setattr(self, service_name.replace("-", "_"), service)
            except asyncio.TimeoutError:
                if required:
                    raise
                self.logger.warning(f"Optional service {service_name} not available")

        self._state = self.ServiceState.READY
        self.logger.info("AI Teddy Bear Service initialized successfully")

    async def shutdown(self) -> None:
        """Graceful shutdown with proper cleanup"""
        self.logger.info("Shutting down AI Teddy Bear Service")

        # End all active sessions gracefully
        shutdown_tasks = []
        for session_id in list(self.active_sessions.keys()):
            shutdown_tasks.append(self.end_session(session_id, reason="shutdown"))

        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        self._state = self.ServiceState.STOPPED
        active_sessions_gauge.set(0)

    async def health_check(self) -> Dict:
        """Comprehensive health check"""
        checks = {
            "service_state": self._state == self.ServiceState.READY,
            "active_sessions": len(self.active_sessions),
            "transcription_circuit": self._transcription_breaker.is_closed,
            "ai_circuit": self._ai_breaker.is_closed,
        }

        # Check critical services
        critical_services = ["ai_service", "voice_service", "session_manager"]
        for service_name in critical_services:
            service = getattr(self, service_name, None)
            if service and hasattr(service, "health_check"):
                try:
                    service_health = await service.health_check()
                    checks[f"{service_name}_healthy"] = service_health.get(
                        "healthy", False
                    )
                except Exception as e:
                    checks[f"{service_name}_healthy"] = False

        healthy = all(
            [
                checks["service_state"],
                checks.get("ai_service_healthy", False),
                checks.get("voice_service_healthy", False),
            ]
        )

        return {
            "healthy": healthy,
            "service": "ai_teddy_bear_main",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def start_session(
        self, child_id: str, metadata: Optional[Dict] = None
    ) -> Dict:
        """Start a new interaction session"""
        session_id = str(uuid.uuid4())

        # Create session context
        session = SessionContext(
            child_id=child_id,
            session_id=session_id,
            start_time=datetime.utcnow(),
            metadata=metadata or {},
        )

        # Get child preferences from database
        preferences = await self._get_child_preferences(child_id)
        session.language_preference = preferences.get("language", "en")
        session.voice_preference = preferences.get("voice", "default")

        # Store session
        self.active_sessions[session_id] = session
        await self.session_manager.create_session(
            session_id,
            {
                "child_id": child_id,
                "start_time": session.start_time.isoformat(),
                "preferences": preferences,
            },
        )

        # Update metrics
        active_sessions_gauge.inc()

        # Audit log
        await self.audit_logger.log_event(
            AuditEventType.SESSION_START, child_id, {"session_id": session_id}
        )

        # Generate welcome message
        welcome_text = await self._generate_welcome_message(child_id, preferences)
        audio_data = await self.voice_service.text_to_speech(
            welcome_text, voice=session.voice_preference, emotion="friendly"
        )

        self.logger.info("Session started", session_id=session_id, child_id=child_id)

        return {
            "session_id": session_id,
            "message": welcome_text,
            "audio_data": audio_data,
            "preferences": preferences,
        }

    @trace_async
    @response_time_histogram.time()
    async def process_voice_interaction(
        self, session_id: str, audio_data: bytes, metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Process voice interaction with proper error handling and monitoring
        """
        if session_id not in self.active_sessions:
            return {"error": "Invalid session", "code": "INVALID_SESSION"}

        session = self.active_sessions[session_id]

        try:
            # Step 1: Speech to text with fallback
            transcription = await self._transcribe_with_fallback(audio_data, session)

            # Step 2: Multi-modal emotion analysis
            emotion_result = await self._analyze_emotions(
                transcription.text, audio_data, session
            )

            # Step 3: Context-aware response generation
            response = await self._generate_contextual_response(
                transcription.text, emotion_result, session
            )

            # Step 4: Generate voice response
            audio_response = await self._generate_voice_response(
                response.text, response.emotion, session
            )

            # Step 5: Update session and log
            interaction = {
                "timestamp": datetime.utcnow(),
                "transcription": transcription.text,
                "confidence": transcription.confidence,
                "emotion": emotion_result.to_dict(),
                "response": response.text,
                "activity_type": response.activity_type.value,
                "duration_ms": response.processing_time,
            }

            session.interactions.append(interaction)
            session.emotions.append(emotion_result)
            await self._persist_interaction(session, interaction)

            # Update metrics
            interaction_counter.labels(
                session_type=response.activity_type.value,
                emotion=emotion_result.primary_emotion,
                success="true",
            ).inc()

            # Audit logging
            await self.audit_logger.log_event(
                AuditEventType.VOICE_INTERACTION,
                session.child_id,
                {
                    "session_id": session_id,
                    "emotion": emotion_result.primary_emotion,
                    "activity": response.activity_type.value,
                },
            )

            return {
                "success": True,
                "transcription": transcription.text,
                "emotion": emotion_result.to_dict(),
                "response": response.text,
                "audio_data": audio_response,
                "activity_type": response.activity_type.value,
                "session_id": session_id,
            }

        except Exception as e:
            self.logger.error(
                "Voice interaction failed",
                session_id=session_id,
                error=str(e),
                exc_info=True,
            )

            # Update metrics
            interaction_counter.labels(
                session_type="error", emotion="unknown", success="false"
            ).inc()

            # Fallback response
            fallback_text = self._get_fallback_response(session)
            fallback_audio = await self._generate_voice_response(
                fallback_text, "caring", session
            )

            return {
                "success": False,
                "error": str(e),
                "response": fallback_text,
                "audio_data": fallback_audio,
                "session_id": session_id,
            }

    async def end_session(self, session_id: str, reason: str = "user_request") -> Dict:
        """End an interaction session with summary"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]

        # Generate session summary
        summary = {
            "session_id": session_id,
            "child_id": session.child_id,
            "duration_minutes": session.duration.total_seconds() / 60,
            "interaction_count": session.interaction_count,
            "emotion_summary": session.get_emotion_summary(),
            "end_reason": reason,
        }

        # Generate goodbye message based on session
        goodbye_text = await self._generate_goodbye_message(session, summary)
        goodbye_audio = await self.voice_service.text_to_speech(
            goodbye_text, voice=session.voice_preference, emotion="warm"
        )

        # Persist session data
        await self._persist_session_summary(session, summary)

        # Clear from memory
        del self.active_sessions[session_id]
        await self.session_manager.end_session(session_id)

        # Update metrics
        active_sessions_gauge.dec()

        # Audit log
        await self.audit_logger.log_event(
            AuditEventType.SESSION_END, session.child_id, summary
        )

        self.logger.info(
            "Session ended",
            session_id=session_id,
            duration_minutes=summary["duration_minutes"],
        )

        return {
            "message": goodbye_text,
            "audio_data": goodbye_audio,
            "summary": summary,
        }

    # Private helper methods

    async def _transcribe_with_fallback(
        self, audio_data: bytes, session: SessionContext
    ) -> TranscriptionResult:
        """Transcribe audio with multiple fallback options"""

        async def _try_transcription():
            # Try cloud service first
            if hasattr(self, "cloud_transcription_service"):
                return await self.cloud_transcription_service.transcribe(
                    audio_data, language=session.language_preference
                )

            # Fallback to voice service
            if self.voice_service and hasattr(self.voice_service, "transcribe"):
                return await self.voice_service.transcribe(
                    audio_data, language=session.language_preference
                )

            raise ValueError("No transcription service available")

        # Use circuit breaker
        result = await self._transcription_breaker.call(_try_transcription)

        return TranscriptionResult(
            text=result.get("text", ""),
            confidence=result.get("confidence", 0.0),
            language=result.get("language", session.language_preference),
            audio_duration_ms=result.get("duration_ms", 0),
        )

    async def _analyze_emotions(
        self, text: str, audio_data: bytes, session: SessionContext
    ) -> EmotionResult:
        """Analyze emotions from both text and audio"""

        if self.emotion_analyzer:
            emotion_data = await self.emotion_analyzer.analyze_multimodal(
                text=text,
                audio_data=audio_data,
                context={
                    "previous_emotions": [e.to_dict() for e in session.emotions[-5:]],
                    "current_activity": session.current_activity,
                },
            )
        else:
            # Fallback to AI service
            emotion_data = await self.ai_service.analyze_emotion(text)

        return EmotionResult(
            primary_emotion=emotion_data.get("primary", "neutral"),
            confidence=emotion_data.get("confidence", 0.5),
            secondary_emotions=emotion_data.get("secondary", {}),
            valence=emotion_data.get("valence", 0.0),
            arousal=emotion_data.get("arousal", 0.0),
        )

    async def _generate_contextual_response(
        self, text: str, emotion: EmotionResult, session: SessionContext
    ) -> ResponseContext:
        """Generate response based on context and emotion"""

        # Determine activity type
        activity_type = await self._determine_activity_type(text, emotion, session)

        # Update session activity
        session.current_activity = activity_type

        # Generate appropriate response
        start_time = datetime.utcnow()

        response_text = await self._generate_response_for_activity(
            text, emotion, activity_type, session
        )

        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return ResponseContext(
            text=response_text,
            emotion=self._map_emotion_to_voice(emotion),
            activity_type=activity_type,
            processing_time=processing_time,
        )

    async def _generate_voice_response(
        self, text: str, emotion: str, session: SessionContext
    ) -> bytes:
        """Generate voice response with appropriate settings"""

        return await self.voice_service.text_to_speech(
            text=text,
            voice=session.voice_preference,
            emotion=emotion,
            speed=1.0,  # Can be adjusted based on child's age
            pitch=0,  # Can be adjusted based on preference
        )

    async def _persist_interaction(
        self, session: SessionContext, interaction: Dict
    ) -> None:
        """Persist interaction data"""

        # Store in session manager (Redis)
        await self.session_manager.add_interaction(session.session_id, interaction)

        # Store in database for long-term analysis
        if hasattr(self, "conversation_repository"):
            await self.conversation_repository.add_interaction(
                child_id=session.child_id,
                session_id=session.session_id,
                interaction_data=interaction,
            )

    async def _get_child_preferences(self, child_id: str) -> Dict:
        """Get child preferences from database"""

        if hasattr(self, "child_repository"):
            child = await self.child_repository.get_by_id(child_id)
            if child:
                return {
                    "language": child.language_preference,
                    "voice": child.voice_preference,
                    "age": child.age,
                    "interests": child.interests,
                }

        return {"language": "en", "voice": "default", "age": 5, "interests": []}

    async def _generate_welcome_message(self, child_id: str, preferences: Dict) -> str:
        """Generate personalized welcome message"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                "generate welcome message",
                context={
                    "mode": "welcome",
                    "child_age": preferences.get("age", 5),
                    "language": preferences.get("language", "en"),
                },
            )

        # Fallback messages
        messages = {
            "en": "Hello! I'm so happy to talk with you today!",
            "es": "¡Hola! ¡Estoy muy feliz de hablar contigo hoy!",
            "fr": "Bonjour! Je suis très heureux de parler avec toi aujourd'hui!",
            "ar": "مرحبا! أنا سعيد جداً للتحدث معك اليوم!",
        }

        language = preferences.get("language", "en")
        return messages.get(language, messages["en"])

    async def _generate_goodbye_message(
        self, session: SessionContext, summary: Dict
    ) -> str:
        """Generate personalized goodbye message"""

        emotion_summary = summary.get("emotion_summary", {})
        dominant_emotion = emotion_summary.get("dominant", "neutral")

        if self.ai_service:
            return await self.ai_service.generate_response(
                "generate goodbye message",
                context={
                    "mode": "goodbye",
                    "dominant_emotion": dominant_emotion,
                    "duration_minutes": summary["duration_minutes"],
                    "language": session.language_preference,
                },
            )

        # Fallback messages
        if dominant_emotion in ["happy", "excited"]:
            return "That was so much fun! I can't wait to play with you again!"
        elif dominant_emotion in ["sad", "upset"]:
            return "I hope you feel better soon. Remember, I'm always here when you need a friend!"
        else:
            return "It was wonderful talking with you! See you next time!"

    async def _persist_session_summary(
        self, session: SessionContext, summary: Dict
    ) -> None:
        """Persist session summary for analytics"""

        if hasattr(self, "conversation_repository"):
            await self.conversation_repository.save_session_summary(
                child_id=session.child_id,
                session_id=session.session_id,
                summary_data=summary,
            )

    def _get_fallback_response(self, session: SessionContext) -> str:
        """Get appropriate fallback response"""

        fallbacks = {
            "en": "I'm having trouble understanding. Can you say that again?",
            "es": "Tengo problemas para entender. ¿Puedes decirlo de nuevo?",
            "fr": "J'ai du mal à comprendre. Peux-tu répéter?",
            "ar": "أواجه صعوبة في الفهم. هل يمكنك تكرار ذلك؟",
        }

        return fallbacks.get(session.language_preference, fallbacks["en"])

    async def _determine_activity_type(
        self, text: str, emotion: EmotionResult, session: SessionContext
    ) -> ActivityType:
        """Determine the appropriate activity type"""

        # Check for emotional distress first
        if emotion.valence < -0.5 or emotion.primary_emotion in [
            "sad",
            "upset",
            "scared",
        ]:
            return ActivityType.COMFORT

        # Use AI to classify intent
        if self.ai_service:
            intent = await self.ai_service.classify_intent(
                text,
                context={
                    "emotion": emotion.to_dict(),
                    "previous_activity": session.current_activity,
                },
            )

            activity_map = {
                "play_game": ActivityType.GAME,
                "tell_story": ActivityType.STORY,
                "learn": ActivityType.LEARNING,
                "sleep": ActivityType.SLEEP_ROUTINE,
                "chat": ActivityType.CONVERSATION,
            }

            return activity_map.get(intent, ActivityType.CONVERSATION)

        # Simple keyword matching as fallback
        text_lower = text.lower()
        if any(word in text_lower for word in ["game", "play", "fun"]):
            return ActivityType.GAME
        elif any(word in text_lower for word in ["story", "tell me", "once upon"]):
            return ActivityType.STORY
        elif any(word in text_lower for word in ["learn", "teach", "what is", "how"]):
            return ActivityType.LEARNING
        elif any(word in text_lower for word in ["sleep", "tired", "bedtime"]):
            return ActivityType.SLEEP_ROUTINE

        return ActivityType.CONVERSATION

    def _map_emotion_to_voice(self, emotion: EmotionResult) -> str:
        """Map emotion analysis to voice emotion"""

        # High arousal positive
        if emotion.valence > 0.5 and emotion.arousal > 0.5:
            return "excited"

        # Low arousal positive
        if emotion.valence > 0.3 and emotion.arousal < 0.5:
            return "warm"

        # Negative emotions
        if emotion.valence < -0.3:
            return "caring"

        # Neutral
        return "friendly"

    async def _generate_response_for_activity(
        self,
        text: str,
        emotion: EmotionResult,
        activity_type: ActivityType,
        session: SessionContext,
    ) -> str:
        """Generate response for specific activity type"""

        context = {
            "text": text,
            "emotion": emotion.to_dict(),
            "child_age": session.metadata.get("age", 5),
            "language": session.language_preference,
            "history": [i["transcription"] for i in session.interactions[-5:]],
        }

        if activity_type == ActivityType.COMFORT:
            return await self._generate_comfort_response(text, emotion, context)
        elif activity_type == ActivityType.GAME:
            return await self._handle_game_interaction(text, session)
        elif activity_type == ActivityType.STORY:
            return await self._handle_story_request(text, emotion, session)
        elif activity_type == ActivityType.LEARNING:
            return await self._handle_learning_interaction(text, context)
        elif activity_type == ActivityType.SLEEP_ROUTINE:
            return await self._handle_sleep_routine(text, session)
        else:
            return await self._handle_conversation(text, context)

    async def _generate_comfort_response(
        self, text: str, emotion: EmotionResult, context: Dict
    ) -> str:
        """Generate comfort response using AI service, not static text"""
        if self.ai_service:
            return await self.ai_service.generate_comfort_response(
                text, emotion, context
            )
        return await self._fallback_response(text)

    async def _handle_game_interaction(self, text: str, session: SessionContext) -> str:
        """Handle game interaction using game engine, not static text"""
        if self.game_engine:
            return await self.game_engine.play_game(text, session.child_id)
        return await self._fallback_response(text)

    async def _handle_story_request(
        self, text: str, emotion: EmotionResult, session: SessionContext
    ) -> str:
        """Handle story request using story generator, not static text"""
        if self.story_generator:
            return await self.story_generator.generate_story(
                text, emotion, session.child_id
            )
        return await self._fallback_response(text)

    async def _handle_learning_interaction(self, text: str, context: Dict) -> str:
        """Handle learning interaction using AI service, not static text"""
        if self.ai_service:
            return await self.ai_service.generate_learning_response(text, context)
        return await self._fallback_response(text)

    async def _handle_sleep_routine(self, text: str, session: SessionContext) -> str:
        """Handle sleep routine using AI service, not static text"""
        if self.ai_service:
            return await self.ai_service.generate_sleep_routine(text, session.child_id)
        return await self._fallback_response(text)

    async def _handle_conversation(self, text: str, context: Dict) -> str:
        """Handle conversation using AI service, not static text"""
        if self.ai_service:
            return await self.ai_service.generate_conversation_response(text, context)
        return await self._fallback_response(text)

    async def _fallback_response(self, text: str) -> str:
        """Fallback response if no service is available"""
        return "عذراً، لا يمكنني معالجة هذا الطلب حالياً. يرجى المحاولة لاحقاً."

    async def _generate_comfort_response(
        self, text: str, emotion: EmotionResult, context: Dict
    ) -> str:
        """Generate comforting response for distressed child"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                text, context={**context, "mode": "comfort"}
            )

        # Fallback comfort responses
        if emotion.primary_emotion == "sad":
            return "I understand you're feeling sad. Would you like to talk about it or shall we do something fun together?"
        elif emotion.primary_emotion == "scared":
            return "It's okay to feel scared sometimes. I'm here with you. You're safe."
        else:
            return "I'm here for you. Would you like to tell me what's bothering you?"

    async def _generate_welcome_message(self, child_id: str, preferences: Dict) -> str:
        """Generate personalized welcome message"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                "generate welcome message",
                context={
                    "mode": "welcome",
                    "child_age": preferences.get("age", 5),
                    "language": preferences.get("language", "en"),
                },
            )

        # Fallback messages
        messages = {
            "en": "Hello! I'm so happy to talk with you today!",
            "es": "¡Hola! ¡Estoy muy feliz de hablar contigo hoy!",
            "fr": "Bonjour! Je suis très heureux de parler avec toi aujourd'hui!",
            "ar": "مرحبا! أنا سعيد جداً للتحدث معك اليوم!",
        }

        language = preferences.get("language", "en")
        return messages.get(language, messages["en"])

    async def _generate_goodbye_message(
        self, session: SessionContext, summary: Dict
    ) -> str:
        """Generate personalized goodbye message"""

        emotion_summary = summary.get("emotion_summary", {})
        dominant_emotion = emotion_summary.get("dominant", "neutral")

        if self.ai_service:
            return await self.ai_service.generate_response(
                "generate goodbye message",
                context={
                    "mode": "goodbye",
                    "dominant_emotion": dominant_emotion,
                    "duration_minutes": summary["duration_minutes"],
                    "language": session.language_preference,
                },
            )

        # Fallback messages
        if dominant_emotion in ["happy", "excited"]:
            return "That was so much fun! I can't wait to play with you again!"
        elif dominant_emotion in ["sad", "upset"]:
            return "I hope you feel better soon. Remember, I'm always here when you need a friend!"
        else:
            return "It was wonderful talking with you! See you next time!"

    async def _persist_session_summary(
        self, session: SessionContext, summary: Dict
    ) -> None:
        """Persist session summary for analytics"""

        if hasattr(self, "conversation_repository"):
            await self.conversation_repository.save_session_summary(
                child_id=session.child_id,
                session_id=session.session_id,
                summary_data=summary,
            )

    def _get_fallback_response(self, session: SessionContext) -> str:
        """Get appropriate fallback response"""

        fallbacks = {
            "en": "I'm having trouble understanding. Can you say that again?",
            "es": "Tengo problemas para entender. ¿Puedes decirlo de nuevo?",
            "fr": "J'ai du mal à comprendre. Peux-tu répéter?",
            "ar": "أواجه صعوبة في الفهم. هل يمكنك تكرار ذلك؟",
        }

        return fallbacks.get(session.language_preference, fallbacks["en"])

    async def _determine_activity_type(
        self, text: str, emotion: EmotionResult, session: SessionContext
    ) -> ActivityType:
        """Determine the appropriate activity type"""

        # Check for emotional distress first
        if emotion.valence < -0.5 or emotion.primary_emotion in [
            "sad",
            "upset",
            "scared",
        ]:
            return ActivityType.COMFORT

        # Use AI to classify intent
        if self.ai_service:
            intent = await self.ai_service.classify_intent(
                text,
                context={
                    "emotion": emotion.to_dict(),
                    "previous_activity": session.current_activity,
                },
            )

            activity_map = {
                "play_game": ActivityType.GAME,
                "tell_story": ActivityType.STORY,
                "learn": ActivityType.LEARNING,
                "sleep": ActivityType.SLEEP_ROUTINE,
                "chat": ActivityType.CONVERSATION,
            }

            return activity_map.get(intent, ActivityType.CONVERSATION)

        # Simple keyword matching as fallback
        text_lower = text.lower()
        if any(word in text_lower for word in ["game", "play", "fun"]):
            return ActivityType.GAME
        elif any(word in text_lower for word in ["story", "tell me", "once upon"]):
            return ActivityType.STORY
        elif any(word in text_lower for word in ["learn", "teach", "what is", "how"]):
            return ActivityType.LEARNING
        elif any(word in text_lower for word in ["sleep", "tired", "bedtime"]):
            return ActivityType.SLEEP_ROUTINE

        return ActivityType.CONVERSATION

    def _map_emotion_to_voice(self, emotion: EmotionResult) -> str:
        """Map emotion analysis to voice emotion"""

        # High arousal positive
        if emotion.valence > 0.5 and emotion.arousal > 0.5:
            return "excited"

        # Low arousal positive
        if emotion.valence > 0.3 and emotion.arousal < 0.5:
            return "warm"

        # Negative emotions
        if emotion.valence < -0.3:
            return "caring"

        # Neutral
        return "friendly"

    async def _generate_response_for_activity(
        self,
        text: str,
        emotion: EmotionResult,
        activity_type: ActivityType,
        session: SessionContext,
    ) -> str:
        """Generate response for specific activity type"""

        context = {
            "text": text,
            "emotion": emotion.to_dict(),
            "child_age": session.metadata.get("age", 5),
            "language": session.language_preference,
            "history": [i["transcription"] for i in session.interactions[-5:]],
        }

        if activity_type == ActivityType.COMFORT:
            return await self._generate_comfort_response(text, emotion, context)
        elif activity_type == ActivityType.GAME:
            return await self._handle_game_interaction(text, session)
        elif activity_type == ActivityType.STORY:
            return await self._handle_story_request(text, emotion, session)
        elif activity_type == ActivityType.LEARNING:
            return await self._handle_learning_interaction(text, context)
        elif activity_type == ActivityType.SLEEP_ROUTINE:
            return await self._handle_sleep_routine(text, session)
        else:
            return await self._handle_conversation(text, context)

    async def _generate_comfort_response(
        self, text: str, emotion: EmotionResult, context: Dict
    ) -> str:
        """Generate comforting response for distressed child"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                text, context={**context, "mode": "comfort"}
            )

        # Fallback comfort responses
        if emotion.primary_emotion == "sad":
            return "I understand you're feeling sad. Would you like to talk about it or shall we do something fun together?"
        elif emotion.primary_emotion == "scared":
            return "It's okay to feel scared sometimes. I'm here with you. You're safe."
        else:
            return "I'm here for you. Would you like to tell me what's bothering you?"

    async def _handle_game_interaction(self, text: str, session: SessionContext) -> str:
        """Handle game interactions"""

        if self.game_engine:
            return await self.game_engine.process_interaction(
                text, session_id=session.session_id
            )

        return "Let's play a fun game! Can you guess what animal I'm thinking of?"

    async def _handle_story_request(
        self, text: str, emotion: EmotionResult, session: SessionContext
    ) -> str:
        """Handle story requests"""

        if self.story_generator:
            return await self.story_generator.generate_story(
                prompt=text,
                emotion=emotion.primary_emotion,
                interests=session.metadata.get("interests", []),
            )

        return "Once upon a time, there was a brave little teddy bear who loved making new friends..."

    async def _handle_learning_interaction(self, text: str, context: Dict) -> str:
        """Handle educational interactions"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                text, context={**context, "mode": "educational"}
            )

        return "That's a great question! Let me explain it in a fun way..."

    async def _handle_sleep_routine(self, text: str, session: SessionContext) -> str:
        """Handle sleep routine interactions"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                text,
                context={
                    "mode": "sleep_routine",
                    "language": session.language_preference,
                },
            )

        return "Let's get ready for bed! Would you like me to tell you a calming bedtime story?"

    async def _handle_conversation(self, text: str, context: Dict) -> str:
        """Handle general conversation"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                text, context={**context, "mode": "conversation"}
            )

        return "That sounds interesting! Tell me more about it."
