"""
Unit Tests for WebSocketClient - Enterprise Communication Testing
"""

import json
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtCore import QUrl
from PySide6.QtWebSockets import QWebSocket

from src.ui.network.websocket_client import (WebSocketClient,
                                             create_websocket_client)


class TestWebSocketClient:
    """Comprehensive test suite for WebSocketClient"""

    @pytest.fixture
    def websocket_client(self):
        """Create WebSocketClient for testing"""
        return WebSocketClient("ws://test.example.com/ws")

    @pytest.fixture
    def mock_websocket(self):
        """Mock QWebSocket for testing"""
        return Mock(spec=QWebSocket)

    def test_client_initialization(self, websocket_client):
        """Test client initialization with proper defaults"""
        assert websocket_client.server_url == "ws://test.example.com/ws"
        assert websocket_client.max_reconnect_attempts == 10
        assert websocket_client.is_connected == False
        assert websocket_client.reconnect_attempts == 0
        assert websocket_client.total_bytes_sent == 0
        assert websocket_client.total_bytes_received == 0
        assert isinstance(websocket_client.message_queue, list)

    def test_url_handling(self):
        """Test URL parsing and handling"""
        client = WebSocketClient("ws://localhost:8000/ws/test")
        assert isinstance(client.url, QUrl)
        assert client.url.toString() == "ws://localhost:8000/ws/test"

    def test_timer_setup(self, websocket_client):
        """Test that timers are properly configured"""
        assert websocket_client.reconnect_timer is not None
        assert websocket_client.heartbeat_timer is not None
        assert websocket_client.heartbeat_timeout_timer is not None

        # Check timer configurations
        assert websocket_client.reconnect_timer.isSingleShot()
        assert websocket_client.heartbeat_timeout_timer.isSingleShot()

    @patch.object(WebSocketClient, "_setup_websocket_connections")
    def test_connect_to_server(self, mock_setup, websocket_client):
        """Test connection initiation"""
        with patch.object(websocket_client.websocket, "open") as mock_open:
            result = websocket_client.connect_to_server()

            assert result == True
            assert websocket_client.is_connecting == True
            assert websocket_client.connection_start_time is not None
            mock_open.assert_called_once_with(websocket_client.url)

    def test_connect_when_already_connected(self, websocket_client):
        """Test connection attempt when already connected"""
        websocket_client.is_connected = True

        result = websocket_client.connect_to_server()
        assert result == False

    def test_disconnect_from_server(self, websocket_client):
        """Test graceful disconnection"""
        websocket_client.is_connected = True
        websocket_client.reconnect_attempts = 5

        with patch.object(websocket_client.websocket, "close") as mock_close:
            websocket_client.disconnect_from_server()

            assert websocket_client.is_connected == False
            assert websocket_client.is_connecting == False
            assert websocket_client.reconnect_attempts == 0
            mock_close.assert_called_once()

    def test_send_message_when_connected(self, websocket_client):
        """Test message sending when connected"""
        websocket_client.is_connected = True
        test_message = {"type": "test", "data": "hello"}

        with patch.object(
            websocket_client.websocket, "sendTextMessage", return_value=100
        ) as mock_send:
            result = websocket_client.send_message(test_message)

            assert result == True
            assert websocket_client.total_bytes_sent == 100
            mock_send.assert_called_once()

            # Check message enhancement
            call_args = mock_send.call_args[0][0]
            sent_data = json.loads(call_args)
            assert sent_data["type"] == "test"
            assert sent_data["data"] == "hello"
            assert "timestamp" in sent_data
            assert "client_id" in sent_data

    def test_send_message_when_disconnected(self, websocket_client):
        """Test message queuing when disconnected"""
        websocket_client.is_connected = False
        test_message = {"type": "test", "data": "queued"}

        result = websocket_client.send_message(test_message)

        assert result == True
        assert len(websocket_client.message_queue) == 1
        assert websocket_client.message_queue[0]["type"] == "test"

    def test_on_connected_handler(self, websocket_client):
        """Test connection success handler"""
        websocket_client.connection_start_time = datetime.now()
        websocket_client.reconnect_attempts = 3
        websocket_client.message_queue = [{"type": "queued"}]

        with patch.object(
            websocket_client, "_send_queued_messages"
        ) as mock_send_queued:
            websocket_client._on_connected()

            assert websocket_client.is_connected == True
            assert websocket_client.is_connecting == False
            assert websocket_client.reconnect_attempts == 0
            assert websocket_client.last_heartbeat_time is not None
            mock_send_queued.assert_called_once()

    def test_on_disconnected_handler(self, websocket_client):
        """Test disconnection handler"""
        websocket_client.is_connected = True
        websocket_client.reconnect_attempts = 2

        with patch.object(websocket_client, "_schedule_reconnection") as mock_schedule:
            websocket_client._on_disconnected()

            assert websocket_client.is_connected == False
            assert websocket_client.is_connecting == False
            mock_schedule.assert_called_once()

    def test_message_reception_regular(self, websocket_client):
        """Test regular message reception"""
        test_message = {"type": "response", "data": "success"}
        json_message = json.dumps(test_message)

        with patch.object(websocket_client, "message_received") as mock_signal:
            websocket_client._on_message_received(json_message)

            assert websocket_client.total_bytes_received > 0
            mock_signal.emit.assert_called_once_with(test_message)

    def test_message_reception_pong(self, websocket_client):
        """Test pong message handling"""
        websocket_client.last_heartbeat_time = datetime.now()
        pong_message = json.dumps({"type": "pong"})

        with patch.object(
            websocket_client.heartbeat_timeout_timer, "stop"
        ) as mock_stop:
            websocket_client._on_message_received(pong_message)
            mock_stop.assert_called_once()

    def test_message_reception_error(self, websocket_client):
        """Test server error message handling"""
        error_message = json.dumps(
            {"type": "error", "message": "Server error", "code": "ERR001"}
        )

        with patch.object(websocket_client, "error_occurred") as mock_signal:
            websocket_client._on_message_received(error_message)
            mock_signal.emit.assert_called_once()

    def test_invalid_json_handling(self, websocket_client):
        """Test handling of invalid JSON messages"""
        invalid_json = "not json at all"

        with patch.object(websocket_client, "error_occurred") as mock_signal:
            websocket_client._on_message_received(invalid_json)
            mock_signal.emit.assert_called_once()

    def test_reconnection_scheduling(self, websocket_client):
        """Test reconnection with exponential backoff"""
        websocket_client.reconnect_attempts = 2

        with patch.object(websocket_client.reconnect_timer, "start") as mock_start:
            websocket_client._schedule_reconnection()

            # Should calculate exponential backoff
            expected_delay = min(5000 * (2**2), 60000)
            mock_start.assert_called_once_with(expected_delay)

    def test_reconnection_limit(self, websocket_client):
        """Test max reconnection attempts"""
        websocket_client.reconnect_attempts = 10

        with patch.object(websocket_client.reconnect_timer, "start") as mock_start:
            websocket_client._schedule_reconnection()
            mock_start.assert_not_called()

    def test_heartbeat_sending(self, websocket_client):
        """Test heartbeat functionality"""
        websocket_client.is_connected = True
        websocket_client.connection_start_time = datetime.now()

        with patch.object(
            websocket_client, "send_message", return_value=True
        ) as mock_send:
            websocket_client._send_heartbeat()

            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["type"] == "ping"
            assert "timestamp" in call_args
            assert "client_uptime" in call_args

    def test_queued_message_sending(self, websocket_client):
        """Test sending of queued messages"""
        websocket_client.is_connected = True
        websocket_client.message_queue = [
            {"type": "msg1", "timestamp": "old"},
            {"type": "msg2", "sequence_number": 123},
        ]

        with patch.object(
            websocket_client, "send_message", return_value=True
        ) as mock_send:
            websocket_client._send_queued_messages()

            assert len(websocket_client.message_queue) == 0
            assert mock_send.call_count == 2

    def test_connection_statistics(self, websocket_client):
        """Test connection statistics gathering"""
        websocket_client.is_connected = True
        websocket_client.total_bytes_sent = 1024
        websocket_client.total_bytes_received = 2048
        websocket_client.connection_start_time = datetime.now()
        websocket_client.message_queue = [{"test": "queued"}]

        stats = websocket_client.get_connection_stats()

        assert stats["is_connected"] == True
        assert stats["total_bytes_sent"] == 1024
        assert stats["total_bytes_received"] == 2048
        assert stats["queued_messages"] == 1
        assert "uptime_seconds" in stats

    def test_message_queue_clearing(self, websocket_client):
        """Test message queue clearing"""
        websocket_client.message_queue = [{"msg": 1}, {"msg": 2}, {"msg": 3}]

        cleared_count = websocket_client.clear_message_queue()

        assert cleared_count == 3
        assert len(websocket_client.message_queue) == 0

    def test_custom_url_connection(self, websocket_client):
        """Test connection with custom URL"""
        custom_url = "ws://custom.server.com/ws"

        with patch.object(websocket_client.websocket, "open") as mock_open:
            websocket_client.connect_to_server(custom_url)

            assert websocket_client.server_url == custom_url
            assert websocket_client.url.toString() == custom_url


class TestWebSocketClientFactory:
    """Test factory function for WebSocketClient"""

    def test_create_websocket_client_default(self):
        """Test factory with default URL"""
        client = create_websocket_client()

        assert isinstance(client, WebSocketClient)
        assert "ws://localhost:8000/ws/ui_session" in client.server_url

    def test_create_websocket_client_custom(self):
        """Test factory with custom URL"""
        custom_url = "ws://custom.example.com/ws"
        client = create_websocket_client(custom_url)

        assert isinstance(client, WebSocketClient)
        assert client.server_url == custom_url


@pytest.mark.integration
class TestWebSocketClientIntegration:
    """Integration tests for WebSocketClient"""

    @pytest.mark.skip(reason="Requires actual WebSocket server")
    def test_real_connection(self):
        """Test connection to real WebSocket server"""
        client = WebSocketClient("ws://echo.websocket.org")

        # This would test with a real server
        # Implementation would depend on available test server
        pass
