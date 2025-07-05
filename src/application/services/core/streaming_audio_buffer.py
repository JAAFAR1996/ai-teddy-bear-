import time
from typing import Optional
import numpy as np

from .transcription_models import TranscriptionConfig


class StreamingAudioBuffer:
    """Smart audio buffer for streaming transcription"""

    def __init__(self, config: TranscriptionConfig):
        self.config = config
        self.buffer = np.array([], dtype=np.float32)
        self.sample_rate = config.sample_rate
        self.chunk_samples = int(config.chunk_duration * self.sample_rate)
        self.overlap_samples = int(config.overlap_duration * self.sample_rate)
        self.min_silence_samples = int(
            config.min_silence_duration * self.sample_rate)

        # State tracking
        self.last_activity = time.time()
        self.is_speech_detected = False

    def add_chunk(self, audio_chunk: np.ndarray) -> None:
        """Add audio chunk to buffer"""
        # Ensure correct format
        if audio_chunk.dtype != np.float32:
            audio_chunk = audio_chunk.astype(np.float32)

        # Normalize if needed
        if np.max(np.abs(audio_chunk)) > 1.0:
            audio_chunk = audio_chunk / np.max(np.abs(audio_chunk))

        # Add to buffer
        self.buffer = np.concatenate([self.buffer, audio_chunk])

        # Update activity detection
        if self._detect_activity(audio_chunk):
            self.last_activity = time.time()
            self.is_speech_detected = True

    def _detect_activity(self, audio_chunk: np.ndarray) -> bool:
        """Simple voice activity detection"""
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_chunk**2))

        # Dynamic threshold based on recent history
        threshold = 0.01  # Base threshold
        return rms > threshold

    def get_ready_chunk(self) -> Optional[np.ndarray]:
        """Get audio chunk ready for transcription"""
        if len(self.buffer) < self.chunk_samples:
            return None

        # Check for silence gap
        silence_duration = time.time() - self.last_activity

        if (
            self.is_speech_detected
            and silence_duration >= self.config.min_silence_duration
        ):
            # Extract complete utterance
            chunk = self.buffer.copy()
            self.buffer = np.array([], dtype=np.float32)
            self.is_speech_detected = False
            return chunk

        # Extract chunk with overlap
        if len(self.buffer) >= self.chunk_samples:
            chunk = self.buffer[: self.chunk_samples]
            # Keep overlap for next chunk
            self.buffer = self.buffer[self.chunk_samples -
                                      self.overlap_samples:]
            return chunk

        return None

    @property
    def duration(self) -> float:
        """Current buffer duration in seconds"""
        return len(self.buffer) / self.sample_rate

    def clear(self) -> None:
        """Clear the buffer"""
        self.buffer = np.array([], dtype=np.float32)
        self.is_speech_detected = False
