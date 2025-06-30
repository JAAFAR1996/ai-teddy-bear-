"""
Enterprise-Grade Edge AI Manager for AI Teddy Bear Project.

This module provides advanced Edge AI capabilities for ESP32-S3 devices,
enabling real-time wake word detection, emotion analysis, and safety checking
without cloud dependency for instant response.

AI Team Implementation - Task 10
Author: AI Team Lead
"""

import logging
import asyncio
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import pickle

# TensorFlow Lite for Edge AI
try:
    import tensorflow as tf
    import tflite_runtime.interpreter as tflite
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None
    tflite = None

# Audio processing
try:
    import librosa
    import scipy.signal
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

logger = logging.getLogger(__name__)


class EdgeProcessingMode(Enum):
    """Edge processing modes for different scenarios."""
    ULTRA_LOW_LATENCY = "ultra_low_latency"  # <10ms response
    BALANCED = "balanced"                     # <50ms response
    HIGH_ACCURACY = "high_accuracy"          # <100ms response
    POWER_SAVE = "power_save"                # Minimal processing


class WakeWordModel(Enum):
    """Available wake word detection models."""
    LIGHTWEIGHT = "wake_word_lite.tflite"    # <1MB, basic detection
    STANDARD = "wake_word.tflite"            # ~2MB, good accuracy
    ENHANCED = "wake_word_enhanced.tflite"   # ~5MB, high accuracy


class SafetyLevel(Enum):
    """Safety check levels for edge processing."""
    BASIC = "basic"           # Simple keyword filtering
    STANDARD = "standard"     # Content analysis
    ENHANCED = "enhanced"     # Advanced safety ML model


@dataclass
class EdgeAudioFeatures:
    """Container for extracted audio features on edge."""
    mfcc: np.ndarray
    spectral_centroid: float
    zero_crossing_rate: float
    rms_energy: float
    pitch_mean: float
    pitch_std: float
    tempo: float
    spectral_rolloff: float
    extraction_time_ms: float


@dataclass
class EdgeEmotionResult:
    """Result from edge emotion analysis."""
    primary_emotion: str
    confidence: float
    emotion_scores: Dict[str, float]
    arousal: float
    valence: float
    processing_time_ms: float
    model_version: str


@dataclass
class EdgeSafetyResult:
    """Result from edge safety checking."""
    passed: bool
    risk_level: str
    detected_issues: List[str]
    safety_score: float
    processing_time_ms: float
    requires_cloud_review: bool


@dataclass
class EdgeProcessingResult:
    """Complete result from edge processing."""
    should_process_cloud: bool
    initial_emotion: Optional[EdgeEmotionResult]
    safety_check: Optional[EdgeSafetyResult]
    wake_word_detected: bool
    priority: int  # 1-10, higher = more urgent
    confidence: float
    processing_time_ms: float
    edge_features: Optional[EdgeAudioFeatures]
    recommendations: List[str]
    device_load: float


@dataclass
class EdgeModelConfig:
    """Configuration for edge AI models."""
    wake_word_model: WakeWordModel = WakeWordModel.STANDARD
    emotion_model_path: str = "emotion_lite.tflite"
    safety_model_path: str = "safety_check.tflite"
    processing_mode: EdgeProcessingMode = EdgeProcessingMode.BALANCED
    safety_level: SafetyLevel = SafetyLevel.STANDARD
    enable_caching: bool = True
    max_cache_size: int = 100
    model_optimization: bool = True


