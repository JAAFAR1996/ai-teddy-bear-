"""
🎙️ Modern Voice Service - 2025 Edition
Clean orchestration of voice interaction with streaming capabilities
"""

import asyncio
import logging
import time
from typing import Dict, Any, AsyncIterator, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Domain imports
from domain.entities.child import Child
from domain.value_objects import EmotionalTone

# Audio services
from .transcription_service import (
    ModernTranscriptionService, 
    TranscriptionConfig,
    create_transcription_service
)
from .synthesis_service import (
    ModernSynthesisService,
    SynthesisConfig,
    VoiceCharacter,
    create_synthesis_service
)

# Application services
from application.services.ai_service import ModernOpenAIService, AIResponseModel

logger = logging.getLogger(__name__)

# ================== CONFIGURATION ==================

@dataclass
class VoiceConfig:
    """Complete voice service configuration"""
    # Transcription settings
    transcription: TranscriptionConfig
    
    # Synthesis settings
    synthesis: SynthesisConfig
    
    # Voice interaction settings
    wake_word_enabled: bool = True
    wake_words: List[str] = None
    
    # Performance settings
    max_interaction_duration: float = 300.0  # 5 minutes
    response_timeout: float = 10.0  # seconds
    streaming_chunk_size: int = 1024
    
    # Language settings
    auto_language_detection: bool = True
    default_language: str = "en"
    supported_languages: List[str] = None
    
    def __post_init__(self):
        if self.wake_words is None:
            self.wake_words = [
                "hey teddy", "hello teddy", "مرحبا دبدوب", 
                "يا دبدوب", "أهلا دبدوب"
            ]
        
        if self.supported_languages is None:
            self.supported_languages = ["en", "ar", "es", "fr"]

@dataclass
class VoiceInteractionResult:
    """Result of a complete voice interaction"""
    session_id: str
    transcription: Dict[str, Any]
    ai_response: AIResponseModel
    synthesis_duration: float
    total_duration: float
    language_detected: str
    confidence: float
    error: Optional[str] = None

# ================== MAIN VOICE SERVICE ==================

