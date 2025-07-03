# src/infrastructure/persistence/connection_pool.py
"""
Enhanced Database Connection Pool Manager
Integrates with models.py and base.py for comprehensive database management
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, Optional

import structlog
from sqlalchemy import event, pool
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool
# Database drivers will be imported dynamically as needed
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

# Import models to ensure they're registered
from .models import Base


class DatabaseConfig:
    """Database configuration"""
    def __init__(
        self,
        url: str,
        pool_size: int = 20,
        max_overflow: int = 40,
        pool_timeout: float = 30.0,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        echo: bool = False,
        echo_pool: bool = False,
        use_native_pool: bool = True,
        **kwargs
    ):
        self.url = url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping
        self.echo = echo
        self.echo_pool = echo_pool
        self.use_native_pool = use_native_pool
        self.extra_options = kwargs


class ConnectionPool:
    """
    Advanced connection pool manager with monitoring and auto-recovery
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._pool_stats: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """Initialize the connection pool"""
        async with self._lock:
            if self._engine is not None:
                return
                
            logger.info("Initializing database connection pool", url=self.config.url)
            
            try:
                # Create engine with appropriate settings
                self._engine = await self._create_engine()
                
                # Create session factory
                self._session_factory = async_sessionmaker(
                    self._engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                
                # Test connection
                await self._test_connection()
                
                # Setup event listeners
                self._setup_event_listeners()
                
                # Start health check task
                self._health_check_task = asyncio.create_task(self._health_check_loop())
                
                logger.info("Database connection pool initialized successfully")
                
            except Exception as e:
                logger.error("Failed to initialize database connection pool", error=str(e))
                raise
    
    async def _create_engine(self) -> AsyncEngine:
        """Create database engine with appropriate configuration"""
        # Determine pool class based on database type
        if "sqlite" in self.config.url:
            pool_class = NullPool  # SQLite doesn't support connection pooling
        else:
            pool_class = AsyncAdaptedQueuePool
        
        # Engine arguments
        engine_args = {
            "echo": self.config.echo,
            "echo_pool": self.config.echo_pool,
            "pool_pre_ping": self.config.pool_pre_ping,
            "pool_recycle": self.config.pool_recycle,
            "query_cache_size": 1200,
            "future": True,
        }
        
        # Add pooling arguments for non-SQLite databases
        if pool_class != NullPool:
            engine_args.update({
                "pool_size": self.config.pool_size,
                "max_overflow": self.config.max_overflow,
                "pool_timeout": self.config.pool_timeout,
                "poolclass": pool_class,
            })
        
        # PostgreSQL specific optimizations
        if "postgresql" in self.config.url:
            if self.config.use_native_pool:
                # Use asyncpg native pool
                engine_args["connect_args"] = {
                    "server_settings": {
                        "application_name": "ai_teddy_bear",
                        "jit": "off"
                    },
                    "command_timeout": 60,
                    "min_size": 10,
                    "max_size": self.config.pool_size,
                }
        
        # MySQL specific optimizations
        elif "mysql" in self.config.url:
            engine_args["connect_args"] = {
                "charset": "utf8mb4",
                "connect_timeout": 10,
                "autocommit": False,
            }
        
        return create_async_engine(self.config.url, **engine_args)
    
    def _setup_event_listeners(self) -> None:
        """Setup SQLAlchemy event listeners for monitoring"""
        @event.listens_for(self._engine.sync_engine, "connect")
        def receive_connect(dbapi_connection, connection_record) -> Any:
            connection_record.info['connect_time'] = datetime.utcnow()
            logger.debug("New database connection established")
        
        @event.listens_for(self._engine.sync_engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy) -> Any:
            # Track checkout time
            connection_proxy._checkout_time = datetime.utcnow()
        
        @event.listens_for(self._engine.sync_engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record) -> Any:
            # Calculate connection usage time
            if hasattr(dbapi_connection, '_checkout_time'):
                duration = (datetime.utcnow() - dbapi_connection._checkout_time).total_seconds()
                if duration > 5:  # Log slow queries
                    logger.warning("Long database connection usage", duration=duration)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _test_connection(self) -> None:
        """Test database connection"""
        from sqlalchemy import text
        async with self._engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session"""
        if self._session_factory is None:
            await self.initialize()
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                logger.error(f"Database session error: {e}", exc_info=True)
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute a raw SQL query"""
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            return result.fetchall()
    
    async def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status"""
        if self._engine is None:
            return {"status": "not_initialized"}
        
        pool = self._engine.pool
        
        return {
            "status": "active",
            "size": pool.size() if hasattr(pool, 'size') else "N/A",
            "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else "N/A",
            "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else "N/A",
            "overflow": pool.overflow() if hasattr(pool, 'overflow') else "N/A",
            "total": pool.total() if hasattr(pool, 'total') else "N/A",
        }
    
    async def _health_check_loop(self) -> None:
        """Periodic health check of database connection"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Perform health check
                await self._test_connection()
                
                # Get pool statistics
                pool_status = await self.get_pool_status()
                
                # Log if pool is exhausted
                if isinstance(pool_status.get("checked_out"), int) and \
                   isinstance(pool_status.get("size"), int):
                    usage = pool_status["checked_out"] / pool_status["size"]
                    if usage > 0.8:
                        logger.warning(
                            "Database connection pool usage high",
                            usage_percent=usage * 100,
                            pool_status=pool_status
                        )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Database health check failed", error=str(e))
                # Try to recover
                try:
                    await self._recover_connection()
                except Exception as recover_error:
                    logger.error("Failed to recover database connection", error=str(recover_error))
    
    async def _recover_connection(self) -> None:
        """Attempt to recover database connection"""
        logger.info("Attempting to recover database connection")
        
        async with self._lock:
            # Dispose of current engine
            if self._engine:
                await self._engine.dispose()
            
            # Recreate engine
            self._engine = await self._create_engine()
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test new connection
            await self._test_connection()
            
        logger.info("Database connection recovered successfully")
    
    async def close(self) -> None:
        """Close the connection pool"""
        async with self._lock:
            # Cancel health check task
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Dispose of engine
            if self._engine:
                await self._engine.dispose()
                self._engine = None
                self._session_factory = None
                
            logger.info("Database connection pool closed")
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class DatabaseManager:
    """
    Manager for multiple database connections
    """
    
    def __init__(self):
        self._pools: Dict[str, ConnectionPool] = {}
        self._default_pool: Optional[str] = None
    
    def add_connection(
        self,
        name: str,
        config: DatabaseConfig,
        is_default: bool = False
    ) -> None:
        """Add a database connection"""
        self._pools[name] = ConnectionPool(config)
        if is_default or self._default_pool is None:
            self._default_pool = name
    
    async def initialize_all(self) -> None:
        """Initialize all connection pools"""
        tasks = [pool.initialize() for pool in self._pools.values()]
        await asyncio.gather(*tasks)
    
    def get_pool(self, name: Optional[str] = None) -> ConnectionPool:
        """Get a specific connection pool"""
        pool_name = name or self._default_pool
        if pool_name not in self._pools:
            raise ValueError(f"Connection pool '{pool_name}' not found")
        return self._pools[pool_name]
    
    @asynccontextmanager
    async def get_session(self, name: Optional[str] = None) -> AsyncGenerator[AsyncSession, None]:
        """Get a session from a specific pool"""
        pool = self.get_pool(name)
        async with pool.get_session() as session:
            yield session
    
    async def close_all(self) -> None:
        """Close all connection pools"""
        tasks = [pool.close() for pool in self._pools.values()]
        await asyncio.gather(*tasks)
    
    async def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all connection pools"""
        status = {}
        for name, pool in self._pools.items():
            status[name] = await pool.get_pool_status()
        return status


# Global database manager instance
db_manager = DatabaseManager()


async def setup_database(config: Dict[str, Any]) -> DatabaseManager:
    """Setup database connections from configuration"""
    # Primary database
    primary_config = DatabaseConfig(
        url=config.get("DATABASE_URL", "sqlite+aiosqlite:///./data/teddy_bear.db"),
        pool_size=config.get("DB_POOL_SIZE", 20),
        max_overflow=config.get("DB_MAX_OVERFLOW", 40),
        echo=config.get("DB_ECHO", False),
    )
    db_manager.add_connection("primary", primary_config, is_default=True)
    
    # Analytics database (if configured)
    if "ANALYTICS_DATABASE_URL" in config:
        analytics_config = DatabaseConfig(
            url=config["ANALYTICS_DATABASE_URL"],
            pool_size=10,
            max_overflow=20,
        )
        db_manager.add_connection("analytics", analytics_config)
    
    # Initialize all pools
    await db_manager.initialize_all()
    
    return db_manager