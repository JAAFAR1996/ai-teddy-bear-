"""
Networking Components for AI Teddy Bear UI
WebSocket client and enterprise message handling
"""

from .websocket_client import WebSocketClient
from .message_sender import EnterpriseMessageSender

__all__ = ['WebSocketClient', 'EnterpriseMessageSender'] 