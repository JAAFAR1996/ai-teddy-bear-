import pytest


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
