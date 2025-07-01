"""Audio management service for ESP32 teddy bear."""

import structlog
from typing import Dict, Any, Optional, List, Callable
import threading
import time
import random

from ....domain.esp32.models import (
    AudioSettings, AudioVisualization, SpeechRecognition, 
    AudioQuality, RecognitionLanguage, MicrophoneSettings
)

logger = structlog.get_logger(__name__)


class AudioManagementService:
    """Service for managing audio recording, playback, and visualization."""
    
    def __init__(self):
        self.settings = AudioSettings()
        self.visualization = AudioVisualization()
        self.is_listening = False
        self.is_playing = False
        self.recognition_callbacks: Dict[str, Callable] = {}
        self.listen_thread = None
        self.visualizer_thread = None
        
        logger.info(" Audio management service initialized")
    
    def register_recognition_callback(self, name: str, callback: Callable[[SpeechRecognition], None]) -> None:
        """Register callback for speech recognition results."""
        self.recognition_callbacks[name] = callback
    
    def update_audio_settings(self, **kwargs) -> bool:
        """Update audio settings."""
        try:
            if 'volume' in kwargs:
                volume = kwargs['volume']
                if not 0 <= volume <= 100:
                    raise ValueError("Volume must be between 0 and 100")
                self.settings.volume = volume
            
            if 'quality' in kwargs:
                quality_str = kwargs['quality']
                self.settings.quality = AudioQuality(quality_str)
            
            if 'language' in kwargs:
                language_str = kwargs['language']
                self.settings.language = RecognitionLanguage(language_str)
            
            if 'wake_words' in kwargs:
                self.settings.wake_words = kwargs['wake_words']
            
            logger.info(f" Audio settings updated: {kwargs}")
            return True
            
        except Exception as e:
            logger.error(f" Audio settings update failed: {e}")
            return False
    
    def update_microphone_sensitivity(self, sensitivity: int) -> bool:
        """Update microphone sensitivity."""
        try:
            if not 100 <= sensitivity <= 1000:
                raise ValueError("Sensitivity must be between 100 and 1000")
            
            self.settings.microphone.energy_threshold = sensitivity
            logger.info(f" Microphone sensitivity: {sensitivity}")
            return True
            
        except Exception as e:
            logger.error(f" Microphone sensitivity update failed: {e}")
            return False
    
    async def start_listening(self) -> bool:
        """Start listening for speech."""
        try:
            if self.is_listening:
                logger.warning("Already listening")
                return True
            
            self.is_listening = True
            
            # Start visualization
            self.start_audio_visualization()
            
            # Start listening thread
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            
            logger.info(" Started listening for speech")
            return True
            
        except Exception as e:
            logger.error(f" Failed to start listening: {e}")
            return False
    
    async def stop_listening(self) -> None:
        """Stop listening for speech."""
        if self.is_listening:
            self.is_listening = False
            
            # Stop visualization
            self.stop_audio_visualization()
            
            if self.listen_thread:
                self.listen_thread.join(timeout=3)
            
            logger.info(" Stopped listening")
    
    async def play_audio(self, text: str, language: Optional[str] = None) -> bool:
        """Play text-to-speech audio."""
        try:
            if self.is_playing:
                logger.warning("Audio already playing")
                return False
            
            self.is_playing = True
            lang = language or self.settings.language.value
            
            # Start visualization during playback
            self.start_audio_visualization()
            
            logger.info(f" Playing audio: {text[:50]}...")
            
            # Simulate TTS playback
            await self._simulate_tts_playback(text)
            
            self.is_playing = False
            self.stop_audio_visualization()
            
            return True
            
        except Exception as e:
            logger.error(f" Audio playback failed: {e}")
            self.is_playing = False
            return False
    
    def start_audio_visualization(self) -> None:
        """Start audio visualization."""
        if not self.visualization.is_active:
            self.visualization.start_animation()
            self.visualizer_thread = threading.Thread(target=self._visualizer_loop, daemon=True)
            self.visualizer_thread.start()
            logger.debug(" Audio visualization started")
    
    def stop_audio_visualization(self) -> None:
        """Stop audio visualization."""
        if self.visualization.is_active:
            self.visualization.stop_animation()
            if self.visualizer_thread:
                self.visualizer_thread.join(timeout=1)
            logger.debug(" Audio visualization stopped")
    
    def get_visualization_data(self) -> Dict[str, Any]:
        """Get current visualization data."""
        return {
            "is_active": self.visualization.is_active,
            "bar_heights": self.visualization.bar_heights,
            "colors": self.visualization.colors,
            "bar_count": self.visualization.bar_count
        }
    
    def get_audio_status(self) -> Dict[str, Any]:
        """Get current audio status."""
        return {
            "is_listening": self.is_listening,
            "is_playing": self.is_playing,
            "volume": self.settings.volume,
            "quality": self.settings.quality.value,
            "language": self.settings.language.value,
            "wake_words": self.settings.wake_words,
            "microphone": {
                "energy_threshold": self.settings.microphone.energy_threshold,
                "is_ultra_sensitive": self.settings.microphone.is_ultra_sensitive,
                "pause_threshold": self.settings.microphone.pause_threshold
            },
            "visualization": self.get_visualization_data()
        }
    
    def detect_wake_word(self, text: str) -> Optional[str]:
        """Detect wake word in text."""
        text_lower = text.lower()
        for wake_word in self.settings.wake_words:
            if wake_word.lower() in text_lower:
                return wake_word
        return None
    
    def _listen_loop(self) -> None:
        """Main listening loop."""
        while self.is_listening:
            try:
                # Simulate speech recognition
                recognition_result = self._simulate_speech_recognition()
                
                if recognition_result and recognition_result.is_valid:
                    # Check for wake word
                    wake_word = self.detect_wake_word(recognition_result.text)
                    if wake_word:
                        recognition_result.wake_word_detected = True
                        recognition_result.detected_wake_word = wake_word
                    
                    # Notify callbacks
                    for callback in self.recognition_callbacks.values():
                        try:
                            callback(recognition_result)
                        except Exception as e:
                            logger.error(f"Recognition callback error: {e}")
                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                logger.error(f" Listen loop error: {e}")
                time.sleep(2)
    
    def _visualizer_loop(self) -> None:
        """Audio visualization loop."""
        while self.visualization.is_active:
            try:
                # Generate random heights for visualization
                heights = [random.randint(10, 70) for _ in range(self.visualization.bar_count)]
                self.visualization.update_bars(heights)
                
                time.sleep(self.visualization.animation_speed / 1000)  # Convert to seconds
                
            except Exception as e:
                logger.error(f" Visualizer error: {e}")
                time.sleep(0.1)
    
    def _simulate_speech_recognition(self) -> Optional[SpeechRecognition]:
        """Simulate speech recognition for testing."""
        # Mock recognition - in real implementation would use actual speech recognition
        mock_phrases = [
            "يا دبدوب كيف حالك",
            "hey teddy, tell me a story",
            "أريد أن ألعب",
            "hello teddy, how are you?",
            "ما اسمك",
            "sing me a song"
        ]
        
        # Random chance of recognition
        if random.random() < 0.1:  # 10% chance per cycle
            phrase = random.choice(mock_phrases)
            confidence = random.uniform(0.7, 0.95)
            
            return SpeechRecognition(
                text=phrase,
                confidence=confidence,
                language=self.settings.language.value
            )
        
        return None
    
    async def _simulate_tts_playback(self, text: str) -> None:
        """Simulate TTS playback duration."""
        # Estimate playback duration based on text length
        words = len(text.split())
        duration = max(2, words * 0.5)  # Minimum 2 seconds, ~0.5 seconds per word
        
        await self._async_sleep(duration)
    
    async def _async_sleep(self, duration: float) -> None:
        """Async sleep helper."""
        import asyncio
        await asyncio.sleep(duration)
