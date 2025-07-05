"""
Enterprise WebSocket Client for AI Teddy Bear
Provides reliable real-time communication with auto-reconnection capability
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict

import structlog
from PySide6.QtCore import QObject, QTimer, QUrl, Signal
from PySide6.QtWebSockets import QWebSocket

logger = structlog.get_logger()


class WebSocketClient(QObject):
    """Enterprise WebSocket client with auto-reconnection"""
    
    connected = Signal()
    disconnected = Signal()
    message_received = Signal(dict)
    error_occurred = Signal(str)
    connection_status_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.websocket = QWebSocket()
        self.url = QUrl("ws://localhost:8000/ws/ui_session")
        self.reconnect_timer = QTimer()
        self.heartbeat_timer = QTimer()
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        
        self._setup_timers()
        self._setup_websocket_signals()
    
    def _setup_timers(self) -> Any:
        """Initialize and configure timers"""
        self.reconnect_timer.timeout.connect(self._attempt_reconnect)
        self.heartbeat_timer.timeout.connect(self._send_heartbeat)
        self.heartbeat_timer.start(30000)  # 30 seconds
    
    def _setup_websocket_signals(self) -> Any:
        """Connect WebSocket signals to handlers"""
        self.websocket.connected.connect(self._on_connected)
        self.websocket.disconnected.connect(self._on_disconnected)
        self.websocket.textMessageReceived.connect(self._on_message_received)
        self.websocket.errorOccurred.connect(self._on_error)
    
    def connect_to_server(self) -> Any:
        """Connect to WebSocket server"""
        logger.info("Attempting WebSocket connection", url=str(self.url))
        self.connection_status_changed.emit("Connecting...")
        self.websocket.open(self.url)
    
    def disconnect_from_server(self) -> Any:
        """Disconnect from WebSocket server"""
        self.websocket.close()
        self.reconnect_timer.stop()
    
    def send_message(Dict[str, Any]) -> None:
        """Send message to server"""
        if self.is_connected:
            json_message = json.dumps(message)
            self.websocket.sendTextMessage(json_message)
            logger.debug("Sent WebSocket message", message_type=message.get("type"))
    
    def _on_connected(self) -> Any:
        """Handle successful connection"""
        self.is_connected = True
        self.reconnect_attempts = 0
        self.reconnect_timer.stop()
        self.connection_status_changed.emit("Connected")
        self.connected.emit()
        logger.info("WebSocket connected successfully")
    
    def _on_disconnected(self) -> Any:
        """Handle disconnection"""
        self.is_connected = False
        self.connection_status_changed.emit("Disconnected")
        self.disconnected.emit()
        logger.warning("WebSocket disconnected")
        
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_timer.start(5000)  # Retry in 5 seconds
    
    def _on_message_received(str) -> None:
        """Handle received message"""
        try:
            data = json.loads(message)
            self.message_received.emit(data)
            logger.debug("Received WebSocket message", message_type=data.get("type"))
        except json.JSONDecodeError as e:
            logger.error("Failed to parse WebSocket message", error=str(e))
            self.error_occurred.emit(f"Invalid message format: {e}")
    
    def _on_error(self, error) -> Any:
        """Handle WebSocket error"""
        error_msg = f"WebSocket error: {error}"
        logger.error(error_msg)
        self.error_occurred.emit(error_msg)
        self.connection_status_changed.emit("Error")
    
    def _attempt_reconnect(self) -> Any:
        """Attempt to reconnect"""
        self.reconnect_attempts += 1
        if self.reconnect_attempts <= self.max_reconnect_attempts:
            logger.info("Attempting reconnection", attempt=self.reconnect_attempts)
            self.connect_to_server()
        else:
            self.reconnect_timer.stop()
            self.connection_status_changed.emit("Failed")
            logger.error("Max reconnection attempts reached")
    
    def _send_heartbeat(self) -> Any:
        """Send heartbeat to keep connection alive"""
        if self.is_connected:
            self.send_message({"type": "ping", "timestamp": datetime.now().isoformat()})
    
    def set_url(str) -> None:
        """Update the WebSocket URL"""
        self.url = QUrl(url)
        logger.info("WebSocket URL updated", url=url)
    
    def get_connection_info(self) -> dict:
        """Get current connection information"""
        return {
            "url": str(self.url),
            "is_connected": self.is_connected,
            "reconnect_attempts": self.reconnect_attempts,
            "max_attempts": self.max_reconnect_attempts
        } 