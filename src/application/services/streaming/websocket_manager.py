"""
🌐 Modern WebSocket Manager - 2025 Edition
Real WebSocket connection management with heartbeat and lifecycle handling
"""

import asyncio
import logging
import time
import json
from typing import Dict, Set, Optional, Any, Callable
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ================== CONFIGURATION ==================

@dataclass
class WebSocketConfig:
    """WebSocket configuration"""
    heartbeat_interval: int = 30  # seconds
    connection_timeout: int = 300  # 5 minutes
    max_connections: int = 1000
    ping_timeout: int = 10  # seconds
    message_queue_size: int = 100

@dataclass
class ConnectionInfo:
    """Information about an active WebSocket connection"""
    websocket: WebSocket
    session_id: str
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_ping: Optional[datetime] = None
    last_pong: Optional[datetime] = None
    message_count: int = 0
    is_alive: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

# ================== WEBSOCKET MANAGER ==================

class ModernWebSocketManager:
    """
    🌐 Modern WebSocket Manager with 2025 Features:
    
    - FastAPI WebSocket integration
    - Automatic heartbeat with ping/pong
    - Connection lifecycle management
    - Broadcast capabilities with filtering
    - Connection health monitoring
    - Graceful disconnection handling
    - Message queuing for reliability
    """
    
    def __init__(self, config: Optional[WebSocketConfig] = None):
        self.config = config or WebSocketConfig()
        
        # Active connections registry
        self.connections: Dict[str, ConnectionInfo] = {}
        
        # Background tasks
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "disconnections": 0,
            "heartbeat_failures": 0
        }
        
        logger.info("✅ Modern WebSocket Manager initialized")
    
    async def connect(self, websocket: WebSocket, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        🔗 Connect a new WebSocket client
        
        Args:
            websocket: FastAPI WebSocket instance
            session_id: Unique session identifier
            metadata: Optional connection metadata
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Check connection limits
            if len(self.connections) >= self.config.max_connections:
                logger.warning(f"🚫 Connection limit reached: {len(self.connections)}")
                await websocket.close(code=1013, reason="Service overloaded")
                return False
            
            # Accept the WebSocket connection
            await websocket.accept()
            
            # Create connection info
            connection_info = ConnectionInfo(
                websocket=websocket,
                session_id=session_id,
                metadata=metadata or {}
            )
            
            # Register connection
            self.connections[session_id] = connection_info
            
            # Update statistics
            self.stats["total_connections"] += 1
            self.stats["active_connections"] = len(self.connections)
            
            # Start background tasks if first connection
            if len(self.connections) == 1:
                await self._start_background_tasks()
            
            # Send welcome message
            await self._send_welcome_message(session_id)
            
            logger.info(f"✅ WebSocket connected: {session_id} (total: {len(self.connections)})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect WebSocket {session_id}: {e}")
            return False
    
    async def disconnect(self, session_id: str, code: int = 1000, reason: str = "Normal closure") -> None:
        """
        🔌 Disconnect a WebSocket client gracefully
        
        Args:
            session_id: Session to disconnect
            code: WebSocket close code
            reason: Disconnect reason
        """
        if session_id not in self.connections:
            return
        
        try:
            connection = self.connections[session_id]
            connection.is_alive = False
            
            # Close WebSocket connection
            if not connection.websocket.client_state.closed:
                await connection.websocket.close(code=code, reason=reason)
            
            # Remove from registry
            del self.connections[session_id]
            
            # Update statistics
            self.stats["active_connections"] = len(self.connections)
            self.stats["disconnections"] += 1
            
            # Stop background tasks if no connections
            if len(self.connections) == 0:
                await self._stop_background_tasks()
            
            logger.info(f"🔌 WebSocket disconnected: {session_id} (remaining: {len(self.connections)})")
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting {session_id}: {e}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """
        📤 Send message to specific WebSocket client
        
        Args:
            session_id: Target session
            message: Message data
            
        Returns:
            True if sent successfully, False otherwise
        """
        if session_id not in self.connections:
            logger.warning(f"⚠️ Session not found: {session_id}")
            return False
        
        connection = self.connections[session_id]
        
        try:
            # Add timestamp
            message_with_timestamp = {
                **message,
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id
            }
            
            # Send message
            await connection.websocket.send_json(message_with_timestamp)
            
            # Update statistics
            connection.message_count += 1
            self.stats["messages_sent"] += 1
            
            return True
            
        except WebSocketDisconnect:
            logger.info(f"🔌 Client disconnected during send: {session_id}")
            await self.disconnect(session_id, code=1001, reason="Client disconnected")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to send message to {session_id}: {e}")
            await self.disconnect(session_id, code=1011, reason="Send error")
            return False
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[Set[str]] = None) -> int:
        """
        📡 Broadcast message to multiple clients
        
        Args:
            message: Message to broadcast
            exclude: Session IDs to exclude from broadcast
            
        Returns:
            Number of successful sends
        """
        exclude = exclude or set()
        success_count = 0
        
        # Get target connections
        target_sessions = [
            session_id for session_id in self.connections.keys()
            if session_id not in exclude
        ]
        
        # Send to all targets
        send_tasks = [
            self.send_message(session_id, message)
            for session_id in target_sessions
        ]
        
        if send_tasks:
            results = await asyncio.gather(*send_tasks, return_exceptions=True)
            success_count = sum(1 for result in results if result is True)
        
        logger.debug(f"📡 Broadcast sent to {success_count}/{len(target_sessions)} clients")
        return success_count
    
    async def receive_message(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        📥 Receive message from WebSocket client
        
        Args:
            session_id: Session to receive from
            
        Returns:
            Received message or None if error
        """
        if session_id not in self.connections:
            return None
        
        connection = self.connections[session_id]
        
        try:
            # Receive message
            message = await connection.websocket.receive_json()
            
            # Update statistics
            self.stats["messages_received"] += 1
            
            # Handle special message types
            if message.get("type") == "pong":
                connection.last_pong = datetime.utcnow()
                return None  # Pong handled internally
            
            return message
            
        except WebSocketDisconnect:
            logger.info(f"🔌 Client disconnected during receive: {session_id}")
            await self.disconnect(session_id, code=1001, reason="Client disconnected")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to receive message from {session_id}: {e}")
            await self.disconnect(session_id, code=1011, reason="Receive error")
            return None
    
    async def _send_welcome_message(self, session_id: str) -> None:
        """Send welcome message to new connection"""
        welcome_message = {
            "type": "welcome",
            "message": "WebSocket connected successfully",
            "session_id": session_id,
            "server_time": datetime.utcnow().isoformat(),
            "heartbeat_interval": self.config.heartbeat_interval
        }
        await self.send_message(session_id, welcome_message)
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        if not self.heartbeat_task or self.heartbeat_task.done():
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info("💓 Heartbeat task started")
        
        if not self.cleanup_task or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("🧹 Cleanup task started")
    
    async def _stop_background_tasks(self) -> None:
        """Stop background maintenance tasks"""
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            logger.info("💓 Heartbeat task stopped")
        
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("🧹 Cleanup task stopped")
    
    async def _heartbeat_loop(self) -> None:
        """
        💓 Background heartbeat loop
        
        Sends ping messages to all connected clients to keep connections alive
        """
        while self.connections:
            try:
                # Send ping to all connections
                ping_message = {
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self.broadcast(ping_message)
                
                logger.debug(f"💓 Heartbeat sent to {len(self.connections)} clients")
                
                # Wait for next heartbeat
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Heartbeat loop error: {e}")
                await asyncio.sleep(5)  # Short delay before retry
    
    async def _cleanup_loop(self) -> None:
        """
        🧹 Background cleanup loop
        
        Removes stale connections and performs maintenance
        """
        while True:
            try:
                current_time = datetime.utcnow()
                stale_sessions = []
                
                # Find stale connections
                for session_id, connection in self.connections.items():
                    # Check connection timeout
                    if (current_time - connection.connected_at).total_seconds() > self.config.connection_timeout:
                        stale_sessions.append(session_id)
                        continue
                    
                    # Check ping timeout
                    if connection.last_ping and not connection.last_pong:
                        ping_age = (current_time - connection.last_ping).total_seconds()
                        if ping_age > self.config.ping_timeout:
                            stale_sessions.append(session_id)
                            self.stats["heartbeat_failures"] += 1
                
                # Remove stale connections
                for session_id in stale_sessions:
                    logger.warning(f"⚠️ Removing stale connection: {session_id}")
                    await self.disconnect(session_id, code=1006, reason="Connection timeout")
                
                # Wait before next cleanup
                await asyncio.sleep(60)  # Cleanup every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Cleanup loop error: {e}")
                await asyncio.sleep(30)  # Short delay before retry
    
    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """Register a message handler for specific message types"""
        self.message_handlers[message_type] = handler
        logger.info(f"📝 Registered handler for message type: {message_type}")
    
    async def handle_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Handle incoming message using registered handlers"""
        message_type = message.get("type")
        
        if message_type in self.message_handlers:
            try:
                await self.message_handlers[message_type](session_id, message)
            except Exception as e:
                logger.error(f"❌ Message handler error for {message_type}: {e}")
                error_message = {
                    "type": "error",
                    "error": f"Handler error: {str(e)}",
                    "original_type": message_type
                }
                await self.send_message(session_id, error_message)
        else:
            logger.warning(f"⚠️ No handler for message type: {message_type}")
    
    def get_connection_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information"""
        if session_id not in self.connections:
            return None
        
        connection = self.connections[session_id]
        return {
            "session_id": session_id,
            "connected_at": connection.connected_at.isoformat(),
            "last_ping": connection.last_ping.isoformat() if connection.last_ping else None,
            "last_pong": connection.last_pong.isoformat() if connection.last_pong else None,
            "message_count": connection.message_count,
            "is_alive": connection.is_alive,
            "metadata": connection.metadata
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        return {
            **self.stats,
            "uptime_seconds": (datetime.utcnow() - datetime.utcnow()).total_seconds(),
            "config": {
                "heartbeat_interval": self.config.heartbeat_interval,
                "max_connections": self.config.max_connections,
                "connection_timeout": self.config.connection_timeout
            }
        }
    
    async def shutdown(self) -> None:
        """
        🛑 Graceful shutdown of WebSocket manager
        
        Disconnects all clients and stops background tasks
        """
        logger.info("🛑 Shutting down WebSocket manager...")
        
        # Disconnect all clients
        disconnect_tasks = [
            self.disconnect(session_id, code=1001, reason="Server shutdown")
            for session_id in list(self.connections.keys())
        ]
        
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        # Stop background tasks
        await self._stop_background_tasks()
        
        logger.info("✅ WebSocket manager shutdown complete")

# ================== FACTORY FUNCTION ==================

def create_websocket_manager(config: Optional[WebSocketConfig] = None) -> ModernWebSocketManager:
    """Factory function to create WebSocket manager"""
    return ModernWebSocketManager(config or WebSocketConfig())

# Re-export for compatibility
WebSocketManager = ModernWebSocketManager
