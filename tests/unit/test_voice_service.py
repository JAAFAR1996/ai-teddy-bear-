"""
🧪 Unit Tests for Voice Service
Comprehensive tests for Speech-to-Text functionality
"""

import base64
import os
import struct
import wave
from io import BytesIO
from unittest.mock import Mock, patch

import pytest

# Import voice service components
from src.application.services.voice_service import (AudioFormat, AudioRequest,
                                                    STTProvider,
                                                    TranscriptionResult,
                                                    VoiceService,
                                                    VoiceServiceConfig,
                                                    WhisperModel,
                                                    create_voice_service)

# ================ TEST FIXTURES ================


@pytest.fixture
def mock_config():
    """Create mock voice service configuration"""
    return VoiceServiceConfig(
        default_provider=STTProvider.WHISPER,
        whisper_model=WhisperModel.BASE,
        azure_key=None,
        max_audio_duration=30,
        supported_formats=[AudioFormat.WAV, AudioFormat.MP3, AudioFormat.OGG],
        enable_fallback=True,
        temp_dir="./test_temp",
    )


@pytest.fixture
def voice_service(mock_config):
    """Create voice service instance for testing"""
    return VoiceService(mock_config)


@pytest.fixture
def sample_wav_data():
    """Generate sample WAV audio data"""
    # Create 1 second of 16kHz sine wave
    sample_rate = 16000
    duration = 1.0
    frequency = 440  # A4 note

    # Generate samples
    num_samples = int(sample_rate * duration)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        sample = int(16384 * math.sin(2 * math.pi * frequency * t))
        samples.append(sample)

    # Create WAV file in memory
    wav_buffer = BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack("<" + "h" * len(samples), *samples))

    return wav_buffer.getvalue()


@pytest.fixture
def sample_mp3_data():
    """Generate sample MP3 data (mock)"""
    # This is a minimal MP3 header + data for testing
    # In real tests, you'd use a proper MP3 file
    mp3_header = b"\xff\xfb\x90\x00"  # MP3 frame header
    mp3_data = mp3_header + b"\x00" * 100  # Minimal MP3 data
    return mp3_data


@pytest.fixture
def sample_audio_request():
    """Create sample audio request"""
    return AudioRequest(
        audio_data="dGVzdCBhdWRpbyBkYXRh",  # "test audio data" in base64
        format=AudioFormat.WAV,
        device_id="TEST_ESP32_001",
        session_id="test_session_123",
        language="ar",
        child_name="أحمد",
        child_age=6,
    )


# ================ BASIC FUNCTIONALITY TESTS ================


class TestVoiceServiceInitialization:
    """Test voice service initialization"""

    def test_service_creation_with_default_config(self):
        """Test creating service with default configuration"""
        service = VoiceService()

        assert service.config.default_provider == STTProvider.WHISPER
        assert service.config.whisper_model == WhisperModel.BASE
        assert service.config.max_audio_duration == 30
        assert AudioFormat.WAV in service.config.supported_formats

    def test_service_creation_with_custom_config(self, mock_config):
        """Test creating service with custom configuration"""
        service = VoiceService(mock_config)

        assert service.config.default_provider == STTProvider.WHISPER
        assert service.config.temp_dir == "./test_temp"
        assert service.config.enable_fallback is True

    def test_factory_function(self):
        """Test factory function creates service correctly"""
        with patch.dict(
            os.environ,
            {
                "STT_PROVIDER": "whisper",
                "WHISPER_MODEL": "small",
                "MAX_AUDIO_DURATION": "60",
            },
        ):
            service = create_voice_service()

            assert isinstance(service, VoiceService)
            assert service.config.whisper_model == WhisperModel.SMALL
            assert service.config.max_audio_duration == 60


