#!/usr/bin/env python3
"""
🚀 High Performance API - AI Teddy Bear Project
API عالي الأداء مع FastAPI و compression و streaming

Features:
- Async FastAPI with high-performance routing
- Response compression and streaming
- Request/response validation optimization
- Connection pooling for external services
- Background task processing with Celery
"""

import asyncio
import gzip
import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Prometheus metrics
API_REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration', ['endpoint', 'method'])
API_REQUEST_TOTAL = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method', 'status'])
API_ACTIVE_CONNECTIONS = Gauge('api_active_connections', 'Active API connections')
API_RESPONSE_SIZE = Histogram('api_response_size_bytes', 'API response size', ['endpoint'])


class OptimizedRequestModel(BaseModel):
    """Optimized request model with validation"""
    
    class Config:
        # Optimize JSON parsing
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        # Use OR mode for faster validation
        validate_assignment = False
        extra = "forbid"


class OptimizedResponseModel(BaseModel):
    """Optimized response model"""
    
    class Config:
        # Optimize JSON serialization
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        # Use OR mode for faster validation
        validate_assignment = False


class AudioStreamRequest(OptimizedRequestModel):
    """Optimized audio stream request"""
    device_id: str = Field(..., min_length=5, max_length=50)
    session_id: Optional[str] = Field(None, min_length=10, max_length=50)
    audio_format: str = Field(default="wav", regex="^(wav|mp3|ogg)$")
    sample_rate: int = Field(default=16000, ge=8000, le=48000)
    chunk_size: int = Field(default=1024, ge=512, le=8192)


class AIResponseRequest(OptimizedRequestModel):
    """Optimized AI response request"""
    message: str = Field(..., min_length=1, max_length=1000)
    child_id: str = Field(..., min_length=5, max_length=50)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    response_format: str = Field(default="text", regex="^(text|audio|both)$")


