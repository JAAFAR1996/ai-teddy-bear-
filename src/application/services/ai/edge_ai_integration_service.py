from typing import Any, Dict, List, Optional

"""
Edge AI Integration Service for AI Teddy Bear Project.

This service integrates the EdgeAIManager with existing audio processing,
cloud services, and device management for seamless operation.

AI Team Implementation - Task 10
Author: AI Team Lead
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Core imports
from .edge_ai_manager import (EdgeAIManager, EdgeModelConfig,
                              EdgeProcessingMode, EdgeProcessingResult,
                              SafetyLevel, WakeWordModel)

# Audio processing integration
try:
    from ...audio.audio_processing import AudioConfig, AudioProcessor
    from ...domain.services.advanced_emotion_analyzer import \
        AdvancedEmotionAnalyzer

    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

# Cloud service integration
try:
    from ...application.services.ai import AIResponseService

    CLOUD_AI_AVAILABLE = True
except ImportError:
    CLOUD_AI_AVAILABLE = False

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EdgeCloudDecision:
    """Decision result for edge vs cloud processing."""

    use_edge_only: bool
    use_cloud_for_response: bool
    edge_confidence: float
    processing_mode: str
    estimated_cloud_time_ms: float
    edge_processing_result: Optional[EdgeProcessingResult]


@dataclass
class IntegratedResponse:
    """Integrated response combining edge and cloud processing."""

    response_text: str
    emotion_analysis: Dict[str, Any]
    safety_status: Dict[str, Any]
    processing_source: str  # "edge", "cloud", or "hybrid"
    total_processing_time_ms: float
    confidence: float
    recommendations: List[str]


class EdgeAIIntegrationService:
    """Integration service for Edge AI with cloud services."""

    def __init__(self, edge_config: Optional[EdgeModelConfig] = None):
        self.edge_config = edge_config or EdgeModelConfig()
        self.edge_ai_manager = EdgeAIManager(self.edge_config)
        self.audio_processor = AudioProcessor() if AUDIO_PROCESSING_AVAILABLE else None
        self.cloud_ai_service = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Integration statistics
        self.integration_stats = {
            "edge_only_responses": 0,
            "cloud_assisted_responses": 0,
            "hybrid_responses": 0,
            "average_edge_time_ms": 0.0,
            "average_cloud_time_ms": 0.0,
            "total_requests": 0,
        }

    async def initialize(self):
        """Initialize the integration service."""
        try:
            # Initialize Edge AI
            await self.edge_ai_manager.initialize()

            # Initialize cloud services if available
            if CLOUD_AI_AVAILABLE:
                # Initialize cloud AI service here if needed
                pass

            self.logger.info("Edge AI Integration Service initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Edge AI Integration Service: {e}")
            raise

    async def process_audio_request(
        self,
        audio_data: np.ndarray,
        child_id: str,
        device_specs: Optional[Dict[str, Any]] = None,
    ) -> IntegratedResponse:
        """Process audio request with edge-cloud integration."""
        start_time = time.time()
        self.integration_stats["total_requests"] += 1

        try:
            # Step 1: Optimize edge processing for device
            if device_specs:
                self.edge_ai_manager.optimize_for_device(device_specs)

            # Step 2: Edge processing
            edge_start = time.time()
            edge_result = await self.edge_ai_manager.process_on_edge(audio_data)
            edge_time = (time.time() - edge_start) * 1000

            # Step 3: Make edge vs cloud decision
            decision = self._make_processing_decision(edge_result, edge_time)

            # Step 4: Process based on decision
            if decision.use_edge_only:
                response = await self._process_edge_only(edge_result, edge_time)
                self.integration_stats["edge_only_responses"] += 1
            elif decision.use_cloud_for_response:
                response = await self._process_cloud_assisted(
                    audio_data, edge_result, child_id, edge_time
                )
                self.integration_stats["cloud_assisted_responses"] += 1
            else:
                response = await self._process_hybrid(
                    audio_data, edge_result, child_id, edge_time
                )
                self.integration_stats["hybrid_responses"] += 1

            # Step 5: Update statistics
            total_time = (time.time() - start_time) * 1000
            self._update_integration_stats(
                edge_time, total_time, response.processing_source
            )

            return response

        except Exception as e:
            self.logger.error(f"Audio request processing failed: {e}")
            return self._create_fallback_response(start_time)

    def _make_processing_decision(
        self, edge_result: EdgeProcessingResult, edge_time_ms: float
    ) -> EdgeCloudDecision:
        """Decide whether to use edge only, cloud assisted, or hybrid processing."""

        # Safety first - always use cloud for safety issues
        if edge_result.safety_check and not edge_result.safety_check.passed:
            return EdgeCloudDecision(
                use_edge_only=False,
                use_cloud_for_response=True,
                edge_confidence=0.0,
                processing_mode="cloud_safety",
                estimated_cloud_time_ms=500.0,
                edge_processing_result=edge_result,
            )

        # Use edge only for simple interactions
        if (
            edge_result.wake_word_detected
            and edge_result.confidence > 0.8
            and edge_result.initial_emotion
            and edge_result.initial_emotion.primary_emotion
            in ["happy", "calm", "excited"]
            and edge_time_ms < 50
        ):

            return EdgeCloudDecision(
                use_edge_only=True,
                use_cloud_for_response=False,
                edge_confidence=edge_result.confidence,
                processing_mode="edge_only",
                estimated_cloud_time_ms=0.0,
                edge_processing_result=edge_result,
            )

        # Use cloud assistance for complex scenarios
        if (
            edge_result.priority > 7
            or (
                edge_result.initial_emotion
                and edge_result.initial_emotion.primary_emotion
                in ["angry", "fear", "sad"]
            )
            or edge_result.confidence < 0.5
        ):

            return EdgeCloudDecision(
                use_edge_only=False,
                use_cloud_for_response=True,
                edge_confidence=edge_result.confidence,
                processing_mode="cloud_assisted",
                estimated_cloud_time_ms=300.0,
                edge_processing_result=edge_result,
            )

        # Use hybrid for balanced scenarios
        return EdgeCloudDecision(
            use_edge_only=False,
            use_cloud_for_response=False,
            edge_confidence=edge_result.confidence,
            processing_mode="hybrid",
            estimated_cloud_time_ms=200.0,
            edge_processing_result=edge_result,
        )

    async def _process_edge_only(
        self, edge_result: EdgeProcessingResult, edge_time_ms: float
    ) -> IntegratedResponse:
        """Process response using edge AI only."""
        # Generate simple response based on edge analysis
        response_text = self._generate_edge_response(edge_result)

        emotion_analysis = {}
        if edge_result.initial_emotion:
            emotion_analysis = {
                "primary_emotion": edge_result.initial_emotion.primary_emotion,
                "confidence": edge_result.initial_emotion.confidence,
                "arousal": edge_result.initial_emotion.arousal,
                "valence": edge_result.initial_emotion.valence,
            }

        safety_status = {}
        if edge_result.safety_check:
            safety_status = {
                "passed": edge_result.safety_check.passed,
                "risk_level": edge_result.safety_check.risk_level,
                "safety_score": edge_result.safety_check.safety_score,
            }

        return IntegratedResponse(
            response_text=response_text,
            emotion_analysis=emotion_analysis,
            safety_status=safety_status,
            processing_source="edge",
            total_processing_time_ms=edge_time_ms,
            confidence=edge_result.confidence,
            recommendations=edge_result.recommendations,
        )

    async def _process_cloud_assisted(
        self,
        audio_data: np.ndarray,
        edge_result: EdgeProcessingResult,
        child_id: str,
        edge_time_ms: float,
    ) -> IntegratedResponse:
        """Process response using cloud assistance."""
        cloud_start = time.time()

        try:
            # Mock cloud processing (replace with actual cloud service)
            cloud_response = await self._mock_cloud_processing(
                audio_data, edge_result, child_id
            )

            cloud_time = (time.time() - cloud_start) * 1000
            total_time = edge_time_ms + cloud_time

            return IntegratedResponse(
                response_text=cloud_response["response_text"],
                emotion_analysis=cloud_response["emotion_analysis"],
                safety_status=cloud_response["safety_status"],
                processing_source="cloud",
                total_processing_time_ms=total_time,
                confidence=cloud_response["confidence"],
                recommendations=cloud_response["recommendations"],
            )

        except Exception as e:
            self.logger.error(f"Cloud processing failed: {e}")
            # Fallback to edge processing
            return await self._process_edge_only(edge_result, edge_time_ms)

    async def _process_hybrid(
        self,
        audio_data: np.ndarray,
        edge_result: EdgeProcessingResult,
        child_id: str,
        edge_time_ms: float,
    ) -> IntegratedResponse:
        """Process response using hybrid edge-cloud approach."""

        # Use edge for immediate response, cloud for enhancement
        edge_response = await self._process_edge_only(edge_result, edge_time_ms)

        # Enhance with cloud processing asynchronously
        try:
            cloud_start = time.time()
            cloud_enhancement = await self._mock_cloud_enhancement(
                edge_result, edge_response
            )
            cloud_time = (time.time() - cloud_start) * 1000

            # Combine edge and cloud results
            enhanced_response = IntegratedResponse(
                response_text=cloud_enhancement.get(
                    "enhanced_text", edge_response.response_text
                ),
                emotion_analysis=cloud_enhancement.get(
                    "enhanced_emotion", edge_response.emotion_analysis
                ),
                safety_status=edge_response.safety_status,
                processing_source="hybrid",
                total_processing_time_ms=edge_time_ms + cloud_time,
                confidence=max(
                    edge_response.confidence, cloud_enhancement.get("confidence", 0.0)
                ),
                recommendations=edge_response.recommendations
                + cloud_enhancement.get("additional_recommendations", []),
            )

            return enhanced_response

        except Exception as e:
            self.logger.error(f"Hybrid processing enhancement failed: {e}")
            return edge_response

    def _generate_edge_response(self, edge_result: EdgeProcessingResult) -> str:
        """Generate simple response text based on edge analysis."""
        if not edge_result.wake_word_detected:
            return "I'm listening! How can I help you?"

        if edge_result.initial_emotion:
            emotion = edge_result.initial_emotion.primary_emotion

            if emotion == "happy":
                return "I'm so happy to hear your cheerful voice! What would you like to talk about?"
            elif emotion == "sad":
                return "I notice you might be feeling sad. I'm here to listen and help you feel better."
            elif emotion == "excited":
                return "Wow, you sound really excited! That makes me excited too! Tell me more!"
            elif emotion == "angry":
                return "I can hear you're upset. Let's take a deep breath together. I'm here to help."
            elif emotion == "fear":
                return "It's okay, I'm here with you. You're safe. Would you like to talk about what's worrying you?"
            elif emotion == "calm":
                return "You sound so peaceful and calm. I love talking with you when you're relaxed."

        return "Hello! I'm so glad you're talking with me. What's on your mind today?"

    async def _mock_cloud_processing(
        self, audio_data: np.ndarray, edge_result: EdgeProcessingResult, child_id: str
    ) -> Dict[str, Any]:
        """Mock cloud processing for demonstration."""
        # Simulate cloud processing delay
        await asyncio.sleep(0.2)

        return {
            "response_text": "This is an enhanced cloud response that takes into account your emotions and provides personalized interaction based on advanced AI analysis.",
            "emotion_analysis": {
                "primary_emotion": (
                    edge_result.initial_emotion.primary_emotion
                    if edge_result.initial_emotion
                    else "neutral"
                ),
                "confidence": 0.95,
                "detailed_analysis": "Advanced cloud-based emotion analysis with contextual understanding",
                "arousal": (
                    edge_result.initial_emotion.arousal
                    if edge_result.initial_emotion
                    else 0.5
                ),
                "valence": (
                    edge_result.initial_emotion.valence
                    if edge_result.initial_emotion
                    else 0.5
                ),
            },
            "safety_status": {
                "passed": True,
                "risk_level": "low",
                "safety_score": 0.98,
                "detailed_analysis": "Advanced cloud safety analysis completed",
            },
            "confidence": 0.92,
            "recommendations": [
                "Cloud-enhanced personalized response",
                "Advanced contextual understanding applied",
                "Enhanced safety verification completed",
            ],
        }

    async def _mock_cloud_enhancement(
        self, edge_result: EdgeProcessingResult, edge_response: IntegratedResponse
    ) -> Dict[str, Any]:
        """Mock cloud enhancement for hybrid processing."""
        # Simulate cloud enhancement delay
        await asyncio.sleep(0.1)

        return {
            "enhanced_text": edge_response.response_text
            + " I've also learned more about how to help you based on our conversation patterns!",
            "enhanced_emotion": {
                **edge_response.emotion_analysis,
                "enhanced_insights": "Cloud-based contextual emotion enhancement",
                "confidence": min(
                    1.0, edge_response.emotion_analysis.get("confidence", 0.5) + 0.2
                ),
            },
            "confidence": min(1.0, edge_response.confidence + 0.15),
            "additional_recommendations": [
                "Cloud enhancement applied",
                "Contextual patterns analyzed",
            ],
        }

    def _create_fallback_response(self, start_time: float) -> IntegratedResponse:
        """Create fallback response when processing fails."""
        processing_time = (time.time() - start_time) * 1000

        return IntegratedResponse(
            response_text="Hi there! I'm having some trouble processing right now, but I'm still here to chat with you!",
            emotion_analysis={"primary_emotion": "neutral", "confidence": 0.5},
            safety_status={"passed": True, "risk_level": "low", "safety_score": 1.0},
            processing_source="fallback",
            total_processing_time_ms=processing_time,
            confidence=0.5,
            recommendations=["Fallback response used due to processing error"],
        )

    def _update_integration_stats(
        self, edge_time_ms: float, total_time_ms: float, processing_source: str
    ):
        """Update integration statistics."""
        # Update edge time average
        current_edge_avg = self.integration_stats["average_edge_time_ms"]
        total_requests = self.integration_stats["total_requests"]
        new_edge_avg = (
            (current_edge_avg * (total_requests - 1)) + edge_time_ms
        ) / total_requests
        self.integration_stats["average_edge_time_ms"] = new_edge_avg

        # Update cloud time average (if cloud was used)
        if processing_source in ["cloud", "hybrid"]:
            cloud_time = total_time_ms - edge_time_ms
            current_cloud_avg = self.integration_stats["average_cloud_time_ms"]
            cloud_requests = (
                self.integration_stats["cloud_assisted_responses"]
                + self.integration_stats["hybrid_responses"]
            )
            if cloud_requests > 0:
                new_cloud_avg = (
                    (current_cloud_avg * (cloud_requests - 1)) + cloud_time
                ) / cloud_requests
                self.integration_stats["average_cloud_time_ms"] = new_cloud_avg

    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get integration service statistics."""
        edge_stats = self.edge_ai_manager.get_performance_stats()

        return {
            "integration_stats": self.integration_stats.copy(),
            "edge_ai_stats": edge_stats,
            "processing_distribution": {
                "edge_only_percentage": (
                    self.integration_stats["edge_only_responses"]
                    / max(1, self.integration_stats["total_requests"])
                )
                * 100,
                "cloud_assisted_percentage": (
                    self.integration_stats["cloud_assisted_responses"]
                    / max(1, self.integration_stats["total_requests"])
                )
                * 100,
                "hybrid_percentage": (
                    self.integration_stats["hybrid_responses"]
                    / max(1, self.integration_stats["total_requests"])
                )
                * 100,
            },
            "performance_metrics": {
                "average_total_response_time_ms": (
                    self.integration_stats["average_edge_time_ms"]
                    + self.integration_stats["average_cloud_time_ms"]
                ),
                "edge_processing_efficiency": min(
                    100,
                    100 / max(1, self.integration_stats["average_edge_time_ms"] / 10),
                ),
                "cloud_dependency_ratio": (
                    (
                        self.integration_stats["cloud_assisted_responses"]
                        + self.integration_stats["hybrid_responses"]
                    )
                    / max(1, self.integration_stats["total_requests"])
                ),
            },
            "capabilities": {
                "edge_ai_available": True,
                "audio_processing_available": AUDIO_PROCESSING_AVAILABLE,
                "cloud_ai_available": CLOUD_AI_AVAILABLE,
                "hybrid_processing": True,
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def configure_for_device(
        self, device_type: str, device_specs: Dict[str, Any]
    ):
        """Configure the integration service for specific device types."""

        if device_type == "ESP32-S3":
            # Optimize for ESP32-S3
            self.edge_config.processing_mode = EdgeProcessingMode.BALANCED
            self.edge_config.wake_word_model = WakeWordModel.STANDARD
            self.edge_config.safety_level = SafetyLevel.STANDARD

        elif device_type == "ESP32-S3-High-Mem":
            # High memory ESP32-S3
            self.edge_config.processing_mode = EdgeProcessingMode.HIGH_ACCURACY
            self.edge_config.wake_word_model = WakeWordModel.ENHANCED
            self.edge_config.safety_level = SafetyLevel.ENHANCED

        elif device_type == "ESP32-C3":
            # Lower power device
            self.edge_config.processing_mode = EdgeProcessingMode.ULTRA_LOW_LATENCY
            self.edge_config.wake_word_model = WakeWordModel.LIGHTWEIGHT
            self.edge_config.safety_level = SafetyLevel.BASIC

        self.edge_ai_manager.optimize_for_device(device_specs)
        self.logger.info(f"Configured for device type: {device_type}")

    async def cleanup(self):
        """Cleanup integration service resources."""
        try:
            await self.edge_ai_manager.cleanup()
            self.logger.info("Edge AI Integration Service cleanup completed")
        except Exception as e:
            self.logger.error(f"Integration cleanup failed: {e}")
            raise
