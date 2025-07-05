#!/usr/bin/env python3
"""
Transcription Service Module - Extracted from main_service.py
Handles speech-to-text conversion for AI Teddy Bear
"""

from dataclasses import dataclass
from typing import Optional
import structlog

from src.infrastructure.exception_handling.circuit_breaker import CircuitBreaker


@dataclass
class TranscriptionResult:
    """Transcription result with metadata"""

    text: str
    confidence: float
    language: str = "en"
    audio_duration_ms: int = 0


class TranscriptionService:
    """Handles audio transcription with multiple provider support"""

    def __init__(
        self, 
        voice_service=None,
        cloud_transcription_service=None,
        whisper_service=None
    ):
        self.logger = structlog.get_logger()
        self.voice_service = voice_service
        self.cloud_transcription_service = cloud_transcription_service
        self.whisper_service = whisper_service
        
        # Circuit breakers for external services
        self._transcription_breaker = CircuitBreaker(
            name="transcription", 
            failure_threshold=3, 
            recovery_timeout=30
        )

    async def transcribe_with_fallback(
        self, 
        audio_data: bytes, 
        language: str = "en"
    ) -> TranscriptionResult:
        """Transcribe audio with multiple fallback options"""

        async def _try_transcription():
            # Try cloud service first (e.g., Google Speech-to-Text)
            if self.cloud_transcription_service:
                try:
                    result = await self.cloud_transcription_service.transcribe(
                        audio_data, language=language
                    )
                    if result and result.get("text"):
                        return result
                except Exception as e:
                    self.logger.warning(f"Cloud transcription failed: {e}")

            # Try Whisper service if available
            if self.whisper_service:
                try:
                    result = await self.whisper_service.transcribe(
                        audio_data, language=language
                    )
                    if result and result.get("text"):
                        return result
                except Exception as e:
                    self.logger.warning(f"Whisper transcription failed: {e}")

            # Fallback to voice service
            if self.voice_service and hasattr(self.voice_service, "transcribe"):
                try:
                    result = await self.voice_service.transcribe(
                        audio_data, language=language
                    )
                    if result and result.get("text"):
                        return result
                except Exception as e:
                    self.logger.warning(f"Voice service transcription failed: {e}")

            raise ValueError("No transcription service available")

        # Use circuit breaker
        try:
            result = await self._transcription_breaker.call(_try_transcription)
        except Exception as e:
            self.logger.error(f"All transcription services failed: {e}")
            # Return empty transcription as last resort
            return TranscriptionResult(
                text="",
                confidence=0.0,
                language=language,
                audio_duration_ms=0
            )

        return TranscriptionResult(
            text=result.get("text", ""),
            confidence=result.get("confidence", 0.0),
            language=result.get("language", language),
            audio_duration_ms=result.get("duration_ms", 0),
        )

    async def validate_audio_format(self, audio_data: bytes) -> bool:
        """Validate audio format before transcription"""
        
        # Check minimum size
        if len(audio_data) < 100:
            self.logger.warning("Audio data too small")
            return False
            
        # Check for common audio format headers
        # WAV format
        if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
            return True
            
        # MP3 format
        if audio_data[:3] == b'ID3' or audio_data[:2] == b'\xff\xfb':
            return True
            
        # OGG format
        if audio_data[:4] == b'OggS':
            return True
            
        # Raw PCM (no header, so we accept it)
        return True

    async def preprocess_audio(
        self, 
        audio_data: bytes,
        target_sample_rate: int = 16000
    ) -> bytes:
        """Preprocess audio for better transcription results"""
        
        # This is a placeholder for audio preprocessing
        # In a real implementation, you might:
        # 1. Convert sample rate
        # 2. Apply noise reduction
        # 3. Normalize audio levels
        # 4. Convert to appropriate format
        
        return audio_data

    def estimate_audio_duration(self, audio_data: bytes, sample_rate: int = 16000) -> int:
        """Estimate audio duration in milliseconds"""
        
        # Rough estimation assuming 16-bit PCM audio
        # Real implementation would parse audio headers
        bytes_per_sample = 2  # 16-bit
        samples = len(audio_data) / bytes_per_sample
        duration_seconds = samples / sample_rate
        
        return int(duration_seconds * 1000)

    async def transcribe_streaming(
        self,
        audio_stream,
        language: str = "en"
    ):
        """Handle streaming audio transcription"""
        
        # This would be implemented for real-time transcription
        # For now, it's a placeholder
        raise NotImplementedError("Streaming transcription not yet implemented")

    def get_supported_languages(self) -> list:
        """Get list of supported languages for transcription"""
        
        # Common languages supported by most services
        return [
            "en",  # English
            "es",  # Spanish
            "fr",  # French
            "de",  # German
            "it",  # Italian
            "pt",  # Portuguese
            "ru",  # Russian
            "ja",  # Japanese
            "ko",  # Korean
            "zh",  # Chinese
            "ar",  # Arabic
            "hi",  # Hindi
        ]

    async def detect_language(self, audio_data: bytes) -> str:
        """Detect language from audio"""
        
        # Try to detect language if service supports it
        if self.cloud_transcription_service and hasattr(
            self.cloud_transcription_service, "detect_language"
        ):
            try:
                language = await self.cloud_transcription_service.detect_language(audio_data)
                if language:
                    return language
            except Exception as e:
                self.logger.warning(f"Language detection failed: {e}")
        
        # Default to English
        return "en" 