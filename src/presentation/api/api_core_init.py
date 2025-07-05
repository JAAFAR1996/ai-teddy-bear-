"""
API Router for AI Teddy Bear System
Updated to include new voice processing and reporting endpoints
"""
import structlog

logger = structlog.get_logger(__name__)


from fastapi import APIRouter

from .endpoints import voice  # New voice endpoints
from .endpoints import (advanced, audio, children, conversations, system,
                        teddy_hardware)

# Create main API router
api_router = APIRouter(prefix="/api", tags=["API"])

# Include all endpoint routers
api_router.include_router(voice.router)  # New voice processing
api_router.include_router(children.router)
api_router.include_router(conversations.router)
api_router.include_router(system.router)
api_router.include_router(teddy_hardware.router)
api_router.include_router(advanced.router)

# Legacy endpoints (if still needed)
try:
    api_router.include_router(audio.router)
except Exception as e:
    logger.error(f"Error: {e}")f"⚠️ Legacy audio router not available: {e}")

# Health check endpoint
@api_router.get("/health")
async def api_health():
    """API health check"""
    return {
        "status": "healthy",
        "version": "2.0",
        "features": [
            "advanced_emotion_analysis",
            "voice_processing", 
            "parent_reports",
            "secure_esp32_communication"
        ]
    }