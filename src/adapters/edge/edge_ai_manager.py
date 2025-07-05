from typing import Any, Dict, List, Optional

"""
Enterprise-Grade Edge AI Manager for AI Teddy Bear Project.

This module provides advanced Edge AI capabilities for ESP32-S3 devices,
enabling real-time wake word detection, emotion analysis, and safety checking
without cloud dependency for instant response.

AI Team Implementation - Task 10
Author: AI Team Lead
"""

import asyncio
import hashlib
import json
import logging
import pickle
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# TensorFlow Lite for Edge AI
try:
    import tensorflow as tf
    import tflite_runtime.interpreter as tflite

    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None
    tflite = None

# Audio processing
try:
    import librosa
    import scipy.signal

    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

from .edge_model_manager import EdgeModelManager
from .edge_feature_extractor import EdgeFeatureExtractor
from .edge_wake_word_detector import EdgeWakeWordDetector
from .edge_emotion_analyzer import EdgeEmotionAnalyzer
from .edge_safety_checker import EdgeSafetyChecker

logger = logging.getLogger(__name__)


class EdgeProcessingMode(Enum):
    """Edge processing modes for different scenarios."""

    ULTRA_LOW_LATENCY = "ultra_low_latency"  # <10ms response
    BALANCED = "balanced"  # <50ms response
    HIGH_ACCURACY = "high_accuracy"  # <100ms response
    POWER_SAVE = "power_save"  # Minimal processing


class WakeWordModel(Enum):
    """Available wake word detection models."""

    LIGHTWEIGHT = "wake_word_lite.tflite"  # <1MB, basic detection
    STANDARD = "wake_word.tflite"  # ~2MB, good accuracy
    ENHANCED = "wake_word_enhanced.tflite"  # ~5MB, high accuracy


class SafetyLevel(Enum):
    """Safety check levels for edge processing."""

    BASIC = "basic"  # Simple keyword filtering
    STANDARD = "standard"  # Content analysis
    ENHANCED = "enhanced"  # Advanced safety ML model


@dataclass
class EdgeAudioFeatures:
    """Container for extracted audio features on edge."""

    mfcc: np.ndarray
    spectral_centroid: float
    zero_crossing_rate: float
    rms_energy: float
    pitch_mean: float
    pitch_std: float
    tempo: float
    spectral_rolloff: float
    extraction_time_ms: float


@dataclass
class EdgeEmotionResult:
    """Result from edge emotion analysis."""

    primary_emotion: str
    confidence: float
    emotion_scores: Dict[str, float]
    arousal: float
    valence: float
    processing_time_ms: float
    model_version: str


@dataclass
class EdgeSafetyResult:
    """Result from edge safety checking."""

    passed: bool
    risk_level: str
    detected_issues: List[str]
    safety_score: float
    processing_time_ms: float
    requires_cloud_review: bool


@dataclass
class EdgeProcessingResult:
    """Complete result from edge processing."""

    should_process_cloud: bool
    initial_emotion: Optional[EdgeEmotionResult]
    safety_check: Optional[EdgeSafetyResult]
    wake_word_detected: bool
    priority: int  # 1-10, higher = more urgent
    confidence: float
    processing_time_ms: float
    edge_features: Optional[EdgeAudioFeatures]
    recommendations: List[str]
    device_load: float


@dataclass
class EdgeModelConfig:
    """Configuration for edge AI models."""

    wake_word_model: WakeWordModel = WakeWordModel.STANDARD
    emotion_model_path: str = "emotion_lite.tflite"
    safety_model_path: str = "safety_check.tflite"
    processing_mode: EdgeProcessingMode = EdgeProcessingMode.BALANCED
    safety_level: SafetyLevel = SafetyLevel.STANDARD
    enable_caching: bool = True
    max_cache_size: int = 100
    model_optimization: bool = True


