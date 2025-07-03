#!/usr/bin/env python3
"""
🧸 AI Teddy Bear Main Service - Refactored for 2025 (Enhanced)
Core orchestration service using modular components

✅ إصلاح Large Method باستخدام EXTRACT FUNCTION
✅ تحسين جودة الكود واتباع SOLID principles
✅ تقليل طول الدالة من 91 سطر إلى دوال متخصصة
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

import structlog
from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

from src.application.patterns.service_base import ServiceBase
from src.infrastructure.security.audit import AuditEventType, AuditLogger
from src.infrastructure.settings import get_settings

# Import modular components
from .modules.session_manager import SessionContext, SessionManager
from .modules.emotion_analyzer import EmotionResult, EmotionAnalyzer
from .modules.response_generator import (
    ActivityType, ResponseContext, ResponseGenerator
)
from .modules.transcription_service import (
    TranscriptionResult, TranscriptionService
)

# Prometheus metrics
interaction_counter = Counter(
    "teddy_interactions_total",
    "Total interactions processed",
    ["session_type", "emotion", "success"],
)

active_sessions_gauge = Gauge(
    "teddy_active_sessions", "Number of active sessions"
)

response_time_histogram = Histogram(
    "teddy_response_time_seconds", "Response time for interactions"
)

# Distributed tracing
trace_async = trace.get_tracer(__name__).start_as_current_span


class AITeddyBearService(ServiceBase):
    """
    Main AI Teddy Bear Service - Enhanced with EXTRACT FUNCTION refactoring
    Properly integrated with service registry and security
    """

    def __init__(self, registry, config: Dict):
        super().__init__(registry, config)
        self.settings = get_settings()
        self.logger = structlog.get_logger()
        self._tracer = trace.get_tracer(__name__)

        # Services will be injected from registry
        self.audit_logger: Optional[AuditLogger] = None
        self.ai_service = None
        self.voice_service = None
        self.game_engine = None
        self.story_generator = None
        self.health_service = None
        
        # Initialize modular components
        self.session_manager = SessionManager()
        self.emotion_analyzer = EmotionAnalyzer()
        self.response_generator = ResponseGenerator()
        self.transcription_service = TranscriptionService()

    async def initialize(self) -> None:
        """Initialize service with proper dependency injection"""
        self.logger.info("Initializing AI Teddy Bear Service")

        # Get services from registry with retry
        services_to_load = [
            ("audit_logger", True),
            ("ai", True),
            ("voice", True),
            ("game_engine", False),
            ("story_generator", False),
            ("health", True),
        ]

        for service_name, required in services_to_load:
            try:
                service = await self.wait_for_service(service_name, timeout=30)
                setattr(self, service_name.replace("-", "_"), service)
            except asyncio.TimeoutError:
                if required:
                    raise
                self.logger.warning(f"Optional service {service_name} not available")

        # Inject dependencies into modules
        self.emotion_analyzer.ai_service = self.ai_service
        self.response_generator.ai_service = self.ai_service
        self.response_generator.story_generator = self.story_generator
        self.response_generator.game_engine = self.game_engine
        self.transcription_service.voice_service = self.voice_service

        self._state = self.ServiceState.READY
        self.logger.info("AI Teddy Bear Service initialized successfully")

    async def shutdown(self) -> None:
        """Graceful shutdown with proper cleanup"""
        self.logger.info("Shutting down AI Teddy Bear Service")

        # End all active sessions gracefully
        active_count = await self.session_manager.get_active_sessions_count()
        if active_count > 0:
            session_ids = list(self.session_manager.active_sessions.keys())
            shutdown_tasks = []
            for session_id in session_ids:
                shutdown_tasks.append(self.end_session(session_id, reason="shutdown"))

            if shutdown_tasks:
                await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        self._state = self.ServiceState.STOPPED
        active_sessions_gauge.set(0)

    async def health_check(self) -> Dict:
        """Comprehensive health check"""
        checks = {
            "service_state": self._state == self.ServiceState.READY,
            "active_sessions": await self.session_manager.get_active_sessions_count(),
            "transcription_healthy": self.transcription_service is not None,
            "emotion_analyzer_healthy": self.emotion_analyzer is not None,
        }

        # Check critical services
        critical_services = ["ai_service", "voice_service"]
        for service_name in critical_services:
            service = getattr(self, service_name, None)
            if service and hasattr(service, "health_check"):
                try:
                    service_health = await service.health_check()
                    checks[f"{service_name}_healthy"] = service_health.get(
                        "healthy", False
                    )
                # FIXME: replace with specific exception
except Exception as exc:checks[f"{service_name}_healthy"] = False

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
        
        # Create session through session manager
        session = await self.session_manager.create_session(child_id, metadata)

        # Get child preferences from database
        preferences = await self._get_child_preferences(child_id)
        session.language_preference = preferences.get("language", "en")
        session.voice_preference = preferences.get("voice", "default")

        # Update metrics
        active_sessions_gauge.inc()

        # Audit log
        await self.audit_logger.log_event(
            AuditEventType.SESSION_START, child_id, {"session_id": session.session_id}
        )

        # Generate welcome message
        welcome_text = await self.response_generator.generate_welcome_message(
            child_id, preferences
        )
        audio_data = await self.voice_service.text_to_speech(
            welcome_text, voice=session.voice_preference, emotion="friendly"
        )

        self.logger.info("Session started", session_id=session.session_id, child_id=child_id)

        return {
            "session_id": session.session_id,
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
        Process voice interaction - Refactored for better maintainability
        """
        session = await self.session_manager.get_session(session_id)
        if not session:
            return {"error": "Invalid session", "code": "INVALID_SESSION"}

        try:
            # 1. Process audio transcription
            transcription = await self._process_audio_transcription(
                audio_data, session
            )

            # 2. Analyze emotion from multiple modalities
            emotion_result = await self._analyze_interaction_emotion(
                transcription, audio_data, session
            )

            # 3. Generate contextual response
            response = await self._generate_contextual_response(
                transcription, emotion_result, session
            )

            # 4. Create voice output
            audio_response = await self._create_voice_output(
                response, session
            )

            # 5. Update session state and metrics
            interaction_data = await self._update_session_and_metrics(
                session, transcription, emotion_result, response
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
            # Handle interaction errors gracefully
            return await self._handle_interaction_error(e, session)

    async def _process_audio_transcription(
        self, audio_data: bytes, session: SessionContext
    ) -> TranscriptionResult:
        """Process speech to text with fallback support"""
        transcription = await self.transcription_service.transcribe_with_fallback(
            audio_data, session.language_preference
        )
        
        self.logger.debug(
            "Transcription completed",
            session_id=session.session_id,
            confidence=transcription.confidence,
            text_length=len(transcription.text)
        )
        
        return transcription

    async def _analyze_interaction_emotion(
        self, 
        transcription: TranscriptionResult, 
        audio_data: bytes, 
        session: SessionContext
    ) -> EmotionResult:
        """Analyze emotion from text and audio with context"""
        emotion_result = await self.emotion_analyzer.analyze_multimodal(
            text=transcription.text,
            audio_data=audio_data,
            context={
                "previous_emotions": [e.to_dict() for e in session.emotions[-5:]],
                "current_activity": session.current_activity,
            },
        )
        
        # Ensure we have a proper EmotionResult object
        if isinstance(emotion_result, dict):
            emotion_result = EmotionResult(
                primary_emotion=emotion_result.get("primary", "neutral"),
                confidence=emotion_result.get("confidence", 0.5),
                secondary_emotions=emotion_result.get("secondary", {}),
                valence=emotion_result.get("valence", 0.0),
                arousal=emotion_result.get("arousal", 0.0),
            )

        self.logger.debug(
            "Emotion analysis completed",
            session_id=session.session_id,
            primary_emotion=emotion_result.primary_emotion,
            confidence=emotion_result.confidence
        )
        
        return emotion_result

    async def _generate_contextual_response(
        self, 
        transcription: TranscriptionResult, 
        emotion_result: EmotionResult, 
        session: SessionContext
    ) -> ResponseContext:
        """Generate appropriate response based on context and emotion"""
        response = await self.response_generator.generate_contextual_response(
            transcription.text, emotion_result, session
        )
        
        self.logger.debug(
            "Response generated",
            session_id=session.session_id,
            activity_type=response.activity_type.value,
            response_length=len(response.text)
        )
        
        return response

    async def _create_voice_output(
        self, response: ResponseContext, session: SessionContext
    ) -> bytes:
        """Generate voice response with appropriate emotion and settings"""
        audio_response = await self._generate_voice_response(
            response.text, response.emotion, session
        )
        
        self.logger.debug(
            "Voice output created",
            session_id=session.session_id,
            emotion=response.emotion
        )
        
        return audio_response

    async def _update_session_and_metrics(
        self, 
        session: SessionContext,
        transcription: TranscriptionResult,
        emotion_result: EmotionResult,
        response: ResponseContext
    ) -> Dict:
        """Update session state, metrics, and perform logging"""
        # Create interaction record
        interaction = {
            "timestamp": datetime.utcnow(),
            "transcription": transcription.text,
            "confidence": transcription.confidence,
            "emotion": emotion_result.to_dict(),
            "response": response.text,
            "activity_type": response.activity_type.value,
            "duration_ms": response.processing_time,
        }

        # Update session data
        await self.session_manager.add_interaction(session.session_id, interaction)
        session.emotions.append(emotion_result)
        await self._persist_interaction(session, interaction)

        # Update Prometheus metrics
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
                "session_id": session.session_id,
                "emotion": emotion_result.primary_emotion,
                "activity": response.activity_type.value,
            },
        )

        self.logger.info(
            "Session state updated",
            session_id=session.session_id,
            interaction_count=session.interaction_count
        )
        
        return interaction

    async def _handle_interaction_error(
        self, error: Exception, session: SessionContext
    ) -> Dict:
        """Handle interaction errors with graceful fallback"""
        self.logger.error(
            "Voice interaction failed",
            session_id=session.session_id,
            error=str(error),
            exc_info=True,
        )

        # Update error metrics
        interaction_counter.labels(
            session_type="error", emotion="unknown", success="false"
        ).inc()

        # Generate fallback response
        fallback_text = self.response_generator.get_fallback_response(session)
        fallback_audio = await self._generate_voice_response(
            fallback_text, "caring", session
        )

        return {
            "success": False,
            "error": str(error),
            "response": fallback_text,
            "audio_data": fallback_audio,
            "session_id": session.session_id,
        }

    # Private helper methods

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

    async def _persist_session_summary(
        self, session: SessionContext, summary: Dict
    ) -> None:
        """Persist session summary for analytics"""

        if hasattr(self, "session_repository"):
            await self.session_repository.save_session_summary(
                session_id=session.session_id,
                child_id=session.child_id,
                summary_data=summary,
            )

    # Periodic maintenance tasks

    async def cleanup_old_sessions(self) -> None:
        """Periodic task to clean up old sessions"""
        cleaned = await self.session_manager.cleanup_old_sessions(max_age_hours=24)
        self.logger.info(f"Cleaned up {cleaned} old sessions")
