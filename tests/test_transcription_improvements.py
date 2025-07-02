"""
🧪 اختبارات شاملة لتحسينات خدمة النسخ الصوتي
Testing the improved transcription service for AI Teddy Bear
"""

import pytest
import numpy as np
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Import our improved classes
from src.application.services.core.transcription_service import (
    TranscriptionConfig,
    AudioProcessor,
    ModernTranscriptionService,
    AudioFormat,
    ProcessingState
)


class TestTranscriptionConfig:
    """🔧 اختبار إعدادات النسخ المحسنة"""
    
    def test_device_selection_cuda_available(self):
        """اختبار اختيار CUDA عند توفره"""
        config = TranscriptionConfig(use_gpu=True)
        
        with patch('torch.cuda.is_available', return_value=True):
            assert config.device == "cuda"
    
    def test_device_selection_mps_available(self):
        """اختبار اختيار MPS (Apple Silicon) عند توفره"""
        config = TranscriptionConfig(use_gpu=True)
        
        with patch('torch.cuda.is_available', return_value=False), \
             patch('torch.backends.mps.is_available', return_value=True):
            
            # Mock torch.backends to have mps attribute
            with patch('torch.backends', Mock()):
                torch_backends_mock = Mock()
                torch_backends_mock.mps.is_available.return_value = True
                
                with patch('torch.backends', torch_backends_mock):
                    assert config.device == "mps"
    
    def test_device_selection_cpu_fallback(self):
        """اختبار الرجوع لـ CPU عند عدم توفر GPU"""
        config = TranscriptionConfig(use_gpu=False)
        assert config.device == "cpu"
    
    def test_should_use_cuda_method(self):
        """اختبار دالة _should_use_cuda المنفصلة"""
        config = TranscriptionConfig(use_gpu=True)
        
        with patch('torch.cuda.is_available', return_value=True):
            assert config._should_use_cuda() is True
        
        with patch('torch.cuda.is_available', return_value=False):
            assert config._should_use_cuda() is False
    
    def test_should_use_mps_method(self):
        """اختبار دالة _should_use_mps المنفصلة"""
        config = TranscriptionConfig(use_gpu=True)
        
        # Mock successful MPS detection
        torch_backends_mock = Mock()
        torch_backends_mock.mps.is_available.return_value = True
        
        with patch('torch.backends', torch_backends_mock):
            assert config._should_use_mps() is True


class TestAudioProcessor:
    """🎛️ اختبار معالج الصوت المحسن"""
    
    def setup_method(self):
        """إعداد للاختبارات"""
        self.config = TranscriptionConfig()
        self.processor = AudioProcessor(self.config)
    
    def test_get_audio_format_caching(self):
        """اختبار تخزين نتائج تحديد نوع الصوت"""
        # Test caching functionality
        format1 = self.processor.get_audio_format("str", False)
        format2 = self.processor.get_audio_format("str", False)
        
        assert format1 == AudioFormat.FILE_PATH
        assert format1 is format2  # Should be cached
    
    def test_get_audio_format_types(self):
        """اختبار تحديد أنواع البيانات الصوتية المختلفة"""
        assert self.processor.get_audio_format("str") == AudioFormat.FILE_PATH
        assert self.processor.get_audio_format("bytes") == AudioFormat.BYTES_DATA
        assert self.processor.get_audio_format("ndarray") == AudioFormat.NUMPY_ARRAY
        assert self.processor.get_audio_format("unknown") == AudioFormat.UNKNOWN
    
    @pytest.mark.asyncio
    async def test_process_with_fallback_success(self):
        """اختبار المعالجة الناجحة بدون استخدام الطريقة الاحتياطية"""
        test_audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        # Mock successful processing
        with patch.object(self.processor, '_process_primary_method', 
                         return_value=test_audio) as mock_primary:
            
            result = await self.processor.process_with_fallback(test_audio)
            
            mock_primary.assert_called_once()
            np.testing.assert_array_equal(result, test_audio)
    
    @pytest.mark.asyncio
    async def test_process_with_fallback_error(self):
        """اختبار استخدام الطريقة الاحتياطية عند فشل الأساسية"""
        test_audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        fallback_result = np.array([0.4, 0.5, 0.6], dtype=np.float32)
        
        # Mock primary method failure and fallback success
        with patch.object(self.processor, '_process_primary_method', 
                         side_effect=Exception("Primary failed")) as mock_primary, \
             patch.object(self.processor, '_process_fallback_method', 
                         return_value=fallback_result) as mock_fallback:
            
            result = await self.processor.process_with_fallback(test_audio)
            
            mock_primary.assert_called_once()
            mock_fallback.assert_called_once()
            np.testing.assert_array_equal(result, fallback_result)
    
    def test_process_array_optimized_stereo_to_mono(self):
        """اختبار تحويل الصوت من ستيريو إلى مونو"""
        # Test channels-first format (2, 100)
        stereo_audio = np.random.randn(2, 100).astype(np.float32)
        result = self.processor._process_array_optimized(stereo_audio)
        
        assert result.ndim == 1
        assert len(result) == 100
        
        # Test samples-first format (100, 2)
        stereo_audio = np.random.randn(100, 2).astype(np.float32)
        result = self.processor._process_array_optimized(stereo_audio)
        
        assert result.ndim == 1
        assert len(result) == 100
    
    def test_convert_bytes_optimized_empty_input(self):
        """اختبار التعامل مع البيانات الفارغة"""
        with pytest.raises(ValueError, match="Empty audio bytes"):
            self.processor._convert_bytes_optimized(b"")
    
    def test_process_array_optimized_empty_input(self):
        """اختبار التعامل مع الصوت الفارغ"""
        with pytest.raises(ValueError, match="Empty audio array"):
            self.processor._process_array_optimized(np.array([]))


