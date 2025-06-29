#!/usr/bin/env python3
"""
🏗️ Clean Dependency Injection Container - 2025 Ready
Modern DI container using dependency-injector library with proper patterns
"""

import logging
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

try:
    # Try absolute imports first (when running from project root)
    from core.infrastructure.config import Settings
    from core.infrastructure.database.connection_pool import DatabasePool
    from core.infrastructure.caching.cache_service import CacheService
    from core.infrastructure.security.api_key_validator import APIKeyValidator
    from core.infrastructure.monitoring.metrics import MetricsCollector
    from core.infrastructure.session_manager import SessionManager
    from core.application.services.ai_service import AIServiceFactory, IAIService
    from core.application.services.voice_service import VoiceServiceFactory, IVoiceService
    from core.application.services.child_service import ChildService
    from core.application.services.emotion_service import EmotionService
    from core.domain.services.emotion_analyzer import EmotionAnalyzer
    from core.domain.repositories.child_repository import IChildRepository
    from core.infrastructure.persistence.child_sqlite_repository import ChildSQLiteRepository
except ImportError:
    # Fall back to relative imports (when running from core directory)
    from infrastructure.config import Settings
    from infrastructure.database.connection_pool import DatabasePool
    from infrastructure.caching.cache_service import CacheService
    from infrastructure.security.api_key_validator import APIKeyValidator
    from infrastructure.monitoring.metrics import MetricsCollector
    from infrastructure.session_manager import SessionManager
    from application.services.ai_service import AIServiceFactory, IAIService
    from application.services.voice_service import VoiceServiceFactory, IVoiceService
    from application.services.child_service import ChildService
    from application.services.emotion_service import EmotionService
    from domain.services.emotion_analyzer import EmotionAnalyzer
    from domain.repositories.child_repository import IChildRepository
    from infrastructure.persistence.child_sqlite_repository import ChildSQLiteRepository

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """
    🎯 Clean DI Container using dependency-injector
    
    Features:
    - Declarative provider configuration
    - No threading locks needed (async-friendly)
    - Easy testing with provider overrides
    - Clear dependency hierarchy
    - Automatic circular dependency detection
    """
    
    # Wiring configuration for automatic injection
    wiring_config = containers.WiringConfiguration(
        packages=["core.api", "core.application"],
        auto_wire=False  # Manual wiring for better control
    )
    
    # ================== CONFIGURATION ==================
    
    config = providers.Configuration()
    
    # ================== INFRASTRUCTURE LAYER ==================
    
    # Settings provider
    settings = providers.Singleton(
        Settings
    )
    
    # Database connection pool
    database_pool = providers.Singleton(
        DatabasePool,
        database_url=settings.provided.database_url
    )
    
    # Cache service
    cache_service = providers.Singleton(
        CacheService,
        settings=settings
    )
    
    # API key validator
    api_key_validator = providers.Singleton(
        APIKeyValidator,
        settings=settings
    )
    
    # Metrics collector
    metrics_collector = providers.Singleton(
        MetricsCollector
    )
    
    # Session manager (aligned with SQLite architecture)
    session_manager = providers.Factory(
        SessionManager,
        db_session=database_pool.provided.get_session
    )
    
    # ================== DOMAIN LAYER ==================
    
    # Emotion analyzer
    emotion_analyzer = providers.Singleton(
        EmotionAnalyzer,
        settings=settings
    )
    
    # Child repository
    child_repository = providers.Singleton(
        ChildSQLiteRepository,
        database_pool=database_pool
    )
    
    # ================== APPLICATION LAYER ==================
    
    # AI Service
    ai_service = providers.Singleton(
        lambda settings, cache, analyzer: AIServiceFactory.create(
            provider="openai",
            settings=settings,
            cache_service=cache,
            emotion_analyzer=analyzer
        ),
        settings=settings,
        cache=cache_service,
        analyzer=emotion_analyzer
    )
    
    # Voice Service
    voice_service = providers.Singleton(
        lambda settings, cache: VoiceServiceFactory.create(
            settings=settings,
            cache_service=cache
        ),
        settings=settings,
        cache=cache_service
    )
    
    # Child Service
    child_service = providers.Singleton(
        ChildService,
        repository=child_repository,
        cache_service=cache_service
    )
    
    # Emotion Service
    emotion_service = providers.Singleton(
        EmotionService,
        emotion_analyzer=emotion_analyzer,
        cache_service=cache_service
    )


# ================== CONTAINER INSTANCE ==================

# Global container instance (singleton)
container = Container()


# ================== CONFIGURATION HELPERS ==================

def configure_container(
    database_url: str = "sqlite+aiosqlite:///data/teddy_bear.db",
    debug: bool = False,
    **kwargs
) -> None:
    """
    Configure the DI container with settings
    
    Args:
        database_url: Database connection URL
        debug: Enable debug mode
        **kwargs: Additional configuration
    """
    config_dict = {
        "database_url": database_url,
        "debug": debug,
        **kwargs
    }
    
    container.config.from_dict(config_dict)
    logger.info(f"✅ Container configured with {len(config_dict)} settings")


