"""
🌊 Modern Streaming Services Package - 2025 Edition

Real-time WebSocket and audio streaming capabilities
"""

from .websocket_manager import (
    ModernWebSocketManager,
    WebSocketManager,
    WebSocketConfig,
    ConnectionInfo,
    create_websocket_manager
)

from .audio_streamer import (
    ModernAudioStreamer,
    AudioStreamer,
    AudioStreamConfig,
    StreamSession,
    StreamingAudioBuffer,
    create_audio_streamer
)

__all__ = [
    # WebSocket Management
    "ModernWebSocketManager",
    "WebSocketManager",
    "WebSocketConfig", 
    "ConnectionInfo",
    "create_websocket_manager",
    
    # Audio Streaming
    "ModernAudioStreamer",
    "AudioStreamer",
    "AudioStreamConfig",
    "StreamSession",
    "StreamingAudioBuffer", 
    "create_audio_streamer"
] 