class HighPerformanceAPI:
    """High-performance API with optimization features"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.app: Optional[FastAPI] = None
        self.connection_pools: Dict[str, Any] = {}
        self.background_tasks: List[asyncio.Task] = []
        self.compression_enabled = config.get("compression_enabled", True)
        self.streaming_enabled = config.get("streaming_enabled", True)
        self.cache_enabled = config.get("cache_enabled", True)
        
    async def initialize(self) -> None:
        """Initialize high-performance API"""
        logger.info("🚀 Initializing high-performance API...")
        
        try:
            # Create FastAPI app with optimizations
            self.app = FastAPI(
                title="🧸 AI Teddy Bear High-Performance API",
                description="Optimized API with compression, streaming, and caching",
                version="4.0.0",
                docs_url="/api/docs",
                redoc_url="/api/redoc",
                # Performance optimizations
                openapi_url="/api/openapi.json" if self.config.get("openapi_enabled", True) else None,
                default_response_class=JSONResponse,
            )
            
            # Add performance middleware
            await self._setup_middleware()
            
            # Setup connection pools
            await self._setup_connection_pools()
            
            # Register routes
            await self._register_routes()
            
            # Start background tasks
            await self._start_background_tasks()
            
            logger.info("✅ High-performance API initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize high-performance API: {e}")
            raise
    
    async def _setup_middleware(self) -> None:
        """Setup performance middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get("cors_origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Compression middleware
        if self.compression_enabled:
            self.app.add_middleware(
                GZipMiddleware,
                minimum_size=1024,  # Compress responses > 1KB
            )
        
        # Custom performance middleware
        self.app.middleware("http")(self._performance_middleware)
    
    async def _performance_middleware(self, request: Request, call_next):
        """Custom performance middleware"""
        start_time = time.time()
        
        # Track active connections
        API_ACTIVE_CONNECTIONS.inc()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            API_REQUEST_DURATION.labels(
                endpoint=request.url.path,
                method=request.method
            ).observe(duration)
            
            API_REQUEST_TOTAL.labels(
                endpoint=request.url.path,
                method=request.method,
                status=response.status_code
            ).inc()
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
            
            return response
            
        except Exception as e:
            # Record error metrics
            API_REQUEST_TOTAL.labels(
                endpoint=request.url.path,
                method=request.method,
                status=500
            ).inc()
            raise
        finally:
            API_ACTIVE_CONNECTIONS.dec()
    
    async def _setup_connection_pools(self) -> None:
        """Setup connection pools for external services"""
        # Redis connection pool
        if self.config.get("redis_enabled", True):
            import aioredis
            self.connection_pools["redis"] = await aioredis.from_url(
                self.config.get("redis_url", "redis://localhost:6379"),
                max_connections=self.config.get("redis_max_connections", 100),
                decode_responses=False
            )
        
        # Database connection pool
        if self.config.get("database_enabled", True):
            from sqlalchemy.ext.asyncio import create_async_engine
            self.connection_pools["database"] = create_async_engine(
                self.config.get("database_url", "sqlite+aiosqlite:///./data/teddy_bear.db"),
                pool_size=self.config.get("database_pool_size", 20),
                max_overflow=self.config.get("database_max_overflow", 40),
                pool_pre_ping=True,
            )
        
        # HTTP client pool
        if self.config.get("http_client_enabled", True):
            import aiohttp
            connector = aiohttp.TCPConnector(
                limit=self.config.get("http_connection_limit", 100),
                limit_per_host=self.config.get("http_limit_per_host", 30),
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            self.connection_pools["http"] = aiohttp.ClientSession(connector=connector)
    
    async def _register_routes(self) -> None:
        """Register optimized API routes"""
        
        @self.app.get("/health", tags=["monitoring"])
        async def health_check():
            """Optimized health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow(),
                "version": "4.0.0",
                "performance": {
                    "compression_enabled": self.compression_enabled,
                    "streaming_enabled": self.streaming_enabled,
                    "cache_enabled": self.cache_enabled,
                }
            }
        
        @self.app.post("/api/v1/audio/stream", tags=["audio"])
        async def stream_audio(request: AudioStreamRequest):
            """High-performance audio streaming endpoint"""
            try:
                # Simulate audio processing
                audio_data = await self._process_audio_stream(request)
                
                # Return streaming response
                return StreamingResponse(
                    self._generate_audio_stream(audio_data),
                    media_type=f"audio/{request.audio_format}",
                    headers={
                        "Content-Disposition": f"attachment; filename=audio.{request.audio_format}",
                        "X-Streaming": "true"
                    }
                )
                
            except Exception as e:
                logger.error(f"Audio streaming error: {e}")
                raise HTTPException(status_code=500, detail="Audio processing failed")
        
        @self.app.post("/api/v1/ai/response", tags=["ai"])
        async def get_ai_response(request: AIResponseRequest):
            """High-performance AI response endpoint"""
            try:
                # Process AI request
                response = await self._process_ai_request(request)
                
                # Cache response if enabled
                if self.cache_enabled:
                    await self._cache_response(request, response)
                
                return response
                
            except Exception as e:
                logger.error(f"AI response error: {e}")
                raise HTTPException(status_code=500, detail="AI processing failed")
        
        @self.app.get("/api/v1/performance/metrics", tags=["monitoring"])
        async def get_performance_metrics():
            """Get performance metrics"""
            return {
                "api_performance": {
                    "active_connections": API_ACTIVE_CONNECTIONS._value.get(),
                    "compression_enabled": self.compression_enabled,
                    "streaming_enabled": self.streaming_enabled,
                    "cache_enabled": self.cache_enabled,
                },
                "connection_pools": {
                    name: "active" for name in self.connection_pools.keys()
                }
            }
    
    async def _process_audio_stream(self, request: AudioStreamRequest) -> bytes:
        """Process audio stream with optimization"""
        # Simulate audio processing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Generate mock audio data
        audio_data = b"mock_audio_data" * request.chunk_size
        
        return audio_data
    
    async def _generate_audio_stream(self, audio_data: bytes):
        """Generate streaming audio response"""
        chunk_size = 1024
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            yield chunk
            await asyncio.sleep(0.01)  # Simulate streaming delay
    
    async def _process_ai_request(self, request: AIResponseRequest) -> Dict[str, Any]:
        """Process AI request with optimization"""
        start_time = time.time()
        
        # Check cache first
        if self.cache_enabled:
            cached_response = await self._get_cached_response(request)
            if cached_response:
                return cached_response
        
        # Simulate AI processing
        await asyncio.sleep(0.05)  # Simulate AI processing time
        
        # Generate response
        response = {
            "text": f"AI response to: {request.message[:50]}...",
            "confidence": 0.95,
            "processing_time_ms": (time.time() - start_time) * 1000,
            "timestamp": datetime.utcnow(),
            "child_id": request.child_id,
        }
        
        return response
    
    async def _cache_response(self, request: AIResponseRequest, response: Dict[str, Any]) -> None:
        """Cache AI response"""
        if "redis" in self.connection_pools:
            cache_key = f"ai_response:{hash(request.message + request.child_id)}"
            cache_data = json.dumps(response).encode('utf-8')
            
            # Compress if beneficial
            if len(cache_data) > 1024 and self.compression_enabled:
                cache_data = gzip.compress(cache_data)
            
            await self.connection_pools["redis"].setex(
                cache_key, 
                300,  # 5 minutes TTL
                cache_data
            )
    
    async def _get_cached_response(self, request: AIResponseRequest) -> Optional[Dict[str, Any]]:
        """Get cached AI response"""
        if "redis" in self.connection_pools:
            cache_key = f"ai_response:{hash(request.message + request.child_id)}"
            cached_data = await self.connection_pools["redis"].get(cache_key)
            
            if cached_data:
                # Decompress if needed
                if cached_data.startswith(b'\x1f\x8b'):  # Gzip header
                    cached_data = gzip.decompress(cached_data)
                
                return json.loads(cached_data.decode('utf-8'))
        
        return None
    
    async def _start_background_tasks(self) -> None:
        """Start background tasks for optimization"""
        # Cache warming task
        if self.cache_enabled:
            task = asyncio.create_task(self._cache_warming_task())
            self.background_tasks.append(task)
        
        # Connection pool health check
        task = asyncio.create_task(self._connection_pool_health_check())
        self.background_tasks.append(task)
    
    async def _cache_warming_task(self) -> None:
        """Background task for cache warming"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                # Warm cache with frequently accessed data
                warm_data = {
                    "common_responses": [
                        "Hello! How are you today?",
                        "That's interesting! Tell me more.",
                        "Great question! Let me think about that."
                    ],
                    "system_config": {
                        "version": "4.0.0",
                        "features": ["compression", "streaming", "caching"]
                    }
                }
                
                if "redis" in self.connection_pools:
                    for key, value in warm_data.items():
                        await self.connection_pools["redis"].setex(
                            f"warm:{key}",
                            3600,  # 1 hour TTL
                            json.dumps(value).encode('utf-8')
                        )
                
                logger.info("✅ Cache warmed successfully")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache warming failed: {e}")
    
    async def _connection_pool_health_check(self) -> None:
        """Background task for connection pool health check"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Check Redis connection
                if "redis" in self.connection_pools:
                    await self.connection_pools["redis"].ping()
                
                # Check database connection
                if "database" in self.connection_pools:
                    async with self.connection_pools["database"].begin() as conn:
                        await conn.execute("SELECT 1")
                
                logger.debug("✅ Connection pools health check passed")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Connection pool health check failed: {e}")
    
    def get_app(self) -> FastAPI:
        """Get FastAPI application"""
        return self.app
    
    async def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the high-performance API server"""
        if not self.app:
            raise RuntimeError("API not initialized")
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            workers=self.config.get("workers", 1),
            loop="asyncio",
            http="httptools",
            ws="websockets",
            # Performance optimizations
            access_log=False,  # Disable access logs for performance
            log_level="info",
            # Connection optimizations
            limit_concurrency=1000,
            limit_max_requests=10000,
            timeout_keep_alive=30,
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def cleanup(self) -> None:
        """Cleanup API resources"""
        logger.info("🛑 Cleaning up high-performance API...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close connection pools
        for name, pool in self.connection_pools.items():
            if hasattr(pool, 'close'):
                await pool.close()
            elif hasattr(pool, 'dispose'):
                await pool.dispose()
        
        logger.info("✅ High-performance API cleanup complete")


# Factory function
async def create_high_performance_api(config: Dict[str, Any]) -> HighPerformanceAPI:
    """Create and initialize high-performance API"""
    api = HighPerformanceAPI(config)
    await api.initialize()
    return api 