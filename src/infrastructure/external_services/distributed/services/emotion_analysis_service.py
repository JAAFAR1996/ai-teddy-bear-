"""
Distributed emotion analysis service deployment.
"""

import logging
import time
from typing import Any, Dict

import numpy as np

try:
    from ray import serve
    AI_SERVICES_AVAILABLE = True
except ImportError:
    AI_SERVICES_AVAILABLE = False
    serve = None

try:
    from ....domain.services.advanced_emotion_analyzer import AdvancedEmotionAnalyzer
    CORE_SERVICES_AVAILABLE = True
except ImportError:
    CORE_SERVICES_AVAILABLE = False

from ..mocks import MockAIServices

logger = logging.getLogger(__name__)

if AI_SERVICES_AVAILABLE:
    @serve.deployment(
        name="emotion-service",
        num_replicas=2,
        ray_actor_options={"num_cpus": 1, "memory": 1000 * 1024 * 1024},  # 1GB
    )
    class EmotionAnalysisService:
        """Distributed emotion analysis service."""

        def __init__(self):
            self.emotion_analyzer = None
            self.service_stats = {"requests": 0, "total_time": 0.0}
            self._initialize_models()

        def _initialize_models(self) -> Any:
            """Initialize emotion analysis models."""
            try:
                if CORE_SERVICES_AVAILABLE:
                    self.emotion_analyzer = AdvancedEmotionAnalyzer()
                    logger.info("✅ Emotion analysis service initialized")
                else:
                    logger.warning(
                        "⚠️ Core services not available, using mock emotion analysis"
                    )
            except Exception as e:
                logger.error(f"❌ Failed to initialize emotion models: {e}")

        async def analyze_emotion(
            self, audio_data: bytes, text: str = ""
        ) -> Dict[str, Any]:
            """Analyze emotion from audio and text."""
            start_time = time.time()
            self.service_stats["requests"] += 1

            try:
                if self.emotion_analyzer and CORE_SERVICES_AVAILABLE:
                    # Real emotion analysis
                    result = await self._analyze_with_core_service(audio_data, text)
                else:
                    # Mock emotion analysis
                    result = await MockAIServices.analyze_emotion(audio_data, text)

                processing_time = (time.time() - start_time) * 1000
                result["processing_time_ms"] = processing_time
                self.service_stats["total_time"] += processing_time

                return result

            except Exception as e:
                logger.error(f"❌ Emotion analysis failed: {e}")
                return await MockAIServices.analyze_emotion(audio_data, text)

        async def _analyze_with_core_service(
            self, audio_data: bytes, text: str
        ) -> Dict[str, Any]:
            """Analyze emotion using core service."""
            try:
                # Convert audio data for analysis
                audio_array = None
                if audio_data:
                    audio_array = (
                        np.frombuffer(
                            audio_data,
                            dtype=np.int16).astype(
                            np.float32) /
                        32768.0)

                # Use advanced emotion analyzer
                result = await self.emotion_analyzer.analyze_comprehensive(
                    text=text, audio_data=audio_array, audio_sr=16000
                )

                return {
                    "primary_emotion": result.dominant_emotion,
                    "confidence": result.confidence,
                    "emotion_scores": result.emotion_scores,
                    "arousal": result.arousal,
                    "valence": result.valence,
                }

            except Exception as e:
                logger.error(f"❌ Core emotion analysis error: {e}")
                return await MockAIServices.analyze_emotion(audio_data, text)
else:
    EmotionAnalysisService = MockAIServices
