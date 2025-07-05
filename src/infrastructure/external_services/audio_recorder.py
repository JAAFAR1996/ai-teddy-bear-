"""Audio file handling module."""

import logging
import os

import numpy as np
import soundfile as sf


class AudioRecorder:
    """Handles audio file input and management."""

    def __init__(self):
        """Initialize audio recorder."""
        self.logger = logging.getLogger(__name__)

    def load_audio_file(self, file_path: str) -> np.ndarray:
        """
        Load audio file and return as numpy array.

        Args:
            file_path (str): Path to the audio file to load.

        Returns:
            np.ndarray: Audio data as a numpy array.
        """
        try:
            # Read audio file
            audio_data, sample_rate = sf.read(file_path)

            # Convert to mono if stereo
            if audio_data.ndim > 1:
                audio_data = audio_data.mean(axis=1)

            # Resample to 16kHz if needed (optional, depends on your
            # requirements)
            if sample_rate != 16000:
                from scipy import signal

                resample_ratio = 16000 / sample_rate
                audio_data = signal.resample(
                    audio_data, int(len(audio_data) * resample_ratio)
                )

            # Normalize audio
            if np.any(audio_data):
                audio_data = audio_data / np.max(np.abs(audio_data))

            return audio_data

        except Exception as e:
            self.logger.error(f"Error loading audio file: {e}")
            return np.array([])

    def save_audio_file(
        self, audio_data: np.ndarray, file_path: str, sample_rate: int = 16000
    ) -> None:
        """
        Save audio data to a file.

        Args:
            audio_data (np.ndarray): Audio data to save.
            file_path (str): Path to save the audio file.
            sample_rate (int, optional): Sample rate. Defaults to 16000.
        """
        try:
            abs_path = os.path.abspath(file_path)
            sf.write(abs_path, audio_data, sample_rate)
            self.logger.info(f"Audio saved to {abs_path}")
        except Exception as e:
            self.logger.error(f"Error saving audio file: {e}")

    def is_valid_audio(self, audio_data: np.ndarray) -> bool:
        """
        Check if audio data is valid.

        Args:
            audio_data (np.ndarray): Audio data to validate.

        Returns:
            bool: True if audio is valid, False otherwise.
        """
        return audio_data is not None and len(
            audio_data) > 0 and np.any(audio_data)

    def get_audio_duration(
        self, audio_data: np.ndarray, sample_rate: int = 16000
    ) -> float:
        """
        Get duration of audio data.

        Args:
            audio_data (np.ndarray): Audio data.
            sample_rate (int, optional): Sample rate. Defaults to 16000.

        Returns:
            float: Duration in seconds.
        """
        return len(audio_data) / sample_rate
