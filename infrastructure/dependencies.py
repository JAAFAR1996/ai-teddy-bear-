"""
🧸 AI Teddy Bear - Dependency Injection
Dependency injection container and providers
"""

from typing import AsyncGenerator, Optional, Type, TypeVar, Generic, Dict, Any
from contextlib import asynccontextmanager
from functools import lru_cache
import logging
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import redis.asyncio as redis
from fastapi import Depends, HTTPException, status

from .config import Settings, get_settings
from ..domain.models import DeviceInfo, ChildProfile


logger = logging.getLogger(__name__)

# Type variables
T = TypeVar("T")
RepositoryType = TypeVar("RepositoryType", bound="BaseRepository")


# ================== DATABASE ==================

Base = declarative_base()

class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.settings.database_url.replace("sqlite://", "sqlite+aiosqlite://"),
                echo=self.settings.debug,
                pool_size=self.settings.database_pool_size,
                pool_timeout=self.settings.database_pool_timeout,
                pool_pre_ping=True,
            )
            
            # Create session factory
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# ================== REDIS ==================

class CacheManager:
    """Redis cache manager"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis_client: Optional[redis.Redis] = None
    
    async def initialize(self):
        """Initialize Redis connection"""
        if self.settings.redis_url:
            try:
                self.redis_client = await redis.from_url(
                    self.settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                # Test connection
                await self.redis_client.ping()
                logger.info("Redis initialized successfully")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                self.redis_client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if self.redis_client:
            try:
                return await self.redis_client.get(key)
            except Exception as e:
                logger.error(f"Cache get error: {e}")
        return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        """Set value in cache"""
        if self.redis_client:
            try:
                ttl = ttl or self.settings.redis_ttl
                await self.redis_client.set(key, value, ex=ttl)
            except Exception as e:
                logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete value from cache"""
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Cache delete error: {e}")


# ================== REPOSITORY BASE ==================

class BaseRepository(ABC):
    """Base repository interface"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        pass


# ================== SERVICE REGISTRY ==================

class ServiceRegistry:
    """Service registry for dependency injection"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register(self, service_type: Type[T], implementation: T, singleton: bool = False):
        """Register a service"""
        if singleton:
            self._singletons[service_type] = implementation
        else:
            self._services[service_type] = implementation
    
    def register_factory(self, service_type: Type[T], factory):
        """Register a service factory"""
        self._factories[service_type] = factory
    
    def get(self, service_type: Type[T]) -> T:
        """Get a service instance"""
        # Check singletons first
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        # Check factories
        if service_type in self._factories:
            instance = self._factories[service_type]()
            if service_type in self._singletons:
                self._singletons[service_type] = instance
            return instance
        
        # Check regular services
        if service_type in self._services:
            return self._services[service_type]
        
        raise ValueError(f"Service {service_type} not registered")


# ================== DI CONTAINER ==================

class DIContainer:
    """Main dependency injection container"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.db_manager = DatabaseManager(settings)
        self.cache_manager = CacheManager(settings)
        self.service_registry = ServiceRegistry()
        self._initialized = False
    
    async def initialize(self):
        """Initialize all services"""
        if self._initialized:
            return
        
        # Initialize database
        await self.db_manager.initialize()
        
        # Initialize cache
        await self.cache_manager.initialize()
        
        # Register services
        self._register_services()
        
        self._initialized = True
        logger.info("DI Container initialized")
    
    async def close(self):
        """Close all services"""
        await self.db_manager.close()
        await self.cache_manager.close()
        logger.info("DI Container closed")
    
    def _register_services(self):
        """Register all services"""
        # Register repositories
        from ..services.storage_service import StorageService
        from ..services.ai_service import AIService
        from ..services.voice_service import VoiceService
        
        # Register as singletons
        self.service_registry.register(
            StorageService,
            StorageService(self.db_manager, self.cache_manager),
            singleton=True
        )
        
        self.service_registry.register(
            AIService,
            AIService(self.settings),
            singleton=True
        )
        
        self.service_registry.register(
            VoiceService,
            VoiceService(self.settings),
            singleton=True
        )
    
    def get_service(self, service_type: Type[T]) -> T:
        """Get a service instance"""
        return self.service_registry.get(service_type)
    
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async with self.db_manager.get_session() as session:
            yield session


# ================== DEPENDENCY PROVIDERS ==================

@lru_cache()
def get_container() -> DIContainer:
    """Get DI container instance"""
    settings = get_settings()
    return DIContainer(settings)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency"""
    container = get_container()
    async with container.get_db_session() as session:
        yield session


async def get_cache_manager() -> CacheManager:
    """Get cache manager dependency"""
    container = get_container()
    return container.cache_manager


def get_service(service_type: Type[T]) -> T:
    """Get service dependency"""
    container = get_container()
    return container.get_service(service_type)


# ================== AUTHENTICATION ==================

async def get_current_device(
    device_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> DeviceInfo:
    """Get current device from request"""
    # TODO: Implement device authentication
    # For now, just validate device exists
    device = await db.get(DeviceInfo, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return device


async def get_current_child(
    device_id: str,
    db: AsyncSession = Depends(get_db_session)
) -> ChildProfile:
    """Get current child profile"""
    # TODO: Implement proper child profile lookup
    # For now, return first child for device
    child = await db.query(ChildProfile).filter_by(device_id=device_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found"
        )
    return child 