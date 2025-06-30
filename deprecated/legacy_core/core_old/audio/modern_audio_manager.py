"""
Modern Audio Manager - 2025 Standards
Pure asyncio implementation, no threading conflicts
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, List, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import structlog
import os
import json

from src.infrastructure.modern_container import BaseService
from .hume_emotion_analyzer import HumeSpeechEmotionAnalyzer, ChildVoiceEmotion

# Import enhanced audio manager components
try:
    from .audio_manager import (
        AudioSessionType,
        AudioQualityMode,
        AudioFormatType,
        AudioSystemConfig,
        AudioSession,
        AudioSystemError,
        EnhancedAudioManager
    )
    ENHANCED_AUDIO_AVAILABLE = True
except ImportError:
    ENHANCED_AUDIO_AVAILABLE = False
    # Define basic enums if enhanced manager not available
    class AudioSessionType(Enum):
        CONVERSATION = "conversation"
        STORY_TELLING = "story_telling"
        LEARNING = "learning"
        PLAY_TIME = "play_time"
        EMERGENCY = "emergency"
    
    class AudioQualityMode(Enum):
        POWER_SAVE = "power_save"
        BALANCED = "balanced"
        HIGH_QUALITY = "high_quality"
        ADAPTIVE = "adaptive"

# Try to import dependency injection
try:
    from ..infrastructure.container import Container
    CONTAINER_AVAILABLE = True
except ImportError:
    CONTAINER_AVAILABLE = False
    
    # Mock container for testing
    class MockContainer:
        def __init__(self):
            self.services = {}
        
        def get(self, service_name):
            return self.services.get(service_name)
        
        def register(self, service_name, service):
            self.services[service_name] = service

# Try to import emotion analysis
try:
    from ..application.services.emotion_analyzer import ChildVoiceEmotion
    EMOTION_ANALYSIS_AVAILABLE = True
except ImportError:
    EMOTION_ANALYSIS_AVAILABLE = False
    
    @dataclass
    class ChildVoiceEmotion:
        dominant_emotion: str = "neutral"
        emotional_intensity: float = 0.5
        sadness: float = 0.0
        joy: float = 0.0
        fear: float = 0.0
        anger: float = 0.0
        curiosity: float = 0.0
        playfulness: float = 0.0
        tiredness: float = 0.0
        calmness: float = 0.0
        developmental_indicators: List[str] = field(default_factory=list)

# Try to import base service
try:
    from ..application.services.base_service import BaseService
    BASE_SERVICE_AVAILABLE = True
except ImportError:
    BASE_SERVICE_AVAILABLE = False
    
    class BaseService:
        def __init__(self):
            self.logger = logging.getLogger(__name__)


class ModernAudioManager(BaseService if BASE_SERVICE_AVAILABLE else object):
    """
    Modern Audio Manager with async support and enhanced features.
    Integrates with the Enhanced Audio Manager for full functionality.
    """

    def __init__(self, container: Optional[Any] = None):
        """Initialize modern audio manager with dependency injection."""
        
        if BASE_SERVICE_AVAILABLE:
            super().__init__()
        else:
            self.logger = logging.getLogger(__name__)
        
        self.container = container or MockContainer()
        
        # Initialize configuration
        self.config = self._create_default_config()
        
        # Enhanced audio manager integration
        self.enhanced_manager: Optional[EnhancedAudioManager] = None
        
        # Session management
        self.active_sessions: Dict[str, AudioSession] = {}
        self.current_session: Optional[AudioSession] = None
        
        # Performance tracking
        self.performance_stats = {
            "total_recordings": 0,
            "total_playbacks": 0,
            "total_errors": 0,
            "average_processing_time": 0.0,
            "last_error": None,
            "uptime_start": datetime.now()
        }
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {
            "session_start": [],
            "session_end": [],
            "recording_start": [],
            "recording_end": [],
            "playback_start": [],
            "playback_end": [],
            "error": []
        }
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Component references (will be injected)
        self._recorder = None
        self._processor = None
        self._tts = None
        self._audio_io = None
        self._hume_analyzer = None
        self._speech_to_text_service = None
        self._tts_service = None
        
        self.logger.info("Modern audio manager initialized")

    def _create_default_config(self) -> AudioSystemConfig:
        """Create default configuration."""
        if ENHANCED_AUDIO_AVAILABLE:
            return AudioSystemConfig(
                default_record_duration=10,
                max_record_duration=60,
                auto_process_audio=True,
                auto_save_sessions=True,
                noise_reduction_enabled=True,
                voice_activity_detection=True,
                adaptive_quality=True,
                session_timeout_minutes=30,
                max_concurrent_sessions=3,
                volume_level=0.8,
                language_preference="en",
                child_safe_mode=True
            )
        else:
            # Return mock config
            return type('Config', (), {
                'default_record_duration': 10,
                'max_record_duration': 60,
                'auto_process_audio': True,
                'auto_save_sessions': True,
                'session_timeout_minutes': 30,
                'max_concurrent_sessions': 3,
                'volume_level': 0.8,
                'language_preference': "en",
                'child_safe_mode': True
            })()

    async def initialize(self) -> None:
        """Initialize the modern audio manager and all components."""
        
        try:
            self.logger.info("Initializing modern audio manager...")
            
            # Initialize enhanced audio manager if available
            if ENHANCED_AUDIO_AVAILABLE:
                self.enhanced_manager = EnhancedAudioManager(self.config)
                self.logger.info("Enhanced audio manager initialized")
            
            # Initialize injected components
            await self._init_components()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.logger.info("Modern audio manager initialization complete")
        
        except Exception as e:
            self.logger.error(f"Error initializing modern audio manager: {e}")
            raise AudioSystemError(f"Failed to initialize: {e}")

    async def _init_components(self):
        """Initialize audio components from container."""
        
        try:
            # Try to get components from container
            if self.container:
                self._recorder = self.container.get("audio_recorder")
                self._processor = self.container.get("audio_processor")
                self._tts = self.container.get("tts_service")
                self._audio_io = self.container.get("audio_io")
                self._hume_analyzer = self.container.get("hume_analyzer")
                self._speech_to_text_service = self.container.get("speech_to_text")
                self._tts_service = self.container.get("tts_service")
            
            # Use enhanced manager components if available
            if self.enhanced_manager:
                if not self._recorder:
                    self._recorder = getattr(self.enhanced_manager, 'recorder', None)
                if not self._processor:
                    self._processor = getattr(self.enhanced_manager, 'processor', None)
                if not self._tts:
                    self._tts = getattr(self.enhanced_manager, 'tts', None)
                if not self._audio_io:
                    self._audio_io = getattr(self.enhanced_manager, 'audio_io', None)
            
            # Create mock components if nothing available
            if not self._recorder:
                self._recorder = MockAudioRecorder()
            if not self._processor:
                self._processor = MockAudioProcessor()
            if not self._tts:
                self._tts = MockTTSEngine()
            if not self._audio_io:
                self._audio_io = MockAudioIO()
            
            self.logger.info("Audio components initialized")
        
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")

    async def _start_background_tasks(self):
        """Start background monitoring and cleanup tasks."""
        
        try:
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self.logger.info("Background tasks started")
        
        except Exception as e:
            self.logger.error(f"Error starting background tasks: {e}")

    async def start_session(
        self,
        child_id: str,
        session_type: AudioSessionType = AudioSessionType.CONVERSATION,
        quality_mode: AudioQualityMode = AudioQualityMode.BALANCED
    ) -> str:
        """Start a new audio session asynchronously."""
        
        try:
            # Use enhanced manager if available
            if self.enhanced_manager:
                session_id = self.enhanced_manager.start_session(
                    child_id, session_type, quality_mode
                )
                # Sync with local tracking
                if session_id in self.enhanced_manager.active_sessions:
                    session = self.enhanced_manager.active_sessions[session_id]
                    self.active_sessions[session_id] = session
                    self.current_session = session
                
                return session_id
            
            # Fallback implementation
            session_id = f"session_{child_id}_{int(datetime.now().timestamp())}"
            
            if ENHANCED_AUDIO_AVAILABLE:
                session = AudioSession(
                    session_id=session_id,
                    session_type=session_type,
                    child_id=child_id,
                    start_time=datetime.now(),
                    quality_mode=quality_mode
                )
            else:
                # Mock session
                session = type('Session', (), {
                    'session_id': session_id,
                    'session_type': session_type,
                    'child_id': child_id,
                    'start_time': datetime.now(),
                    'quality_mode': quality_mode,
                    'total_recordings': 0,
                    'total_duration': 0.0,
                    'end_time': None,
                    'metadata': {}
                })()
            
            self.active_sessions[session_id] = session
            self.current_session = session
            
            # Trigger event
            await self._trigger_event("session_start", {
                "session_id": session_id,
                "child_id": child_id,
                "session_type": session_type.value
            })
            
            self.logger.info(f"Started session: {session_id}")
            return session_id
        
        except Exception as e:
            self.logger.error(f"Error starting session: {e}")
            raise

    async def end_session(self, session_id: str) -> bool:
        """End an audio session asynchronously."""
        
        try:
            # Use enhanced manager if available
            if self.enhanced_manager:
                success = self.enhanced_manager.end_session(session_id)
                # Sync with local tracking
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                if self.current_session and self.current_session.session_id == session_id:
                    self.current_session = None
                return success
            
            # Fallback implementation
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            session.end_time = datetime.now()
            
            # Save session data if configured
            if self.config.auto_save_sessions:
                await self._save_session_data(session)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
            
            # Trigger event
            await self._trigger_event("session_end", {
                "session_id": session_id,
                "duration": (session.end_time - session.start_time).total_seconds()
            })
            
            self.logger.info(f"Audio session ended: {session_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
            return False

    async def record_audio(
        self,
        duration: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """Record audio asynchronously."""
        
        try:
            # Use enhanced manager if available
            if self.enhanced_manager:
                result = self.enhanced_manager.record_audio(
                    duration=duration,
                    session_id=session_id
                )
                if result:
                    self.performance_stats["total_recordings"] += 1
                return result
            
            # Fallback async implementation
            if duration is None:
                duration = self.config.default_record_duration
            
            session = self._get_session(session_id)
            
            # Trigger recording start event
            await self._trigger_event("recording_start", {
                "duration": duration,
                "session_id": session.session_id if session else None
            })
            
            start_time = time.time()
            
            # Async recording (mock)
            await asyncio.sleep(0.1)  # Simulate recording setup
            audio_data = await self._recorder.record_async(duration)
            
            # Create metadata
            metadata = {
                "duration": duration,
                "sample_rate": 44100,
                "channels": 1,
                "timestamp": datetime.now().isoformat(),
                "session_id": session.session_id if session else None
            }
            
            # Update stats
            processing_time = time.time() - start_time
            self.performance_stats["total_recordings"] += 1
            self._update_avg_processing_time(processing_time)
            
            # Trigger recording end event
            await self._trigger_event("recording_end", {
                "duration": duration,
                "processing_time": processing_time,
                "session_id": session.session_id if session else None
            })
            
            return audio_data, metadata
        
        except Exception as e:
            self.logger.error(f"Error recording audio: {e}")
            self.performance_stats["total_errors"] += 1
            self.performance_stats["last_error"] = str(e)
            
            await self._trigger_event("error", {
                "type": "recording_error",
                "error": str(e)
            })
            
            return None

    async def play_audio(
        self,
        audio_data: Optional[np.ndarray] = None,
        filename: Optional[str] = None,
        volume: Optional[float] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """Play audio asynchronously."""
        
        try:
            # Use enhanced manager if available
            if self.enhanced_manager:
                success = self.enhanced_manager.play_audio(
                    audio_data=audio_data,
                    filename=filename,
                    volume=volume,
                    session_id=session_id
                )
                if success:
                    self.performance_stats["total_playbacks"] += 1
                return success
            
            # Fallback async implementation
            if not self._audio_io:
                raise AudioSystemError("Audio I/O not initialized")
            
            session = self._get_session(session_id)
            play_volume = volume or self.config.volume_level
            
            # Trigger playback start event
            await self._trigger_event("playback_start", {
                "session_id": session.session_id if session else None,
                "volume": play_volume
            })
            
            # Play audio (mock implementation)
            if audio_data is not None:
                success = await self._audio_io.play_array_async(audio_data, volume=play_volume)
            elif filename:
                success = await self._audio_io.play_file_async(filename, volume=play_volume)
            else:
                raise ValueError("Either audio_data or filename must be provided")
            
            # Update performance stats
            if success:
                self.performance_stats["total_playbacks"] += 1
            
            # Trigger playback end event
            await self._trigger_event("playback_end", {
                "session_id": session.session_id if session else None,
                "success": success
            })
            
            return success
            
        except Exception as e:
            self.logger.error(f"Audio playback failed: {e}")
            self.performance_stats["total_errors"] += 1
            self.performance_stats["last_error"] = str(e)
            
            await self._trigger_event("error", {
                "type": "playback_error",
                "error": str(e)
            })
            
            return False

    async def speak(
        self,
        text: str,
        language: Optional[str] = None,
        speed: float = 1.0,
        volume: Optional[float] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """Convert text to speech and play asynchronously."""
        
        try:
            # Use enhanced manager if available
            if self.enhanced_manager:
                return self.enhanced_manager.speak(
                    text=text,
                    language=language,
                    speed=speed,
                    volume=volume,
                    session_id=session_id
                )
            
            # Fallback async implementation
            if not self._tts:
                raise AudioSystemError("TTS engine not initialized")
            
            session = self._get_session(session_id)
            speak_language = language or self.config.language_preference
            speak_volume = volume or self.config.volume_level
            
            # Generate speech audio
            audio_data = await self._tts.synthesize_async(
                text=text,
                language=speak_language,
                speed=speed
            )
            
            # Play the generated audio
            return await self.play_audio(
                audio_data=audio_data,
                volume=speak_volume,
                session_id=session_id
            )
            
        except Exception as e:
            self.logger.error(f"Text-to-speech failed: {e}")
            await self._trigger_event("error", {
                "type": "tts_error",
                "error": str(e)
            })
            return False

    async def stop_all(self, session_id: Optional[str] = None):
        """Stop all audio operations asynchronously."""
        
        try:
            # Use enhanced manager if available
            if self.enhanced_manager:
                self.enhanced_manager.stop_all(session_id)
                return
            
            # Fallback implementation
            if self._recorder:
                await self._recorder.stop_async()
            if self._audio_io:
                await self._audio_io.stop_all_async()
            if self._tts:
                await self._tts.stop_async()
                
            self.logger.info("All audio operations stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping audio operations: {e}")

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        
        # Use enhanced manager if available
        if self.enhanced_manager:
            return self.enhanced_manager.get_session_info(session_id)
        
        # Fallback implementation
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        return {
            "session_id": session.session_id,
            "session_type": session.session_type.value,
            "child_id": session.child_id,
            "start_time": session.start_time.isoformat(),
            "total_recordings": session.total_recordings,
            "total_duration": session.total_duration,
            "quality_mode": session.quality_mode.value
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system performance statistics."""
        
        # Use enhanced manager if available
        if self.enhanced_manager:
            return self.enhanced_manager.get_system_stats()
        
        # Fallback implementation
        uptime = (datetime.now() - self.performance_stats["uptime_start"]).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "active_sessions": len(self.active_sessions),
            "total_recordings": self.performance_stats["total_recordings"],
            "total_playbacks": self.performance_stats["total_playbacks"],
            "total_errors": self.performance_stats["total_errors"],
            "error_rate": self.performance_stats["total_errors"] / max(1, self.performance_stats["total_recordings"]),
            "average_processing_time": self.performance_stats["average_processing_time"],
            "last_error": self.performance_stats["last_error"]
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check asynchronously."""
        
        healthy = True
        components = {}
        
        # Check components
        try:
            if self._recorder:
                components["recorder"] = await self._recorder.health_check()
            if self._processor:
                components["processor"] = await self._processor.health_check()
            if self._tts:
                components["tts"] = await self._tts.health_check()
            if self._audio_io:
                components["audio_io"] = await self._audio_io.health_check()
        except Exception as e:
            healthy = False
            self.logger.error(f"Health check failed: {e}")
        
        return {
            "healthy": healthy,
            "components": components,
            "active_sessions": len(self.active_sessions),
            "uptime": (datetime.now() - self.performance_stats["uptime_start"]).total_seconds(),
            "enhanced_manager_available": self.enhanced_manager is not None
        }

    # Enhanced emotion processing method

    async def process_child_voice_with_emotion(
        self, 
        audio_data: bytes, 
        child_age: int = 6, 
        child_name: str = "طفل"
    ) -> Dict[str, Any]:
        """
        Process child voice with comprehensive emotion analysis.
        معالجة صوت الطفل مع تحليل المشاعر الكامل
        """
        
        try:
            print(f"🎤 Processing voice for {child_name} (age {child_age})...")
            
            # 1. Emotion analysis using HUME AI (if available)
            emotion_analysis = None
            if self._hume_analyzer:
                emotion_analysis = await self._hume_analyzer.analyze_child_voice(
                    audio_data=audio_data,
                    child_age=child_age,
                    child_name=child_name,
                    context={
                        "time_of_day": self._get_time_context(),
                        "session_number": getattr(self, 'session_count', 1)
                    }
                )
            else:
                # Mock emotion analysis
                emotion_analysis = ChildVoiceEmotion(
                    dominant_emotion="curious",
                    emotional_intensity=0.7,
                    curiosity=0.8,
                    joy=0.6
                )
            
            # 2. Speech-to-text conversion (if needed)
            transcription = ""
            try:
                if self._speech_to_text_service:
                    transcription = await self._speech_to_text_service.transcribe_audio(audio_data)
            except Exception as e:
                print(f"⚠️ Transcription failed (okay for pure emotion analysis): {e}")
            
            # 3. Generate personalized response based on emotions
            personalized_response = await self._generate_emotion_aware_response(
                emotion_analysis, transcription, child_name, child_age
            )
            
            # 4. Convert response to speech
            response_audio = None
            if personalized_response and self._tts_service:
                try:
                    response_audio = await self._tts_service.synthesize_speech(
                        personalized_response, 
                        voice_style=self._select_voice_for_emotion(emotion_analysis.dominant_emotion)
                    )
                except Exception as e:
                    print(f"⚠️ TTS failed: {e}")
            
            return {
                "success": True,
                "emotion_analysis": emotion_analysis,
                "transcription": transcription,
                "response_text": personalized_response,
                "response_audio": response_audio,
                "recommendations": self._get_parent_recommendations(emotion_analysis),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Voice processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_emotion": "curious",
                "timestamp": datetime.now().isoformat()
            }

    # Helper methods for emotion processing

    def _get_time_context(self) -> str:
        """Determine current time context."""
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 12:
            return "morning"
        elif 12 <= current_hour < 17:
            return "afternoon"
        elif 17 <= current_hour < 21:
            return "evening"
        else:
            return "night"

    async def _generate_emotion_aware_response(
        self, 
        emotion: ChildVoiceEmotion, 
        transcription: str, 
        child_name: str, 
        child_age: int
    ) -> str:
        """Generate smart response tailored to child's emotions."""
        
        dominant = emotion.dominant_emotion
        intensity = emotion.emotional_intensity
        
        # Emotion-specific responses
        if dominant == "joy" and intensity > 0.7:
            responses = [
                f"واااو {child_name}! أشعر بسعادتك الكبيرة! 😄 هذا رائع جداً!",
                f"يا لك من طفل سعيد يا {child_name}! أحب هذه الطاقة الإيجابية! ✨",
                f"سعادتك تجعلني سعيداً أيضاً يا {child_name}! ما الذي جعلك فرحاناً هكذا؟ 🎉"
            ]
            
        elif dominant == "sadness" and intensity > 0.6:
            responses = [
                f"أشعر أنك حزين قليلاً يا {child_name}... تعال نتحدث، أنا هنا لأسمعك 🤗",
                f"لا بأس يا {child_name}، أحياناً نشعر بالحزن وهذا طبيعي... دعني أساعدك 💙",
                f"أعرف أنك تشعر بالحزن يا {child_name}، هل تريد أن أحكي لك قصة مضحكة؟ 🌈"
            ]
            
        elif dominant == "fear" and intensity > 0.5:
            responses = [
                f"أشعر أنك خائف قليلاً يا {child_name}... لا تخف، أنا معك دائماً! 🛡️",
                f"لا بأس يا {child_name}، أنت في أمان! دعني أطمئنك... 🤗",
                f"أعرف أنك تشعر بالقلق يا {child_name}، لكن كل شيء سيكون بخير! 💪"
            ]
            
        elif dominant == "curiosity" and intensity > 0.6:
            responses = [
                f"أراك فضولياً جداً يا {child_name}! هذا رائع! ماذا تريد أن تعرف؟ 🤔✨",
                f"أحب فضولك يا {child_name}! دعني أعلمك شيئاً جديداً اليوم! 📚",
                f"يا له من عقل ذكي ومتسائل! ماذا يدور في رأسك يا {child_name}؟ 🧠💡"
            ]
            
        elif dominant == "playfulness" and intensity > 0.7:
            responses = [
                f"أراك في مزاج للعب يا {child_name}! هيا نلعب معاً! 🎮",
                f"طاقة اللعب تملأك يا {child_name}! ما رأيك في لعبة جديدة؟ 🎲",
                f"يالها من روح مرحة! هيا نستمتع يا {child_name}! 🎊"
            ]
            
        elif dominant == "tiredness" and intensity > 0.6:
            responses = [
                f"أشعر أنك متعب قليلاً يا {child_name}... هل تريد قصة هادئة؟ 😴",
                f"يبدو أنك بحاجة لقليل من الراحة يا {child_name}... دعني أهدئك 🌙",
                f"وقت الهدوء يا {child_name}... تعال نسترخي معاً 🍃"
            ]
            
        else:
            # General positive response
            responses = [
                f"أهلاً وسهلاً يا {child_name}! كيف حالك اليوم؟ 😊",
                f"سعيد لسماع صوتك يا {child_name}! ماذا نفعل اليوم؟ 🌟",
                f"يا {child_name} العزيز! أنا هنا لأكون صديقك! 🧸"
            ]
        
        # Choose random appropriate response
        import random
        selected_response = random.choice(responses)
        
        # Age customization
        if child_age <= 4:
            selected_response = selected_response.replace("كيف حالك", "كيف حالك يا صغيري")
        elif child_age >= 8:
            selected_response = selected_response.replace("يا صغيري", "")
        
        return selected_response

    def _select_voice_for_emotion(self, dominant_emotion: str) -> str:
        """Select appropriate voice tone for emotion."""
        
        voice_styles = {
            "joy": "cheerful",
            "excitement": "energetic", 
            "sadness": "gentle",
            "fear": "calm",
            "anger": "soothing",
            "curiosity": "friendly",
            "playfulness": "playful",
            "tiredness": "soft",
            "calmness": "peaceful"
        }
        
        return voice_styles.get(dominant_emotion, "friendly")

    def _get_parent_recommendations(self, emotion: ChildVoiceEmotion) -> List[str]:
        """Generate recommendations for parents based on emotion analysis."""
        
        recommendations = []
        
        if emotion.sadness > 0.7:
            recommendations.append("الطفل يظهر علامات حزن - قد يحتاج دعم عاطفي إضافي")
            recommendations.append("أنشطة مرحة ومحفزة للمزاج مستحسنة")
            
        if emotion.fear > 0.6:
            recommendations.append("الطفل يظهر علامات قلق - بيئة آمنة ومطمئنة مهمة")
            recommendations.append("تجنب المحتوى المخيف أو المثير للقلق")
            
        if emotion.curiosity > 0.8:
            recommendations.append("فضول عالي - وقت ممتاز لأنشطة تعليمية")
            recommendations.append("شجع الاستكشاف والتعلم التفاعلي")
            
        if emotion.tiredness > 0.7:
            recommendations.append("علامات تعب واضحة - قد يحتاج راحة")
            recommendations.append("أنشطة هادئة أو وقت نوم")
            
        if emotion.playfulness > 0.8:
            recommendations.append("طاقة لعب عالية - وقت ممتاز للأنشطة التفاعلية")
            recommendations.append("ألعاب حركية أو أنشطة إبداعية")
        
        # Add developmental indicators
        recommendations.extend(emotion.developmental_indicators)
        
        return recommendations

    # Utility methods

    def _get_session(self, session_id: Optional[str]) -> Optional[AudioSession]:
        """Get session by ID or current session."""
        if session_id:
            return self.active_sessions.get(session_id)
        return self.current_session

    async def _trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger event callbacks asynchronously."""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_data)
                    else:
                        callback(event_data)
                except Exception as e:
                    self.logger.error(f"Event callback error: {e}")

    def _update_avg_processing_time(self, new_time: float):
        """Update average processing time."""
        current_avg = self.performance_stats["average_processing_time"]
        total_recordings = self.performance_stats["total_recordings"]

        if total_recordings == 1:
            self.performance_stats["average_processing_time"] = new_time
        else:
            # Moving average
            self.performance_stats["average_processing_time"] = (
                (current_avg * (total_recordings - 1) + new_time) / total_recordings
            )

    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while True:
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                # Check session timeouts
                current_time = datetime.now()
                timeout_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if (current_time - session.start_time).total_seconds() > (self.config.session_timeout_minutes * 60):
                        timeout_sessions.append(session_id)
                
                # End timed out sessions
                for session_id in timeout_sessions:
                    await self.end_session(session_id)
                    self.logger.info(f"Session timed out: {session_id}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
                # Perform periodic cleanup tasks
                # This could include clearing temporary files, optimizing memory, etc.
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")

    async def _save_session_data(self, session: AudioSession):
        """Save session data (implementation depends on storage backend)."""
        try:
            # In a real implementation, this would save to database
            self.logger.info(f"Saving session data: {session.session_id}")
        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")

    async def cleanup(self) -> None:
        """Cleanup resources asynchronously."""
        
        self.logger.info("Starting modern audio manager cleanup")
        
        # Cancel background tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Stop all audio operations
        await self.stop_all()
        
        # End all active sessions
        session_ids = list(self.active_sessions.keys())
        for session_id in session_ids:
            await self.end_session(session_id)
        
        # Cleanup enhanced manager
        if self.enhanced_manager:
            self.enhanced_manager.cleanup()
        
        # Cleanup components
        if self._recorder:
            await self._recorder.cleanup()
        if self._processor:
            await self._processor.cleanup()
        if self._tts:
            await self._tts.cleanup()
        if self._audio_io:
            await self._audio_io.cleanup()
        
        self.logger.info("Modern audio manager cleanup complete")


# Mock implementations for testing when real components aren't available

class MockAudioRecorder:
    """Mock audio recorder for testing."""
    
    async def record_async(self, duration: int) -> np.ndarray:
        """Mock audio recording."""
        await asyncio.sleep(0.1)  # Simulate recording delay
        audio_data = np.random.random((duration * 22050,)).astype(np.float32)
        return audio_data
    
    async def stop_async(self):
        pass
    
    async def health_check(self) -> bool:
        return True
    
    async def cleanup(self):
        pass


class MockAudioProcessor:
    """Mock audio processor for testing."""
    
    async def process_async(self, audio_data: np.ndarray) -> np.ndarray:
        """Mock audio processing."""
        await asyncio.sleep(0.05)  # Simulate processing delay
        # Simple normalization
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val * 0.95
        return audio_data
    
    async def health_check(self) -> bool:
        return True
    
    async def cleanup(self):
        pass


class MockTTSEngine:
    """Mock TTS engine for testing."""
    
    async def synthesize_async(self, text: str, language: str, speed: float) -> np.ndarray:
        """Mock TTS synthesis."""
        await asyncio.sleep(0.1)  # Simulate synthesis delay
        # Generate sine wave based on text length
        duration = len(text) * 0.05 / speed
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        return audio_data
    
    async def stop_async(self):
        pass
    
    async def health_check(self) -> bool:
        return True
    
    async def cleanup(self):
        pass


class MockAudioIO:
    """Mock audio I/O for testing."""
    
    async def play_array_async(self, audio_data: np.ndarray, volume: float) -> bool:
        """Mock array playback."""
        await asyncio.sleep(0.1)  # Simulate playback delay
        return True
    
    async def play_file_async(self, filename: str, volume: float) -> bool:
        """Mock file playback."""
        await asyncio.sleep(0.1)  # Simulate playback delay
        return True
    
    async def stop_all_async(self):
        pass
    
    async def health_check(self) -> bool:
        return True
    
    async def cleanup(self):
        pass


# Convenience functions

async def create_modern_audio_manager(container: Optional[Any] = None) -> ModernAudioManager:
    """Create and initialize modern audio manager."""
    manager = ModernAudioManager(container)
    await manager.initialize()
    return manager


# Integration with enhanced audio manager

def bridge_to_enhanced_manager(enhanced_manager: 'EnhancedAudioManager') -> ModernAudioManager:
    """Create a modern audio manager that bridges to an enhanced manager."""
    
    modern_manager = ModernAudioManager()
    modern_manager.enhanced_manager = enhanced_manager
    
    # Sync configurations
    if hasattr(enhanced_manager, 'config'):
        modern_manager.config = enhanced_manager.config
    
    # Sync sessions
    if hasattr(enhanced_manager, 'active_sessions'):
        modern_manager.active_sessions = enhanced_manager.active_sessions
        modern_manager.current_session = enhanced_manager.current_session
    
    return modern_manager 