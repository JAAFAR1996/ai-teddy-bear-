"""
Audio Processing Domain Service
Handles audio enhancement and processing
"""

import logging

import numpy as np
from ..models.voice_models import AudioConfig

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False

try:
    import pyrubberband as pyrb
    PYRUBBERBAND_AVAILABLE = True
except ImportError:
    PYRUBBERBAND_AVAILABLE = False


class AudioProcessor:
    """Advanced audio processing"""

    def __init__(self, config: AudioConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    async def process_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply audio processing pipeline"""
        try:
            # Validate input
            if audio_data is None or len(audio_data) == 0:
                return audio_data

            # Noise reduction
            if self.config.enable_noise_reduction:
                audio_data = await self.reduce_noise(audio_data)

            # Normalization
            if self.config.enable_normalization:
                audio_data = await self.normalize_audio(audio_data)

            return audio_data

        except Exception as e:
            self.logger.error(f"Audio processing error: {e}")
            return audio_data

    async def reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """Reduce background noise"""
        try:
            if audio_data is None or len(audio_data) == 0:
                return audio_data

            if not NOISEREDUCE_AVAILABLE:
                self.logger.warning("noisereduce library not available, skipping noise reduction")
                return audio_data

            # Use noisereduce library
            reduced = nr.reduce_noise(
                y=audio_data,
                sr=self.config.sample_rate,
                prop_decrease=self.config.noise_reduction_strength,
            )
            return reduced

        except Exception as e:
            self.logger.error(f"Noise reduction error: {e}")
            return audio_data

    async def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio levels"""
        try:
            if audio_data is None or len(audio_data) == 0:
                return audio_data

            # Calculate current RMS
            rms = np.sqrt(np.mean(audio_data**2))

            if rms > 0:
                # Calculate target RMS from dB
                target_rms = 10 ** (self.config.target_loudness / 20)

                # Apply normalization
                normalized = audio_data * (target_rms / rms)

                # Prevent clipping
                max_val = np.max(np.abs(normalized))
                if max_val > 1.0:
                    normalized = normalized / max_val

                return normalized

            return audio_data

        except Exception as e:
            self.logger.error(f"Normalization error: {e}")
            return audio_data

    async def change_pitch(
        self, audio_data: np.ndarray, semitones: float
    ) -> np.ndarray:
        """Change audio pitch"""
        try:
            if audio_data is None or len(audio_data) == 0:
                return audio_data

            if not PYRUBBERBAND_AVAILABLE:
                self.logger.warning("pyrubberband library not available, skipping pitch shift")
                return audio_data

            # Use pyrubberband for pitch shifting
            shifted = pyrb.pitch_shift(audio_data, self.config.sample_rate, semitones)
            return shifted

        except Exception as e:
            self.logger.error(f"Pitch shift error: {e}")
            return audio_data

    async def change_speed(
        self, audio_data: np.ndarray, speed_factor: float
    ) -> np.ndarray:
        """Change audio speed without affecting pitch"""
        try:
            if audio_data is None or len(audio_data) == 0:
                return audio_data

            if not PYRUBBERBAND_AVAILABLE:
                self.logger.warning("pyrubberband library not available, skipping speed change")
                return audio_data

            # Use pyrubberband for time stretching
            stretched = pyrb.time_stretch(
                audio_data, self.config.sample_rate, speed_factor
            )
            return stretched

        except Exception as e:
            self.logger.error(f"Speed change error: {e}")
            return audio_data

    def validate_audio_data(self, audio_data: np.ndarray) -> bool:
        """Validate audio data quality"""
        try:
            if audio_data is None or len(audio_data) == 0:
                return False

            # Check for extreme values
            if np.max(np.abs(audio_data)) > 10.0:
                return False

            # Check for NaN or infinite values
            if np.isnan(audio_data).any() or np.isinf(audio_data).any():
                return False

            return True

        except Exception as e:
            self.logger.error(f"Audio validation error: {e}")
            return False
