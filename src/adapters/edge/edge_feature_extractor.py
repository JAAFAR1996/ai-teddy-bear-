import numpy as np
import time
import logging

try:
    import librosa

    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

from .edge_ai_manager import EdgeAudioFeatures

logger = logging.getLogger(__name__)


class EdgeFeatureExtractor:
    """Fast audio feature extraction optimized for edge devices."""

    def __init__(self):
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")
        self.sample_rate = 16000  # Standard for voice processing

    async def extract_features(
        self, audio_data: np.ndarray, quick_mode: bool = True
    ) -> "EdgeAudioFeatures":
        """Extract audio features optimized for edge processing."""
        start_time = time.time()

        try:
            if not AUDIO_PROCESSING_AVAILABLE:
                return self._extract_basic_features(audio_data, start_time)

            # Ensure correct audio format
            audio_data = self._normalize_audio(audio_data)

            if quick_mode:
                return await self._extract_quick_features(audio_data, start_time)
            else:
                return await self._extract_full_features(audio_data, start_time)

        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return self._extract_basic_features(audio_data, start_time)

    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio for consistent processing."""
        # Convert to float32 and normalize
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Normalize to [-1, 1] range
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))

        return audio_data

    async def _extract_quick_features(
        self, audio_data: np.ndarray, start_time: float
    ) -> "EdgeAudioFeatures":
        """Extract minimal features for ultra-low latency."""
        # Basic energy and timing features
        rms_energy = float(np.sqrt(np.mean(np.square(audio_data))))
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(audio_data)))
        spectral_centroid = float(
            np.mean(
                librosa.feature.spectral_centroid(
                    y=audio_data,
                    sr=self.sample_rate)))

        # Simple MFCC (reduced coefficients)
        mfcc = librosa.feature.mfcc(
            y=audio_data, sr=self.sample_rate, n_mfcc=5, hop_length=512
        )

        processing_time = (time.time() - start_time) * 1000

        return EdgeAudioFeatures(
            mfcc=np.mean(mfcc, axis=1),
            spectral_centroid=spectral_centroid,
            zero_crossing_rate=zcr,
            rms_energy=rms_energy,
            pitch_mean=0.0,  # Skip for speed
            pitch_std=0.0,  # Skip for speed
            tempo=0.0,  # Skip for speed
            spectral_rolloff=0.0,  # Skip for speed
            extraction_time_ms=processing_time,
        )

    async def _extract_full_features(
        self, audio_data: np.ndarray, start_time: float
    ) -> "EdgeAudioFeatures":
        """Extract comprehensive features for high accuracy."""
        # MFCC features
        mfcc = librosa.feature.mfcc(
            y=audio_data, sr=self.sample_rate, n_mfcc=13)

        # Spectral features
        spectral_centroid = float(
            np.mean(
                librosa.feature.spectral_centroid(
                    y=audio_data,
                    sr=self.sample_rate)))
        spectral_rolloff = float(
            np.mean(
                librosa.feature.spectral_rolloff(
                    y=audio_data,
                    sr=self.sample_rate)))

        # Temporal features
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(audio_data)))
        rms_energy = float(np.sqrt(np.mean(np.square(audio_data))))

        # Pitch features
        pitches, _ = librosa.piptrack(
            y=audio_data, sr=self.sample_rate)
        pitch_values = pitches[pitches > 0]
        pitch_mean = float(np.mean(pitch_values)) if len(
            pitch_values) > 0 else 0.0
        pitch_std = float(np.std(pitch_values)) if len(
            pitch_values) > 0 else 0.0

        # Tempo
        tempo, _ = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)

        processing_time = (time.time() - start_time) * 1000

        return EdgeAudioFeatures(
            mfcc=np.mean(mfcc, axis=1),
            spectral_centroid=spectral_centroid,
            zero_crossing_rate=zcr,
            rms_energy=rms_energy,
            pitch_mean=pitch_mean,
            pitch_std=pitch_std,
            tempo=float(tempo),
            spectral_rolloff=spectral_rolloff,
            extraction_time_ms=processing_time,
        )

    def _extract_basic_features(
        self, audio_data: np.ndarray, start_time: float
    ) -> "EdgeAudioFeatures":
        """Basic feature extraction without librosa dependency."""
        # Simple statistical features
        rms_energy = float(np.sqrt(np.mean(np.square(audio_data))))

        # Simple zero crossing rate
        zcr = float(np.mean(np.diff(np.signbit(audio_data))))

        # Mock MFCC with statistical features
        mfcc = np.array(
            [
                np.mean(audio_data),
                np.std(audio_data),
                np.max(audio_data),
                np.min(audio_data),
                rms_energy,
            ]
        )

        processing_time = (time.time() - start_time) * 1000

        return EdgeAudioFeatures(
            mfcc=mfcc,
            spectral_centroid=float(np.mean(np.abs(audio_data))),
            zero_crossing_rate=zcr,
            rms_energy=rms_energy,
            pitch_mean=0.0,
            pitch_std=0.0,
            tempo=0.0,
            spectral_rolloff=0.0,
            extraction_time_ms=processing_time,
        )
