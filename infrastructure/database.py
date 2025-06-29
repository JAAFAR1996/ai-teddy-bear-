#!/usr/bin/env python3
"""
🗄️ Database Management System
Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise-grade database management with connection pooling and migrations
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import structlog

logger = structlog.get_logger()


class Database:
    """
    🏗️ Enterprise Database Manager
    Features:
    - Connection pooling with SQLAlchemy
    - Async and sync session support
    - Database migrations
    - Health monitoring
    - Connection retry logic
    """
    
    def __init__(
        self,
        connection_string: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600
    ):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        
        # Database engines
        self.engine: Optional[Any] = None
        self.async_engine: Optional[Any] = None
        
        # Session factories
        self.session_factory: Optional[sessionmaker] = None
        self.async_session_factory: Optional[async_sessionmaker] = None
        
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections and session factories"""
        if self._initialized:
            return
        
        logger.info("🗄️ Initializing database connections", 
                   connection_string=self._mask_connection_string())
        
        try:
            # Create sync engine
            self.engine = create_engine(
                self.connection_string,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                echo=False  # Set to True for SQL debugging
            )
            
            # Create async engine (if using async SQLAlchemy)
            if self.connection_string.startswith("sqlite"):
                # For SQLite, use aiosqlite
                async_connection_string = self.connection_string.replace("sqlite://", "sqlite+aiosqlite://")
            else:
                # For PostgreSQL, use asyncpg
                async_connection_string = self.connection_string.replace("postgresql://", "postgresql+asyncpg://")
            
            self.async_engine = create_async_engine(
                async_connection_string,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle
            )
            
            # Create session factories
            self.session_factory = sessionmaker(
                bind=self.engine,
                expire_on_commit=False
            )
            
            self.async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connections
            await self._test_connections()
            
            self._initialized = True
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error("❌ Failed to initialize database", error=str(e))
            raise
    
    async def _test_connections(self):
        """Test database connections"""
        # Test sync connection
        with self.get_session() as session:
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        
        # Test async connection
        async with self.get_async_session() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        
        logger.info("✅ Database connections tested successfully")
    
    def get_session(self) -> Session:
        """Get synchronous database session"""
        if not self._initialized:
            raise RuntimeError("Database not initialized")
        
        return self.session_factory()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncSession:
        """Get asynchronous database session"""
        if not self._initialized:
            raise RuntimeError("Database not initialized")
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def run_migrations(self):
        """Run database migrations"""
        logger.info("🔄 Running database migrations...")
        
        try:
            # Create tables if they don't exist
            await self._create_tables()
            
            # Run data migrations
            await self._run_data_migrations()
            
            logger.info("✅ Database migrations completed")
            
        except Exception as e:
            logger.error("❌ Database migrations failed", error=str(e))
            raise
    
    async def _create_tables(self):
        """Create database tables"""
        from src.infrastructure.persistence.models import Base
        
        # Use sync engine for table creation
        Base.metadata.create_all(self.engine)
        logger.info("✅ Database tables created/verified")
    
    async def _run_data_migrations(self):
        """Run data migrations"""
        migrations = [
            self._migration_001_initial_data,
            self._migration_002_default_settings,
            # Add more migrations here
        ]
        
        for migration in migrations:
            try:
                await migration()
                logger.info(f"✅ Migration completed: {migration.__name__}")
            except Exception as e:
                logger.error(f"❌ Migration failed: {migration.__name__}", error=str(e))
                raise
    
    async def _migration_001_initial_data(self):
        """Migration 001: Initial data setup"""
        async with self.get_async_session() as session:
            # Check if initial data exists
            result = await session.execute(text("SELECT COUNT(*) FROM children"))
            count = result.scalar()
            
            if count == 0:
                # Insert default data
                await session.execute(text("""
                    INSERT INTO app_settings (key, value) 
                    VALUES ('app_version', '1.0.0')
                    ON CONFLICT (key) DO NOTHING
                """))
                
                logger.info("Initial data migration completed")
    
    async def _migration_002_default_settings(self):
        """Migration 002: Default application settings"""
        async with self.get_async_session() as session:
            default_settings = [
                ('max_conversation_length', '1000'),
                ('default_language', 'en'),
                ('safety_level', 'high'),
                ('ai_model_version', 'gpt-4'),
            ]
            
            for key, value in default_settings:
                await session.execute(text("""
                    INSERT INTO app_settings (key, value) 
                    VALUES (:key, :value)
                    ON CONFLICT (key) DO NOTHING
                """), {"key": key, "value": value})
            
            logger.info("Default settings migration completed")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            # Test connection
            start_time = asyncio.get_event_loop().time()
            
            async with self.get_async_session() as session:
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
            
            duration = asyncio.get_event_loop().time() - start_time
            
            # Get connection pool status
            pool_status = {
                "size": self.engine.pool.size(),
                "checked_in": self.engine.pool.checkedin(),
                "checked_out": self.engine.pool.checkedout(),
                "overflow": self.engine.pool.overflow(),
                "invalid": self.engine.pool.invalid()
            }
            
            return {
                "healthy": True,
                "response_time": duration,
                "pool_status": pool_status,
                "connection_string": self._mask_connection_string()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "connection_string": self._mask_connection_string()
            }
    
    async def close(self):
        """Close database connections"""
        logger.info("🔒 Closing database connections...")
        
        try:
            if self.engine:
                self.engine.dispose()
            
            if self.async_engine:
                await self.async_engine.dispose()
            
            self._initialized = False
            logger.info("✅ Database connections closed")
            
        except Exception as e:
            logger.error("❌ Error closing database connections", error=str(e))
    
    def _mask_connection_string(self) -> str:
        """Mask sensitive information in connection string"""
        # Hide password in connection string for logging
        if "://" in self.connection_string:
            scheme, rest = self.connection_string.split("://", 1)
            if "@" in rest:
                auth, host_db = rest.split("@", 1)
                if ":" in auth:
                    username, _ = auth.split(":", 1)
                    return f"{scheme}://{username}:***@{host_db}"
        
        return self.connection_string
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.engine:
            return {"status": "not_initialized"}
        
        pool = self.engine.pool
        
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
            "total_connections": pool.size() + pool.overflow(),
            "available_connections": pool.checkedin()
        } 