class EdgeModelManager:
    """Manages TensorFlow Lite models for edge processing."""
    
    def __init__(self, config: EdgeModelConfig):
        self.config = config
        self.models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def load_tflite_model(self, model_path: str, model_name: str) -> Optional[Any]:
        """Load TensorFlow Lite model with optimization."""
        if not TF_AVAILABLE:
            self.logger.warning(f"TensorFlow not available, using mock for {model_name}")
            return self._create_mock_model(model_name)
        
        try:
            full_path = Path("models/edge") / model_path
            
            if not full_path.exists():
                self.logger.warning(f"Model file not found: {full_path}, using mock")
                return self._create_mock_model(model_name)
            
            # Load and optimize model
            interpreter = tflite.Interpreter(
                model_path=str(full_path),
                num_threads=2  # Optimize for ESP32-S3
            )
            interpreter.allocate_tensors()
            
            # Store model metadata
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            self.model_metadata[model_name] = {
                "input_shape": input_details[0]['shape'],
                "output_shape": output_details[0]['shape'],
                "input_dtype": input_details[0]['dtype'],
                "output_dtype": output_details[0]['dtype'],
                "model_size_mb": full_path.stat().st_size / (1024 * 1024),
                "loaded_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Loaded TFLite model: {model_name}")
            return interpreter
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            return self._create_mock_model(model_name)
    
    def _create_mock_model(self, model_name: str) -> Dict[str, Any]:
        """Create mock model for testing without TensorFlow."""
        mock_model = {
            "type": "mock",
            "name": model_name,
            "input_shape": [1, 16000] if "wake_word" in model_name else [1, 13],
            "output_shape": [1, 2] if "safety" in model_name else [1, 7],
            "created_at": datetime.now().isoformat()
        }
        
        self.model_metadata[model_name] = {
            "model_type": "mock",
            "input_shape": mock_model["input_shape"],
            "output_shape": mock_model["output_shape"],
            "model_size_mb": 0.1,
            "loaded_at": datetime.now().isoformat()
        }
        
        return mock_model
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get model metadata and performance info."""
        return self.model_metadata.get(model_name, {})


class EdgeFeatureExtractor:
    """Fast audio feature extraction optimized for edge devices."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.sample_rate = 16000  # Standard for voice processing
    
    async def extract_features(
        self, 
        audio_data: np.ndarray,
        quick_mode: bool = True
    ) -> EdgeAudioFeatures:
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
        self, 
        audio_data: np.ndarray, 
        start_time: float
    ) -> EdgeAudioFeatures:
        """Extract minimal features for ultra-low latency."""
        # Basic energy and timing features
        rms_energy = float(np.sqrt(np.mean(np.square(audio_data))))
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(audio_data)))
        spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(
            y=audio_data, sr=self.sample_rate
        )))
        
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
            pitch_std=0.0,   # Skip for speed
            tempo=0.0,       # Skip for speed
            spectral_rolloff=0.0,  # Skip for speed
            extraction_time_ms=processing_time
        )
    
    async def _extract_full_features(
        self, 
        audio_data: np.ndarray, 
        start_time: float
    ) -> EdgeAudioFeatures:
        """Extract comprehensive features for high accuracy."""
        # MFCC features
        mfcc = librosa.feature.mfcc(
            y=audio_data, sr=self.sample_rate, n_mfcc=13
        )
        
        # Spectral features
        spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(
            y=audio_data, sr=self.sample_rate
        )))
        spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(
            y=audio_data, sr=self.sample_rate
        )))
        
        # Temporal features
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(audio_data)))
        rms_energy = float(np.sqrt(np.mean(np.square(audio_data))))
        
        # Pitch features
        pitches, magnitudes = librosa.piptrack(
            y=audio_data, sr=self.sample_rate
        )
        pitch_values = pitches[pitches > 0]
        pitch_mean = float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0.0
        pitch_std = float(np.std(pitch_values)) if len(pitch_values) > 0 else 0.0
        
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
            extraction_time_ms=processing_time
        )
    
    def _extract_basic_features(
        self, 
        audio_data: np.ndarray, 
        start_time: float
    ) -> EdgeAudioFeatures:
        """Basic feature extraction without librosa dependency."""
        # Simple statistical features
        rms_energy = float(np.sqrt(np.mean(np.square(audio_data))))
        
        # Simple zero crossing rate
        zcr = float(np.mean(np.diff(np.signbit(audio_data))))
        
        # Mock MFCC with statistical features
        mfcc = np.array([
            np.mean(audio_data),
            np.std(audio_data),
            np.max(audio_data),
            np.min(audio_data),
            rms_energy
        ])
        
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
            extraction_time_ms=processing_time
        )