class EdgeAIManager:
    """Main Edge AI Manager for ESP32-S3 real-time processing."""

    def __init__(self, config: Optional[EdgeModelConfig] = None):
        self.config = config or EdgeModelConfig()
        self.model_manager = EdgeModelManager(self.config)
        self.feature_extractor = EdgeFeatureExtractor()
        self.wake_word_detector = EdgeWakeWordDetector(self.model_manager)
        self.emotion_analyzer = EdgeEmotionAnalyzer(self.model_manager)
        self.safety_checker = EdgeSafetyChecker(
            self.model_manager, self.config.safety_level
        )
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

        # Performance monitoring
        self.processing_stats = {
            "total_processed": 0,
            "wake_words_detected": 0,
            "average_processing_time": 0.0,
            "error_count": 0,
        }

    async def initialize(self):
        """Initialize all Edge AI components."""
        try:
            # Initialize models
            await self.wake_word_detector.initialize(self.config.wake_word_model.value)
            await self.emotion_analyzer.initialize(self.config.emotion_model_path)
            await self.safety_checker.initialize(self.config.safety_model_path)

            self.logger.info("Edge AI Manager initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Edge AI Manager: {e}")
            raise

    async def process_on_edge(
        self, audio_chunk: np.ndarray, transcribed_text: Optional[str] = None
    ) -> EdgeProcessingResult:
        """Main edge processing pipeline for instant response."""
        start_time = time.time()

        try:
            # Update processing stats
            self.processing_stats["total_processed"] += 1

            # Step 1: Extract audio features
            features = await self.feature_extractor.extract_features(
                audio_chunk,
                quick_mode=(
                    self.config.processing_mode == EdgeProcessingMode.ULTRA_LOW_LATENCY
                ),
            )

            # Step 2: Wake word detection
            wake_word_detected, wake_confidence = (
                await self.wake_word_detector.detect_wake_word(audio_chunk)
            )

            if wake_word_detected:
                self.processing_stats["wake_words_detected"] += 1

            # Step 3: Emotion analysis (if wake word detected or in continuous
            # mode)
            emotion_result = None
            if (wake_word_detected or self.config.processing_mode ==
                    EdgeProcessingMode.HIGH_ACCURACY):
                emotion_result = await self.emotion_analyzer.analyze_emotion(features)

            # Step 4: Safety check
            safety_result = await self.safety_checker.check_safety(
                features, transcribed_text
            )

            # Step 5: Calculate priority and decide on cloud processing
            priority = self._calculate_priority(
                emotion_result, safety_result, wake_confidence
            )
            should_process_cloud = self._should_process_cloud(
                wake_word_detected, emotion_result, safety_result
            )

            # Step 6: Generate recommendations
            recommendations = self._generate_recommendations(
                emotion_result, safety_result, wake_word_detected
            )

            # Calculate overall processing time
            total_processing_time = (time.time() - start_time) * 1000

            # Update average processing time
            self._update_processing_stats(total_processing_time)

            # Calculate device load (mock implementation)
            device_load = min(total_processing_time / 100.0, 1.0)

            return EdgeProcessingResult(
                should_process_cloud=should_process_cloud,
                initial_emotion=emotion_result,
                safety_check=safety_result,
                wake_word_detected=wake_word_detected,
                priority=priority,
                confidence=wake_confidence if wake_word_detected else 0.5,
                processing_time_ms=total_processing_time,
                edge_features=features,
                recommendations=recommendations,
                device_load=device_load,
            )

        except Exception as e:
            self.logger.error(f"Edge processing failed: {e}")
            self.processing_stats["error_count"] += 1
            return self._create_fallback_result(start_time)

    def _calculate_priority(
        self,
        emotion_result: Optional[EdgeEmotionResult],
        safety_result: EdgeSafetyResult,
        wake_confidence: float,
    ) -> int:
        """Calculate processing priority (1-10, higher = more urgent)."""
        priority = 5  # Base priority

        # Safety considerations (highest priority)
        if not safety_result.passed:
            priority += 3
        elif safety_result.risk_level == "medium":
            priority += 1

        # Emotion considerations
        if emotion_result:
            urgent_emotions = ["angry", "fear", "sad"]
            if emotion_result.primary_emotion in urgent_emotions:
                priority += 2
            elif emotion_result.primary_emotion == "excited":
                priority += 1

        # Wake word confidence
        if wake_confidence > 0.8:
            priority += 1

        return min(10, max(1, priority))

    def _should_process_cloud(
        self,
        wake_word_detected: bool,
        emotion_result: Optional[EdgeEmotionResult],
        safety_result: EdgeSafetyResult,
    ) -> bool:
        """Decide if cloud processing is needed."""
        # Always process if safety check failed
        if not safety_result.passed:
            return True

        # Process if wake word detected
        if wake_word_detected:
            return True

        # Process if complex emotion detected
        if emotion_result:
            complex_emotions = ["angry", "fear", "sad", "surprise"]
            if emotion_result.primary_emotion in complex_emotions:
                return True

        # Don't process for simple/calm interactions
        return False

    def _generate_recommendations(
        self,
        emotion_result: Optional[EdgeEmotionResult],
        safety_result: EdgeSafetyResult,
        wake_word_detected: bool,
    ) -> List[str]:
        """Generate edge-based recommendations."""
        recommendations = []

        # Safety-based recommendations
        if not safety_result.passed:
            recommendations.append("Immediate safety review required")
            recommendations.append("Consider parental notification")

        # Emotion-based recommendations
        if emotion_result:
            if emotion_result.primary_emotion == "sad":
                recommendations.append("Provide comforting response")
            elif emotion_result.primary_emotion == "angry":
                recommendations.append("Use calming techniques")
            elif emotion_result.primary_emotion == "excited":
                recommendations.append("Engage with enthusiasm")
            elif emotion_result.primary_emotion == "fear":
                recommendations.append("Provide reassurance")

        # Wake word recommendations
        if wake_word_detected:
            recommendations.append("Child is actively engaging")
            recommendations.append("Prioritize response quality")

        return recommendations

    def _update_processing_stats(self, processing_time_ms: float) -> None:
        """Update processing statistics."""
        current_avg = self.processing_stats["average_processing_time"]
        total_processed = self.processing_stats["total_processed"]

        # Calculate running average
        new_avg = (
            (current_avg * (total_processed - 1)) + processing_time_ms
        ) / total_processed
        self.processing_stats["average_processing_time"] = new_avg

    def _create_fallback_result(
            self, start_time: float) -> EdgeProcessingResult:
        """Create fallback result when processing fails."""
        processing_time = (time.time() - start_time) * 1000

        return EdgeProcessingResult(
            should_process_cloud=True,  # Send to cloud when edge fails
            initial_emotion=None,
            safety_check=EdgeSafetyResult(
                passed=True,
                risk_level="unknown",
                detected_issues=[],
                safety_score=0.5,
                processing_time_ms=0,
                requires_cloud_review=True,
            ),
            wake_word_detected=False,
            priority=5,
            confidence=0.0,
            processing_time_ms=processing_time,
            edge_features=None,
            recommendations=["Edge processing failed, using cloud fallback"],
            device_load=1.0,
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get Edge AI performance statistics."""
        return {
            "processing_stats": self.processing_stats.copy(),
            "model_info": {
                "wake_word": self.model_manager.get_model_info("wake_word"),
                "emotion": self.model_manager.get_model_info("emotion"),
                "safety": self.model_manager.get_model_info("safety"),
            },
            "configuration": {
                "processing_mode": self.config.processing_mode.value,
                "safety_level": self.config.safety_level.value,
                "wake_word_model": self.config.wake_word_model.value,
            },
            "device_capabilities": {
                "tensorflow_available": TF_AVAILABLE,
                "audio_processing_available": AUDIO_PROCESSING_AVAILABLE,
                "max_concurrent_threads": 2,
            },
        }

    def optimize_for_device(self, device_specs: Dict[str, Any]) -> None:
        """Optimize processing based on device specifications."""
        # Adjust processing mode based on device capabilities
        memory_mb = device_specs.get("memory_mb", 512)
        cpu_cores = device_specs.get("cpu_cores", 2)

        if memory_mb < 256:
            self.config.processing_mode = EdgeProcessingMode.POWER_SAVE
        elif memory_mb < 512:
            self.config.processing_mode = EdgeProcessingMode.ULTRA_LOW_LATENCY
        else:
            self.config.processing_mode = EdgeProcessingMode.BALANCED

        self.logger.info(
            f"Optimized for device: {device_specs}, mode: {self.config.processing_mode.value}"
        )

    async def cleanup(self):
        """Cleanup Edge AI resources."""
        try:
            self.executor.shutdown(wait=True)
            self.logger.info("Edge AI Manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
