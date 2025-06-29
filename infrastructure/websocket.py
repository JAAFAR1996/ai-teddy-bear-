#!/usr/bin/env python3
"""
⚡ WebSocket Handler
Lead Architect: جعفر أديب (Jaafar Adeeb)
Real-time communication with WebSocket
"""

import asyncio
import json
import websockets
from typing import Dict, Any, Set
import structlog

logger = structlog.get_logger()


class WebSocketHandler:
    """Enterprise WebSocket handler for real-time communication"""
    
    def __init__(self, container):
        self.container = container
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
    
    async def handle_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        logger.info("⚡ New WebSocket connection", path=path)
        
        self.connected_clients.add(websocket)
        
        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error("WebSocket error", error=str(e))
        finally:
            self.connected_clients.discard(websocket)
    
    async def _handle_message(self, websocket, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "conversation":
                await self._handle_conversation_message(websocket, data)
            elif message_type == "health_check":
                await self._handle_health_check(websocket)
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON format"
            }))
        except Exception as e:
            logger.error("Error handling WebSocket message", error=str(e))
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))
    
    async def _handle_conversation_message(self, websocket, data: Dict[str, Any]):
        """Handle conversation message"""
        try:
            ai_service = self.container.ai_service()
            
            message = data.get("message", "")
            child_context = data.get("child_context", {})
            
            response = await ai_service.generate_response(message, child_context)
            
            await websocket.send(json.dumps({
                "type": "conversation_response",
                "response": response,
                "timestamp": "2024-01-01T00:00:00Z"
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))
    
    async def _handle_health_check(self, websocket):
        """Handle health check request"""
        try:
            health_checker = self.container.health_checker()
            health_status = await health_checker.check_all()
            
            await websocket.send(json.dumps({
                "type": "health_status",
                "status": health_status
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.connected_clients:
            return
        
        message_json = json.dumps(message)
        
        # Send to all connected clients
        tasks = []
        for websocket in self.connected_clients.copy():
            tasks.append(self._safe_send(websocket, message_json))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_send(self, websocket, message: str):
        """Safely send message to WebSocket"""
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            self.connected_clients.discard(websocket)
        except Exception as e:
            logger.error("Error sending WebSocket message", error=str(e))
            self.connected_clients.discard(websocket) 