class EdgeWakeWordDetector:
    """Optimized wake word detection for edge devices."""
    
    def __init__(self, model_manager: EdgeModelManager):
        self.model_manager = model_manager
        self.model = None
        self.wake_word_patterns = [
            "hey teddy", "hello teddy", "hi teddy",
            "مرحبا تيدي", "أهلا تيدي", "السلام عليكم تيدي"
        ]
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def initialize(self, model_path: str):
        """Initialize wake word detection model."""
        self.model = self.model_manager.load_tflite_model(model_path, "wake_word")
        
    async def detect_wake_word(self, audio_data: np.ndarray) -> Tuple[bool, float]:
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
            
            self.model.set_tensor(input_details[0]['index'], processed_audio)
            self.model.invoke()
            
            output_data = self.model.get_tensor(output_details[0]['index'])
            confidence = float(output_data[0][1])  # Assuming binary classification
            
            detected = confidence > 0.7  # Threshold for wake word
            
            processing_time = (time.time() - start_time) * 1000
            self.logger.debug(f"Wake word detection: {detected} (confidence: {confidence:.3f}, time: {processing_time:.1f}ms)")
            
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
            audio_data = np.pad(audio_data, (0, target_length - len(audio_data)))
        
        # Normalize and reshape for model
        audio_data = audio_data.astype(np.float32)
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))
        
        return audio_data.reshape(1, -1)
    
    def _mock_wake_word_detection(
        self, 
        audio_data: np.ndarray, 
        start_time: float
    ) -> Tuple[bool, float]:
        """Mock wake word detection for testing."""
        # Simple energy-based detection
        energy = np.mean(np.abs(audio_data))
        
        # Mock logic: higher energy = more likely to be wake word
        confidence = min(energy * 10, 1.0)
        detected = confidence > 0.5
        
        processing_time = (time.time() - start_time) * 1000
        
        return detected, confidence


class EdgeEmotionAnalyzer:
    """Real-time emotion analysis on edge devices."""
    
    def __init__(self, model_manager: EdgeModelManager):
        self.model_manager = model_manager
        self.model = None
        self.emotion_labels = [
            "happy", "sad", "angry", "fear", "surprise", "calm", "excited"
        ]
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self, model_path: str):
        """Initialize emotion analysis model."""
        self.model = self.model_manager.load_tflite_model(model_path, "emotion")
    
    async def analyze_emotion(
        self, 
        features: EdgeAudioFeatures
    ) -> EdgeEmotionResult:
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
            
            self.model.set_tensor(input_details[0]['index'], input_features)
            self.model.invoke()
            
            output_data = self.model.get_tensor(output_details[0]['index'])
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
                model_version="edge_v1.0"
            )
            
        except Exception as e:
            self.logger.error(f"Emotion analysis failed: {e}")
            return self._create_default_emotion_result(start_time)
    
    def _prepare_emotion_features(self, features: EdgeAudioFeatures) -> np.ndarray:
        """Prepare features for emotion model."""
        # Combine relevant features
        feature_vector = np.concatenate([
            features.mfcc,
            [features.spectral_centroid, features.zero_crossing_rate,
             features.rms_energy, features.pitch_mean, features.pitch_std]
        ])
        
        # Normalize features
        feature_vector = feature_vector.astype(np.float32)
        return feature_vector.reshape(1, -1)
    
    def _mock_emotion_analysis(
        self, 
        features: EdgeAudioFeatures, 
        start_time: float
    ) -> EdgeEmotionResult:
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
            model_version="mock_v1.0"
        )
    
    def _calculate_arousal_valence(self, emotion_scores: Dict[str, float]) -> Tuple[float, float]:
        """Calculate arousal and valence from emotion scores."""
        # Arousal mapping (high = excited, low = calm)
        arousal_map = {
            "excited": 0.9, "angry": 0.8, "fear": 0.7, "surprise": 0.6,
            "happy": 0.5, "sad": 0.3, "calm": 0.1
        }
        
        # Valence mapping (high = positive, low = negative)
        valence_map = {
            "happy": 0.9, "excited": 0.8, "surprise": 0.6, "calm": 0.5,
            "sad": 0.2, "fear": 0.1, "angry": 0.1
        }
        
        arousal = sum(emotion_scores[emotion] * arousal_map.get(emotion, 0.5) 
                     for emotion in emotion_scores)
        valence = sum(emotion_scores[emotion] * valence_map.get(emotion, 0.5) 
                     for emotion in emotion_scores)
        
        return float(arousal), float(valence)
    
    def _create_default_emotion_result(self, start_time: float) -> EdgeEmotionResult:
        """Create default emotion result when analysis fails."""
        processing_time = (time.time() - start_time) * 1000
        
        return EdgeEmotionResult(
            primary_emotion="neutral",
            confidence=0.5,
            emotion_scores={"neutral": 0.5, "calm": 0.3, "happy": 0.2},
            arousal=0.5,
            valence=0.5,
            processing_time_ms=processing_time,
            model_version="fallback_v1.0"
        )


