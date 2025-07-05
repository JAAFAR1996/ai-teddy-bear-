from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .edge_ai_manager import EdgeModelConfig

from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
import tflite_runtime.interpreter as tflite

from .edge_ai_manager import TF_AVAILABLE


class EdgeModelManager:
    """Manages TensorFlow Lite models for edge processing."""

    def __init__(self, config: "EdgeModelConfig"):
        self.config = config
        self.models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict] = {}
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    def load_tflite_model(
            self,
            model_path: str,
            model_name: str) -> Optional[Any]:
        """Load TensorFlow Lite model with optimization."""
        if not TF_AVAILABLE:
            self.logger.warning(
                f"TensorFlow not available, using mock for {model_name}"
            )
            return self._create_mock_model(model_name)

        try:
            full_path = Path("models/edge") / model_path

            if not full_path.exists():
                self.logger.warning(
                    f"Model file not found: {full_path}, using mock")
                return self._create_mock_model(model_name)

            # Load and optimize model
            interpreter = tflite.Interpreter(
                # Optimize for ESP32-S3
                model_path=str(full_path), num_threads=2
            )
            interpreter.allocate_tensors()

            # Store model metadata
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()

            self.model_metadata[model_name] = {
                "input_shape": input_details[0]["shape"],
                "output_shape": output_details[0]["shape"],
                "input_dtype": input_details[0]["dtype"],
                "output_dtype": output_details[0]["dtype"],
                "model_size_mb": full_path.stat().st_size / (1024 * 1024),
                "loaded_at": datetime.now().isoformat(),
            }

            self.logger.info(f"Loaded TFLite model: {model_name}")
            return interpreter

        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            return self._create_mock_model(model_name)

    def _create_mock_model(self, model_name: str) -> Dict[str, Any]:
        """Create mock model for testing without TensorFlow."""
        mock_model = {
            "type": "mock", "name": model_name, "input_shape": [
                1, 16000] if "wake_word" in model_name else [
                1, 13], "output_shape": [
                1, 2] if "safety" in model_name else [
                    1, 7], "created_at": datetime.now().isoformat(), }

        self.model_metadata[model_name] = {
            "model_type": "mock",
            "input_shape": mock_model["input_shape"],
            "output_shape": mock_model["output_shape"],
            "model_size_mb": 0.1,
            "loaded_at": datetime.now().isoformat(),
        }

        return mock_model

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get model metadata and performance info."""
        return self.model_metadata.get(model_name, {})
