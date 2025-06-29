import asyncio
from typing import Dict, Any
import numpy as np

class EdgeProcessor:
    """Process data at edge for lower latency"""
    
    def __init__(self, device_id: str, capabilities: Dict[str, bool]):
        self.device_id = device_id
        self.capabilities = capabilities
        self._models = {}
        
    async def initialize(self):
        """Initialize edge models based on device capabilities"""
        if self.capabilities.get("neural_engine"):
            await self._load_edge_models()
            
    async def _load_edge_models(self):
        """Load TensorFlow Lite models for edge processing"""
        try:
            import tflite_runtime.interpreter as tflite
            
            # Voice activity detection model
            self._models["vad"] = tflite.Interpreter(
                model_path="models/vad_edge.tflite"
            )
            self._models["vad"].allocate_tensors()
            
            # Emotion detection model
            self._models["emotion"] = tflite.Interpreter(
                model_path="models/emotion_edge.tflite"
            )
            self._models["emotion"].allocate_tensors()
        except ImportError:
            # Fallback to mock models
            self._models = {"vad": "mock", "emotion": "mock"}
        
    async def process_audio_edge(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Process audio at edge before sending to cloud"""
        results = {}
        
        # Quick VAD check
        if "vad" in self._models:
            results["has_speech"] = await self._run_vad(audio_data)
            if not results["has_speech"]:
                return results  # Don't send silence to cloud
                
        # Quick emotion check
        if "emotion" in self._models:
            results["emotion"] = await self._run_emotion_detection(audio_data)
            
        return results
    
    async def _run_vad(self, audio_data: np.ndarray) -> bool:
        """Run voice activity detection"""
        if self._models["vad"] == "mock":
            # Mock VAD - check if audio has significant energy
            return np.mean(np.abs(audio_data)) > 0.01
        
        # Real TFLite inference would go here
        return True
    
    async def _run_emotion_detection(self, audio_data: np.ndarray) -> str:
        """Run emotion detection on audio"""
        if self._models["emotion"] == "mock":
            # Mock emotion detection
            energy = np.mean(np.abs(audio_data))
            if energy > 0.1:
                return "excited"
            elif energy > 0.05:
                return "happy"
            else:
                return "calm"
        
        # Real TFLite inference would go here
        return "neutral"
    
    async def should_process_cloud(self, edge_results: Dict[str, Any]) -> bool:
        """Decide if cloud processing is needed"""
        # Don't send to cloud if no speech detected
        if not edge_results.get("has_speech", True):
            return False
        
        # Send complex emotions to cloud for better processing
        complex_emotions = ["confused", "frustrated", "excited"]
        if edge_results.get("emotion") in complex_emotions:
            return True
        
        return True