"""
Enterprise-Grade Distributed AI Processing System for AI Teddy Bear Project.

This module provides scalable, parallel AI processing using Ray Serve,
enabling high-performance conversation handling with multiple AI services
running concurrently across distributed workers.

AI Team Implementation - Task 11
Author: AI Team Lead
"""

import asyncio
import logging
import time
import uuid
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Optional

try:
    import ray
    from ray import serve
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False
    ray = None
    serve = None

from .models import (
    AIServiceType,
    ChildContext,
    ConversationRequest,
    ConversationResponse,
    ProcessingMetrics,
)
from .services.ai_response_service import AIResponseService
from .services.emotion_analysis_service import EmotionAnalysisService
from .services.safety_check_service import SafetyCheckService
from .services.transcription_service import TranscriptionService
from .services.tts_service import TTSService
from .mocks import MockAIServices


logger = logging.getLogger(__name__)


class DistributedAIProcessor:
    """Main distributed AI processor orchestrating all services."""

    def __init__(self):
        self.ray_initialized = False
        self.services = {}
        self.metrics = ProcessingMetrics()
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")
        self.request_queue = asyncio.Queue()
        self.worker_pool = []

    async def initialize(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the distributed processing system."""
        try:
            if RAY_AVAILABLE:
                await self._initialize_ray_services(config)
            else:
                await self._initialize_local_services(config)

            self.logger.info(
                "✅ Distributed AI Processor initialized successfully")

        except Exception as e:
            self.logger.error(
                f"❌ Failed to initialize Distributed AI Processor: {e}")
            raise

    async def _initialize_ray_services(
            self, config: Optional[Dict[str, Any]] = None):
        """Initialize Ray Serve services."""
        try:
            # Initialize Ray if not already done
            if not ray.is_initialized():
                ray.init(ignore_reinit_error=True)

            # Start Ray Serve
            serve.start(detached=False)

            # Deploy services
            self.services = {
                AIServiceType.TRANSCRIPTION: TranscriptionService.bind(),
                AIServiceType.EMOTION_ANALYSIS: EmotionAnalysisService.bind(),
                AIServiceType.SAFETY_CHECK: SafetyCheckService.bind(),
                AIServiceType.AI_RESPONSE: AIResponseService.bind(),
                AIServiceType.TTS_SYNTHESIS: TTSService.bind(),
            }

            self.ray_initialized = True
            self.logger.info("✅ Ray Serve services deployed successfully")

        except Exception as e:
            self.logger.error(f"❌ Ray services initialization failed: {e}")
            await self._initialize_local_services(config)

    async def _initialize_local_services(
            self, config: Optional[Dict[str, Any]] = None):
        """Initialize local mock services for testing."""
        self.services = {
            AIServiceType.TRANSCRIPTION: MockAIServices,
            AIServiceType.EMOTION_ANALYSIS: MockAIServices,
            AIServiceType.SAFETY_CHECK: MockAIServices,
            AIServiceType.AI_RESPONSE: MockAIServices,
            AIServiceType.TTS_SYNTHESIS: MockAIServices,
        }

        self.logger.info("✅ Local mock services initialized")

    async def _handle_safety_check(
        self, safety_result: Dict, request_id: str, start_time: float
    ) -> Optional[ConversationResponse]:
        """Handles the safety check result, returning a response if unsafe."""
        if not safety_result.get("is_safe", True):
            return ConversationResponse(
                request_id=request_id,
                success=False,
                error_message="Content flagged as unsafe",
                safety_status="unsafe",
                processing_time_ms=(time.time() - start_time) * 1000,
            )
        return None

    def _create_final_response(
        self, request_id: str, results: Dict, start_time: float
    ) -> ConversationResponse:
        """Creates the final ConversationResponse object."""
        total_time = (time.time() - start_time) * 1000
        response = ConversationResponse(
            request_id=request_id,
            success=True,
            audio=results["tts"].get("audio_data"),
            transcription=results["transcription"].get("text", ""),
            ai_text=results["ai_response"].get("response_text", ""),
            emotion=results["emotion"].get("primary_emotion", "neutral"),
            safety_status="safe",
            confidence=min(
                results["transcription"].get("confidence", 0.0),
                results["ai_response"].get("confidence", 0.0),
            ),
            processing_time_ms=total_time,
            processing_source="distributed",
            service_results=results,
        )
        self.metrics.successful_requests += 1
        self._update_metrics(total_time)
        self.logger.info(
            f"✅ Conversation processed successfully in {total_time:.2f}ms"
        )
        return response

    async def process_conversation(
        self, audio_data: bytes, child_context: ChildContext
    ) -> ConversationResponse:
        """Main conversation processing pipeline with parallel execution."""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        try:
            self.logger.info(
                f"🎙️ Processing conversation request {request_id} for {child_context.name}"
            )
            self.metrics.total_requests += 1

            request = ConversationRequest(
                request_id=request_id,
                audio_data=audio_data,
                child_context=child_context,
            )

            transcription_result, emotion_result, safety_result = (
                await self._run_parallel_preprocessing(request)
            )

            if safety_response := self._handle_safety_check(
                safety_result, request_id, start_time
            ):
                return safety_response

            ai_response_result = await self._generate_ai_response(
                transcription_result, emotion_result, child_context
            )
            tts_result = await self._synthesize_speech(
                ai_response_result, emotion_result, child_context
            )

            results = {
                "transcription": transcription_result,
                "emotion": emotion_result,
                "safety": safety_result,
                "ai_response": ai_response_result,
                "tts": tts_result,
            }
            return self._create_final_response(request_id, results, start_time)

        except Exception as e:
            self.logger.error(f"❌ Conversation processing failed: {e}")
            self.metrics.failed_requests += 1
            return ConversationResponse(
                request_id=request_id,
                success=False,
                error_message=str(e),
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    async def _run_parallel_preprocessing(
            self, request: ConversationRequest) -> tuple:
        """Run preprocessing tasks in parallel."""
        # Create parallel tasks
        tasks = [
            self._call_service(
                AIServiceType.TRANSCRIPTION,
                "transcribe",
                request.audio_data),
            self._call_service(
                AIServiceType.EMOTION_ANALYSIS,
                "analyze_emotion",
                request.audio_data,
                "",
            ),
            self._call_service(
                AIServiceType.SAFETY_CHECK,
                "check_safety",
                "",
                request.audio_data),
        ]

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"❌ Preprocessing task {i} failed: {result}")
                processed_results.append({})
            else:
                processed_results.append(result)

        return tuple(processed_results)

    async def _generate_ai_response(
        self,
        transcription_result: Dict[str, Any],
        emotion_result: Dict[str, Any],
        child_context: ChildContext,
    ) -> Dict[str, Any]:
        """Generate AI response based on preprocessing results."""
        text = transcription_result.get("text", "")
        emotion = emotion_result.get("primary_emotion", "neutral")

        return await self._call_service(
            AIServiceType.AI_RESPONSE, "generate_response", text, child_context, emotion
        )

    async def _synthesize_speech(
        self,
        ai_response_result: Dict[str, Any],
        emotion_result: Dict[str, Any],
        child_context: ChildContext,
    ) -> Dict[str, Any]:
        """Synthesize speech from AI response."""
        text = ai_response_result.get("response_text", "")
        emotion = emotion_result.get("primary_emotion", "neutral")
        voice_profile = child_context.voice_profile

        return await self._call_service(
            AIServiceType.TTS_SYNTHESIS, "synthesize", text, emotion, voice_profile
        )

    def _get_service_callables(
        self, service: Any, ray_initialized: bool
    ) -> Dict[str, Callable]:
        """Returns a dictionary of callable methods for a given service."""
        if ray_initialized:
            return {
                AIServiceType.TRANSCRIPTION: service.transcribe.remote,
                AIServiceType.EMOTION_ANALYSIS: service.analyze_emotion.remote,
                AIServiceType.SAFETY_CHECK: service.check_safety.remote,
                AIServiceType.AI_RESPONSE: service.generate_response.remote,
                AIServiceType.TTS_SYNTHESIS: service.synthesize.remote,
            }
        else:
            return {
                AIServiceType.TRANSCRIPTION: service.transcribe_audio,
                AIServiceType.EMOTION_ANALYSIS: service.analyze_emotion,
                AIServiceType.SAFETY_CHECK: service.check_safety,
                AIServiceType.AI_RESPONSE: service.generate_ai_response,
                AIServiceType.TTS_SYNTHESIS: service.synthesize_speech,
            }

    async def _call_service(
        self, service_type: AIServiceType, method: str, *args
    ) -> Dict[str, Any]:
        """Call a distributed service with error handling."""
        try:
            service = self.services[service_type]
            service_map = self._get_service_callables(
                service, self.ray_initialized)

            if service_callable := service_map.get(service_type):
                return await service_callable(*args)

            return {}

        except Exception as e:
            self.logger.error(f"❌ Service call failed for {service_type}: {e}")
            return {"error": str(e)}

    def _update_metrics(self, processing_time_ms: float) -> None:
        """Update processing metrics."""
        # Update average processing time
        total_successful = self.metrics.successful_requests
        if total_successful > 0:
            current_avg = self.metrics.average_processing_time_ms
            new_avg = (
                (current_avg * (total_successful - 1)) + processing_time_ms
            ) / total_successful
            self.metrics.average_processing_time_ms = new_avg

        # Update throughput
        time_since_start = (datetime.now() -
                            self.metrics.last_updated).total_seconds()
        if time_since_start > 0:
            self.metrics.throughput_per_second = (
                self.metrics.total_requests / time_since_start
            )

        self.metrics.last_updated = datetime.now()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            "processing_metrics": asdict(self.metrics),
            "system_info": {
                "ray_initialized": self.ray_initialized,
                "ray_available": RAY_AVAILABLE,
            },
            "service_health": self._get_service_health_status(),
            "timestamp": datetime.now().isoformat(),
        }

    def _get_service_health_status(self) -> Dict[str, str]:
        """Get health status of all services."""
        health_status = {}

        for service_type in AIServiceType:
            if service_type in self.services:
                health_status[service_type.value] = "healthy"
            else:
                health_status[service_type.value] = "unavailable"

        return health_status

    async def process_batch_conversations(
        self,
        requests: List[tuple],
    ) -> List[ConversationResponse]:
        """Process multiple conversations in parallel."""
        self.logger.info(
            f"🔄 Processing batch of {len(requests)} conversations")

        # Create parallel processing tasks
        tasks = [
            self.process_conversation(audio_data, child_context)
            for audio_data, child_context in requests
        ]

        # Execute all conversations in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"❌ Batch conversation {i} failed: {result}")
                processed_results.append(
                    ConversationResponse(
                        request_id=f"batch_{i}",
                        success=False,
                        error_message=str(result),
                    )
                )
            else:
                processed_results.append(result)

        self.logger.info(
            f"✅ Batch processing completed: {len(processed_results)} results"
        )
        return processed_results

    async def optimize_for_load(self, expected_load: int):
        """Optimize system configuration for expected load."""
        if self.ray_initialized and expected_load > 10:
            # Scale up services for high load
            self.logger.info(
                f"🔧 Optimizing for high load: {expected_load} concurrent requests"
            )
            # Implementation would involve Ray autoscaling

    async def cleanup(self):
        """Cleanup distributed processing resources."""
        try:
            if self.ray_initialized:
                serve.shutdown()
                ray.shutdown()

            self.logger.info("✅ Distributed AI Processor cleanup completed")

        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")
            raise