def configure_from_env(prefix: str = "TEDDY", delimiter: str = "_") -> None:
    """
    Configure container from environment variables
    
    Args:
        prefix: Environment variable prefix (e.g., TEDDY_DATABASE_URL)
        delimiter: Delimiter for nested config (e.g., _ for TEDDY_API_KEY)
    """
    container.config.from_env(prefix, delimiter=delimiter)
    logger.info(f"✅ Container configured from environment ({prefix}*)")


async def initialize_container() -> None:
    """
    Initialize container resources that need async setup
    """
    try:
        logger.info("🏗️ Initializing container resources...")
        
        # Initialize database
        db_pool = container.database_pool()
        await db_pool.initialize()
        
        # Initialize cache
        cache = container.cache_service()
        await cache.connect()
        
        # Start metrics
        metrics = container.metrics_collector()
        await metrics.start()
        
        logger.info("✅ Container resources initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Container initialization failed: {e}")
        raise


async def shutdown_container() -> None:
    """
    Shutdown container resources gracefully
    """
    try:
        logger.info("🛑 Shutting down container resources...")
        
        # Stop metrics
        try:
            metrics = container.metrics_collector()
            await metrics.stop()
        except Exception as e:
            logger.warning(f"Error stopping metrics: {e}")
        
        # Disconnect cache
        try:
            cache = container.cache_service()
            await cache.disconnect()
        except Exception as e:
            logger.warning(f"Error disconnecting cache: {e}")
        
        # Close database
        try:
            db_pool = container.database_pool()
            await db_pool.close()
        except Exception as e:
            logger.warning(f"Error closing database: {e}")
        
        logger.info("✅ Container shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during container shutdown: {e}")


# ================== DEPENDENCY INJECTION DECORATORS ==================

def get_ai_service() -> IAIService:
    """Get AI service (for FastAPI Depends)"""
    return container.ai_service()


def get_voice_service() -> IVoiceService:
    """Get voice service (for FastAPI Depends)"""
    return container.voice_service()


def get_child_service() -> ChildService:
    """Get child service (for FastAPI Depends)"""
    return container.child_service()


def get_session_manager() -> SessionManager:
    """Get session manager (for FastAPI Depends)"""
    return container.session_manager()


def get_emotion_service() -> EmotionService:
    """Get emotion service (for FastAPI Depends)"""
    return container.emotion_service()


# ================== WIRE CONTAINER ==================

def wire_container(modules: list = None) -> None:
    """
    Wire the container to modules for automatic injection
    
    Args:
        modules: List of modules to wire (defaults to API modules)
    """
    if modules is None:
        modules = [
            "core.api.production_api",
            "core.application.services",
        ]
    
    try:
        container.wire(modules=modules)
        logger.info(f"✅ Container wired to {len(modules)} modules")
    except Exception as e:
        logger.error(f"❌ Container wiring failed: {e}")
        raise


def unwire_container() -> None:
    """Unwire the container (useful for testing)"""
    container.unwire()
    logger.info("🔌 Container unwired")


# ================== CONTEXT MANAGER ==================

class ContainerContext:
    """Context manager for container lifecycle"""
    
    def __init__(self, **config):
        self.config = config
    
    async def __aenter__(self):
        """Async context manager entry"""
        if self.config:
            container.config.from_dict(self.config)
        
        await initialize_container()
        return container
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await shutdown_container()


# ================== TESTING HELPERS ==================

class TestContainer:
    """Helper for testing with container overrides"""
    
    def __init__(self):
        self.overrides = []
    
    def override_ai_service(self, mock_service):
        """Override AI service for testing"""
        container.ai_service.override(mock_service)
        self.overrides.append("ai_service")
    
    def override_voice_service(self, mock_service):
        """Override voice service for testing"""
        container.voice_service.override(mock_service)
        self.overrides.append("voice_service")
    
    def override_session_manager(self, mock_manager):
        """Override session manager for testing"""
        container.session_manager.override(mock_manager)
        self.overrides.append("session_manager")
    
    def reset_overrides(self):
        """Reset all overrides"""
        for override in self.overrides:
            getattr(container, override).reset_override()
        self.overrides.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reset_overrides()


# ================== MODULE EXPORTS ==================

__all__ = [
    'Container',
    'container',
    'configure_container',
    'configure_from_env',
    'initialize_container',
    'shutdown_container',
    'wire_container',
    'unwire_container',
    'ContainerContext',
    'TestContainer',
    'get_ai_service',
    'get_voice_service',
    'get_child_service',
    'get_session_manager',
    'get_emotion_service',
    'Provide',
    'inject'
] 