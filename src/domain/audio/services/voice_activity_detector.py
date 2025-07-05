"""
Voice Activity Detection Domain Service
Detects speech in audio streams
"""

import logging
from typing import List

import numpy as np
from ..models.voice_models import AudioConfig

try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False


class VoiceActivityDetector:
    """Voice Activity Detection wrapper"""

    def __init__(self, config: AudioConfig):
        self.config = config
        self.frame_duration = config.vad_frame_duration
        self.sample_rate = config.sample_rate
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if WEBRTCVAD_AVAILABLE:
            self.vad = webrtcvad.Vad(config.vad_mode)
        else:
            self.vad = None
            self.logger.warning("webrtcvad library not available, using fallback VAD")

    def is_speech(self, audio_frame: bytes) -> bool:
        """Check if audio frame contains speech"""
        try:
            if self.vad is None:
                # Fallback: simple energy-based detection
                return self._fallback_speech_detection(audio_frame)
            
            return self.vad.is_speech(audio_frame, self.sample_rate)
        except Exception as e:
            self.logger.error(f"VAD speech detection error: {e}")
            return False
    
    def _fallback_speech_detection(self, audio_frame: bytes) -> bool:
        """Fallback speech detection using energy threshold"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_frame, dtype=np.int16)
            # Calculate RMS energy
            rms = np.sqrt(np.mean(audio_array.astype(float) ** 2))
            # Simple threshold (can be adjusted)
            threshold = 1000  # Adjust based on your needs
            return rms > threshold
        except Exception as e:
            self.logger.error(f"Fallback VAD error: {e}")
            return False

    def get_speech_segments(self, audio_data: np.ndarray) -> List[tuple]:
        """Get speech segments from audio"""
        try:
            # Convert to bytes
            audio_bytes = audio_data.astype("int16").tobytes()

            # Frame size
            frame_size = int(self.sample_rate * self.frame_duration / 1000)

            segments = []
            speech_start = None

            for i in range(0, len(audio_data) - frame_size, frame_size):
                frame = audio_bytes[i * 2 : (i + frame_size) * 2]

                if self.is_speech(frame):
                    if speech_start is None:
                        speech_start = i
                else:
                    if speech_start is not None:
                        segments.append((speech_start, i))
                        speech_start = None

            # Handle last segment
            if speech_start is not None:
                segments.append((speech_start, len(audio_data)))

            return segments

        except Exception as e:
            self.logger.error(f"Speech segmentation error: {e}")
            return []

    def calculate_speech_ratio(self, audio_data: np.ndarray) -> float:
        """Calculate ratio of speech to total audio"""
        try:
            segments = self.get_speech_segments(audio_data)
            if not segments:
                return 0.0

            speech_duration = sum(end - start for start, end in segments)
            total_duration = len(audio_data)

            return speech_duration / total_duration if total_duration > 0 else 0.0

        except Exception as e:
            self.logger.error(f"Speech ratio calculation error: {e}")
            return 0.0
