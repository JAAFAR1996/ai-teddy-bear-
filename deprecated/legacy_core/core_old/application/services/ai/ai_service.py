"""
AI Service - Refactored and Modernized for 2025
Main orchestrator for AI capabilities
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from opentelemetry import trace

from src.application.services.service_registry import ServiceBase
from src.application.services.circuit_breaker import CircuitBreaker
from src.infrastructure.observability import trace_async, get_tracer
from src.infrastructure.security.audit_logger import AuditLogger, AuditEventType
from src.infrastructure.security.data_encryption import DataEncryptionService, EncryptionLevel
from core.infrastructure.session_manager import SessionManager

from .emotion_analyzer import EmotionAnalyzer, EmotionAnalysis
from .response_generator import ResponseGenerator
from .models import ResponseMode, EmotionalTone, AIResponse

logger = structlog.get_logger()


class AIService(ServiceBase):
    """
    Modern AI Service with modular architecture
    Coordinates emotion analysis, response generation, and more
    """
    
    def __init__(self, registry, config: Dict):
        super().__init__(registry, config)
        self._tracer = get_tracer(__name__)
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            half_open_max_calls=3
        )
        
        # Initialize components
        self.emotion_analyzer = EmotionAnalyzer(registry, config)
        self.response_generator = ResponseGenerator(registry, config)
        
        # Services will be injected
        self.session_manager: Optional[SessionManager] = None
        self.audit_logger: Optional[AuditLogger] = None
        self.encryption_service: Optional[DataEncryptionService] = None
        self.moderation_service = None
        self.memory_service = None
    
    async def initialize(self) -> None:
        """Initialize the AI service and all components"""
        with self._tracer.start_as_current_span("ai_service_init"):
            self.logger.info("Initializing AI service")
            
            # Initialize components
            await self.emotion_analyzer.initialize()
            await self.response_generator.initialize()
            
            # Get required services
            self.session_manager = await self.wait_for_service("session_manager")
            self.audit_logger = await self.wait_for_service("audit_logger")
            self.encryption_service = await self.wait_for_service("encryption")
            self.moderation_service = await self.wait_for_service("moderation")
            self.memory_service = await self.wait_for_service("memory")
            
            self._state = self.ServiceState.READY
            self.logger.info("AI service initialized successfully")
    
    async def shutdown(self) -> None:
        """Shutdown the AI service"""
        self.logger.info("Shutting down AI service")
        
        # Shutdown components
        await self.emotion_analyzer.shutdown()
        await self.response_generator.shutdown()
        
        self._state = self.ServiceState.STOPPED
    
    async def health_check(self) -> Dict:
        """Health check for AI service"""
        health_results = {
            "healthy": True,
            "service": "ai_service",
            "components": {}
        }
        
        # Check each component
        for name, component in [
            ("emotion_analyzer", self.emotion_analyzer),
            ("response_generator", self.response_generator)
        ]:
            try:
                component_health = await component.health_check()
                health_results["components"][name] = component_health.get("healthy", False)
                if not component_health.get("healthy", False):
                    health_results["healthy"] = False
            except Exception as e:
                health_results["components"][name] = False
                health_results["healthy"] = False
                self.logger.error(f"Health check failed for {name}", error=str(e))
        
        return health_results
    
    @trace_async("ai_generate_response")
    async def generate_response(
        self,
        text: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Main entry point for generating AI responses
        """
        span = trace.get_current_span()
        span.set_attribute("session_id", session_id)
        
        try:
            # Get session data
            session = await self.session_manager.get_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            
            child_id = session.child_id
            
            # Decrypt child data if needed
            child_info = await self._get_child_info(child_id)
            
            # Analyze emotion with circuit breaker
            emotion_analysis = await self._circuit_breaker.call(
                self.emotion_analyzer.analyze,
                text,
                child_info.get("language", "ar")
            )
            
            # Check moderation
            moderation_result = await self.moderation_service.moderate_input(
                text=text,
                user_id=child_id,
                session_id=session_id
            )
            
            if not moderation_result.get("safe", True):
                # Log moderation event
                await self.audit_logger.log_event(
                    event_type=AuditEventType.MODERATION_ACTION,
                    action="input_blocked",
                    result="blocked",
                    child_id=child_id,
                    session_id=session_id,
                    details={"reason": moderation_result.get("reason")}
                )
                
                return await self._generate_safe_response(child_info)
            
            # Determine response mode based on context and emotion
            response_mode = await self._determine_response_mode(
                emotion_analysis, context, child_info
            )
            
            # Get conversation context from memory service
            conversation_context = await self.memory_service.get_conversation_context(
                session_id, child_id
            )
            
            # Generate response
            response_text = await self._circuit_breaker.call(
                self.response_generator.generate,
                text,
                emotion_analysis,
                response_mode,
                conversation_context,
                child_info
            )
            
            # Moderate output
            output_moderation = await self.moderation_service.moderate_output(
                text=response_text,
                user_id=child_id,
                session_id=session_id
            )
            
            if not output_moderation.get("safe", True):
                response_text = await self._generate_safe_response(child_info)
            
            # Update conversation memory
            await self.memory_service.add_to_conversation(
                session_id=session_id,
                child_id=child_id,
                user_message=text,
                ai_response=response_text,
                emotion=emotion_analysis.primary_emotion.value,
                metadata={
                    "response_mode": response_mode.value,
                    "emotion_confidence": emotion_analysis.confidence
                }
            )
            
            # Log successful interaction
            await self.audit_logger.log_event(
                event_type=AuditEventType.CHILD_CONVERSATION,
                action="response_generated",
                result="success",
                child_id=child_id,
                session_id=session_id,
                details={
                    "emotion": emotion_analysis.primary_emotion.value,
                    "response_mode": response_mode.value,
                    "response_length": len(response_text)
                }
            )
            
            # Update session activity
            await self.session_manager.update_session(
                session_id,
                data={
                    "last_interaction": datetime.utcnow().isoformat(),
                    "interaction_count": session.data.get("interaction_count", 0) + 1
                }
            )
            
            return response_text
            
        except Exception as e:
            span.record_exception(e)
            self.logger.error("Failed to generate response", error=str(e), session_id=session_id)
            
            # Log error
            await self.audit_logger.log_event(
                event_type=AuditEventType.ERROR_OCCURRED,
                action="response_generation",
                result="failure",
                session_id=session_id,
                details={"error": str(e)}
            )
            
            # Return safe fallback
            try:
                child_info = await self._get_child_info(session.child_id if session else None)
                return await self._generate_safe_response(child_info)
            except:
                return "عذراً، لم أفهم. هل يمكنك إعادة المحاولة؟"
    
    @trace_async("create_session_context")
    async def create_session_context(self, child, session_id: str) -> None:
        """Create initial context for a new session"""
        try:
            # Initialize memory for session
            await self.memory_service.initialize_session(
                session_id=session_id,
                child_id=child.id,
                child_info={
                    "name": child.name,
                    "age": child.age,
                    "language": child.preferences.language,
                    "interests": child.preferences.interests
                }
            )
            
            self.logger.info("Session context created", session_id=session_id, child_id=child.id)
            
        except Exception as e:
            self.logger.error("Failed to create session context", error=str(e))
            raise
    
    async def _get_child_info(self, child_id: Optional[str]) -> Dict[str, Any]:
        """Get decrypted child information"""
        if not child_id:
            return {
                "name": "صديقي",
                "age": 5,
                "language": "ar",
                "interests": []
            }
        
        try:
            # Get child data from repository
            child_repo = self.get_service("child_repository")
            child = await child_repo.get(child_id)
            
            if not child:
                return self._get_default_child_info()
            
            # Decrypt sensitive data if needed
            decrypted_name = await self.encryption_service.decrypt_field(
                child.name, child_id, "name"
            )
            
            return {
                "name": decrypted_name,
                "age": child.age,
                "language": child.preferences.language,
                "interests": child.preferences.interests
            }
            
        except Exception as e:
            self.logger.error("Failed to get child info", error=str(e), child_id=child_id)
            return self._get_default_child_info()
    
    def _get_default_child_info(self) -> Dict[str, Any]:
        """Get default child info"""
        return {
            "name": "صديقي",
            "age": 5,
            "language": "ar",
            "interests": []
        }
    
    async def _determine_response_mode(
        self,
        emotion: EmotionAnalysis,
        context: Optional[Dict[str, Any]],
        child_info: Dict[str, Any]
    ) -> ResponseMode:
        """Determine the appropriate response mode"""
        # Check for specific context hints
        if context:
            if context.get("mode"):
                return ResponseMode(context["mode"])
            
            if context.get("educational"):
                return ResponseMode.EDUCATIONAL
            
            if context.get("story_mode"):
                return ResponseMode.STORYTELLING
        
        # Determine based on emotion
        if emotion.primary_emotion.value in ["sad", "scared", "angry"]:
            return ResponseMode.SUPPORTIVE
        
        if emotion.primary_emotion.value == "curious":
            return ResponseMode.EDUCATIONAL
        
        if emotion.primary_emotion.value == "excited":
            return ResponseMode.PLAYFUL
        
        # Default mode
        return ResponseMode.CONVERSATIONAL
    
    async def _generate_safe_response(self, child_info: Dict[str, Any]) -> str:
        """Generate a safe fallback response"""
        if child_info.get("language") == "ar":
            responses = [
                "هذا موضوع مهم! دعنا نتحدث عن شيء آخر ممتع.",
                "أحب أن أتعلم أشياء جديدة معك! ماذا تريد أن نفعل اليوم؟",
                "دعنا نلعب لعبة أو نحكي قصة جميلة!"
            ]
        else:
            responses = [
                "That's an important topic! Let's talk about something else fun.",
                "I love learning new things with you! What would you like to do today?",
                "Let's play a game or tell a nice story!"
            ]
        
        import random
        return random.choice(responses)
    
    def get_response_mode_for_context(self, context: str) -> ResponseMode:
        """Get appropriate response mode for a given context"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["learn", "تعلم", "teach", "علم"]):
            return ResponseMode.EDUCATIONAL
        elif any(word in context_lower for word in ["play", "لعب", "game", "fun"]):
            return ResponseMode.PLAYFUL
        elif any(word in context_lower for word in ["story", "قصة", "tale"]):
            return ResponseMode.STORYTELLING
        elif any(word in context_lower for word in ["sad", "حزين", "scared", "خائف"]):
            return ResponseMode.SUPPORTIVE
        elif any(word in context_lower for word in ["create", "imagine", "تخيل"]):
            return ResponseMode.CREATIVE
        
        return ResponseMode.CONVERSATIONAL 