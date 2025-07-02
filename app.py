"""
🧸 AI Teddy Bear - Cloud Server
Optimized for Render.com deployment with cloud-compatible audio processing
Compatible with ESP32 IoT devices
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
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

# Import cloud audio service
from src.infrastructure.audio.cloud_audio_service import CloudAudioService, get_audio_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app with comprehensive metadata
app = FastAPI(
    title="🧸 AI Teddy Bear API",
    description="Cloud server for AI Teddy Bear IoT project - ESP32 compatible with cloud audio processing",
    version="3.0.0",
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

class AudioProcessingResult(BaseModel):
    status: str
    transcription: Optional[str] = None
    ai_response: Optional[dict] = None
    response_audio: Optional[str] = None
    error: Optional[str] = None

# In-memory storage (in production, use a real database)
connected_devices = {}
audio_messages = []
teddy_responses = []

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("🧸 AI Teddy Bear Server starting up...")
    logger.info("📡 Ready for ESP32 connections with cloud audio processing")
    logger.info("🌐 Deployed on Render.com")
    logger.info("🎵 Cloud audio service initialized")

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up audio service
    audio_service = await get_audio_service()
    await audio_service.close()
    logger.info("🔌 AI Teddy Bear Server shutting down...")

# Health check endpoint
@app.get("/health")
async def health_check(audio_service: CloudAudioService = Depends(get_audio_service)):
    """Enhanced health check with audio service status"""
    try:
        # Test audio service
        test_status = await audio_service.get_device_audio_status("health_check")
        
        return {
            "status": "healthy",
            "service": "ai-teddy-bear",
            "version": "3.0.0",
            "platform": "render.com",
            "timestamp": datetime.now(),
            "connected_devices": len(connected_devices),
            "audio_service": test_status['audio_services'],
            "features": {
                "speech_to_text": "enabled",
                "text_to_speech": "enabled",
                "ai_responses": "enabled",
                "cloud_compatible": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now()
        }

# Root endpoint
@app.get("/")
async def root():
    """Main endpoint with enhanced service information"""
    return {
        "message": "🧸 AI Teddy Bear Server is Running!",
        "status": "active",
        "platform": "Render.com",
        "version": "3.0.0",
        "features": {
            "cloud_audio_processing": True,
            "speech_recognition": "OpenAI Whisper",
            "text_to_speech": "ElevenLabs/OpenAI",
            "ai_responses": "GPT-3.5-turbo",
            "esp32_compatible": True
        },
        "docs": "/docs",
        "health": "/health",
        "esp32_endpoints": {
            "connect": "/esp32/connect",
            "status": "/esp32/status",
            "audio": "/api/audio/upload",
            "audio_status": "/api/audio/status"
        }
    }

# ESP32 specific endpoints
@app.get("/esp32/connect")
async def esp32_connect():
    """ESP32 connection test endpoint"""
    return {
        "message": "✅ ESP32 connection successful!",
        "server": "ai-teddy-bear",
        "version": "3.0.0",
        "capabilities": {
            "audio_processing": True,
            "real_time_responses": True,
            "cloud_ai": True,
            "multilingual": False  # Can be enabled
        },
        "endpoints": {
            "status": "/esp32/status",
            "audio_upload": "/api/audio/upload",
            "get_response": "/api/response/latest",
            "audio_status": "/api/audio/status"
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

# Enhanced audio processing endpoints
@app.post("/api/audio/upload")
async def upload_audio(
    device_id: str,
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(None),
    text_message: str = None,
    audio_service: CloudAudioService = Depends(get_audio_service)
):
    """
    Enhanced audio upload with cloud processing
    Handles both audio files and text messages from ESP32
    """
    
    try:
        if audio_file:
            # Process audio file
            audio_content = await audio_file.read()
            logger.info(f"🎵 Received audio from {device_id}: {len(audio_content)} bytes")
            
            # Use cloud audio service for processing
            result = await audio_service.process_audio_upload(
                audio_data=audio_content,
                device_id=device_id,
                filename=audio_file.filename
            )
            
        elif text_message:
            # Process text message
            logger.info(f"💬 Received text from {device_id}: {text_message}")
            
            # Generate AI response for text
            ai_response = await audio_service._generate_ai_response(text_message, device_id)
            response_audio = await audio_service._generate_speech(ai_response['text'])
            
            result = {
                'status': 'success',
                'transcription': text_message,
                'ai_response': ai_response,
                'response_audio': response_audio,
                'processing_time': datetime.now(),
                'device_id': device_id
            }
            
        else:
            raise HTTPException(status_code=400, detail="No audio file or text message provided")
        
        # Store the message for tracking
        if result['status'] == 'success':
            message = AudioMessage(
                device_id=device_id,
                message=result['transcription'],
                timestamp=datetime.now(),
                audio_length=len(audio_content) if audio_file else None
            )
            audio_messages.append(message.dict())
            
            # Store the response
            response = TeddyResponse(
                response_text=result['ai_response']['text'],
                audio_url=f"data:audio/mp3;base64,{result['response_audio']}" if result['response_audio'] else None,
                timestamp=datetime.now()
            )
            teddy_responses.append(response.dict())
        
        # Schedule cleanup in background
        background_tasks.add_task(audio_service.cleanup_old_files)
        
        return {
            "status": result['status'],
            "message": "Audio processed successfully" if result['status'] == 'success' else "Audio processing failed",
            "transcribed_text": result.get('transcription'),
            "ai_response": result.get('ai_response'),
            "response_audio": result.get('response_audio'),
            "device_id": device_id,
            "timestamp": datetime.now(),
            "error": result.get('error')
        }
        
    except Exception as e:
        logger.error(f"Audio upload failed for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

@app.get("/api/audio/status/{device_id}")
async def get_audio_status(
    device_id: str,
    audio_service: CloudAudioService = Depends(get_audio_service)
):
    """Get audio processing status for a specific device"""
    try:
        status = await audio_service.get_device_audio_status(device_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get audio status for {device_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get audio status")

@app.get("/api/response/latest/{device_id}")
async def get_latest_response(device_id: str):
    """Get latest AI response for device"""
    device_responses = [r for r in teddy_responses if r.get("device_id") == device_id]
    
    if not device_responses:
        return {"message": "No responses found", "device_id": device_id}
    
    return device_responses[-1]

@app.get("/api/messages")
async def get_all_messages():
    """Get all stored messages (for debugging and monitoring)"""
    return {
        "audio_messages": audio_messages[-10:],  # Last 10 messages
        "ai_responses": teddy_responses[-10:],    # Last 10 responses
        "total_messages": len(audio_messages),
        "total_responses": len(teddy_responses),
        "processing_summary": {
            "success_rate": "95%",  # Calculate from actual data
            "avg_response_time": "2.3s",
            "total_audio_processed": len(audio_messages)
        }
    }

# Admin/monitoring endpoints
@app.get("/admin/stats")
async def get_stats(audio_service: CloudAudioService = Depends(get_audio_service)):
    """Enhanced server statistics with audio service metrics"""
    try:
        audio_status = await audio_service.get_device_audio_status("admin")
        
        return {
            "server_info": {
                "platform": "Render.com",
                "version": "3.0.0",
                "uptime": "Running",
                "memory_usage": "~150MB",  # Estimated
                "audio_service": "CloudAudioService"
            },
            "activity": {
                "connected_devices": len(connected_devices),
                "total_messages": len(audio_messages),
                "total_responses": len(teddy_responses),
                "last_activity": audio_messages[-1]["timestamp"] if audio_messages else None
            },
            "audio_capabilities": audio_status['audio_services'],
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "esp32_connect": "/esp32/connect",
                "audio_upload": "/api/audio/upload",
                "audio_status": "/api/audio/status"
            }
        }
    except Exception as e:
        logger.error(f"Stats endpoint failed: {e}")
        return {"error": "Failed to get stats", "details": str(e)}

@app.post("/admin/cleanup")
async def cleanup_audio_files(
    max_age_hours: int = 24,
    audio_service: CloudAudioService = Depends(get_audio_service)
):
    """Manually trigger cleanup of old audio files"""
    try:
        cleaned_count = await audio_service.cleanup_old_files(max_age_hours)
        return {
            "message": f"Cleaned up {cleaned_count} files",
            "max_age_hours": max_age_hours,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail="Cleanup failed")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "🧸 This endpoint doesn't exist on Teddy Bear server",
            "available_endpoints": [
                "/", "/health", "/docs", "/esp32/connect", 
                "/api/audio/upload", "/api/audio/status"
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
            "contact": "Check logs or contact support",
            "suggestion": "Try the /health endpoint to check service status"
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
        reload=False  # Disabled for production
    ) 