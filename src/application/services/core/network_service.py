"""
Network Communication Service - Handles communication with ESP32 devices
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionStatus(str, Enum):
    """Network connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"


class NetworkMessage:
    """Network message model"""
    
    def __init__(self, message_type: str, data: Dict[str, Any], device_id: str):
        self.message_type = message_type
        self.data = data
        self.device_id = device_id
        self.timestamp = datetime.utcnow()
        self.message_id = f"{device_id}_{self.timestamp.timestamp()}"


class CloudNetworkService:
    """Service for handling network communication with ESP32 devices."""

    def __init__(self):
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        logger.info("CloudNetworkService initialized")

    async def handle_device_connection(
        self, 
        device_id: str, 
        connection_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle new device connection
        
        Args:
            device_id: ESP32 device identifier
            connection_info: Connection details
            
        Returns:
            Connection acknowledgment
        """
        try:
            # Store connection info
            self.active_connections[device_id] = {
                "status": ConnectionStatus.CONNECTED,
                "connected_at": datetime.utcnow(),
                "ip_address": connection_info.get("ip_address"),
                "firmware_version": connection_info.get("firmware_version"),
                "last_heartbeat": datetime.utcnow()
            }
            
            logger.info(f"Device connected: {device_id}")
            
            return {
                "status": "connected",
                "device_id": device_id,
                "server_time": datetime.utcnow().isoformat(),
                "heartbeat_interval": 30  # seconds
            }
            
        except Exception as e:
            logger.error(f"Connection handling failed for {device_id}: {str(e)}")
            raise

    async def handle_device_disconnection(self, device_id: str) -> bool:
        """Handle device disconnection"""
        try:
            if device_id in self.active_connections:
                del self.active_connections[device_id]
                logger.info(f"Device disconnected: {device_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Disconnection handling failed for {device_id}: {str(e)}")
            return False

    async def send_message_to_device(
        self, 
        device_id: str, 
        message: NetworkMessage
    ) -> bool:
        """
        Send message to specific device
        
        Args:
            device_id: Target device ID
            message: Message to send
            
        Returns:
            Success status
        """
        try:
            if device_id not in self.active_connections:
                logger.warning(f"Cannot send message to offline device: {device_id}")
                return False
            
            # In real implementation, this would send via WebSocket/HTTP
            logger.info(f"Sending message to {device_id}: {message.message_type}")
            
            # Update last communication time
            self.active_connections[device_id]["last_communication"] = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Message sending failed to {device_id}: {str(e)}")
            return False

    async def broadcast_message(
        self, 
        message: NetworkMessage, 
        exclude_devices: List[str] = None
    ) -> int:
        """
        Broadcast message to all connected devices
        
        Args:
            message: Message to broadcast
            exclude_devices: Devices to exclude from broadcast
            
        Returns:
            Number of devices reached
        """
        try:
            exclude_devices = exclude_devices or []
            sent_count = 0
            
            for device_id in self.active_connections:
                if device_id not in exclude_devices:
                    if await self.send_message_to_device(device_id, message):
                        sent_count += 1
            
            logger.info(f"Broadcast message sent to {sent_count} devices")
            return sent_count
            
        except Exception as e:
            logger.error(f"Broadcast failed: {str(e)}")
            return 0

    async def update_device_heartbeat(self, device_id: str) -> bool:
        """Update device heartbeat timestamp"""
        try:
            if device_id in self.active_connections:
                self.active_connections[device_id]["last_heartbeat"] = datetime.utcnow()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Heartbeat update failed for {device_id}: {str(e)}")
            return False

    async def cleanup_stale_connections(self, timeout_minutes: int = 5) -> int:
        """Remove stale connections"""
        try:
            from datetime import timedelta
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
            stale_devices = []
            
            for device_id, connection in self.active_connections.items():
                if connection["last_heartbeat"] < cutoff_time:
                    stale_devices.append(device_id)
            
            for device_id in stale_devices:
                await self.handle_device_disconnection(device_id)
            
            logger.info(f"Cleaned up {len(stale_devices)} stale connections")
            return len(stale_devices)
            
        except Exception as e:
            logger.error(f"Connection cleanup failed: {str(e)}")
            return 0

    def get_connection_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get connection status for specific device"""
        return self.active_connections.get(device_id)

    def get_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Get all active connections"""
        return self.active_connections.copy()

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "active_devices": list(self.active_connections.keys()),
            "server_uptime": "calculated_uptime_here"
        }
