"""
🧸 Device Management Endpoints
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from infrastructure.dependencies import get_container

router = APIRouter()


class DeviceRegistration(BaseModel):
    """Device registration model"""

    device_id: str = Field(..., description="Unique device identifier")
    device_type: str = Field(default="esp32_teddy", description="Device type")
    firmware_version: str = Field(..., description="Firmware version")
    child_name: Optional[str] = Field(None, description="Child's name")
    child_age: Optional[int] = Field(None, description="Child's age")


class DeviceStatus(BaseModel):
    """Device status model"""

    device_id: str
    status: str
    last_seen: str
    battery_level: Optional[int] = None
    wifi_strength: Optional[int] = None


@router.post("/register", response_model=Dict[str, Any])
async def register_device(
    device: DeviceRegistration, container=Depends(get_container)
) -> Dict[str, Any]:
    """Register new ESP32 device"""
    try:
        # Generate unique device token
        device_token = f"tddy_{device.device_id}_{hash(device.device_id) % 10000}"

        # Store device in database
        # TODO: Add database persistence

        return {
            "status": "success",
            "device_token": device_token,
            "message": f"Device {device.device_id} registered successfully",
            "config": {
                "websocket_url": "ws://localhost:8000/ws/device",
                "upload_endpoint": "/api/devices/audio/upload",
                "heartbeat_interval": 30,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device registration failed: {str(e)}",
        )


@router.get("/status/{device_id}", response_model=DeviceStatus)
async def get_device_status(device_id: str) -> DeviceStatus:
    """Get device status"""
    # TODO: Fetch from database
    return DeviceStatus(
        device_id=device_id, status="online", last_seen="2025-01-01T12:00:00Z"
    )


@router.post("/audio/upload")
async def upload_audio(
    device_id: str, audio_data: bytes, container=Depends(get_container)
) -> Dict[str, Any]:
    """Handle audio upload from ESP32"""
    try:
        ai_service = await container.ai_service()
        voice_service = await container.voice_service()

        # Process audio
        transcript = await voice_service.transcribe_audio(audio_data)
        response = await ai_service.generate_response(transcript, device_id)

        return {
            "status": "success",
            "transcript": transcript,
            "response": response,
            "response_audio_url": f"/api/audio/tts/{response['id']}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio processing failed: {str(e)}",
        )


@router.get("/config/{device_id}")
async def get_device_config(device_id: str) -> Dict[str, Any]:
    """Get device configuration"""
    return {
        "device_id": device_id,
        "sample_rate": 16000,
        "audio_format": "wav",
        "compression": "mp3",
        "wake_word": "hey_teddy",
        "response_timeout": 10,
    }
