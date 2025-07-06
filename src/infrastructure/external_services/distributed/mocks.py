"""
Mock AI services for testing the distributed processor without external dependencies.
"""

import asyncio
from typing import Any, Dict

import numpy as np

from .models import ChildContext


class MockAIServices:
    """Mock AI services for testing without external dependencies."""

    @staticmethod
    async def transcribe_audio(audio_data: bytes) -> Dict[str, Any]:
        """Mock audio transcription."""
        await asyncio.sleep(0.1)  # Simulate processing time
        return {
            "text": "مرحبا تيدي، كيف حالك اليوم؟",
            "confidence": 0.92,
            "language": "ar",
            "processing_time_ms": 100,
        }

    @staticmethod
    async def analyze_emotion(audio_data: bytes, text: str) -> Dict[str, Any]:
        """Mock emotion analysis."""
        await asyncio.sleep(0.05)  # Simulate processing time
        return {
            "primary_emotion": "happy",
            "confidence": 0.88,
            "emotion_scores": {
                "happy": 0.88,
                "sad": 0.05,
                "angry": 0.02,
                "excited": 0.03,
                "calm": 0.02,
            },
            "arousal": 0.7,
            "valence": 0.85,
            "processing_time_ms": 50,
        }

    @staticmethod
    async def check_safety(text: str, audio_data: bytes) -> Dict[str, Any]:
        """Mock safety checking."""
        await asyncio.sleep(0.02)  # Simulate processing time
        return {
            "is_safe": True,
            "risk_level": "low",
            "confidence": 0.98,
            "detected_issues": [],
            "processing_time_ms": 20,
        }

    @staticmethod
    async def generate_ai_response(
        text: str, child_context: ChildContext
    ) -> Dict[str, Any]:
        """Mock AI response generation."""
        await asyncio.sleep(0.2)  # Simulate processing time
        return {
            "response_text": f"مرحبا {child_context.name}! أنا سعيد للحديث معك. كيف يمكنني مساعدتك اليوم؟",
            "emotion": "happy",
            "confidence": 0.95,
            "personalized": True,
            "processing_time_ms": 200,
        }

    @staticmethod
    async def synthesize_speech(
        text: str, emotion: str, voice_profile: str
    ) -> Dict[str, Any]:
        """Mock text-to-speech synthesis."""
        await asyncio.sleep(0.15)  # Simulate processing time
        # Generate mock audio data
        mock_audio = np.random.uniform(-0.1, 0.1, 16000).astype(np.float32)
        audio_bytes = (mock_audio * 32767).astype(np.int16).tobytes()

        return {
            "audio_data": audio_bytes,
            "sample_rate": 16000,
            "duration_seconds": 1.0,
            "quality": "high",
            "processing_time_ms": 150,
        }