class ModernVoiceService:
    """
    🎙️ Modern Voice Service with 2025 Features:
    
    This is the clean replacement for the massive voice_interaction_service.py
    
    Features:
    - Clean separation of concerns (Transcription → AI → Synthesis)
    - Real-time streaming voice interaction
    - Multi-language support with auto-detection
    - Emotional voice modulation
    - Performance monitoring and health checks
    - Smart fallback mechanisms
    - Session management and context preservation
    """
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig(
            transcription=TranscriptionConfig(),
            synthesis=SynthesisConfig()
        )
        
        # Core services (will be injected)
        self.transcription_service: Optional[ModernTranscriptionService] = None
        self.synthesis_service: Optional[ModernSynthesisService] = None
        self.ai_service: Optional[ModernOpenAIService] = None
        
        # Session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "average_response_time": 0.0,
            "language_distribution": {},
            "emotion_distribution": {}
        }
        
        logger.info("✅ Modern Voice Service initialized")
    
    async def initialize(
        self,
        transcription_service: ModernTranscriptionService,
        synthesis_service: ModernSynthesisService,
        ai_service: ModernOpenAIService
    ) -> None:
        """Initialize voice service with dependencies"""
        try:
            self.transcription_service = transcription_service
            self.synthesis_service = synthesis_service
            self.ai_service = ai_service
            
            # Health check all services
            health_checks = await asyncio.gather(
                self.transcription_service.health_check(),
                self.synthesis_service.health_check(),
                return_exceptions=True
            )
            
            logger.info("🚀 Voice service fully initialized")
            logger.debug(f"Service health: {health_checks}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize voice service: {e}")
            raise
    
    async def process_voice_interaction(
        self,
        audio_stream: AsyncIterator[bytes],
        child: Child,
        session_id: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """
        🌊 Main voice interaction pipeline with streaming
        
        This replaces the complex voice interaction in the old service
        
        Flow: Audio Stream → Transcription → AI Processing → Synthesis → Audio Stream
        
        Args:
            audio_stream: Incoming audio stream from ESP32/client
            child: Child profile for personalization
            session_id: Session identifier
            
        Yields:
            Audio response chunks
        """
        start_time = time.time()
        interaction_session_id = session_id or f"voice_{child.device_id}_{int(start_time)}"
        
        try:
            logger.info(f"🎙️ Starting voice interaction for {child.name} (session: {interaction_session_id})")
            
            # Convert audio stream to numpy arrays for transcription
            audio_numpy_stream = self._convert_audio_stream(audio_stream)
            
            # Stream transcription
            transcription_results = []
            async for transcription_result in self.transcription_service.transcribe_stream(audio_numpy_stream):
                transcription_results.append(transcription_result)
                
                # Check if we have enough confidence to process
                if transcription_result["confidence"] >= 0.8:
                    logger.info(f"🎯 Transcribed: '{transcription_result['text']}'")
                    
                    # Generate AI response
                    ai_response = await self.ai_service.generate_response(
                        message=transcription_result["text"],
                        child=child,
                        session_id=interaction_session_id
                    )
                    
                    # Detect emotion for voice synthesis
                    emotion = EmotionalTone.from_string(ai_response.emotion)
                    
                    # Determine language and character
                    language = transcription_result.get("language", "en")
                    character_id = "teddy_ar" if language == "ar" else "teddy_en"
                    
                    # Stream synthesis
                    logger.info(f"🔊 Synthesizing response with emotion: {emotion}")
                    async for audio_chunk in self.synthesis_service.synthesize_stream(
                        text=ai_response.text,
                        emotion=emotion,
                        character_id=character_id,
                        language=language
                    ):
                        yield audio_chunk
                    
                    # Update statistics
                    self._update_interaction_stats(
                        language=language,
                        emotion=emotion,
                        duration=time.time() - start_time,
                        success=True
                    )
                    
                    break  # Process one interaction at a time
            
        except Exception as e:
            logger.error(f"❌ Voice interaction failed: {e}")
            self._update_interaction_stats(success=False)
            
            # Generate fallback response
            async for chunk in self._generate_fallback_response(child):
                yield chunk
    
    async def process_single_voice_interaction(
        self,
        audio_data: bytes,
        child: Child,
        session_id: Optional[str] = None
    ) -> VoiceInteractionResult:
        """
        🎯 Process a single voice interaction (non-streaming)
        
        Perfect for testing and simple interactions
        
        Args:
            audio_data: Audio data as bytes
            child: Child profile
            session_id: Session identifier
            
        Returns:
            Complete interaction result
        """
        start_time = time.time()
        interaction_session_id = session_id or f"single_{child.device_id}_{int(start_time)}"
        
        try:
            logger.info(f"🎯 Processing single voice interaction for {child.name}")
            
            # Transcribe audio
            transcription_result = await self.transcription_service.transcribe_audio(
                audio_data=audio_data,
                language=None,  # Auto-detect
                provider="whisper"
            )
            
            if transcription_result["confidence"] < 0.5:
                raise ValueError(f"Low transcription confidence: {transcription_result['confidence']}")
            
            logger.info(f"📝 Transcribed: '{transcription_result['text']}'")
            
            # Generate AI response
            ai_response = await self.ai_service.generate_response(
                message=transcription_result["text"],
                child=child,
                session_id=interaction_session_id
            )
            
            # Synthesize response
            emotion = EmotionalTone.from_string(ai_response.emotion)
            language = transcription_result.get("language", "en")
            character_id = "teddy_ar" if language == "ar" else "teddy_en"
            
            synthesis_start = time.time()
            audio_response = await self.synthesis_service.synthesize_audio(
                text=ai_response.text,
                emotion=emotion,
                character_id=character_id,
                language=language
            )
            synthesis_duration = time.time() - synthesis_start
            
            total_duration = time.time() - start_time
            
            # Create result
            result = VoiceInteractionResult(
                session_id=interaction_session_id,
                transcription=transcription_result,
                ai_response=ai_response,
                synthesis_duration=synthesis_duration,
                total_duration=total_duration,
                language_detected=language,
                confidence=transcription_result["confidence"]
            )
            
            # Update statistics
            self._update_interaction_stats(
                language=language,
                emotion=emotion,
                duration=total_duration,
                success=True
            )
            
            logger.info(f"✅ Voice interaction completed in {total_duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Single voice interaction failed: {e}")
            self._update_interaction_stats(success=False)
            
            return VoiceInteractionResult(
                session_id=interaction_session_id,
                transcription={"text": "", "confidence": 0.0},
                ai_response=AIResponseModel(
                    text="I'm sorry, I didn't understand that. Could you try again?",
                    emotion="friendly",
                    category="error",
                    learning_points=[],
                    session_id=interaction_session_id
                ),
                synthesis_duration=0.0,
                total_duration=time.time() - start_time,
                language_detected="unknown",
                confidence=0.0,
                error=str(e)
            )
    
    async def _convert_audio_stream(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator:
        """Convert byte audio stream to numpy arrays for transcription"""
        import numpy as np
        
        async for audio_chunk in audio_stream:
            try:
                # Convert bytes to numpy array
                audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
                yield audio_array
            except Exception as e:
                logger.error(f"❌ Audio conversion error: {e}")
                continue
    
    async def _generate_fallback_response(self, child: Child) -> AsyncIterator[bytes]:
        """Generate fallback response when main pipeline fails"""
        try:
            fallback_text = f"Sorry {child.name}, I didn't catch that. Could you try again?"
            
            async for chunk in self.synthesis_service.synthesize_stream(
                text=fallback_text,
                emotion=EmotionalTone.FRIENDLY,
                character_id="teddy_en",
                language="en"
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ Fallback response generation failed: {e}")
            # Generate silence as last resort
            silence = b'\x00' * 1024
            for _ in range(10):  # 10 chunks of silence
                yield silence
                await asyncio.sleep(0.1)
    
    def _update_interaction_stats(
        self,
        language: str = "unknown",
        emotion: EmotionalTone = EmotionalTone.NEUTRAL,
        duration: float = 0.0,
        success: bool = True
    ) -> None:
        """Update interaction statistics"""
        self.stats["total_interactions"] += 1
        
        if success:
            self.stats["successful_interactions"] += 1
            
            # Update average response time
            current_avg = self.stats["average_response_time"]
            count = self.stats["successful_interactions"]
            self.stats["average_response_time"] = (
                (current_avg * (count - 1) + duration) / count
            )
            
            # Update language distribution
            if language not in self.stats["language_distribution"]:
                self.stats["language_distribution"][language] = 0
            self.stats["language_distribution"][language] += 1
            
            # Update emotion distribution
            emotion_str = emotion.value if hasattr(emotion, 'value') else str(emotion)
            if emotion_str not in self.stats["emotion_distribution"]:
                self.stats["emotion_distribution"][emotion_str] = 0
            self.stats["emotion_distribution"][emotion_str] += 1
            
        else:
            self.stats["failed_interactions"] += 1
    
    async def detect_wake_word(
        self,
        audio_data: bytes,
        wake_words: Optional[List[str]] = None
    ) -> bool:
        """
        🎯 Wake word detection
        
        Simplified and clean wake word detection
        
        Args:
            audio_data: Audio data to analyze
            wake_words: List of wake words (uses config default if None)
            
        Returns:
            True if wake word detected
        """
        if not self.config.wake_word_enabled:
            return True  # Always "detected" if disabled
        
        try:
            # Use transcription service for wake word detection
            transcription_result = await self.transcription_service.transcribe_audio(
                audio_data=audio_data,
                language=None  # Auto-detect
            )
            
            if transcription_result["confidence"] < 0.5:
                return False
            
            text = transcription_result["text"].lower().strip()
            target_wake_words = wake_words or self.config.wake_words
            
            # Check for wake words
            for wake_word in target_wake_words:
                if wake_word.lower() in text:
                    logger.info(f"🎯 Wake word detected: '{wake_word}' in '{text}'")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Wake word detection failed: {e}")
            return False  # Fail safe
    
    async def set_voice_character(
        self,
        character_id: str,
        language: Optional[str] = None
    ) -> bool:
        """Set voice character for synthesis"""
        if self.synthesis_service:
            success = self.synthesis_service.set_character(character_id)
            if success:
                logger.info(f"🎭 Voice character changed to: {character_id}")
            return success
        return False
    
    def get_available_characters(self) -> List[Dict[str, Any]]:
        """Get available voice characters"""
        if self.synthesis_service:
            return self.synthesis_service.get_available_characters()
        return []
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages"""
        return self.config.supported_languages
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        base_stats = self.stats.copy()
        
        # Add success rate
        total = base_stats["total_interactions"]
        if total > 0:
            base_stats["success_rate"] = base_stats["successful_interactions"] / total
            base_stats["failure_rate"] = base_stats["failed_interactions"] / total
        else:
            base_stats["success_rate"] = 0.0
            base_stats["failure_rate"] = 0.0
        
        # Add service metrics if available
        if self.transcription_service:
            base_stats["transcription_metrics"] = self.transcription_service.get_performance_metrics()
        
        if self.synthesis_service:
            base_stats["synthesis_metrics"] = self.synthesis_service.get_performance_metrics()
        
        return base_stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            health_status = {
                "voice_service": "healthy",
                "transcription_service": "unknown",
                "synthesis_service": "unknown",
                "ai_service": "unknown"
            }
            
            # Check transcription service
            if self.transcription_service:
                transcription_health = await self.transcription_service.health_check()
                health_status["transcription_service"] = transcription_health.get("status", "unknown")
            
            # Check synthesis service
            if self.synthesis_service:
                synthesis_health = await self.synthesis_service.health_check()
                health_status["synthesis_service"] = synthesis_health.get("status", "unknown")
            
            # Check AI service (if it has health check)
            if hasattr(self.ai_service, 'health_check'):
                ai_health = await self.ai_service.health_check()
                health_status["ai_service"] = ai_health.get("status", "healthy")
            else:
                health_status["ai_service"] = "healthy" if self.ai_service else "unavailable"
            
            # Overall health
            services_healthy = all(
                status in ["healthy", "degraded"] 
                for status in health_status.values()
            )
            
            health_status["overall"] = "healthy" if services_healthy else "unhealthy"
            health_status["timestamp"] = datetime.utcnow().isoformat()
            
            return health_status
            
        except Exception as e:
            return {
                "overall": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# ================== FACTORY FUNCTION ==================

async def create_voice_service(
    config: Optional[VoiceConfig] = None,
    transcription_config: Optional[TranscriptionConfig] = None,
    synthesis_config: Optional[SynthesisConfig] = None,
    openai_api_key: Optional[str] = None,
    elevenlabs_api_key: Optional[str] = None,
    azure_speech_key: Optional[str] = None,
    azure_speech_region: str = "eastus"
) -> ModernVoiceService:
    """
    🏭 Factory function to create a complete voice service
    
    This replaces the complex initialization in the old service
    """
    # Create configuration
    if config is None:
        config = VoiceConfig(
            transcription=transcription_config or TranscriptionConfig(),
            synthesis=synthesis_config or SynthesisConfig()
        )
    
    # Create and initialize services
    transcription_service = await create_transcription_service(
        config=config.transcription,
        openai_api_key=openai_api_key
    )
    
    synthesis_service = await create_synthesis_service(
        config=config.synthesis,
        elevenlabs_api_key=elevenlabs_api_key,
        openai_api_key=openai_api_key,
        azure_speech_key=azure_speech_key,
        azure_speech_region=azure_speech_region
    )
    
    # AI service would be injected from the main container
    # For now, we'll set it during voice service initialization
    
    # Create voice service
    voice_service = ModernVoiceService(config)
    
    return voice_service

# Re-export for compatibility
VoiceService = ModernVoiceService