class TestModernTranscriptionService:
    """🎯 اختبار خدمة النسخ المحسنة"""
    
    def setup_method(self):
        """إعداد للاختبارات"""
        self.config = TranscriptionConfig()
        self.service = ModernTranscriptionService(self.config)
    
    def test_initialization_with_audio_processor(self):
        """اختبار التهيئة مع معالج الصوت"""
        assert self.service.audio_processor is not None
        assert isinstance(self.service.audio_processor, AudioProcessor)
        assert "fallback_usage" in self.service.stats
    
    @pytest.mark.asyncio
    async def test_prepare_audio_with_processor(self):
        """اختبار استخدام AudioProcessor في إعداد الصوت"""
        test_audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        # Mock audio processor
        with patch.object(self.service.audio_processor, 'process_with_fallback',
                         return_value=test_audio) as mock_processor:
            
            result = await self.service._prepare_audio(test_audio)
            
            mock_processor.assert_called_once()
            assert isinstance(result, np.ndarray)
    
    @pytest.mark.asyncio
    async def test_emergency_fallback_usage(self):
        """اختبار استخدام الطريقة الطارئة عند فشل كل شيء"""
        test_audio = "test_file.wav"
        
        # Mock complete failure
        with patch.object(self.service.audio_processor, 'process_with_fallback',
                         side_effect=Exception("Complete failure")):
            
            result = await self.service._prepare_audio(test_audio)
            
            assert isinstance(result, np.ndarray)
            assert self.service.stats["error_count"] > 0
            assert self.service.stats["fallback_usage"] > 0
    
    def test_finalize_audio_quality(self):
        """اختبار تحسين جودة الصوت النهائية"""
        # Test with audio that needs normalization
        loud_audio = np.array([2.0, -2.0, 1.5], dtype=np.float32)
        result = self.service._finalize_audio_quality(loud_audio)
        
        # Should be normalized to prevent saturation
        assert np.max(np.abs(result)) <= 0.95
    
    def test_trim_silence(self):
        """اختبار إزالة الصمت من بداية ونهاية التسجيل"""
        # Create audio with silence at start and end
        sample_rate = self.config.sample_rate
        margin_samples = int(0.1 * sample_rate)
        
        # Silent start + speech + silent end
        audio = np.concatenate([
            np.zeros(margin_samples),  # Silent start
            np.random.randn(sample_rate) * 0.5,  # Speech
            np.zeros(margin_samples)   # Silent end
        ]).astype(np.float32)
        
        result = self.service._trim_silence(audio, threshold=0.01)
        
        # Should be shorter than original
        assert len(result) < len(audio)
        assert len(result) > 0
    
    def test_enhanced_performance_metrics(self):
        """اختبار الإحصائيات المحسنة"""
        # Add some test data
        self.service.stats["total_transcriptions"] = 100
        self.service.stats["error_count"] = 2
        self.service.stats["fallback_usage"] = 5
        self.service.stats["total_processing_time"] = 150.0
        self.service.stats["average_confidence"] = 0.85
        
        metrics = self.service.get_performance_metrics()
        
        # Check enhanced metrics
        assert "is_child_friendly" in metrics
        assert "response_quality" in metrics
        assert "processing_speed" in metrics
        assert "fallback_rate" in metrics
        assert metrics["error_rate"] == 0.02  # 2/100
        assert metrics["fallback_rate"] == 0.05  # 5/100


