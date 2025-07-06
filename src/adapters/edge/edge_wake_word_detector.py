from typing import Tuple
import numpy as np
import time
import logging

try:
    import tflite_runtime.interpreter
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

from .edge_model_manager import EdgeModelManager

logger = logging.getLogger(__name__)


class EdgeWakeWordDetector:
    """Optimized wake word detection for edge devices."""

    def __init__(self, model_manager: "EdgeModelManager"):
        self.model_manager = model_manager
        self.model = None
        self.wake_word_patterns = [
            "hey teddy",
            "hello teddy",
            "hi teddy",
            "مرحبا تيدي",
            "أهلا تيدي",
            "السلام عليكم تيدي",
        ]
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    async def initialize(self, model_path: str):
        """Initialize wake word detection model."""
        self.model = self.model_manager.load_tflite_model(
            model_path, "wake_word")

    async def detect_wake_word(
            self, audio_data: np.ndarray) -> Tuple[bool, float]:
        """Detect wake word in audio data."""
        start_time = time.time()

        try:
            if self.model is None:
                return False, 0.0

            if self.model.get("type") == "mock":
                return self._mock_wake_word_detection(audio_data, start_time)

            # Preprocess audio for model
            processed_audio = self._preprocess_audio(audio_data)

            # Run inference
            input_details = self.model.get_input_details()
            output_details = self.model.get_output_details()

            self.model.set_tensor(input_details[0]["index"], processed_audio)
            self.model.invoke()

            output_data = self.model.get_tensor(output_details[0]["index"])
            # Assuming binary classification
            confidence = float(output_data[0][1])

            detected = confidence > 0.7  # Threshold for wake word

            processing_time = (time.time() - start_time) * 1000
            self.logger.debug(
                f"Wake word detection: {detected} (confidence: {confidence:.3f}, time: {processing_time:.1f}ms)"
            )

            return detected, confidence

        except Exception as e:
            self.logger.error(f"Wake word detection failed: {e}")
            return False, 0.0

    def _preprocess_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Preprocess audio for wake word model."""
        # Ensure correct input size (typically 16000 samples for 1 second)
        target_length = 16000

        if len(audio_data) > target_length:
            # Take the last second
            audio_data = audio_data[-target_length:]
        elif len(audio_data) < target_length:
            # Pad with zeros
            audio_data = np.pad(
                audio_data, (0, target_length - len(audio_data)))

        # Normalize and reshape for model
        audio_data = audio_data.astype(np.float32)
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))

        return audio_data.reshape(1, -1)

    def _mock_wake_word_detection(
        self, audio_data: np.ndarray, start_time: float
    ) -> Tuple[bool, float]:
        """Mock wake word detection for testing."""
        # Simple energy-based detection
        energy = np.mean(np.abs(audio_data))

        # Mock logic: higher energy = more likely to be wake word
        confidence = min(energy * 10, 1.0)
        detected = confidence > 0.5

        return detected, confidence