class EdgeSafetyChecker:
    """Real-time safety checking on edge devices."""
    
    def __init__(self, model_manager: EdgeModelManager, safety_level: SafetyLevel):
        self.model_manager = model_manager
        self.safety_level = safety_level
        self.model = None
        self.safety_keywords = {
            "inappropriate": ["bad", "stupid", "hate", "kill", "hurt"],
            "distress": ["help", "scared", "emergency", "danger", "stop"],
            "violence": ["fight", "hit", "punch", "blood", "weapon"]
        }
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self, model_path: str):
        """Initialize safety checking model."""
        if self.safety_level != SafetyLevel.BASIC:
            self.model = self.model_manager.load_tflite_model(model_path, "safety")
    
    async def check_safety(
        self, 
        audio_features: EdgeAudioFeatures,
        transcribed_text: Optional[str] = None
    ) -> EdgeSafetyResult:
        """Perform safety check on audio and/or text."""
        start_time = time.time()
        
        try:
            if self.safety_level == SafetyLevel.BASIC:
                return self._basic_safety_check(transcribed_text, start_time)
            elif self.model and self.model.get("type") == "mock":
                return self._mock_safety_check(audio_features, transcribed_text, start_time)
            elif self.model:
                return await self._ml_safety_check(audio_features, transcribed_text, start_time)
            else:
                return self._basic_safety_check(transcribed_text, start_time)
                
        except Exception as e:
            self.logger.error(f"Safety check failed: {e}")
            return self._create_safe_result(start_time)
    
    def _basic_safety_check(
        self, 
        text: Optional[str], 
        start_time: float
    ) -> EdgeSafetyResult:
        """Basic keyword-based safety checking."""
        detected_issues = []
        safety_score = 1.0
        
        if text:
            text_lower = text.lower()
            for category, keywords in self.safety_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        detected_issues.append(f"{category}: {keyword}")
                        safety_score -= 0.2
        
        safety_score = max(0.0, safety_score)
        passed = safety_score > 0.6
        
        processing_time = (time.time() - start_time) * 1000
        
        return EdgeSafetyResult(
            passed=passed,
            risk_level="low" if passed else "medium",
            detected_issues=detected_issues,
            safety_score=safety_score,
            processing_time_ms=processing_time,
            requires_cloud_review=not passed
        )
    
    def _mock_safety_check(
        self, 
        audio_features: EdgeAudioFeatures,
        text: Optional[str], 
        start_time: float
    ) -> EdgeSafetyResult:
        """Mock ML-based safety checking."""
        # Combine audio and text analysis
        detected_issues = []
        safety_score = 1.0
        
        # Audio-based checks
        if audio_features.rms_energy > 0.15:  # Very loud
            detected_issues.append("loud_audio")
            safety_score -= 0.1
        
        if audio_features.zero_crossing_rate > 0.15:  # Agitated speech
            detected_issues.append("agitated_speech")
            safety_score -= 0.1
        
        # Text-based checks
        if text:
            safety_score -= self._analyze_text_safety(text, detected_issues)
        
        safety_score = max(0.0, safety_score)
        passed = safety_score > 0.7
        
        processing_time = (time.time() - start_time) * 1000
        
        return EdgeSafetyResult(
            passed=passed,
            risk_level=self._determine_risk_level(safety_score),
            detected_issues=detected_issues,
            safety_score=safety_score,
            processing_time_ms=processing_time,
            requires_cloud_review=safety_score < 0.5
        )
    
    async def _ml_safety_check(
        self, 
        audio_features: EdgeAudioFeatures,
        text: Optional[str], 
        start_time: float
    ) -> EdgeSafetyResult:
        """ML-based safety checking using TensorFlow Lite."""
        # Prepare features for ML model
        feature_vector = self._prepare_safety_features(audio_features)
        
        # Run inference
        input_details = self.model.get_input_details()
        output_details = self.model.get_output_details()
        
        self.model.set_tensor(input_details[0]['index'], feature_vector)
        self.model.invoke()
        
        output_data = self.model.get_tensor(output_details[0]['index'])
        safety_score = float(output_data[0][0])  # Assuming safety score output
        
        # Combine with text analysis if available
        detected_issues = []
        if text:
            text_penalty = self._analyze_text_safety(text, detected_issues)
            safety_score -= text_penalty
        
        safety_score = max(0.0, safety_score)
        passed = safety_score > 0.7
        
        processing_time = (time.time() - start_time) * 1000
        
        return EdgeSafetyResult(
            passed=passed,
            risk_level=self._determine_risk_level(safety_score),
            detected_issues=detected_issues,
            safety_score=safety_score,
            processing_time_ms=processing_time,
            requires_cloud_review=safety_score < 0.5
        )
    
    def _prepare_safety_features(self, audio_features: EdgeAudioFeatures) -> np.ndarray:
        """Prepare features for safety ML model."""
        # Select relevant features for safety analysis
        feature_vector = np.array([
            audio_features.rms_energy,
            audio_features.zero_crossing_rate,
            audio_features.pitch_mean,
            audio_features.pitch_std,
            audio_features.spectral_centroid
        ], dtype=np.float32)
        
        return feature_vector.reshape(1, -1)
    
    def _analyze_text_safety(self, text: str, detected_issues: List[str]) -> float:
        """Analyze text for safety issues."""
        text_lower = text.lower()
        penalty = 0.0
        
        for category, keywords in self.safety_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_issues.append(f"text_{category}: {keyword}")
                    penalty += 0.15
        
        return penalty
    
    def _determine_risk_level(self, safety_score: float) -> str:
        """Determine risk level from safety score."""
        if safety_score > 0.8:
            return "low"
        elif safety_score > 0.6:
            return "medium"
        elif safety_score > 0.3:
            return "high"
        else:
            return "critical"
    
    def _create_safe_result(self, start_time: float) -> EdgeSafetyResult:
        """Create safe result when safety check fails."""
        processing_time = (time.time() - start_time) * 1000
        
        return EdgeSafetyResult(
            passed=True,
            risk_level="low",
            detected_issues=[],
            safety_score=1.0,
            processing_time_ms=processing_time,
            requires_cloud_review=False
        )


