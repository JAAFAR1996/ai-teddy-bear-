"""
🌐 WebSocket Manager
High cohesion component for WebSocket connection management
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Set, Optional, Callable, Any
import websockets
from websockets.server import WebSocketServerProtocol

from .models import WebSocketMessage, ConnectionConfig, ProcessingResult


class WebSocketManager:
    """
    Dedicated service for WebSocket connection management.
    High cohesion: all methods work with WebSocket connections and messaging.
    """
    
    def __init__(self, config: ConnectionConfig):
        """Initialize WebSocket manager"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Connection management
        self.active_connections: Set[WebSocketServerProtocol] = set()
        self.connection_sessions: Dict[WebSocketServerProtocol, str] = {}
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.connection_count = 0
        self.total_messages_sent = 0
        self.total_messages_received = 0
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register handler for specific message type"""
        self.message_handlers[message_type] = handler
        self.logger.info(f"Registered handler for message type: {message_type}")
    
    async def start_server(self) -> None:
        """Start WebSocket server"""
        try:
            async def server():
                async with websockets.serve(
                    self.handle_client_connection,
                    self.config.host,
                    self.config.port
                ):
                    self.logger.info(f"WebSocket server started on {self.config.host}:{self.config.port}")
                    await asyncio.Future()  # run forever
            
            asyncio.create_task(server())
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    async def handle_client_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle incoming WebSocket connection from client"""
        session_id = str(uuid.uuid4())
        
        try:
            # Register connection
            await self._register_connection(websocket, session_id)
            
            # Send welcome message
            await self._send_welcome_message(websocket, session_id)
            
            # Handle messages
            await self._handle_client_messages(websocket, session_id)
            
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client disconnected: {session_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling client connection {session_id}: {e}")
            
        finally:
            await self._unregister_connection(websocket, session_id)
    
    async def _register_connection(self, websocket: WebSocketServerProtocol, session_id: str):
        """Register new connection"""
        self.active_connections.add(websocket)
        self.connection_sessions[websocket] = session_id
        self.connection_count += 1
        
        self.logger.info(f"Client connected: {session_id} (total: {len(self.active_connections)})")
    
    async def _send_welcome_message(self, websocket: WebSocketServerProtocol, session_id: str):
        """Send welcome message to new connection"""
        welcome_message = WebSocketMessage(
            type="connection",
            data={
                "status": "connected",
                "message": "Welcome to AI Teddy Bear streaming service!"
            },
            session_id=session_id
        )
        
        await self.send_message_to_client(websocket, welcome_message)
    
    async def _handle_client_messages(self, websocket: WebSocketServerProtocol, session_id: str):
        """Handle messages from a specific client"""
        async for raw_message in websocket:
            try:
                await self._process_raw_message(websocket, raw_message, session_id)
                self.total_messages_received += 1
                
            except Exception as e:
                self.logger.error(f"Error processing message from {session_id}: {e}")
                await self._send_error_message(websocket, str(e))
    
    async def _process_raw_message(self, websocket: WebSocketServerProtocol, raw_message: str, session_id: str):
        """Process raw message from client"""
        try:
            data = json.loads(raw_message)
            message_type = data.get('type')
            
            if not message_type:
                raise ValueError("Message type is required")
            
            # Create structured message
            message = WebSocketMessage(
                type=message_type,
                data=data,
                session_id=session_id
            )
            
            # Route to appropriate handler
            await self._route_message(websocket, message)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
    
    async def _route_message(self, websocket: WebSocketServerProtocol, message: WebSocketMessage):
        """Route message to appropriate handler"""
        handler = self.message_handlers.get(message.type)
        
        if handler:
            try:
                await handler(websocket, message)
            except Exception as e:
                self.logger.error(f"Error in message handler for {message.type}: {e}")
                await self._send_error_message(websocket, f"Handler error: {str(e)}")
        else:
            self.logger.warning(f"No handler registered for message type: {message.type}")
            await self._send_error_message(websocket, f"Unknown message type: {message.type}")
    
    async def _unregister_connection(self, websocket: WebSocketServerProtocol, session_id: str):
        """Unregister connection"""
        self.active_connections.discard(websocket)
        self.connection_sessions.pop(websocket, None)
        
        self.logger.info(f"Client unregistered: {session_id} (remaining: {len(self.active_connections)})")
    
    async def send_message_to_client(self, websocket: WebSocketServerProtocol, message: WebSocketMessage) -> ProcessingResult:
        """Send message to specific client"""
        try:
            json_message = json.dumps(message.to_json())
            await websocket.send(json_message)
            
            self.total_messages_sent += 1
            self.logger.debug(f"Message sent to client: {message.type}")
            
            return ProcessingResult.success_result(
                data={"message_sent": True},
                metadata={"message_type": message.type, "session_id": message.session_id}
            )
            
        except Exception as e:
            self.logger.error(f"Error sending message to client: {e}")
            return ProcessingResult.error_result(f"Failed to send message: {str(e)}")
    
    async def broadcast_message(self, message: WebSocketMessage, exclude_session: Optional[str] = None) -> ProcessingResult:
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return ProcessingResult.error_result("No active connections")
        
        successful_sends = 0
        failed_sends = 0
        
        for websocket in self.active_connections.copy():
            session_id = self.connection_sessions.get(websocket)
            
            # Skip excluded session
            if exclude_session and session_id == exclude_session:
                continue
            
            try:
                result = await self.send_message_to_client(websocket, message)
                if result.success:
                    successful_sends += 1
                else:
                    failed_sends += 1
                    
            except Exception as e:
                self.logger.error(f"Error broadcasting to session {session_id}: {e}")
                failed_sends += 1
        
        self.logger.info(f"Broadcast completed: {successful_sends} successful, {failed_sends} failed")
        
        return ProcessingResult.success_result(
            data={
                "successful_sends": successful_sends,
                "failed_sends": failed_sends,
                "total_connections": len(self.active_connections)
            }
        )
    
    async def _send_error_message(self, websocket: WebSocketServerProtocol, error_message: str):
        """Send error message to client"""
        session_id = self.connection_sessions.get(websocket, "unknown")
        
        error_msg = WebSocketMessage(
            type="error",
            data={"message": error_message},
            session_id=session_id
        )
        
        await self.send_message_to_client(websocket, error_msg)
    
    async def send_ping_to_client(self, websocket: WebSocketServerProtocol) -> ProcessingResult:
        """Send ping to specific client"""
        session_id = self.connection_sessions.get(websocket, "unknown")
        
        ping_message = WebSocketMessage(
            type="ping",
            data={"message": "ping"},
            session_id=session_id
        )
        
        return await self.send_message_to_client(websocket, ping_message)
    
    async def close_all_connections(self):
        """Close all active connections"""
        for websocket in self.active_connections.copy():
            try:
                await websocket.close()
            except Exception as e:
                self.logger.error(f"Error closing connection: {e}")
        
        self.active_connections.clear()
        self.connection_sessions.clear()
        
        self.logger.info("All WebSocket connections closed")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "service_name": "WebSocketManager",
            "active_connections": len(self.active_connections),
            "total_connections": self.connection_count,
            "messages_sent": self.total_messages_sent,
            "messages_received": self.total_messages_received,
            "server_config": {
                "host": self.config.host,
                "port": self.config.port
            },
            "high_cohesion": True,
            "responsibility": "WebSocket connection management and messaging"
        }
    
    def get_session_for_websocket(self, websocket: WebSocketServerProtocol) -> Optional[str]:
        """Get session ID for a specific WebSocket connection"""
        return self.connection_sessions.get(websocket)
    
    async def send_audio_response(
        self, 
        websocket: WebSocketServerProtocol, 
        audio_data: bytes,
        original_text: str,
        response_text: str,
        audio_format: str = "mp3"
    ) -> ProcessingResult:
        """Send audio response to client"""
        import base64
        
        session_id = self.connection_sessions.get(websocket, "unknown")
        
        audio_message = WebSocketMessage(
            type="audio",
            data={
                "audio": base64.b64encode(audio_data).decode("utf-8"),
                "format": audio_format,
                "text": original_text,
                "response": response_text,
                "timestamp": message.timestamp.isoformat()
            },
            session_id=session_id
        )
        
        return await self.send_message_to_client(websocket, audio_message) 