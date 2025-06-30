"""
Professional Audio Processing Engine for AI Teddy Bear
Enterprise-grade audio enhancement with noise reduction and voice optimization
"""

import time
import platform
import psutil
import numpy as np
import structlog

# Audio processing imports with graceful fallbacks
try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️ librosa not available. Install with: pip install librosa")

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False
    print("⚠️ noisereduce not available. Install with: pip install noisereduce")

try:
    from scipy import signal
    from scipy.signal import butter, filtfilt
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️ scipy not available. Install with: pip install scipy")

logger = structlog.get_logger()


class AudioProcessingEngine:
    """Professional audio processing engine with noise reduction and voice enhancement"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.performance_mode = self._detect_system_performance()
        self.processing_stats = {}
        
        logger.info("Audio processing engine initialized", 
                   performance_mode=self.performance_mode,
                   librosa_available=LIBROSA_AVAILABLE,
                   noisereduce_available=NOISEREDUCE_AVAILABLE,
                   scipy_available=SCIPY_AVAILABLE)
    
    def _detect_system_performance(self) -> str:
        """Detect system performance level for optimization"""
        try:
            cpu_count = psutil.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            if cpu_count >= 8 and memory_gb >= 16:
                return "high"
            elif cpu_count >= 4 and memory_gb >= 8:
                return "medium"
            else:
                return "low"
                
        except Exception:
            logger.warning("Could not detect system performance, using medium mode")
            return "medium"
    
    def process_audio(self, audio_data: np.ndarray, processing_level: str = "auto") -> tuple:
        """Process audio with comprehensive enhancement"""
        start_time = time.time()
        
        if processing_level == "auto":
            processing_level = self.performance_mode
        
        processing_info = {
            "original_length": len(audio_data),
            "sample_rate": self.sample_rate,
            "processing_level": processing_level,
            "steps_applied": []
        }
        
        try:
            processed_audio = self._normalize_audio(audio_data)
            processing_info["steps_applied"].append("normalization")
            
            if processing_level in ["medium", "high"] and NOISEREDUCE_AVAILABLE:
                processed_audio = self._reduce_noise(processed_audio, processing_level)
                processing_info["steps_applied"].append("noise_reduction")
            
            if processing_level in ["medium", "high"] and SCIPY_AVAILABLE:
                processed_audio = self._enhance_voice(processed_audio, processing_level)
                processing_info["steps_applied"].append("voice_enhancement")
            
            if processing_level == "high" and LIBROSA_AVAILABLE:
                processed_audio = self._advanced_processing(processed_audio)
                processing_info["steps_applied"].append("advanced_processing")
            
            processed_audio = self._final_normalization(processed_audio)
            processing_info["steps_applied"].append("final_normalization")
            
            processing_time = time.time() - start_time
            processing_info.update({
                "processing_time": processing_time,
                "final_length": len(processed_audio),
                "quality_improvement": self._calculate_quality_improvement(audio_data, processed_audio)
            })
            
            logger.info("Audio processing completed", **processing_info)
            return processed_audio, processing_info
            
        except Exception as e:
            logger.error("Audio processing failed", error=str(e))
            processing_info["error"] = str(e)
            return audio_data, processing_info
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Basic audio normalization"""
        if np.max(np.abs(audio)) > 0:
            return audio / np.max(np.abs(audio)) * 0.8
        return audio
    
    def _reduce_noise(self, audio: np.ndarray, level: str) -> np.ndarray:
        """Advanced noise reduction using noisereduce"""
        try:
            if level == "medium":
                reduced_audio = nr.reduce_noise(
                    y=audio, 
                    sr=self.sample_rate,
                    prop_decrease=0.6,
                    stationary=True
                )
            else:  # high
                reduced_audio = nr.reduce_noise(
                    y=audio, 
                    sr=self.sample_rate,
                    prop_decrease=0.8,
                    stationary=False,
                    use_torch=False
                )
            
            return reduced_audio
            
        except Exception as e:
            logger.warning("Noise reduction failed, using original", error=str(e))
            return audio
    
    def _enhance_voice(self, audio: np.ndarray, level: str) -> np.ndarray:
        """Voice enhancement using frequency filtering"""
        try:
            nyquist = self.sample_rate / 2
            
            if level == "medium":
                low_cutoff = 80 / nyquist
                high_cutoff = 4000 / nyquist
                b, a = butter(4, [low_cutoff, high_cutoff], btype='band')
            else:  # high
                low_cutoff = 60 / nyquist
                high_cutoff = 6000 / nyquist
                b, a = butter(6, [low_cutoff, high_cutoff], btype='band')
            
            filtered_audio = filtfilt(b, a, audio)
            
            speech_low = 1000 / nyquist
            speech_high = 3000 / nyquist
            b_speech, a_speech = butter(2, [speech_low, speech_high], btype='band')
            speech_enhanced = filtfilt(b_speech, a_speech, audio)
            
            enhanced_audio = filtered_audio + (speech_enhanced * 0.3)
            
            return enhanced_audio
            
        except Exception as e:
            logger.warning("Voice enhancement failed, using original", error=str(e))
            return audio
    
    def _advanced_processing(self, audio: np.ndarray) -> np.ndarray:
        """Advanced processing using librosa"""
        try:
            harmonic, percussive = librosa.effects.hpss(audio)
            processed_audio = harmonic + (percussive * 0.1)
            processed_audio = self._dynamic_range_compression(processed_audio)
            
            return processed_audio
            
        except Exception as e:
            logger.warning("Advanced processing failed, using original", error=str(e))
            return audio
    
    def _dynamic_range_compression(self, audio: np.ndarray, ratio: float = 4.0) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            threshold = 0.1
            audio_abs = np.abs(audio)
            above_threshold = audio_abs > threshold
            
            compressed = audio.copy()
            compressed[above_threshold] = np.sign(audio[above_threshold]) * (
                threshold + (audio_abs[above_threshold] - threshold) / ratio
            )
            
            return compressed
            
        except Exception as e:
            logger.warning("Dynamic range compression failed", error=str(e))
            return audio
    
    def _final_normalization(self, audio: np.ndarray) -> np.ndarray:
        """Final normalization with clipping prevention"""
        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            target_rms = 0.15
            audio = audio * (target_rms / rms)
        
        audio = np.clip(audio, -0.95, 0.95)
        return audio
    
    def _calculate_quality_improvement(self, original: np.ndarray, processed: np.ndarray) -> dict:
        """Calculate quality improvement metrics"""
        try:
            original_rms = np.sqrt(np.mean(original**2))
            processed_rms = np.sqrt(np.mean(processed**2))
            
            original_dynamic_range = np.max(np.abs(original)) - np.min(np.abs(original))
            processed_dynamic_range = np.max(np.abs(processed)) - np.min(np.abs(processed))
            
            return {
                "rms_ratio": processed_rms / (original_rms + 1e-10),
                "dynamic_range_improvement": processed_dynamic_range / (original_dynamic_range + 1e-10),
                "peak_reduction": np.max(np.abs(original)) / (np.max(np.abs(processed)) + 1e-10)
            }
            
        except Exception:
            return {"error": "Could not calculate quality metrics"}
    
    def clean_audio(self, input_audio: np.ndarray, processing_level: str = "auto") -> tuple:
        """Main function for cleaning and enhancing audio"""
        return self.process_audio(input_audio, processing_level)
    
    def get_processing_capabilities(self) -> dict:
        """Get available processing capabilities"""
        return {
            "performance_mode": self.performance_mode,
            "librosa_available": LIBROSA_AVAILABLE,
            "noisereduce_available": NOISEREDUCE_AVAILABLE,
            "scipy_available": SCIPY_AVAILABLE,
            "recommended_level": self.performance_mode,
            "max_processing_time": {
                "low": "< 1 second",
                "medium": "< 3 seconds", 
                "high": "< 10 seconds"
            }[self.performance_mode]
        } 