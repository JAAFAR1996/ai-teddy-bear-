from typing import Dict, Tuple
import numpy as np
import time
import logging

from .edge_model_manager import EdgeModelManager
from .edge_ai_manager import EdgeAudioFeatures, EdgeEmotionResult

logger = logging.getLogger(__name__)


class EdgeEmotionAnalyzer:
    """Real-time emotion analysis on edge devices."""

    def __init__(self, model_manager: "EdgeModelManager"):
        self.model_manager = model_manager
        self.model = None
        self.emotion_labels = [
            "happy",
            "sad",
            "angry",
            "fear",
            "surprise",
            "calm",
            "excited",
        ]
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    async def initialize(self, model_path: str):
        """Initialize emotion analysis model."""
        self.model = self.model_manager.load_tflite_model(
            model_path, "emotion")

    async def analyze_emotion(
        self, features: "EdgeAudioFeatures"
    ) -> "EdgeEmotionResult":
        """Analyze emotion from audio features."""
        start_time = time.time()

        try:
            if self.model is None:
                return self._create_default_emotion_result(start_time)

            if self.model.get("type") == "mock":
                return self._mock_emotion_analysis(features, start_time)

            # Prepare input features
            input_features = self._prepare_emotion_features(features)

            # Run inference
            input_details = self.model.get_input_details()
            output_details = self.model.get_output_details()

            self.model.set_tensor(input_details[0]["index"], input_features)
            self.model.invoke()

            output_data = self.model.get_tensor(output_details[0]["index"])
            emotion_scores = {
                emotion: float(score)
                for emotion, score in zip(self.emotion_labels, output_data[0])
            }

            # Find primary emotion
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])

            # Calculate arousal and valence
            arousal, valence = self._calculate_arousal_valence(emotion_scores)

            processing_time = (time.time() - start_time) * 1000

            return EdgeEmotionResult(
                primary_emotion=primary_emotion[0],
                confidence=primary_emotion[1],
                emotion_scores=emotion_scores,
                arousal=arousal,
                valence=valence,
                processing_time_ms=processing_time,
                model_version="edge_v1.0",
            )

        except Exception as e:
            self.logger.error(f"Emotion analysis failed: {e}")
            return self._create_default_emotion_result(start_time)

    def _prepare_emotion_features(
            self, features: "EdgeAudioFeatures") -> np.ndarray:
        """Prepare features for emotion model."""
        # Combine relevant features
        feature_vector = np.concatenate(
            [
                features.mfcc,
                [
                    features.spectral_centroid,
                    features.zero_crossing_rate,
                    features.rms_energy,
                    features.pitch_mean,
                    features.pitch_std,
                ],
            ]
        )

        # Normalize features
        feature_vector = feature_vector.astype(np.float32)
        return feature_vector.reshape(1, -1)

    def _mock_emotion_analysis(
        self, features: "EdgeAudioFeatures", start_time: float
    ) -> "EdgeEmotionResult":
        """Mock emotion analysis for testing."""
        # Simple rule-based emotion detection
        energy = features.rms_energy
        pitch = features.pitch_mean
        zcr = features.zero_crossing_rate

        emotion_scores = {}

        if energy > 0.1 and pitch > 200:
            emotion_scores = {"excited": 0.8, "happy": 0.6, "calm": 0.2}
        elif energy < 0.03:
            emotion_scores = {"calm": 0.8, "sad": 0.4, "happy": 0.3}
        elif zcr > 0.1:
            emotion_scores = {"angry": 0.7, "excited": 0.5, "fear": 0.3}
        else:
            emotion_scores = {"happy": 0.6, "calm": 0.5, "excited": 0.3}

        # Fill remaining emotions
        for emotion in self.emotion_labels:
            if emotion not in emotion_scores:
                emotion_scores[emotion] = 0.1

        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        arousal, valence = self._calculate_arousal_valence(emotion_scores)

        processing_time = (time.time() - start_time) * 1000

        return EdgeEmotionResult(
            primary_emotion=primary_emotion[0],
            confidence=primary_emotion[1],
            emotion_scores=emotion_scores,
            arousal=arousal,
            valence=valence,
            processing_time_ms=processing_time,
            model_version="mock_v1.0",
        )

    def _calculate_arousal_valence(
        self, emotion_scores: Dict[str, float]
    ) -> Tuple[float, float]:
        """Calculate arousal and valence from emotion scores."""
        # Arousal mapping (high = excited, low = calm)
        arousal_map = {
            "excited": 0.9,
            "angry": 0.8,
            "fear": 0.7,
            "surprise": 0.6,
            "happy": 0.5,
            "sad": 0.3,
            "calm": 0.1,
        }

        # Valence mapping (high = positive, low = negative)
        valence_map = {
            "happy": 0.9,
            "excited": 0.8,
            "surprise": 0.6,
            "calm": 0.5,
            "sad": 0.2,
            "fear": 0.1,
            "angry": 0.1,
        }

        arousal = sum(
            emotion_scores[emotion] * arousal_map.get(emotion, 0.5)
            for emotion in emotion_scores
        )
        valence = sum(
            emotion_scores[emotion] * valence_map.get(emotion, 0.5)
            for emotion in emotion_scores
        )

        return float(arousal), float(valence)

    def _create_default_emotion_result(
            self, start_time: float) -> "EdgeEmotionResult":
        """Create default emotion result when analysis fails."""
        processing_time = (time.time() - start_time) * 1000

        return EdgeEmotionResult(
            primary_emotion="neutral",
            confidence=0.5,
            emotion_scores={"neutral": 0.5, "calm": 0.3, "happy": 0.2},
            arousal=0.5,
            valence=0.5,
            processing_time_ms=processing_time,
            model_version="fallback_v1.0",
        )