class TestAudioFormatHandling:
    """Test audio format conversion and handling"""

    @pytest.mark.asyncio
    async def test_wav_duration_calculation(self, voice_service, sample_wav_data):
        """Test WAV duration calculation"""
        duration = voice_service._get_wav_duration(sample_wav_data)

        # Should be approximately 1 second
        assert 0.9 <= duration <= 1.1

    @pytest.mark.asyncio
    async def test_wav_passthrough(self, voice_service, sample_wav_data):
        """Test WAV audio passes through without conversion"""
        wav_data, duration = await voice_service._convert_to_wav(
            sample_wav_data, AudioFormat.WAV
        )

        assert wav_data == sample_wav_data
        assert 0.9 <= duration <= 1.1

    @pytest.mark.asyncio
    @patch("src.application.services.voice_service.PYDUB_AVAILABLE", True)
    async def test_mp3_to_wav_conversion_with_pydub(
        self, voice_service, sample_mp3_data
    ):
        """Test MP3 to WAV conversion using pydub"""
        with patch("src.application.services.voice_service.AudioSegment") as mock_audio:
            # Mock pydub conversion
            mock_segment = Mock()
            mock_segment.set_frame_rate.return_value = mock_segment
            mock_segment.set_channels.return_value = mock_segment
            mock_segment.set_sample_width.return_value = mock_segment
            mock_segment.__len__.return_value = 1000  # 1 second in ms

            mock_audio.from_file.return_value = mock_segment
            mock_segment.export.return_value = None

            # Mock the WAV export
            with patch("builtins.open", create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.getvalue.return_value = (
                    b"wav_data"
                )

                wav_data, duration = await voice_service._convert_with_pydub(
                    sample_mp3_data, AudioFormat.MP3
                )

                assert duration == 1.0
                mock_audio.from_file.assert_called_once()


# ================ TRANSCRIPTION TESTS ================


class TestTranscriptionFunctionality:
    """Test core transcription functionality"""

    @pytest.mark.asyncio
    async def test_transcribe_audio_with_base64_input(
        self, voice_service, sample_wav_data
    ):
        """Test transcription with base64 encoded audio"""
        # Encode audio to base64
        audio_base64 = base64.b64encode(sample_wav_data).decode("utf-8")

        # Mock the transcription provider
        with patch.object(
            voice_service, "_transcribe_with_provider"
        ) as mock_transcribe:
            mock_transcribe.return_value = ("مرحباً دبدوب", 0.9, [], {"test": True})

            result = await voice_service.transcribe_audio(
                audio_data=audio_base64, format=AudioFormat.WAV, language="ar"
            )

            assert isinstance(result, TranscriptionResult)
            assert result.text == "مرحباً دبدوب"
            assert result.confidence == 0.9
            assert result.language == "ar"
            assert result.provider in ["whisper", "fallback"]

    @pytest.mark.asyncio
    async def test_transcribe_audio_with_bytes_input(
        self, voice_service, sample_wav_data
    ):
        """Test transcription with raw bytes"""
        with patch.object(
            voice_service, "_transcribe_with_provider"
        ) as mock_transcribe:
            mock_transcribe.return_value = ("أهلاً وسهلاً", 0.85, [], {})

            result = await voice_service.transcribe_audio(
                audio_data=sample_wav_data, format=AudioFormat.WAV, language="ar"
            )

            assert result.text == "أهلاً وسهلاً"
            assert result.confidence == 0.85

    @pytest.mark.asyncio
    async def test_transcribe_empty_audio_returns_fallback(self, voice_service):
        """Test transcription with empty audio returns fallback"""
        result = await voice_service.transcribe_audio(
            audio_data=b"", format=AudioFormat.WAV
        )

        assert result.text == "مرحباً دبدوب"  # Fallback text
        assert result.confidence == 0.0
        assert result.provider == "fallback"
        assert "error" in result.metadata

    @pytest.mark.asyncio
    async def test_transcribe_invalid_base64_returns_fallback(self, voice_service):
        """Test transcription with invalid base64 returns fallback"""
        result = await voice_service.transcribe_audio(
            audio_data="invalid_base64_!@#$", format=AudioFormat.WAV
        )

        assert result.provider == "fallback"
        assert "error" in result.metadata

    @pytest.mark.asyncio
    async def test_transcribe_audio_too_long_raises_error(self, voice_service):
        """Test transcription fails for audio exceeding duration limit"""
        # Mock a very long audio duration
        with patch.object(voice_service, "_convert_to_wav") as mock_convert:
            mock_convert.return_value = (b"wav_data", 60.0)  # 60 seconds

            result = await voice_service.transcribe_audio(
                audio_data=b"test_data", format=AudioFormat.WAV
            )

            # Should return fallback due to duration error
            assert result.provider == "fallback"
            assert "error" in result.metadata


class TestMockTranscription:
    """Test mock transcription provider"""

    @pytest.mark.asyncio
    async def test_mock_transcription_returns_arabic_text(self, voice_service):
        """Test mock transcription returns appropriate Arabic text"""
        text, confidence, segments, metadata = await voice_service._transcribe_mock(
            b"test_audio", "ar"
        )

        assert isinstance(text, str)
        assert len(text) > 0
        assert 0.0 <= confidence <= 1.0
        assert isinstance(segments, list)
        assert metadata["provider"] == "mock"
        assert metadata["simulated"] is True

        # Should be Arabic text
        arabic_words = ["مرحباً", "دبدوب", "أريد", "احكِ", "أحبك", "ما"]
        assert any(word in text for word in arabic_words)


# ================ ESP32 SPECIFIC TESTS ================


class TestESP32AudioProcessing:
    """Test ESP32-specific audio processing"""

    @pytest.mark.asyncio
    async def test_process_esp32_audio_request(
        self, voice_service, sample_audio_request
    ):
        """Test processing ESP32 audio request"""
        with patch.object(voice_service, "transcribe_audio") as mock_transcribe:
            mock_result = TranscriptionResult(
                text="مرحباً يا أحمد",
                language="ar",
                confidence=0.9,
                provider="whisper",
                processing_time_ms=500,
                audio_duration_ms=2000,
                segments=[],
                metadata={},
            )
            mock_transcribe.return_value = mock_result

            result = await voice_service.process_esp32_audio(sample_audio_request)

            assert result.text == "مرحباً يا أحمد"
            assert result.metadata["device_id"] == "TEST_ESP32_001"
            assert result.metadata["child_name"] == "أحمد"
            assert result.metadata["child_age"] == 6
            assert result.metadata["source"] == "esp32"

    @pytest.mark.asyncio
    async def test_esp32_audio_with_mp3_format(self, voice_service):
        """Test ESP32 audio processing with MP3 format"""
        mp3_request = AudioRequest(
            audio_data="bXAzIGF1ZGlvIGRhdGE=",  # "mp3 audio data" in base64
            format=AudioFormat.MP3,
            device_id="ESP32_MP3_001",
            language="ar",
        )

        with patch.object(voice_service, "transcribe_audio") as mock_transcribe:
            mock_result = TranscriptionResult(
                text="تم استلام الصوت المضغوط",
                language="ar",
                confidence=0.8,
                provider="whisper",
                processing_time_ms=300,
                audio_duration_ms=1500,
                segments=[],
                metadata={},
            )
            mock_transcribe.return_value = mock_result

            result = await voice_service.process_esp32_audio(mp3_request)

            assert result.metadata["source"] == "esp32"
            assert result.text == "تم استلام الصوت المضغوط"


# ================ HEALTH CHECK TESTS ================


class TestHealthCheck:
    """Test voice service health check functionality"""

    @pytest.mark.asyncio
    async def test_health_check_returns_comprehensive_status(self, voice_service):
        """Test health check returns comprehensive system status"""
        health = await voice_service.health_check()

        assert "service" in health
        assert "providers" in health
        assert "dependencies" in health
        assert "config" in health

        assert health["service"] == "healthy"
        assert "whisper" in health["dependencies"]
        assert "azure_speech" in health["dependencies"]
        assert "pydub" in health["dependencies"]

        assert "default_provider" in health["config"]
        assert "supported_formats" in health["config"]

    @pytest.mark.asyncio
    async def test_health_check_with_whisper_available(self, voice_service):
        """Test health check when Whisper is available"""
        # Mock Whisper model
        mock_model = Mock()
        mock_model.transcribe.return_value = {"text": "test"}
        voice_service.whisper_model = mock_model

        health = await voice_service.health_check()

        assert health["providers"]["whisper"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_with_azure_configured(self, voice_service):
        """Test health check when Azure is configured"""
        # Mock Azure config
        voice_service.azure_speech_config = Mock()

        health = await voice_service.health_check()

        assert health["providers"]["azure"] == "configured"


# ================ ERROR HANDLING TESTS ================


class TestErrorHandling:
    """Test error handling and fallback mechanisms"""

    @pytest.mark.asyncio
    async def test_transcription_error_returns_fallback(
        self, voice_service, sample_wav_data
    ):
        """Test that transcription errors return fallback results"""
        with patch.object(
            voice_service, "_transcribe_with_provider"
        ) as mock_transcribe:
            mock_transcribe.side_effect = Exception("Transcription failed")

            result = await voice_service.transcribe_audio(
                audio_data=sample_wav_data, format=AudioFormat.WAV
            )

            assert result.provider == "fallback"
            assert result.confidence == 0.0
            assert "error" in result.metadata
            assert result.text == "مرحباً دبدوب"  # Fallback text

    @pytest.mark.asyncio
    async def test_audio_conversion_error_handled_gracefully(self, voice_service):
        """Test that audio conversion errors are handled gracefully"""
        with patch.object(voice_service, "_convert_to_wav") as mock_convert:
            mock_convert.side_effect = Exception("Conversion failed")

            result = await voice_service.transcribe_audio(
                audio_data=b"invalid_audio", format=AudioFormat.MP3
            )

            assert result.provider == "fallback"
            assert "error" in result.metadata


# ================ INTEGRATION TESTS ================


class TestVoiceServiceIntegration:
    """Integration tests for voice service components"""

    @pytest.mark.asyncio
    async def test_full_pipeline_with_mock_providers(
        self, voice_service, sample_wav_data
    ):
        """Test full audio processing pipeline"""
        audio_base64 = base64.b64encode(sample_wav_data).decode("utf-8")

        # Test the full pipeline
        result = await voice_service.transcribe_audio(
            audio_data=audio_base64,
            format=AudioFormat.WAV,
            language="ar",
            provider=STTProvider.WHISPER,  # Will fall back to mock if Whisper not available
        )

        assert isinstance(result, TranscriptionResult)
        assert len(result.text) > 0
        assert result.language == "ar"
        assert result.processing_time_ms > 0
        assert result.audio_duration_ms > 0


# ================ PERFORMANCE TESTS ================


class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_transcription_performance_reasonable(
        self, voice_service, sample_wav_data
    ):
        """Test that transcription performance is reasonable"""
        import time

        start_time = time.time()

        result = await voice_service.transcribe_audio(
            audio_data=sample_wav_data, format=AudioFormat.WAV
        )

        end_time = time.time()
        actual_time = (end_time - start_time) * 1000  # Convert to ms

        # Processing should be reasonable (less than 10x real-time for 1s audio)
        assert actual_time < 10000  # 10 seconds max for 1 second audio
        assert result.processing_time_ms > 0


# ================ CONFIGURATION TESTS ================


class TestConfiguration:
    """Test configuration handling"""

    def test_config_model_validation(self):
        """Test configuration model validates correctly"""
        config = VoiceServiceConfig(
            default_provider=STTProvider.AZURE,
            whisper_model=WhisperModel.LARGE,
            azure_key="test_key_123",
            azure_region="westus",
            max_audio_duration=60,
        )

        assert config.default_provider == STTProvider.AZURE
        assert config.whisper_model == WhisperModel.LARGE
        assert config.azure_key == "test_key_123"
        assert config.max_audio_duration == 60

    def test_config_defaults(self):
        """Test configuration defaults are reasonable"""
        config = VoiceServiceConfig()

        assert config.default_provider == STTProvider.WHISPER
        assert config.whisper_model == WhisperModel.BASE
        assert config.max_audio_duration == 30
        assert AudioFormat.WAV in config.supported_formats
        assert config.enable_fallback is True


# ================ CLEANUP ================


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after each test"""
    yield

    # Clean up any temporary files created during tests
    temp_dirs = ["./test_temp", "./temp_audio"]
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


# ================ MATH IMPORT FOR FIXTURES ================
import math
