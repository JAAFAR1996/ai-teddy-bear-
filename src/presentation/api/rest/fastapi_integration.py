"""
🚀 FastAPI Integration Example - 2025 Edition
Modern WebSocket and Audio Streaming with FastAPI
"""

import logging
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

from fastapi import Depends, FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# DI helper
from infrastructure.di import provide

from .audio_streamer import AudioStreamConfig, ModernAudioStreamer
from .websocket_manager import ModernWebSocketManager, WebSocketConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== MODELS ==================


class StreamingStats(BaseModel):
    """Streaming statistics model"""

    websocket_stats: Dict[str, Any]
    audio_stats: Dict[str, Any]
    timestamp: str


# ================== DEPENDENCY INJECTION ==================


def get_websocket_manager() -> ModernWebSocketManager:
    """Provide a *singleton* WebSocket manager via the DI container."""

    def _factory() -> ModernWebSocketManager:
        cfg = WebSocketConfig(
            heartbeat_interval=30, max_connections=1000, connection_timeout=300
        )
        return ModernWebSocketManager(cfg)

    return provide(ModernWebSocketManager, _factory)


def get_audio_streamer() -> ModernAudioStreamer:
    """Provide a *singleton* audio streamer via the DI container."""

    def _factory() -> ModernAudioStreamer:
        ws_manager = get_websocket_manager()
        cfg = AudioStreamConfig(
            sample_rate=16000,
            enable_real_time_processing=True,
            streaming_enabled=True,
        )
        return ModernAudioStreamer(ws_manager, None, cfg)

    return provide(ModernAudioStreamer, _factory)


# ================== FASTAPI APPLICATION ==================


def create_streaming_app() -> FastAPI:
    """Create FastAPI application with modern streaming capabilities"""

    app = FastAPI(
        title="AI Teddy Bear Streaming API",
        description="Modern WebSocket and Audio Streaming - 2025 Edition",
        version="2.0.0",
    )

    @app.get("/", response_class=HTMLResponse)
    async def get_test_client():
        """Serve a simple test client for WebSocket testing."""
        html_path = Path(__file__).parent / "test_client.html"
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "<h1>Test client HTML file not found.</h1>"

    # ================== WEBSOCKET ENDPOINTS ==================

    @app.websocket("/ws/audio/{session_id}")
    async def websocket_audio_endpoint(
        websocket: WebSocket,
        session_id: str,
        audio_streamer: ModernAudioStreamer = Depends(get_audio_streamer),
    ):
        """Main WebSocket endpoint for audio streaming - replaces TODO placeholder"""
        logger.info(f"🎵 New audio stream connection: {session_id}")

        await audio_streamer.handle_audio_stream(
            websocket=websocket, session_id=session_id, child=None
        )

    # ================== REST API ENDPOINTS ==================

    @app.get("/api/streaming/stats", response_model=StreamingStats)
    async def get_streaming_stats(
        ws_manager: ModernWebSocketManager = Depends(get_websocket_manager),
        audio_streamer: ModernAudioStreamer = Depends(get_audio_streamer),
    ):
        """Get streaming statistics"""
        return StreamingStats(
            websocket_stats=ws_manager.get_stats(),
            audio_stats=audio_streamer.get_stats(),
            timestamp=datetime.utcnow().isoformat(),
        )

    @app.get("/api/streaming/sessions")
    async def get_active_sessions(
        ws_manager: ModernWebSocketManager = Depends(get_websocket_manager),
        audio_streamer: ModernAudioStreamer = Depends(get_audio_streamer),
    ):
        """Get list of active streaming sessions"""
        ws_sessions = list(ws_manager.connections.keys())
        audio_sessions = list(audio_streamer.sessions.keys())

        return {
            "websocket_sessions": ws_sessions,
            "audio_sessions": audio_sessions,
            "total_active": len(set(ws_sessions + audio_sessions)),
            "timestamp": datetime.utcnow().isoformat(),
        }

    @app.get("/health")
    async def health_check(
        ws_manager: ModernWebSocketManager = Depends(get_websocket_manager),
        audio_streamer: ModernAudioStreamer = Depends(get_audio_streamer),
    ):
        """Health check endpoint"""
        return {
            "status": "healthy",
            "services": {
                "websocket_manager": "operational",
                "audio_streamer": "operational",
            },
            "active_connections": len(ws_manager.connections),
            "active_audio_sessions": len(audio_streamer.sessions),
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ================== LIFECYCLE EVENTS ==================

    @app.on_event("startup")
    async def startup_event():
        """Application startup"""
        logger.info("🚀 Starting AI Teddy Bear Streaming API...")
        logger.info("✅ Modern streaming services initialized")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown"""
        logger.info("🛑 Shutting down AI Teddy Bear Streaming API...")

        # Gracefully shut down singleton services.
        await get_websocket_manager().shutdown()
        await get_audio_streamer().shutdown()

        logger.info("✅ Graceful shutdown complete")

    return app


# ================== FACTORY FUNCTION ==================


def create_app() -> FastAPI:
    """Factory function to create the FastAPI application"""
    return create_streaming_app()


if __name__ == "__main__":
    import uvicorn

    app = create_app()

    logger.info("🚀 Starting development server...")
    logger.info("📱 Test client available at: http://localhost:8000")
    logger.info(
        "🌊 WebSocket endpoint: ws://localhost:8000/ws/audio/{session_id}")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True)
