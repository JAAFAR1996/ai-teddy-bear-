"""
Networking Components for AI Teddy Bear UI
WebSocket client and enterprise message handling
"""

from .message_sender import EnterpriseMessageSender
from .websocket_client import WebSocketClient

__all__ = ["WebSocketClient", "EnterpriseMessageSender"]
