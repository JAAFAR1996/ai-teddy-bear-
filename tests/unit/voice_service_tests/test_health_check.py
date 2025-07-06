from unittest.mock import Mock

import pytest


class TestHealthCheck:
    """Test voice service health check functionality"""

    @pytest.mark.asyncio
    async def test_health_check_returns_comprehensive_status(
            self, voice_service):
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
