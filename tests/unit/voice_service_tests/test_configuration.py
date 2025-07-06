import pytest

try:
    from src.application.services.voice_service import (
        AudioFormat,
        STTProvider,
        VoiceServiceConfig,
        WhisperModel,
    )
except ImportError:
    # Fallback for mock environment
    from .conftest import (AudioFormat, STTProvider, VoiceServiceConfig,
                           WhisperModel)


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
