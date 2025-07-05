"""
🧸 AI Teddy Bear Production API Server
Clean, enterprise-grade API with proper separation of concerns

Integrated with fastapi_integration.py and federation_gateway.py for comprehensive API management.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from src.application.services.ai_service import AIService
from src.application.services.child_service import ChildService
from src.application.services.voice_service import VoiceService
from src.infrastructure.modern_container import (
    container,
    get_ai_service,
    get_child_service,
    get_voice_service,
    initialize_container,
    shutdown_container,
)
from src.infrastructure.monitoring.metrics import metrics_collector
from src.infrastructure.security.rate_limiter import RateLimiterMiddleware
from src.infrastructure.security.request_id import RequestIdMiddleware

logger = logging.getLogger(__name__)

# ================== REQUEST/RESPONSE MODELS ==================


class RegisterDeviceRequest(BaseModel):
    """Device registration request with validation"""

    device_id: str = Field(
        ..., min_length=5, max_length=50, pattern="^ESP32_[A-Z0-9_]+$"
    )
    firmware_version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    hardware_info: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("device_id")
    def validate_device_id(cls, v) -> Any:
        if not v.startswith("ESP32_"):
            raise ValueError("Device ID must start with ESP32_")
        return v


class AudioProcessRequest(BaseModel):
    """Audio processing request with validation"""

    audio: str = Field(..., description="Base64 encoded audio data")
    device_id: str = Field(..., min_length=5, max_length=50)
    session_id: Optional[str] = Field(None, min_length=10, max_length=50)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("audio")
    def validate_audio_not_empty(cls, v) -> Any:
        if not v or len(v) < 100:  # Minimum reasonable audio size
            raise ValueError("Audio data too small")
        return v


class ChildProfileRequest(BaseModel):
    """Child profile creation request"""

    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=2, le=14)
    language: str = Field(default="Arabic", pattern="^(Arabic|English)$")
    device_id: str = Field(..., min_length=5, max_length=50)
    preferences: Dict[str, Any] = Field(default_factory=dict)


class ConversationRecord(BaseModel):
    """Encapsulates conversation data for saving - Parameter Object Pattern"""

    device_id: str = Field(..., description="Device identifier")
    message: str = Field(..., description="Child's message")
    response: str = Field(..., description="AI response")
    emotion: str = Field(..., description="Detected emotion")
    category: str = Field(..., description="Conversation category")
    learning_points: List[str] = Field(
        default_factory=list, description="Learning points"
    )

    def to_metadata(self) -> Dict[str, Any]:
        """Convert analysis data to metadata dictionary"""
        return {
            "emotion": self.emotion,
            "category": self.category,
            "learning_points": self.learning_points,
        }


class AIResponse(BaseModel):
    """Structured AI response"""

    text: str
    emotion: str
    category: str
    learning_points: List[str]
    session_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ================== DEPENDENCY INJECTION ==================
# Dependencies are now provided by the clean container module

# ================== APPLICATION LIFECYCLE ==================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Starting AI Teddy Bear API Server...")

    # Configure container from environment
    container.config.from_env("TEDDY", delimiter="_")

    # Initialize container resources
    await initialize_container()

    logger.info("✅ API Server started successfully")

    yield

    # Cleanup
    logger.info("🛑 Shutting down API Server...")
    await shutdown_container()
    logger.info("✅ API Server shut down complete")


# ================== CREATE FASTAPI APP ==================

app = FastAPI(
    title="🧸 AI Teddy Bear Production API",
    description="Enterprise-grade AI Teddy Bear system with clean architecture",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(RateLimiterMiddleware, calls=100, period=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== HEALTH & MONITORING ENDPOINTS ==================


@app.get("/health", tags=["monitoring"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "3.0.0",
        "services": {
            "ai": "operational",
            "voice": "operational",
            "database": "operational",
        },
    }


@app.get("/metrics", tags=["monitoring"])
async def get_metrics():
    """Get application metrics"""
    return await metrics_collector.get_metrics()


# ================== DEVICE ENDPOINTS ==================


@app.post(
    "/api/v1/devices/register",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    tags=["devices"],
)
async def register_device(
    request: RegisterDeviceRequest,
    child_service: ChildService = Depends(get_child_service),
):
    """Register a new ESP32 device"""
    try:
        result = await child_service.register_device(
            device_id=request.device_id,
            firmware_version=request.firmware_version,
            hardware_info=request.hardware_info,
        )

        logger.info(f"Device registered: {request.device_id}")
        return {
            "status": "success",
            "device_id": request.device_id,
            "registration_id": result.registration_id,
            "timestamp": datetime.utcnow(),
        }

    except ValueError as e:
        logger.error(f"Device registration failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during device registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ================== AUDIO PROCESSING ENDPOINTS ==================


async def _validate_and_get_child(device_id: str, child_service: ChildService):
    """
    Validate device and get child profile.
    Extracted from process_audio to reduce complexity.
    """
    child = await child_service.get_by_device_id(device_id)
    if not child:
        raise HTTPException(
            status_code=404,
            detail=f"No child profile found for device {device_id}",
        )
    return child


async def _transcribe_audio_data(
    audio_data: str, language: str, voice_service: VoiceService
):
    """
    Transcribe audio data to text with validation.
    Extracted from process_audio to reduce complexity.
    """
    transcribed_text = await voice_service.transcribe_audio(
        audio_data=audio_data, language=language
    )

    if not transcribed_text:
        raise HTTPException(
            status_code=422,
            detail="Could not transcribe audio")

    return transcribed_text


async def _generate_ai_response(
    message: str, child, session_id: Optional[str], ai_service: AIService
):
    """
    Generate AI response for the transcribed message.
    Extracted from process_audio to reduce complexity.
    """
    return await ai_service.generate_response(
        message=message, child=child, session_id=session_id
    )


async def _synthesize_response_audio(
    text: str, emotion: str, language: str, voice_service: VoiceService
):
    """
    Convert AI response text to audio.
    Extracted from process_audio to reduce complexity.
    """
    return await voice_service.synthesize_speech(
        text=text, emotion=emotion, language=language
    )


async def _save_conversation_data(
    conversation: ConversationRecord, child_service: ChildService
):
    """
    Save conversation data to database.
    Refactored using Parameter Object pattern - reduces from 7 to 2 arguments.
    """
    await child_service.save_conversation(
        device_id=conversation.device_id,
        message=conversation.message,
        response=conversation.response,
        metadata=conversation.to_metadata(),
    )


def _build_ai_response(
    ai_response, response_audio: str, transcribed_text: str
) -> AIResponse:
    """
    Build the final AI response object.
    Extracted from process_audio to reduce complexity.
    """
    return AIResponse(
        text=ai_response.text,
        emotion=ai_response.emotion,
        category=ai_response.category,
        learning_points=ai_response.learning_points,
        session_id=ai_response.session_id,
        timestamp=datetime.utcnow(),
        metadata={
            "audio_response": response_audio,
            "transcribed_text": transcribed_text,
        },
    )


@app.post("/api/v1/audio/process", response_model=AIResponse, tags=["audio"])
async def process_audio(
    request: AudioProcessRequest,
    ai_service: AIService = Depends(get_ai_service),
    voice_service: VoiceService = Depends(get_voice_service),
    child_service: ChildService = Depends(get_child_service),
):
    """
    Process audio from ESP32 device.
    Refactored to reduce complexity using extracted functions.
    """
    try:
        # Step 1: Validate and get child profile
        child = await _validate_and_get_child(request.device_id, child_service)

        # Step 2: Transcribe audio to text
        transcribed_text = await _transcribe_audio_data(
            request.audio, child.language, voice_service
        )

        # Step 3: Generate AI response
        ai_response = await _generate_ai_response(
            transcribed_text, child, request.session_id, ai_service
        )

        # Step 4: Convert response to audio
        response_audio = await _synthesize_response_audio(
            ai_response.text, ai_response.emotion, child.language, voice_service
        )

        # Step 5: Save conversation using Parameter Object pattern
        conversation_record = ConversationRecord(
            device_id=request.device_id,
            message=transcribed_text,
            response=ai_response.text,
            emotion=ai_response.emotion,
            category=ai_response.category,
            learning_points=ai_response.learning_points,
        )
        await _save_conversation_data(conversation_record, child_service)

        # Step 6: Build and return response
        return _build_ai_response(
            ai_response,
            response_audio,
            transcribed_text)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process audio")


# ================== CHILD PROFILE ENDPOINTS ==================


@app.post("/api/v1/children",
          status_code=status.HTTP_201_CREATED,
          tags=["children"])
async def create_child_profile(
    request: ChildProfileRequest,
    child_service: ChildService = Depends(get_child_service),
):
    """Create a new child profile"""
    try:
        child = await child_service.create_child(
            name=request.name,
            age=request.age,
            device_id=request.device_id,
            language=request.language,
            preferences=request.preferences,
        )

        logger.info(f"Child profile created: {child.id}")
        return {
            "status": "success",
            "child_id": str(child.id),
            "device_id": request.device_id,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create child profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/children/{device_id}", tags=["children"])
async def get_child_profile(
    device_id: str, child_service: ChildService = Depends(get_child_service)
):
    """Get child profile by device ID"""
    child = await child_service.get_by_device_id(device_id)
    if not child:
        raise HTTPException(
            status_code=404,
            detail=f"No child profile found for device {device_id}")

    return child.to_dict()


# ================== WEBSOCKET ENDPOINT ==================


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, device_id: str):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        logger.info(f"WebSocket connected: {device_id}")

    def disconnect(self, device_id: str) -> None:
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            logger.info(f"WebSocket disconnected: {device_id}")

    async def send_message(self, message: str, device_id: str):
        if device_id in self.active_connections:
            await self.active_connections[device_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{device_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    device_id: str,
    ai_service: AIService = Depends(get_ai_service),
    child_service: ChildService = Depends(get_child_service),
):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, device_id)

    try:
        while True:
            data = await websocket.receive_json()

            # Process message
            if data.get("type") == "voice_message":
                child = await child_service.get_by_device_id(device_id)
                if child:
                    response = await ai_service.generate_response(
                        message=data.get("message"), child=child
                    )

                    await websocket.send_json(
                        {"type": "ai_response", "data": response.to_dict()}
                    )

    except WebSocketDisconnect:
        manager.disconnect(device_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(device_id)


# ================== ERROR HANDLERS ==================


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500, content={
            "error": "Internal server error"})


def create_app() -> FastAPI:
    """Factory function to create app instance"""
    return app


if __name__ == "__main__":
    uvicorn.run(
        "core.api.production_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        },
    )