class TestChildModeFeatures:
    """👶 اختبار الميزات الخاصة بالأطفال"""
    
    def setup_method(self):
        """إعداد للاختبارات"""
        self.config = TranscriptionConfig()
        self.service = ModernTranscriptionService(self.config)
    
    def test_enhance_for_children(self):
        """اختبار تحسين الصوت للأطفال"""
        test_audio = np.random.randn(1000).astype(np.float32) * 0.1
        
        enhanced = self.service._enhance_for_children(test_audio)
        
        assert isinstance(enhanced, np.ndarray)
        assert len(enhanced) == len(test_audio)
    
    def test_boost_high_frequencies(self):
        """اختبار تعزيز الترددات العالية"""
        test_audio = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float32)
        
        boosted = self.service._boost_high_frequencies(test_audio)
        
        assert len(boosted) == len(test_audio)
        assert isinstance(boosted, np.ndarray)
    
    def test_reduce_background_noise(self):
        """اختبار تقليل الضوضاء الخلفية"""
        # Create audio with noise
        signal = np.array([0.5, 0.6, 0.7], dtype=np.float32)  # Strong signal
        noise = np.array([0.01, 0.02, 0.01], dtype=np.float32)  # Weak noise
        test_audio = np.concatenate([signal, noise])
        
        filtered = self.service._reduce_background_noise(test_audio)
        
        # Noise should be reduced to zero
        assert np.sum(filtered[-3:]) < np.sum(noise)
    
    def test_normalize_for_quiet_children(self):
        """اختبار تطبيع الصوت للأطفال الهادئين"""
        # Very quiet audio (below 0.3 threshold)
        quiet_audio = np.array([0.1, 0.15, 0.2], dtype=np.float32)
        
        normalized = self.service._normalize_for_quiet_children(quiet_audio)
        
        # Should be boosted
        assert np.max(np.abs(normalized)) > np.max(np.abs(quiet_audio))
    
    def test_fix_common_child_speech_errors(self):
        """اختبار إصلاح أخطاء النطق الشائعة للأطفال"""
        test_cases = [
            ("I wike to play", "I like to play"),
            ("I wove my teddy", "I love my teddy"),
            ("Pwease tell me a story", "Please tell me a story"),
            ("My fwiend is nice", "My friend is nice"),
        ]
        
        for input_text, expected in test_cases:
            result = self.service._fix_common_child_speech_errors(input_text)
            assert result == expected
    
    def test_is_clear_child_speech(self):
        """اختبار تحديد الكلام الواضح للأطفال"""
        # Clear speech indicators
        clear_examples = [
            "Hello teddy bear I want to play",
            "Can you tell me a story please",
            "Hi there let's have fun together"
        ]
        
        unclear_examples = [
            "um... uh...",
            "[noise]",
            "a"
        ]
        
        for text in clear_examples:
            assert self.service._is_clear_child_speech(text) is True
        
        for text in unclear_examples:
            assert self.service._is_clear_child_speech(text) is False
    
    def test_post_process_child_speech(self):
        """اختبار المعالجة اللاحقة لكلام الأطفال"""
        result = {
            "text": "I wike to play with teddy",
            "confidence": 0.7
        }
        
        processed = self.service._post_process_child_speech(result)
        
        assert processed["text"] == "I like to play with teddy"
        assert processed["confidence"] > 0.7  # Should be boosted
        assert processed["child_optimized"] is True


@pytest.mark.asyncio
class TestAsyncFunctionality:
    """⚡ اختبار الوظائف غير المتزامنة"""
    
    def setup_method(self):
        """إعداد للاختبارات"""
        self.config = TranscriptionConfig()
        self.service = ModernTranscriptionService(self.config)
    
    async def test_transcribe_audio_child_mode(self):
        """اختبار النسخ في وضع الأطفال"""
        test_audio = np.random.randn(1000).astype(np.float32) * 0.1
        
        # Mock the transcription methods
        with patch.object(self.service, '_transcribe_whisper',
                         return_value={"text": "hello teddy", "confidence": 0.8}):
            
            result = await self.service.transcribe_audio(
                test_audio, 
                child_mode=True
            )
            
            assert result["child_mode"] is True
            assert "processing_time_ms" in result
    
    async def test_transcribe_audio_confidence_adjustment(self):
        """اختبار تعديل عتبة الثقة في وضع الطفل"""
        original_threshold = self.service.config.confidence_threshold
        test_audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        with patch.object(self.service, '_transcribe_whisper',
                         return_value={"text": "test", "confidence": 0.6}):
            
            await self.service.transcribe_audio(test_audio, child_mode=True)
            
            # Threshold should be restored after processing
            assert self.service.config.confidence_threshold == original_threshold


if __name__ == "__main__":
    """تشغيل الاختبارات"""
    pytest.main([__file__, "-v", "--tb=short"]) 