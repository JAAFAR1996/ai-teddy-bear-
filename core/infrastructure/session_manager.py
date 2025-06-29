#!/usr/bin/env python3
"""
🎯 Clean Session Manager - SQLite + SQLAlchemy Async
Simple, production-ready session management aligned with project architecture
"""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, update, select, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class SessionStatus(Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    ENDED = "ended"
    TIMEOUT = "timeout"
    ERROR = "error"


class Session(Base):
    """
    🗃️ Session model - Clean SQLAlchemy model
    Replaces the complex Redis-based session storage
    """
    __tablename__ = "sessions"
    
    # Primary fields
    id = Column(String(36), primary_key=True)
    child_id = Column(String(36), nullable=False, index=True)
    
    # Status and timing
    status = Column(String(20), default=SessionStatus.ACTIVE.value, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Session data (JSON-like but stored as text for SQLite compatibility)
    data = Column(Text, default="{}")  # JSON string
    session_metadata = Column(Text, default="{}")  # JSON string
    
    # Activity tracking
    interaction_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Session(id='{self.id}', child_id='{self.child_id}', status='{self.status}')>"


class SessionManager:
    """
    🎯 Clean Session Manager
    
    Replaces the over-engineered system_orchestrator.py with simple, working session management
    Uses SQLite + SQLAlchemy Async for consistency with the rest of the project
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize with database session"""
        self.db = db_session
        self._active_sessions: Dict[str, Session] = {}
        self.session_timeout = timedelta(minutes=30)
        
        logger.info("SessionManager initialized with SQLite backend")
    
    async def create_session(self, child_id: str, initial_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session
        
        Args:
            child_id: ID of the child
            initial_data: Optional initial session data
            
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        
        # Prepare session data
        session_data = initial_data or {}
        session_metadata = {
            "device_type": "teddy_bear",
            "created_by": "session_manager"
        }
        
        # Create session record
        session = Session(
            id=session_id,
            child_id=child_id,
            status=SessionStatus.ACTIVE.value,
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            data=str(session_data),  # Simple string storage for SQLite
            session_metadata=str(session_metadata),
            interaction_count=0
        )
        
        # Save to database
        self.db.add(session)
        await self.db.commit()
        
        # Cache in memory for quick access
        self._active_sessions[session_id] = session
        
        logger.info(f"✅ Session created: {session_id} for child {child_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object or None if not found
        """
        # Check memory cache first
        if session_id in self._active_sessions:
            return self._active_sessions[session_id]
        
        # Query database
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        # Cache if found and active
        if session and session.status == SessionStatus.ACTIVE.value:
            self._active_sessions[session_id] = session
        
        return session
    
    async def update_activity(self, session_id: str) -> bool:
        """
        Update session activity timestamp
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if updated, False if session not found
        """
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        session.interaction_count += 1
        
        # Update in database
        await self.db.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(
                last_activity=datetime.utcnow(),
                interaction_count=Session.interaction_count + 1
            )
        )
        await self.db.commit()
        
        logger.debug(f"Activity updated for session {session_id}")
        return True
    
    async def end_session(self, session_id: str, reason: str = "manual") -> bool:
        """
        End a session
        
        Args:
            session_id: Session identifier
            reason: Reason for ending (manual, timeout, error)
            
        Returns:
            True if ended successfully, False if session not found
        """
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"Cannot end session {session_id} - not found")
            return False
        
        # Determine status based on reason
        if reason == "timeout":
            status = SessionStatus.TIMEOUT.value
        elif reason == "error":
            status = SessionStatus.ERROR.value
        else:
            status = SessionStatus.ENDED.value
        
        # Update session
        session.status = status
        session.ended_at = datetime.utcnow()
        
        # Update in database
        await self.db.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(
                status=status,
                ended_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        # Remove from memory cache
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        
        logger.info(f"✅ Session ended: {session_id}, reason: {reason}")
        return True
    
    async def get_active_sessions(self) -> List[Session]:
        """
        Get all active sessions
        
        Returns:
            List of active Session objects
        """
        result = await self.db.execute(
            select(Session).where(Session.status == SessionStatus.ACTIVE.value)
        )
        return result.scalars().all()
    
    async def get_sessions_for_child(self, child_id: str, limit: int = 10) -> List[Session]:
        """
        Get recent sessions for a child
        
        Args:
            child_id: Child identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of Session objects ordered by start time (newest first)
        """
        result = await self.db.execute(
            select(Session)
            .where(Session.child_id == child_id)
            .order_by(Session.started_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def cleanup_inactive_sessions(self) -> int:
        """
        Clean up inactive sessions (timeout old active sessions)
        
        Returns:
            Number of sessions cleaned up
        """
        cutoff_time = datetime.utcnow() - self.session_timeout
        
        # Update old active sessions to timeout
        result = await self.db.execute(
            update(Session)
            .where(Session.last_activity < cutoff_time)
            .where(Session.status == SessionStatus.ACTIVE.value)
            .values(
                status=SessionStatus.TIMEOUT.value,
                ended_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        # Clear from memory cache
        to_remove = []
        for session_id, session in self._active_sessions.items():
            if session.last_activity < cutoff_time:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self._active_sessions[session_id]
        
        cleaned_count = result.rowcount
        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} inactive sessions")
        
        return cleaned_count
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics
        
        Returns:
            Dictionary with session statistics
        """
        # Active sessions count
        active_result = await self.db.execute(
            select(Session).where(Session.status == SessionStatus.ACTIVE.value)
        )
        active_count = len(active_result.scalars().all())
        
        # Total sessions today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await self.db.execute(
            select(Session).where(Session.started_at >= today_start)
        )
        today_count = len(today_result.scalars().all())
        
        return {
            "active_sessions": active_count,
            "sessions_today": today_count,
            "memory_cache_size": len(self._active_sessions),
            "session_timeout_minutes": self.session_timeout.total_seconds() / 60
        }


# Background cleanup task (optional - can be run periodically)
async def periodic_cleanup(session_manager: SessionManager, interval_seconds: int = 300):
    """
    Periodic cleanup task - can be run in background
    
    Args:
        session_manager: SessionManager instance
        interval_seconds: Cleanup interval in seconds (default: 5 minutes)
    """
    while True:
        try:
            await session_manager.cleanup_inactive_sessions()
            await asyncio.sleep(interval_seconds)
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying 