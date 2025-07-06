import base64

import pytest

try:
    from src.application.services.voice_service import (
        AudioFormat,
        STTProvider,
        TranscriptionResult,
    )
except ImportError:
    # Fallback for mock environment
    from .conftest import AudioFormat, STTProvider, TranscriptionResult


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
