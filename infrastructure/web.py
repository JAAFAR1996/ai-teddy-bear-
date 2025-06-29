#!/usr/bin/env python3
"""
🌐 FastAPI Web Application Factory
Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise web application with FastAPI
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import structlog
from typing import Dict, Any

logger = structlog.get_logger()


def create_fastapi_app(container) -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="AI Teddy Bear API",
        description="Enterprise AI Teddy Bear Platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("🌐 FastAPI application starting up...")
        # Initialize services if needed
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("🌐 FastAPI application shutting down...")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            health_checker = container.health_checker()
            health_status = await health_checker.check_all()
            
            return JSONResponse(
                content=health_status,
                status_code=200 if health_status.get("overall", {}).get("healthy", False) else 503
            )
        except Exception as e:
            return JSONResponse(
                content={"healthy": False, "error": str(e)},
                status_code=503
            )
    
    @app.get("/metrics")
    async def metrics():
        """Metrics endpoint for monitoring"""
        try:
            database = container.database()
            redis_client = container.redis_client()
            
            stats = {
                "database": await database.get_stats(),
                "redis": await redis_client.get_stats(),
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            return stats
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/conversation")
    async def start_conversation(request: Dict[str, Any]):
        """Start conversation with AI teddy"""
        try:
            ai_service = container.ai_service()
            
            message = request.get("message", "")
            child_context = request.get("child_context", {})
            
            response = await ai_service.generate_response(message, child_context)
            
            return {"response": response, "status": "success"}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app 