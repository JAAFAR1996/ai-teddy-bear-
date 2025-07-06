import pytest


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

        # Processing should be reasonable (less than 10x real-time for 1s
        # audio)
        assert actual_time < 10000  # 10 seconds max for 1 second audio
        assert result.processing_time_ms > 0
