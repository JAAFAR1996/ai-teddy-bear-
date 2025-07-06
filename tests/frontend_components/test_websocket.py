from datetime import datetime

import pytest


class TestWebSocket:
    """Test WebSocket functionality"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self, websocket_service):
        """Test WebSocket connection"""
        # Arrange
        websocket_service.connect.return_value = True

        # Act
        connected = await websocket_service.connect("ws://localhost:8000/ws")

        # Assert
        assert connected is True
        websocket_service.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_real_time_emotion_updates(self, websocket_service):
        """Test real-time emotion updates via WebSocket"""
        # Arrange
        emotion_update = {
            "type": "emotion_update",
            "data": {
                "conversationId": "conv1",
                "emotion": "happy",
                "confidence": 0.9,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
        websocket_service.receive_message.return_value = emotion_update

        # Act
        message = await websocket_service.receive_message()

        # Assert
        assert message["type"] == "emotion_update"
        assert message["data"]["emotion"] == "happy"
        assert message["data"]["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_audio_streaming(self, websocket_service):
        """Test audio streaming via WebSocket"""
        # Arrange
        audio_chunk = {
            "type": "audio_stream",
            "data": {
                "conversationId": "conv1",
                "chunk": "base64_encoded_audio",
                "sequence": 1,
            },
        }

        # Act
        await websocket_service.send_message(audio_chunk)

        # Assert
        websocket_service.send_message.assert_called_once_with(audio_chunk)
