"""
🚀 AI Teddy Bear Application Entry Point
=======================================

Main application startup with Clean Architecture structure.
Sets up dependency injection, initializes adapters, and starts the application.

Architecture:
- Clean Architecture with Hexagonal Design
- Dependency Injection Container
- Event-Driven Architecture
- Comprehensive Error Handling
- Production-Ready Monitoring
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.config import ConfigFactory
from infrastructure.container import ApplicationContainer
from infrastructure.monitoring import setup_monitoring, setup_logging
from infrastructure.security import setup_security
from adapters.inbound.fastapi_app import create_fastapi_app
from adapters.inbound.websocket import setup_websocket_handlers
from adapters.inbound.grpc import setup_grpc_server
from core.application.events import EventBus


class ApplicationStartup:
    """Application startup orchestrator"""
    
    def __init__(self):
        self.container: Optional[ApplicationContainer] = None
        self.config = None
        self.logger = None

    async def initialize(self) -> None:
        """Initialize all application components"""
        try:
            # Load configuration
            self.config = ConfigFactory.create()
            
            # Setup logging
            self.logger = setup_logging(self.config.logging)
            self.logger.info("🚀 Starting AI Teddy Bear Application")
            
            # Setup security
            setup_security(self.config.security)
            
            # Setup monitoring
            setup_monitoring(self.config.monitoring)
            
            # Initialize dependency injection container
            self.container = ApplicationContainer()
            self.container.config.from_dict(self.config.to_dict())
            
            # Wire dependencies
            await self._wire_dependencies()
            
            # Initialize event bus
            await self._setup_event_bus()
            
            # Setup database
            await self._setup_database()
            
            self.logger.info("✅ Application initialized successfully")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to initialize application: {e}")
            else:
                print(f"❌ Failed to initialize application: {e}")
            raise

    async def _wire_dependencies(self) -> None:
        """Wire all dependencies in the container"""
        self.container.wire(modules=[
            "core.application.use_cases",
            "adapters.inbound.rest",
            "adapters.inbound.websocket", 
            "adapters.inbound.grpc",
            "adapters.outbound.persistence",
            "adapters.outbound.ai_services",
            "adapters.outbound.messaging"
        ])

    async def _setup_event_bus(self) -> None:
        """Setup and configure the event bus"""
        event_bus = self.container.event_bus()
        
        # Register event handlers
        from core.application.event_handlers import (
            ChildEventHandlers,
            ConversationEventHandlers,
            LearningEventHandlers,
            SafetyEventHandlers
        )
        
        await event_bus.register_handlers([
            ChildEventHandlers(),
            ConversationEventHandlers(),
            LearningEventHandlers(),
            SafetyEventHandlers()
        ])

    async def _setup_database(self) -> None:
        """Setup database connections and run migrations"""
        database_manager = self.container.database_manager()
        await database_manager.initialize()
        await database_manager.run_migrations()

    async def create_fastapi_application(self):
        """Create and configure FastAPI application"""
        return create_fastapi_app(self.container)

    async def start_websocket_server(self) -> None:
        """Start WebSocket server for real-time communication"""
        websocket_handler = setup_websocket_handlers(self.container)
        await websocket_handler.start()

    async def start_grpc_server(self) -> None:
        """Start gRPC server for high-performance communication"""
        grpc_server = setup_grpc_server(self.container)
        await grpc_server.start()

    async def shutdown(self) -> None:
        """Graceful application shutdown"""
        if self.logger:
            self.logger.info("🛑 Shutting down AI Teddy Bear Application")
        
        if self.container:
            # Close database connections
            database_manager = self.container.database_manager()
            await database_manager.close()
            
            # Stop event bus
            event_bus = self.container.event_bus()
            await event_bus.stop()
            
            # Clear container
            self.container.unwire()

        if self.logger:
            self.logger.info("✅ Application shutdown complete")


async def run_development_server():
    """Run development server with hot reload"""
    import uvicorn
    
    startup = ApplicationStartup()
    await startup.initialize()
    
    app = await startup.create_fastapi_application()
    
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    finally:
        await startup.shutdown()


async def run_production_server():
    """Run production server with all services"""
    startup = ApplicationStartup()
    await startup.initialize()
    
    # Start all services concurrently
    tasks = [
        startup.create_fastapi_application(),
        startup.start_websocket_server(),
        startup.start_grpc_server()
    ]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal")
    finally:
        await startup.shutdown()


def main():
    """Main entry point"""
    import os
    
    # Determine run mode
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development":
        print("🔧 Starting in development mode")
        asyncio.run(run_development_server())
    else:
        print("🏭 Starting in production mode")
        asyncio.run(run_production_server())


if __name__ == "__main__":
    main() 