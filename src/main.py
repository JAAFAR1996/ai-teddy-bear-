from typing import Any, Dict, List, Optional

#!/usr/bin/env python3
"""
🚀 AI Teddy Bear - Unified Application Entry Point
Lead Architect: جعفر أديب (Jaafar Adeeb)
Senior Backend Developer & Professor

Enterprise-grade application bootstrap with:
- Unified IoC Container with dependency-injector
- Comprehensive health checks and migrations
- Prometheus metrics server
- Multi-server concurrent startup (GraphQL, WebSocket, gRPC)
- Graceful shutdown and error handling
- Vault integration for secrets management
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

import structlog
from dependency_injector import containers, providers
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
STARTUP_TIME = Histogram('app_startup_duration_seconds',
                         'Application startup time')
HEALTH_CHECK_FAILURES = Counter(
    'app_health_check_failures_total', 'Health check failures', ['service'])
ACTIVE_CONNECTIONS = Gauge('app_active_connections',
                           'Active connections', ['server_type'])
SERVICE_STATUS = Gauge('app_service_status', 'Service status', ['service'])


class Container(containers.DeclarativeContainer):
    """
    🏗️ Enterprise IoC Container
    Advanced dependency injection with lifecycle management
    """

    # Configuration provider
    config = providers.Configuration()

    # ================== INFRASTRUCTURE LAYER ==================

    # Database connection
    database = providers.Singleton(
        "infrastructure.database.Database",
        connection_string=config.database.url,
        pool_size=config.database.pool_size.as_int(),
        max_overflow=config.database.max_overflow.as_int()
    )

    # Vault client for secrets management
    vault_client = providers.Singleton(
        "infrastructure.vault.VaultClient",
        url=config.vault.url,
        token=config.vault.token
    )

    # Redis cache
    redis_client = providers.Singleton(
        "infrastructure.cache.RedisClient",
        url=config.redis.url,
        max_connections=config.redis.max_connections.as_int()
    )

    # Message broker
    message_broker = providers.Singleton(
        "infrastructure.messaging.MessageBroker",
        broker_url=config.messaging.broker_url
    )

    # ================== DOMAIN REPOSITORIES ==================

    # Child repository
    child_repository = providers.Factory(
        "src.domain.entities.child_repository.ChildRepository",
        session_factory=database.provided.get_session
    )

    # Conversation repository
    conversation_repository = providers.Factory(
        "src.infrastructure.persistence.repositories.conversation_repository.ConversationRepository",
        session_factory=database.provided.get_session
    )

    # ================== APPLICATION SERVICES ==================

    # Enhanced Audio Processor - 2025 Edition
    enhanced_audio_processor = providers.Singleton(
        "src.infrastructure.audio.enhanced_audio_processor.EnhancedAudioProcessor"
    )

    # Advanced AI Orchestrator - 2025 Edition
    advanced_ai_orchestrator = providers.Singleton(
        "src.infrastructure.ai.advanced_ai_orchestrator.AdvancedAIOrchestrator"
    )

    # Advanced Content Filter - 2025 Edition
    advanced_content_filter = providers.Singleton(
        "src.infrastructure.security.advanced_content_filter.AdvancedContentFilter"
    )

    # AI service with vault-managed API keys
    ai_service = providers.Factory(
        "infrastructure.ai.AIService",
        openai_api_key=vault_client.provided.get_secret("openai_api_key"),
        anthropic_api_key=vault_client.provided.get_secret("anthropic_api_key")
    )

    # Speech service
    speech_service = providers.Factory(
        "infrastructure.ai.SpeechService",
        elevenlabs_api_key=vault_client.provided.get_secret(
            "elevenlabs_api_key")
    )

    # Emotion analysis service
    emotion_service = providers.Factory(
        "infrastructure.ai.EmotionService",
        hume_api_key=vault_client.provided.get_secret("hume_api_key")
    )

    # ================== COMMAND/QUERY HANDLERS ==================

    # Command bus
    command_bus = providers.Singleton(
        "src.application.commands.command_bus.CommandBus"
    )

    # Query bus
    query_bus = providers.Singleton(
        "src.application.queries.query_bus.QueryBus"
    )

    # ================== PRESENTATION LAYER ==================

    # FastAPI application
    fastapi_app = providers.Factory(
        "infrastructure.web.create_fastapi_app",
        container=providers.Self()
    )

    # WebSocket handler
    websocket_handler = providers.Factory(
        "infrastructure.websocket.WebSocketHandler",
        container=providers.Self()
    )

    # gRPC server
    grpc_server = providers.Factory(
        "infrastructure.grpc.GRPCServer",
        container=providers.Self()
    )

    # GraphQL server
    graphql_server = providers.Factory(
        "infrastructure.graphql.GraphQLServer",
        container=providers.Self()
    )

    # ================== MONITORING & HEALTH ==================

    # Health checker
    health_checker = providers.Singleton(
        "infrastructure.health.HealthChecker",
        container=providers.Self()
    )

    # Metrics collector
    metrics_collector = providers.Singleton(
        "infrastructure.metrics.MetricsCollector"
    )


class Application:
    """
    🎯 Main Application Class
    Orchestrates startup, health checks, and graceful shutdown
    """

    def __init__(self):
        self.container = Container()
        self.servers = []
        self.shutdown_event = asyncio.Event()

        # Load configuration from environment
        self._load_configuration()

        # Setup signal handlers
        self._setup_signal_handlers()

    def _load_configuration(self) -> Any:
        """Load configuration from environment variables"""
        config = {
            "database": {
                "url": "sqlite:///ai_teddy.db",
                "pool_size": 10,
                "max_overflow": 20
            },
            "vault": {
                "url": "http://localhost:8200",
                "token": "dev-token"
            },
            "redis": {
                "url": "redis://localhost:6379/0",
                "max_connections": 10
            },
            "messaging": {
                "broker_url": "redis://localhost:6379/1"
            },
            "servers": {
                "fastapi_port": 8000,
                "websocket_port": 8765,
                "grpc_port": 50051,
                "graphql_port": 8080,
                "metrics_port": 9090
            }
        }

        self.container.config.from_dict(config)

    def _setup_signal_handlers(self) -> Any:
        """Setup graceful shutdown signal handlers"""
        if sys.platform != 'win32':
            for sig in (signal.SIGTERM, signal.SIGINT):
                signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum, frame) -> Any:
        """Handle shutdown signals"""
        logger.info("Received shutdown signal", signal=signum)
        self.shutdown_event.set()

    @STARTUP_TIME.time()
    async def startup(self):
        """
        🚀 Application startup sequence
        1. Health checks
        2. Database migrations  
        3. Metrics server
        4. Service initialization
        """
        logger.info("🚀 Starting AI Teddy Bear Application...")

        try:
            # Step 1: Run health checks
            await self._run_health_checks()

            # Step 2: Run database migrations
            await self._run_migrations()

            # Step 3: Start metrics server
            self._start_metrics_server()

            # Step 4: Initialize services
            await self._initialize_services()

            logger.info("✅ Application startup completed successfully")

        except Exception as e:
            logger.error("❌ Application startup failed", error=str(e))
            raise

    async def _run_health_checks(self):
        """Run comprehensive health checks"""
        logger.info("🏥 Running health checks...")

        health_checker = self.container.health_checker()
        health_status = await health_checker.check_all()

        failed_checks = [
            service for service, status in health_status.items()
            if not status["healthy"]
        ]

        if failed_checks:
            logger.error("Health checks failed", failed_services=failed_checks)
            for service in failed_checks:
                HEALTH_CHECK_FAILURES.labels(service=service).inc()
            raise RuntimeError(f"Health checks failed for: {failed_checks}")

        logger.info("✅ All health checks passed")

        # Update service status metrics
        for service, status in health_status.items():
            SERVICE_STATUS.labels(service=service).set(
                1 if status["healthy"] else 0)

    async def _run_migrations(self):
        """Run database migrations"""
        logger.info("🗄️ Running database migrations...")

        try:
            database = self.container.database()
            await database.run_migrations()
            logger.info("✅ Database migrations completed")

        except Exception as e:
            logger.error("❌ Database migrations failed", error=str(e))
            raise

    def _start_metrics_server(self) -> Any:
        """Start Prometheus metrics server"""
        metrics_port = self.container.config()["servers"]["metrics_port"]

        logger.info("📊 Starting metrics server", port=metrics_port)
        start_http_server(metrics_port)
        logger.info("✅ Metrics server started")

    async def _initialize_services(self):
        """Initialize all application services"""
        logger.info("⚙️ Initializing services...")

        # Initialize Enhanced Components - 2025 Edition
        try:
            enhanced_audio_processor = self.container.enhanced_audio_processor()
            logger.info("✅ Enhanced Audio Processor initialized")

            advanced_ai_orchestrator = self.container.advanced_ai_orchestrator()
            logger.info("✅ Advanced AI Orchestrator initialized")

            advanced_content_filter = self.container.advanced_content_filter()
            logger.info("✅ Advanced Content Filter initialized")

        except Exception as e:
            logger.warning(
                f"⚠️ Enhanced components initialization failed: {e}")
            logger.info("🔄 Falling back to basic components")

        # Initialize AI services
        try:
            ai_service = self.container.ai_service()
            await ai_service.initialize()
            logger.info("✅ AI Service initialized")
        except Exception as e:
            logger.warning(f"⚠️ AI service initialization failed: {e}")

        # Initialize speech service
        try:
            speech_service = self.container.speech_service()
            await speech_service.initialize()
            logger.info("✅ Speech Service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Speech service initialization failed: {e}")

        # Initialize emotion service
        try:
            emotion_service = self.container.emotion_service()
            await emotion_service.initialize()
            logger.info("✅ Emotion Service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Emotion service initialization failed: {e}")

        # Initialize command/query buses
        try:
            command_bus = self.container.command_bus()
            await command_bus.initialize()

            query_bus = self.container.query_bus()
            await query_bus.initialize()

            logger.info("✅ Command/Query buses initialized")
        except Exception as e:
            logger.warning(f"⚠️ Buses initialization failed: {e}")

        logger.info("✅ All services initialized with Enhanced 2025 Components")

    async def run(self):
        """
        🏃 Main application run loop
        Starts all servers concurrently and waits for shutdown signal
        """
        try:
            # Run startup sequence
            await self.startup()

            # Start all servers concurrently
            server_tasks = await asyncio.gather(
                self._run_fastapi_server(),
                self._run_websocket_server(),
                self._run_grpc_server(),
                self._run_graphql_server(),
                return_exceptions=True
            )

            # Wait for shutdown signal
            await self.shutdown_event.wait()

        except KeyboardInterrupt:
            logger.info("🛑 Received keyboard interrupt")
        except Exception as e:
            logger.error("💥 Application run failed", error=str(e))
            raise
        finally:
            await self._shutdown()

    async def _run_fastapi_server(self):
        """Start FastAPI server"""
        import uvicorn

        config = self.container.config()
        port = config["servers"]["fastapi_port"]

        logger.info("🌐 Starting FastAPI server", port=port)

        app = self.container.fastapi_app()

        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",  # SECURITY: Bind to localhost only
            port=port,
            log_level="info",
            access_log=True
        )

        server = uvicorn.Server(config)
        ACTIVE_CONNECTIONS.labels(server_type="fastapi").set(1)

        try:
            await server.serve()
        finally:
            ACTIVE_CONNECTIONS.labels(server_type="fastapi").set(0)

    async def _run_websocket_server(self):
        """Start WebSocket server"""
        import websockets

        config = self.container.config()
        port = config["servers"]["websocket_port"]

        logger.info("⚡ Starting WebSocket server", port=port)

        handler = self.container.websocket_handler()

        ACTIVE_CONNECTIONS.labels(server_type="websocket").set(1)

        try:
            async with websockets.serve(handler.handle_connection, "0.0.0.0", port):
                await self.shutdown_event.wait()
        finally:
            ACTIVE_CONNECTIONS.labels(server_type="websocket").set(0)

    async def _run_grpc_server(self):
        """Start gRPC server"""
        config = self.container.config()
        port = config["servers"]["grpc_port"]

        logger.info("🔧 Starting gRPC server", port=port)

        server = self.container.grpc_server()

        ACTIVE_CONNECTIONS.labels(server_type="grpc").set(1)

        try:
            await server.start(port)
            await self.shutdown_event.wait()
        finally:
            await server.stop()
            ACTIVE_CONNECTIONS.labels(server_type="grpc").set(0)

    async def _run_graphql_server(self):
        """Start GraphQL server"""
        config = self.container.config()
        port = config["servers"]["graphql_port"]

        logger.info("📊 Starting GraphQL server", port=port)

        server = self.container.graphql_server()

        ACTIVE_CONNECTIONS.labels(server_type="graphql").set(1)

        try:
            await server.start(port)
            await self.shutdown_event.wait()
        finally:
            await server.stop()
            ACTIVE_CONNECTIONS.labels(server_type="graphql").set(0)

    async def _shutdown(self):
        """
        🛑 Graceful application shutdown
        """
        logger.info("🛑 Starting graceful shutdown...")

        try:
            # Cleanup Enhanced Components - 2025 Edition
            try:
                enhanced_audio_processor = self.container.enhanced_audio_processor()
                await enhanced_audio_processor.cleanup()

                advanced_ai_orchestrator = self.container.advanced_ai_orchestrator()
                await advanced_ai_orchestrator.cleanup()

                advanced_content_filter = self.container.advanced_content_filter()
                await advanced_content_filter.cleanup()

                logger.info("✅ Enhanced components cleaned up")
            except Exception as e:
                logger.warning(f"⚠️ Enhanced components cleanup failed: {e}")

            # Close database connections
            try:
                database = self.container.database()
                await database.close()
            except Exception as e:
                logger.warning(f"⚠️ Database closure failed: {e}")

            # Close Redis connections
            try:
                redis_client = self.container.redis_client()
                await redis_client.close()
            except Exception as e:
                logger.warning(f"⚠️ Redis closure failed: {e}")

            # Close message broker
            try:
                message_broker = self.container.message_broker()
                await message_broker.close()
            except Exception as e:
                logger.warning(f"⚠️ Message broker closure failed: {e}")

            # Reset metrics
            for server_type in ["fastapi", "websocket", "grpc", "graphql"]:
                ACTIVE_CONNECTIONS.labels(server_type=server_type).set(0)

            logger.info(
                "✅ Graceful shutdown completed with Enhanced 2025 Components")

        except Exception as e:
            logger.error("❌ Error during shutdown", error=str(e))


def main() -> Any:
    """
    🎯 Main entry point
    Creates and runs the application
    """
    logger.info("🧸 AI Teddy Bear - Enterprise Application")
    logger.info("👨‍💻 Lead Architect: جعفر أديب (Jaafar Adeeb)")
    logger.info("🏆 Senior Backend Developer & Professor")
    logger.info("=" * 50)

    app = Application()

    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.info("\n🛑 Application stopped by user")
    except Exception as e:
        logger.error(f"\n💥 Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
