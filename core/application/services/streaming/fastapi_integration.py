"""
🚀 FastAPI Integration Example - 2025 Edition
Modern WebSocket and Audio Streaming with FastAPI
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .websocket_manager import ModernWebSocketManager, WebSocketConfig
from .audio_streamer import ModernAudioStreamer, AudioStreamConfig

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

# Global instances (in production, use proper DI container)
websocket_manager: Optional[ModernWebSocketManager] = None
audio_streamer: Optional[ModernAudioStreamer] = None

def get_websocket_manager() -> ModernWebSocketManager:
    """Get WebSocket manager instance"""
    global websocket_manager
    if websocket_manager is None:
        config = WebSocketConfig(
            heartbeat_interval=30,
            max_connections=1000,
            connection_timeout=300
        )
        websocket_manager = ModernWebSocketManager(config)
    return websocket_manager

def get_audio_streamer() -> ModernAudioStreamer:
    """Get audio streamer instance"""
    global audio_streamer
    if audio_streamer is None:
        ws_manager = get_websocket_manager()
        config = AudioStreamConfig(
            sample_rate=16000,
            enable_real_time_processing=True,
            streaming_enabled=True
        )
        audio_streamer = ModernAudioStreamer(ws_manager, None, config)
    return audio_streamer

# ================== FASTAPI APPLICATION ==================

def create_streaming_app() -> FastAPI:
    """Create FastAPI application with modern streaming capabilities"""
    
    app = FastAPI(
        title="AI Teddy Bear Streaming API",
        description="Modern WebSocket and Audio Streaming - 2025 Edition",
        version="2.0.0"
    )
    
    @app.get("/", response_class=HTMLResponse)
    async def get_test_client():
        """Serve a simple test client for WebSocket testing"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>🎵 Modern Streaming Test Client - 2025</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f0f8ff; }
        .container { max-width: 800px; margin: 0 auto; }
        .section { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        button:hover { background: #0056b3; }
        .log { background: #f8f9fa; padding: 10px; border-radius: 4px; max-height: 300px; overflow-y: auto; font-family: monospace; }
        .connected { color: green; }
        .error { color: red; }
        input[type="text"] { width: 300px; padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Modern Streaming Test Client - 2025 Edition</h1>
        
        <div class="section">
            <h2>📡 WebSocket Connection</h2>
            <button id="connect">Connect WebSocket</button>
            <button id="disconnect">Disconnect</button>
            <button id="ping">Send Ping</button>
            <div>Status: <span id="status">Disconnected</span></div>
        </div>
        
        <div class="section">
            <h2>🎤 Audio Streaming</h2>
            <input type="text" id="textInput" placeholder="Type a message to send...">
            <button id="sendText">Send Text</button>
        </div>
        
        <div class="section">
            <h2>📊 Statistics</h2>
            <button id="getStats">Get Stats</button>
            <div id="stats"></div>
        </div>
        
        <div class="section">
            <h2>📜 Message Log</h2>
            <div id="log" class="log"></div>
            <button onclick="clearLog()">Clear Log</button>
        </div>
    </div>

    <script>
        let ws = null;
        let sessionId = null;
        
        function log(message, className = '') {
            const logDiv = document.getElementById('log');
            const time = new Date().toLocaleTimeString();
            logDiv.innerHTML += `<div class="${className}">[${time}] ${message}</div>`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        function clearLog() {
            document.getElementById('log').innerHTML = '';
        }
        
        function updateStatus(status) {
            document.getElementById('status').textContent = status;
            document.getElementById('status').className = status.toLowerCase().includes('connected') ? 'connected' : 'error';
        }
        
        // WebSocket connection
        document.getElementById('connect').onclick = function() {
            if (ws) {
                log('⚠️ Already connected', 'error');
                return;
            }
            
            sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
            ws = new WebSocket(`ws://localhost:8000/ws/audio/${sessionId}`);
            
            ws.onopen = function() {
                log('✅ WebSocket connected', 'connected');
                updateStatus('Connected');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                log(`📥 Received: ${JSON.stringify(data, null, 2)}`);
            };
            
            ws.onclose = function() {
                log('❌ WebSocket disconnected', 'error');
                updateStatus('Disconnected');
                ws = null;
                sessionId = null;
            };
            
            ws.onerror = function(error) {
                log(`❌ WebSocket error: ${error}`, 'error');
            };
        };
        
        document.getElementById('disconnect').onclick = function() {
            if (ws) {
                ws.close();
            }
        };
        
        document.getElementById('ping').onclick = function() {
            if (!ws) {
                log('⚠️ Not connected', 'error');
                return;
            }
            
            ws.send(JSON.stringify({type: 'ping', timestamp: new Date().toISOString()}));
            log('📤 Ping sent');
        };
        
        document.getElementById('sendText').onclick = function() {
            const text = document.getElementById('textInput').value;
            if (!text || !ws) {
                log('⚠️ No text or not connected', 'error');
                return;
            }
            
            ws.send(JSON.stringify({
                type: 'text_input',
                text: text,
                timestamp: new Date().toISOString()
            }));
            log(`📤 Text sent: ${text}`);
            document.getElementById('textInput').value = '';
        };
        
        document.getElementById('getStats').onclick = async function() {
            try {
                const response = await fetch('/api/streaming/stats');
                const stats = await response.json();
                document.getElementById('stats').innerHTML = `<pre>${JSON.stringify(stats, null, 2)}</pre>`;
                log('📊 Stats retrieved');
            } catch (error) {
                log(`❌ Failed to get stats: ${error}`, 'error');
            }
        };
    </script>
</body>
</html>
        """
    
    # ================== WEBSOCKET ENDPOINTS ==================
    
    @app.websocket("/ws/audio/{session_id}")
    async def websocket_audio_endpoint(
        websocket: WebSocket,
        session_id: str,
        audio_streamer: ModernAudioStreamer = Depends(get_audio_streamer)
    ):
        """Main WebSocket endpoint for audio streaming - replaces TODO placeholder"""
        logger.info(f"🎵 New audio stream connection: {session_id}")
        
        await audio_streamer.handle_audio_stream(
            websocket=websocket,
            session_id=session_id,
            child=None
        )
    
    # ================== REST API ENDPOINTS ==================
    
    @app.get("/api/streaming/stats", response_model=StreamingStats)
    async def get_streaming_stats(
        ws_manager: ModernWebSocketManager = Depends(get_websocket_manager),
        audio_streamer: ModernAudioStreamer = Depends(get_audio_streamer)
    ):
        """Get streaming statistics"""
        return StreamingStats(
            websocket_stats=ws_manager.get_stats(),
            audio_stats=audio_streamer.get_stats(),
            timestamp=datetime.utcnow().isoformat()
        )
    
    @app.get("/api/streaming/sessions")
    async def get_active_sessions(
        ws_manager: ModernWebSocketManager = Depends(get_websocket_manager),
        audio_streamer: ModernAudioStreamer = Depends(get_audio_streamer)
    ):
        """Get list of active streaming sessions"""
        ws_sessions = list(ws_manager.connections.keys())
        audio_sessions = list(audio_streamer.sessions.keys())
        
        return {
            "websocket_sessions": ws_sessions,
            "audio_sessions": audio_sessions,
            "total_active": len(set(ws_sessions + audio_sessions)),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/health")
    async def health_check(
        ws_manager: ModernWebSocketManager = Depends(get_websocket_manager),
        audio_streamer: ModernAudioStreamer = Depends(get_audio_streamer)
    ):
        """Health check endpoint"""
        return {
            "status": "healthy",
            "services": {
                "websocket_manager": "operational",
                "audio_streamer": "operational"
            },
            "active_connections": len(ws_manager.connections),
            "active_audio_sessions": len(audio_streamer.sessions),
            "timestamp": datetime.utcnow().isoformat()
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
        
        if websocket_manager:
            await websocket_manager.shutdown()
        
        if audio_streamer:
            await audio_streamer.shutdown()
        
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
    logger.info("🌊 WebSocket endpoint: ws://localhost:8000/ws/audio/{session_id}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
