from typing import Any, Dict, List, Optional
import numpy as np
import time
import logging

from .edge_model_manager import EdgeModelManager
from .edge_ai_manager import EdgeAudioFeatures, EdgeSafetyResult, SafetyLevel

logger = logging.getLogger(__name__)


class EdgeSafetyChecker:
    """Real-time safety checking on edge devices."""

    def __init__(
            self,
            model_manager: "EdgeModelManager",
            safety_level: "SafetyLevel"):
        self.model_manager = model_manager
        self.safety_level = safety_level
        self.model = None
        self.safety_keywords = {
            "inappropriate": ["bad", "stupid", "hate", "kill", "hurt"],
            "distress": ["help", "scared", "emergency", "danger", "stop"],
            "violence": ["fight", "hit", "punch", "blood", "weapon"],
        }
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    async def initialize(self, model_path: str):
        """Initialize safety checking model."""
        if self.safety_level != SafetyLevel.BASIC:
            self.model = self.model_manager.load_tflite_model(
                model_path, "safety")

    async def check_safety(
        self,
        audio_features: "EdgeAudioFeatures",
        transcribed_text: Optional[str] = None,
    ) -> "EdgeSafetyResult":
        """Perform safety check on audio and/or text."""
        start_time = time.time()

        try:
            if self.safety_level == SafetyLevel.BASIC:
                return self._basic_safety_check(transcribed_text, start_time)
            elif self.model and self.model.get("type") == "mock":
                return self._mock_safety_check(
                    audio_features, transcribed_text, start_time
                )
            elif self.model:
                return await self._ml_safety_check(
                    audio_features, transcribed_text, start_time
                )
            else:
                return self._basic_safety_check(transcribed_text, start_time)

        except Exception as e:
            self.logger.error(f"Safety check failed: {e}")
            return self._create_safe_result(start_time)

    def _basic_safety_check(
        self, text: Optional[str], start_time: float
    ) -> "EdgeSafetyResult":
        """Basic keyword-based safety checking."""
        detected_issues = []
        safety_score = 1.0

        if text:
            text_lower = text.lower()
            for category, keywords in self.safety_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        detected_issues.append(f"{category}: {keyword}")
                        safety_score -= 0.2

        safety_score = max(0.0, safety_score)
        passed = safety_score > 0.6

        processing_time = (time.time() - start_time) * 1000

        return EdgeSafetyResult(
            passed=passed,
            risk_level="low" if passed else "medium",
            detected_issues=detected_issues,
            safety_score=safety_score,
            processing_time_ms=processing_time,
            requires_cloud_review=not passed,
        )

    def _mock_safety_check(
        self,
        audio_features: "EdgeAudioFeatures",
        text: Optional[str],
        start_time: float,
    ) -> "EdgeSafetyResult":
        """Mock ML-based safety checking."""
        # Combine audio and text analysis
        detected_issues = []
        safety_score = 1.0

        # Audio-based checks
        if audio_features.rms_energy > 0.15:  # Very loud
            detected_issues.append("loud_audio")
            safety_score -= 0.1

        if audio_features.zero_crossing_rate > 0.15:  # Agitated speech
            detected_issues.append("agitated_speech")
            safety_score -= 0.1

        # Text-based checks
        if text:
            safety_score -= self._analyze_text_safety(text, detected_issues)

        safety_score = max(0.0, safety_score)
        passed = safety_score > 0.7

        processing_time = (time.time() - start_time) * 1000

        return EdgeSafetyResult(
            passed=passed,
            risk_level=self._determine_risk_level(safety_score),
            detected_issues=detected_issues,
            safety_score=safety_score,
            processing_time_ms=processing_time,
            requires_cloud_review=safety_score < 0.5,
        )

    async def _ml_safety_check(
        self,
        audio_features: "EdgeAudioFeatures",
        text: Optional[str],
        start_time: float,
    ) -> "EdgeSafetyResult":
        """ML-based safety checking using TensorFlow Lite."""
        # Prepare features for ML model
        feature_vector = self._prepare_safety_features(audio_features)

        # Run inference
        input_details = self.model.get_input_details()
        output_details = self.model.get_output_details()

        self.model.set_tensor(input_details[0]["index"], feature_vector)
        self.model.invoke()

        output_data = self.model.get_tensor(output_details[0]["index"])
        safety_score = float(output_data[0][0])  # Assuming safety score output

        # Combine with text analysis if available
        detected_issues = []
        if text:
            text_penalty = self._analyze_text_safety(text, detected_issues)
            safety_score -= text_penalty

        safety_score = max(0.0, safety_score)
        passed = safety_score > 0.7

        processing_time = (time.time() - start_time) * 1000

        return EdgeSafetyResult(
            passed=passed,
            risk_level=self._determine_risk_level(safety_score),
            detected_issues=detected_issues,
            safety_score=safety_score,
            processing_time_ms=processing_time,
            requires_cloud_review=safety_score < 0.5,
        )

    def _prepare_safety_features(
        self, audio_features: "EdgeAudioFeatures"
    ) -> np.ndarray:
        """Prepare features for safety ML model."""
        # Select relevant features for safety analysis
        feature_vector = np.array(
            [
                audio_features.rms_energy,
                audio_features.zero_crossing_rate,
                audio_features.pitch_mean,
                audio_features.pitch_std,
                audio_features.spectral_centroid,
            ],
            dtype=np.float32,
        )

        return feature_vector.reshape(1, -1)

    def _analyze_text_safety(
            self,
            text: str,
            detected_issues: List[str]) -> float:
        """Analyze text for safety issues."""
        text_lower = text.lower()
        penalty = 0.0

        for category, keywords in self.safety_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_issues.append(f"text_{category}: {keyword}")
                    penalty += 0.15

        return penalty

    def _determine_risk_level(self, safety_score: float) -> str:
        """Determine risk level from safety score."""
        if safety_score > 0.8:
            return "low"
        elif safety_score > 0.6:
            return "medium"
        elif safety_score > 0.3:
            return "high"
        else:
            return "critical"

    def _create_safe_result(self, start_time: float) -> "EdgeSafetyResult":
        """Create safe result when safety check fails."""
        processing_time = (time.time() - start_time) * 1000

        return EdgeSafetyResult(
            passed=True,
            risk_level="low",
            detected_issues=[],
            safety_score=1.0,
            processing_time_ms=processing_time,
            requires_cloud_review=False,
        )
