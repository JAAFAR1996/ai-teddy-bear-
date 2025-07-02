"""
🧸 AI Teddy Bear - Cloud Server
Optimized for Render.com deployment
Compatible with ESP32 IoT devices
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Optional
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app with comprehensive metadata
app = FastAPI(
    title="🧸 AI Teddy Bear API",
    description="Cloud server for AI Teddy Bear IoT project - ESP32 compatible",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for ESP32 and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class DeviceStatus(BaseModel):
    device_id: str
    status: str
    last_seen: datetime
    battery_level: Optional[int] = None
    wifi_strength: Optional[int] = None

class AudioMessage(BaseModel):
    device_id: str
    message: str
    timestamp: datetime
    audio_length: Optional[float] = None

class TeddyResponse(BaseModel):
    response_text: str
    audio_url: Optional[str] = None
    timestamp: datetime

# In-memory storage (in production, use a real database)
connected_devices = {}
audio_messages = []
teddy_responses = []

# Startup message
@app.on_event("startup")
async def startup_event():
    logger.info("🧸 AI Teddy Bear Server starting up...")
    logger.info("📡 Ready for ESP32 connections")
    logger.info("🌐 Deployed on Render.com")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "ai-teddy-bear",
        "version": "2.0.0",
        "platform": "render.com",
        "timestamp": datetime.now(),
        "connected_devices": len(connected_devices)
    }

# Root endpoint
@app.get("/")
async def root():
    """Main endpoint with service information"""
    return {
        "message": "🧸 AI Teddy Bear Server is Running!",
        "status": "active",
        "platform": "Render.com",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "esp32_endpoints": {
            "connect": "/esp32/connect",
            "status": "/esp32/status",
            "audio": "/api/audio/upload"
        }
    }

# ESP32 specific endpoints
@app.get("/esp32/connect")
async def esp32_connect():
    """ESP32 connection test endpoint"""
    return {
        "message": "✅ ESP32 connection successful!",
        "server": "ai-teddy-bear",
        "endpoints": {
            "status": "/esp32/status",
            "audio_upload": "/api/audio/upload",
            "get_response": "/api/response/latest"
        },
        "websocket": "/ws",  # For future WebSocket implementation
        "timestamp": datetime.now()
    }

@app.post("/esp32/status")
async def update_device_status(status: DeviceStatus):
    """Update device status from ESP32"""
    connected_devices[status.device_id] = status.dict()
    logger.info(f"📱 Device {status.device_id} status updated")
    
    return {
        "message": "Status updated successfully",
        "device_id": status.device_id,
        "timestamp": datetime.now()
    }

@app.get("/esp32/status/{device_id}")
async def get_device_status(device_id: str):
    """Get specific device status"""
    if device_id not in connected_devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return connected_devices[device_id]

@app.get("/esp32/devices")
async def list_devices():
    """List all connected devices"""
    return {
        "devices": list(connected_devices.values()),
        "total_devices": len(connected_devices),
        "timestamp": datetime.now()
    }

# Audio processing endpoints
@app.post("/api/audio/upload")
async def upload_audio(
    device_id: str,
    audio_file: UploadFile = File(None),
    text_message: str = None
):
    """Handle audio upload from ESP32 or text message"""
    
    if audio_file:
        # Handle audio file
        audio_content = await audio_file.read()
        logger.info(f"🎵 Received audio from {device_id}: {len(audio_content)} bytes")
        
        # Simulate audio processing (in real implementation, use speech-to-text)
        transcribed_text = f"Audio message from {device_id} received"
        
    elif text_message:
        transcribed_text = text_message
        logger.info(f"💬 Received text from {device_id}: {text_message}")
    else:
        raise HTTPException(status_code=400, detail="No audio file or text message provided")
    
    # Store the message
    message = AudioMessage(
        device_id=device_id,
        message=transcribed_text,
        timestamp=datetime.now(),
        audio_length=len(audio_content) if audio_file else None
    )
    audio_messages.append(message.dict())
    
    # Generate AI response (simplified - in real implementation, use OpenAI API)
    ai_response = await generate_ai_response(transcribed_text, device_id)
    
    return {
        "status": "success",
        "message": "Audio processed successfully",
        "transcribed_text": transcribed_text,
        "ai_response": ai_response,
        "device_id": device_id,
        "timestamp": datetime.now()
    }

async def generate_ai_response(message: str, device_id: str) -> dict:
    """Generate AI response (simplified version)"""
    
    # Simulate AI processing delay
    await asyncio.sleep(0.5)
    
    # Simple response logic (replace with OpenAI API in production)
    if "hello" in message.lower() or "مرحبا" in message.lower():
        response_text = "Hello little friend! I'm your AI Teddy Bear. How are you today? 🧸"
    elif "play" in message.lower() or "العب" in message.lower():
        response_text = "Let's play a fun game! I can tell you stories or sing songs. What would you like? 🎵"
    elif "story" in message.lower() or "قصة" in message.lower():
        response_text = "Once upon a time, there was a magical teddy bear who lived in the clouds... 📚✨"
    else:
        response_text = f"That's interesting! Tell me more about it, my little friend. I love listening to you! 💕"
    
    # Store the response
    response = TeddyResponse(
        response_text=response_text,
        timestamp=datetime.now()
    )
    teddy_responses.append(response.dict())
    
    logger.info(f"🤖 Generated response for {device_id}")
    
    return {
        "text": response_text,
        "timestamp": response.timestamp,
        "length": len(response_text)
    }

@app.get("/api/response/latest/{device_id}")
async def get_latest_response(device_id: str):
    """Get latest AI response for device"""
    device_responses = [r for r in teddy_responses if r.get("device_id") == device_id]
    
    if not device_responses:
        return {"message": "No responses found", "device_id": device_id}
    
    return device_responses[-1]

@app.get("/api/messages")
async def get_all_messages():
    """Get all stored messages (for debugging)"""
    return {
        "audio_messages": audio_messages[-10:],  # Last 10 messages
        "ai_responses": teddy_responses[-10:],    # Last 10 responses
        "total_messages": len(audio_messages),
        "total_responses": len(teddy_responses)
    }

# Admin/monitoring endpoints
@app.get("/admin/stats")
async def get_stats():
    """Get server statistics"""
    return {
        "server_info": {
            "platform": "Render.com",
            "version": "2.0.0",
            "uptime": "Running",
            "memory_usage": "~100MB"  # Simplified
        },
        "activity": {
            "connected_devices": len(connected_devices),
            "total_messages": len(audio_messages),
            "total_responses": len(teddy_responses),
            "last_activity": audio_messages[-1]["timestamp"] if audio_messages else None
        },
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "esp32_connect": "/esp32/connect",
            "audio_upload": "/api/audio/upload"
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "🧸 This endpoint doesn't exist on Teddy Bear server",
            "available_endpoints": [
                "/", "/health", "/docs", "/esp32/connect", "/api/audio/upload"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "🧸 Oops! Something went wrong. Please try again.",
            "contact": "Check logs or contact support"
        }
    )

# Development server (for local testing)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True
    ) 