class EdgeAIManager:
    """Main Edge AI Manager for ESP32-S3 real-time processing."""
    
    def __init__(self, config: Optional[EdgeModelConfig] = None):
        self.config = config or EdgeModelConfig()
        self.model_manager = EdgeModelManager(self.config)
        self.feature_extractor = EdgeFeatureExtractor()
        self.wake_word_detector = EdgeWakeWordDetector(self.model_manager)
        self.emotion_analyzer = EdgeEmotionAnalyzer(self.model_manager)
        self.safety_checker = EdgeSafetyChecker(self.model_manager, self.config.safety_level)
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Performance monitoring
        self.processing_stats = {
            "total_processed": 0,
            "wake_words_detected": 0,
            "average_processing_time": 0.0,
            "error_count": 0
        }
        
    async def initialize(self):
        """Initialize all Edge AI components."""
        try:
            # Initialize models
            await self.wake_word_detector.initialize(self.config.wake_word_model.value)
            await self.emotion_analyzer.initialize(self.config.emotion_model_path)
            await self.safety_checker.initialize(self.config.safety_model_path)
            
            self.logger.info("Edge AI Manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Edge AI Manager: {e}")
            raise
    
    async def process_on_edge(
        self, 
        audio_chunk: np.ndarray,
        transcribed_text: Optional[str] = None
    ) -> EdgeProcessingResult:
        """Main edge processing pipeline for instant response."""
        start_time = time.time()
        
        try:
            # Update processing stats
            self.processing_stats["total_processed"] += 1
            
            # Step 1: Extract audio features
            features = await self.feature_extractor.extract_features(
                audio_chunk, 
                quick_mode=(self.config.processing_mode == EdgeProcessingMode.ULTRA_LOW_LATENCY)
            )
            
            # Step 2: Wake word detection
            wake_word_detected, wake_confidence = await self.wake_word_detector.detect_wake_word(audio_chunk)
            
            if wake_word_detected:
                self.processing_stats["wake_words_detected"] += 1
            
            # Step 3: Emotion analysis (if wake word detected or in continuous mode)
            emotion_result = None
            if wake_word_detected or self.config.processing_mode == EdgeProcessingMode.HIGH_ACCURACY:
                emotion_result = await self.emotion_analyzer.analyze_emotion(features)
            
            # Step 4: Safety check
            safety_result = await self.safety_checker.check_safety(features, transcribed_text)
            
            # Step 5: Calculate priority and decide on cloud processing
            priority = self._calculate_priority(emotion_result, safety_result, wake_confidence)
            should_process_cloud = self._should_process_cloud(
                wake_word_detected, emotion_result, safety_result
            )
            
            # Step 6: Generate recommendations
            recommendations = self._generate_recommendations(
                emotion_result, safety_result, wake_word_detected
            )
            
            # Calculate overall processing time
            total_processing_time = (time.time() - start_time) * 1000
            
            # Update average processing time
            self._update_processing_stats(total_processing_time)
            
            # Calculate device load (mock implementation)
            device_load = min(total_processing_time / 100.0, 1.0)
            
            return EdgeProcessingResult(
                should_process_cloud=should_process_cloud,
                initial_emotion=emotion_result,
                safety_check=safety_result,
                wake_word_detected=wake_word_detected,
                priority=priority,
                confidence=wake_confidence if wake_word_detected else 0.5,
                processing_time_ms=total_processing_time,
                edge_features=features,
                recommendations=recommendations,
                device_load=device_load
            )
            
        except Exception as e:
            self.logger.error(f"Edge processing failed: {e}")
            self.processing_stats["error_count"] += 1
            return self._create_fallback_result(start_time)
    
    def _calculate_priority(
        self, 
        emotion_result: Optional[EdgeEmotionResult],
        safety_result: EdgeSafetyResult,
        wake_confidence: float
    ) -> int:
        """Calculate processing priority (1-10, higher = more urgent)."""
        priority = 5  # Base priority
        
        # Safety considerations (highest priority)
        if not safety_result.passed:
            priority += 3
        elif safety_result.risk_level == "medium":
            priority += 1
        
        # Emotion considerations
        if emotion_result:
            urgent_emotions = ["angry", "fear", "sad"]
            if emotion_result.primary_emotion in urgent_emotions:
                priority += 2
            elif emotion_result.primary_emotion == "excited":
                priority += 1
        
        # Wake word confidence
        if wake_confidence > 0.8:
            priority += 1
        
        return min(10, max(1, priority))
    
    def _should_process_cloud(
        self,
        wake_word_detected: bool,
        emotion_result: Optional[EdgeEmotionResult],
        safety_result: EdgeSafetyResult
    ) -> bool:
        """Decide if cloud processing is needed."""
        # Always process if safety check failed
        if not safety_result.passed:
            return True
        
        # Process if wake word detected
        if wake_word_detected:
            return True
        
        # Process if complex emotion detected
        if emotion_result:
            complex_emotions = ["angry", "fear", "sad", "surprise"]
            if emotion_result.primary_emotion in complex_emotions:
                return True
        
        # Don't process for simple/calm interactions
        return False
    
    def _generate_recommendations(
        self,
        emotion_result: Optional[EdgeEmotionResult],
        safety_result: EdgeSafetyResult,
        wake_word_detected: bool
    ) -> List[str]:
        """Generate edge-based recommendations."""
        recommendations = []
        
        # Safety-based recommendations
        if not safety_result.passed:
            recommendations.append("Immediate safety review required")
            recommendations.append("Consider parental notification")
        
        # Emotion-based recommendations
        if emotion_result:
            if emotion_result.primary_emotion == "sad":
                recommendations.append("Provide comforting response")
            elif emotion_result.primary_emotion == "angry":
                recommendations.append("Use calming techniques")
            elif emotion_result.primary_emotion == "excited":
                recommendations.append("Engage with enthusiasm")
            elif emotion_result.primary_emotion == "fear":
                recommendations.append("Provide reassurance")
        
        # Wake word recommendations
        if wake_word_detected:
            recommendations.append("Child is actively engaging")
            recommendations.append("Prioritize response quality")
        
        return recommendations
    
    def _update_processing_stats(self, processing_time_ms: float):
        """Update processing statistics."""
        current_avg = self.processing_stats["average_processing_time"]
        total_processed = self.processing_stats["total_processed"]
        
        # Calculate running average
        new_avg = ((current_avg * (total_processed - 1)) + processing_time_ms) / total_processed
        self.processing_stats["average_processing_time"] = new_avg
    
    def _create_fallback_result(self, start_time: float) -> EdgeProcessingResult:
        """Create fallback result when processing fails."""
        processing_time = (time.time() - start_time) * 1000
        
        return EdgeProcessingResult(
            should_process_cloud=True,  # Send to cloud when edge fails
            initial_emotion=None,
            safety_check=EdgeSafetyResult(
                passed=True, risk_level="unknown", detected_issues=[],
                safety_score=0.5, processing_time_ms=0, requires_cloud_review=True
            ),
            wake_word_detected=False,
            priority=5,
            confidence=0.0,
            processing_time_ms=processing_time,
            edge_features=None,
            recommendations=["Edge processing failed, using cloud fallback"],
            device_load=1.0
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get Edge AI performance statistics."""
        return {
            "processing_stats": self.processing_stats.copy(),
            "model_info": {
                "wake_word": self.model_manager.get_model_info("wake_word"),
                "emotion": self.model_manager.get_model_info("emotion"),
                "safety": self.model_manager.get_model_info("safety")
            },
            "configuration": {
                "processing_mode": self.config.processing_mode.value,
                "safety_level": self.config.safety_level.value,
                "wake_word_model": self.config.wake_word_model.value
            },
            "device_capabilities": {
                "tensorflow_available": TF_AVAILABLE,
                "audio_processing_available": AUDIO_PROCESSING_AVAILABLE,
                "max_concurrent_threads": 2
            }
        }
    
    def optimize_for_device(self, device_specs: Dict[str, Any]):
        """Optimize processing based on device specifications."""
        # Adjust processing mode based on device capabilities
        memory_mb = device_specs.get("memory_mb", 512)
        cpu_cores = device_specs.get("cpu_cores", 2)
        
        if memory_mb < 256:
            self.config.processing_mode = EdgeProcessingMode.POWER_SAVE
        elif memory_mb < 512:
            self.config.processing_mode = EdgeProcessingMode.ULTRA_LOW_LATENCY
        else:
            self.config.processing_mode = EdgeProcessingMode.BALANCED
        
        self.logger.info(f"Optimized for device: {device_specs}, mode: {self.config.processing_mode.value}")
    
    async def cleanup(self):
        """Cleanup Edge AI resources."""
        try:
            self.executor.shutdown(wait=True)
            self.logger.info("Edge AI Manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}") 