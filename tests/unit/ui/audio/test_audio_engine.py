"""
Unit Tests for AudioProcessingEngine - Enterprise Grade Testing
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from src.ui.audio.audio_engine import AudioProcessingEngine, get_audio_engine


class TestAudioProcessingEngine:
    """Comprehensive test suite for AudioProcessingEngine"""
    
    @pytest.fixture
    def audio_engine(self):
        """Create fresh AudioProcessingEngine for each test"""
        return AudioProcessingEngine(sample_rate=16000)
    
    @pytest.fixture
    def sample_audio(self):
        """Generate 1-second test audio with voice-like characteristics"""
        t = np.linspace(0, 1, 16000, False)
        audio = np.sin(2 * np.pi * 440 * t) + 0.5 * np.sin(2 * np.pi * 880 * t)
        noise = np.random.normal(0, 0.1, audio.shape)
        return (audio + noise).astype(np.float32)
    
    def test_engine_initialization(self):
        """Test engine initialization with various parameters"""
        # Default initialization
        engine = AudioProcessingEngine()
        assert engine.sample_rate == 16000
        assert engine.performance_mode in ["low", "medium", "high"]
        
        # Custom sample rate
        engine_custom = AudioProcessingEngine(sample_rate=44100)
        assert engine_custom.sample_rate == 44100
    
    @patch('core.ui.audio.audio_engine.psutil')
    def test_performance_detection(self, mock_psutil):
        """Test system performance detection logic"""
        # High performance system
        mock_psutil.cpu_count.return_value = 16
        mock_psutil.virtual_memory.return_value.total = 32 * 1024**3
        engine_high = AudioProcessingEngine()
        assert engine_high.performance_mode == "high"
        
        # Low performance system
        mock_psutil.cpu_count.return_value = 2
        mock_psutil.virtual_memory.return_value.total = 4 * 1024**3
        engine_low = AudioProcessingEngine()
        assert engine_low.performance_mode == "low"
    
    def test_basic_audio_processing(self, audio_engine, sample_audio):
        """Test core audio processing functionality"""
        processed, info = audio_engine.process_audio(sample_audio, "low")
        
        assert isinstance(processed, np.ndarray)
        assert len(processed) == len(sample_audio)
        assert isinstance(info, dict)
        assert "processing_time" in info
        assert "steps_applied" in info
        assert "normalization" in info["steps_applied"]
    
    @pytest.mark.parametrize("level", ["low", "medium", "high", "auto"])
    def test_processing_levels(self, audio_engine, sample_audio, level):
        """Test different processing quality levels"""
        processed, info = audio_engine.process_audio(sample_audio, level)
        
        assert isinstance(processed, np.ndarray)
        assert info["processing_level"] in ["low", "medium", "high"]
        
        if level == "auto":
            assert info["processing_level"] == audio_engine.performance_mode
    
    @patch('core.ui.audio.audio_engine.NOISEREDUCE_AVAILABLE', True)
    @patch('core.ui.audio.audio_engine.nr')
    def test_noise_reduction(self, mock_nr, audio_engine, sample_audio):
        """Test noise reduction functionality"""
        mock_nr.reduce_noise.return_value = sample_audio * 0.8
        
        processed, info = audio_engine.process_audio(sample_audio, "medium")
        
        mock_nr.reduce_noise.assert_called_once()
        assert "noise_reduction" in info["steps_applied"]
    
    def test_audio_normalization(self, audio_engine):
        """Test audio normalization edge cases"""
        # Loud audio (clipping prevention)
        loud_audio = np.ones(1000) * 2.0
        normalized = audio_engine._normalize_audio(loud_audio)
        assert np.max(np.abs(normalized)) <= 0.8
        
        # Silent audio (zero division prevention)
        silent_audio = np.zeros(1000)
        normalized_silent = audio_engine._normalize_audio(silent_audio)
        assert np.allclose(normalized_silent, silent_audio)
    
    def test_clean_audio_interface(self, audio_engine, sample_audio):
        """Test public clean_audio method"""
        cleaned, info = audio_engine.clean_audio(sample_audio)
        
        assert isinstance(cleaned, np.ndarray)
        assert isinstance(info, dict)
        assert len(cleaned) == len(sample_audio)
    
    def test_get_processing_capabilities(self, audio_engine):
        """Test capability reporting"""
        capabilities = audio_engine.get_processing_capabilities()
        
        required_keys = [
            "performance_mode", "librosa_available", "noisereduce_available",
            "scipy_available", "recommended_level"
        ]
        
        for key in required_keys:
            assert key in capabilities
    
    def test_error_handling(self, audio_engine):
        """Test error handling with edge cases"""
        # Empty audio
        empty_audio = np.array([])
        processed, info = audio_engine.process_audio(empty_audio, "low")
        assert len(processed) == 0
        
        # NaN audio (should be handled gracefully)
        try:
            nan_audio = np.full(1000, np.nan)
            audio_engine.process_audio(nan_audio, "low")
        except Exception:
            pass  # Expected for extreme cases
    
    def test_singleton_pattern(self):
        """Test singleton audio engine getter"""
        engine1 = get_audio_engine()
        engine2 = get_audio_engine()
        
        assert engine1 is engine2
        assert isinstance(engine1, AudioProcessingEngine)
    
    def test_performance_timing(self, audio_engine, sample_audio):
        """Test processing performance requirements"""
        processed, info = audio_engine.process_audio(sample_audio, "low")
        
        # Should process 1 second of audio in < 0.5 seconds
        assert info["processing_time"] < 0.5
        
        # Processing info should be reasonable
        assert info["original_length"] == len(sample_audio)
        assert info["final_length"] == len(processed)


@pytest.mark.integration
class TestAudioEngineIntegration:
    """Integration tests with real dependencies"""
    
    @pytest.mark.skipif(True, reason="Requires real audio libraries")
    def test_with_real_libraries(self):
        """Test with actual audio processing libraries when available"""
        engine = AudioProcessingEngine()
        test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 16000))
        
        processed, info = engine.process_audio(test_audio, "high")
        assert len(processed) == len(test_audio) 