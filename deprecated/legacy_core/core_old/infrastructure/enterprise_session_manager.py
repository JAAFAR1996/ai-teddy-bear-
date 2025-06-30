"""
Enterprise Session Manager
Production-ready session management with Redis fallback to memory
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set
from uuid import uuid4

import structlog

logger = structlog.get_logger()


class EnterpriseSessionManager:
    """
    Enterprise session manager with Redis support and memory fallback
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.redis_client = None
        self.memory_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_expiry: Dict[str, float] = {}
        self.default_ttl = 3600  # 1 hour
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """Initialize session manager"""
        try:
            if self.redis_url:
                # Try to connect to Redis
                import redis.asyncio as redis
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("Redis session manager initialized", url=self.redis_url)
            else:
                raise Exception("Redis URL not provided")
        except Exception as e:
            logger.warning("Redis not available, using memory sessions", error=str(e))
            self.redis_client = None
            
        # Start cleanup task for memory sessions
        if not self.redis_client:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
            
        logger.info("Enterprise Session Manager initialized", 
                   backend="redis" if self.redis_client else "memory")
    
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new session"""
        session_id = str(uuid4())
        session_data.update({
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "access_count": 1
        })
        
        if self.redis_client:
            await self.redis_client.setex(
                f"session:{session_id}",
                self.default_ttl,
                json.dumps(session_data)
            )
        else:
            self.memory_sessions[session_id] = session_data
            self.session_expiry[session_id] = time.time() + self.default_ttl
            
        logger.info("Session created", session_id=session_id)
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        try:
            if self.redis_client:
                data = await self.redis_client.get(f"session:{session_id}")
                if data:
                    session_data = json.loads(data)
                    # Update last accessed
                    session_data["last_accessed"] = datetime.utcnow().isoformat()
                    session_data["access_count"] = session_data.get("access_count", 0) + 1
                    await self.redis_client.setex(
                        f"session:{session_id}",
                        self.default_ttl,
                        json.dumps(session_data)
                    )
                    return session_data
            else:
                if session_id in self.memory_sessions:
                    if time.time() < self.session_expiry[session_id]:
                        session_data = self.memory_sessions[session_id]
                        session_data["last_accessed"] = datetime.utcnow().isoformat()
                        session_data["access_count"] = session_data.get("access_count", 0) + 1
                        # Extend expiry
                        self.session_expiry[session_id] = time.time() + self.default_ttl
                        return session_data
                    else:
                        # Session expired
                        del self.memory_sessions[session_id]
                        del self.session_expiry[session_id]
                        
        except Exception as e:
            logger.error("Error getting session", session_id=session_id, error=str(e))
            
        return None
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            session_data = await self.get_session(session_id)
            if session_data:
                session_data.update(data)
                session_data["last_accessed"] = datetime.utcnow().isoformat()
                
                if self.redis_client:
                    await self.redis_client.setex(
                        f"session:{session_id}",
                        self.default_ttl,
                        json.dumps(session_data)
                    )
                else:
                    self.memory_sessions[session_id] = session_data
                    self.session_expiry[session_id] = time.time() + self.default_ttl
                    
                logger.debug("Session updated", session_id=session_id)
                return True
                
        except Exception as e:
            logger.error("Error updating session", session_id=session_id, error=str(e))
            
        return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            if self.redis_client:
                result = await self.redis_client.delete(f"session:{session_id}")
                success = result > 0
            else:
                success = session_id in self.memory_sessions
                if success:
                    del self.memory_sessions[session_id]
                    if session_id in self.session_expiry:
                        del self.session_expiry[session_id]
                        
            if success:
                logger.info("Session deleted", session_id=session_id)
            return success
            
        except Exception as e:
            logger.error("Error deleting session", session_id=session_id, error=str(e))
            return False
    
    async def get_active_sessions(self) -> Set[str]:
        """Get all active session IDs"""
        try:
            if self.redis_client:
                keys = await self.redis_client.keys("session:*")
                return {key.decode().split(":", 1)[1] for key in keys}
            else:
                current_time = time.time()
                active_sessions = set()
                for session_id, expiry_time in self.session_expiry.items():
                    if current_time < expiry_time:
                        active_sessions.add(session_id)
                return active_sessions
                
        except Exception as e:
            logger.error("Error getting active sessions", error=str(e))
            return set()
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            active_sessions = await self.get_active_sessions()
            
            return {
                "total_active_sessions": len(active_sessions),
                "backend": "redis" if self.redis_client else "memory",
                "redis_connected": self.redis_client is not None,
                "default_ttl_seconds": self.default_ttl,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Error getting session stats", error=str(e))
            return {"error": str(e)}
    
    async def _cleanup_expired_sessions(self) -> None:
        """Background task to clean expired memory sessions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                current_time = time.time()
                expired_sessions = [
                    session_id for session_id, expiry_time in self.session_expiry.items()
                    if current_time >= expiry_time
                ]
                
                for session_id in expired_sessions:
                    if session_id in self.memory_sessions:
                        del self.memory_sessions[session_id]
                    if session_id in self.session_expiry:
                        del self.session_expiry[session_id]
                        
                if expired_sessions:
                    logger.info("Cleaned expired sessions", count=len(expired_sessions))
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in session cleanup", error=str(e))
    
    async def shutdown(self) -> None:
        """Shutdown session manager"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
        if self.redis_client:
            await self.redis_client.close()
            
        logger.info("Enterprise Session Manager shutdown") 