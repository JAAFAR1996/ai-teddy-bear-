"""
🧸 AI Teddy Bear - Production System v2.0
نظام إنتاج الدب الذكي المحسن - معايير 2025
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from infrastructure.config import get_settings
from infrastructure.dependencies import get_container
from api.endpoints.device import router as device_router
from api.endpoints.audio import router as audio_router
from api.endpoints.children import router as children_router
from api.endpoints.dashboard import router as dashboard_router
from api.websocket.manager import WebSocketManager


# Initialize settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=settings.log_level.value,
    format=settings.log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/{settings.environment.value}.log")
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting AI Teddy Bear Production System v2.0...")
    
    # Initialize DI container
    container = get_container()
    await container.initialize()
    
    # Initialize WebSocket manager
    websocket_manager = WebSocketManager()
    app.state.websocket_manager = websocket_manager
    
    logger.info("✅ System initialized successfully!")
    
    yield
    
    # Cleanup
    logger.info("🔄 Shutting down system...")
    await container.close()
    logger.info("✅ System shutdown complete!")


# Create FastAPI application
app = FastAPI(
    title="🧸 AI Teddy Bear Production API",
    description="Complete production-ready AI Teddy Bear system with 2025 standards",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment.value == "development" else None,
    redoc_url="/redoc" if settings.environment.value == "development" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    **settings.get_cors_config()
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.environment.value,
        "timestamp": asyncio.get_event_loop().time()
    }

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "🧸 AI Teddy Bear Production System v2.0",
        "status": "running",
        "docs": "/docs" if settings.environment.value == "development" else "disabled",
        "version": "2.0.0"
    }

# Include routers
app.include_router(device_router, prefix="/api/devices", tags=["devices"])
app.include_router(audio_router, prefix="/api/audio", tags=["audio"])
app.include_router(children_router, prefix="/api/children", tags=["children"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


def main():
    """Main application entry point"""
    # Ensure log directory exists
    Path("logs").mkdir(exist_ok=True)
    
    logger.info(f"🚀 Starting AI Teddy Bear System v2.0")
    logger.info(f"Environment: {settings.environment.value}")
    logger.info(f"Host: {settings.host}:{settings.port}")
    
    # Run server
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers if settings.environment.value == "production" else 1,
        reload=settings.environment.value == "development",
        log_level=settings.log_level.value.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main() 