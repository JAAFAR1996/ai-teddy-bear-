"""Audio-based emotion analysis infrastructure."""

from typing import Dict, Optional

import numpy as np
import structlog

logger = structlog.get_logger(__name__)

try:
    import librosa

    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning(" Librosa not available")


class AudioEmotionAnalyzer:
    """Infrastructure component for audio emotion analysis."""

    def __init__(self):
        self.is_ready = LIBROSA_AVAILABLE

    async def analyze_audio(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Optional[Dict[str, float]]:
        """Analyze audio and return emotion scores."""
        if not self.is_ready:
            return None

        try:
            features = self._extract_features(audio_data, sample_rate)
            emotion_scores = self._map_features_to_emotions(features)
            return emotion_scores

        except Exception as e:
            logger.error(f" Audio analysis failed: {e}")
            return None

    def _extract_features(self, audio: np.ndarray,
                          sr: int) -> Dict[str, float]:
        """Extract audio features."""
        features = {}

        # Pitch features
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        features["pitch_mean"] = (np.mean(pitches[pitches > 0]) if len(
            pitches[pitches > 0]) > 0 else 0)
        features["pitch_std"] = (np.std(pitches[pitches > 0]) if len(
            pitches[pitches > 0]) > 0 else 0)

        # Energy features
        features["rms_mean"] = np.mean(librosa.feature.rms(y=audio))
        features["rms_std"] = np.std(librosa.feature.rms(y=audio))

        # Spectral features
        features["spectral_centroid"] = np.mean(
            librosa.feature.spectral_centroid(y=audio, sr=sr)
        )
        features["zcr_mean"] = np.mean(
            librosa.feature.zero_crossing_rate(audio))

        # Tempo
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        features["tempo"] = tempo

        return features

    def _map_features_to_emotions(
            self, features: Dict[str, float]) -> Dict[str, float]:
        """Map audio features to emotion scores."""
        scores = {
            "happy": 0.0,
            "sad": 0.0,
            "angry": 0.0,
            "scared": 0.0,
            "calm": 0.0,
            "curious": 0.0,
        }

        emotion_rules = [
            ("happy", lambda f: f["pitch_mean"] > 300 and f["rms_mean"] > 0.1, 0.4),
            ("sad", lambda f: f["pitch_mean"] < 200 and f["rms_mean"] < 0.05, 0.4),
            ("angry", lambda f: f["rms_mean"] > 0.15 and f["pitch_std"] > 50, 0.4),
            ("scared", lambda f: f["rms_mean"] < 0.05 and f["zcr_mean"] > 0.05, 0.3),
            ("calm", lambda f: f["pitch_std"] < 30 and f["rms_std"] < 0.05, 0.3),
        ]

        for emotion, rule, weight in emotion_rules:
            if rule(features):
                scores[emotion] += weight

        # Normalize
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        else:
            scores["calm"] = 0.5

        return scores

    def is_available(self) -> bool:
        """Check if the analyzer is available."""
        return self.is_ready
