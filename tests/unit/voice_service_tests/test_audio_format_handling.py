from unittest.mock import Mock, patch

import pytest

try:
    from src.application.services.voice_service import AudioFormat
except ImportError:
    # Fallback for mock environment
    from .conftest import AudioFormat


class TestAudioFormatHandling:
    """Test audio format conversion and handling"""

    @pytest.mark.asyncio
    async def test_wav_duration_calculation(
            self, voice_service, sample_wav_data):
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
                    b"wav_data")

                wav_data, duration = await voice_service._convert_with_pydub(
                    sample_mp3_data, AudioFormat.MP3
                )

                assert duration == 1.0
                mock_audio.from_file.assert_called_once()
