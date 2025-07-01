"""Network communication service for ESP32 teddy bear."""

import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import requests
import structlog

from ....domain.esp32.models import (ConnectionStatus, NetworkConnection,
                                     ServerConnection, WiFiSecurityType,
                                     WiFiStatus)

logger = structlog.get_logger(__name__)


class NetworkCommunicationService:
    """Service for managing network connections and server communication."""

    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        self.network = NetworkConnection()
        self.network.server.server_url = server_url
        self.connection_callbacks: Dict[str, Callable] = {}
        self.monitoring_active = False
        self.monitor_thread = None

        logger.info(f" Network service initialized: {server_url}")

    def register_connection_callback(
        self, name: str, callback: Callable[[NetworkConnection], None]
    ) -> None:
        """Register callback for connection status changes."""
        self.connection_callbacks[name] = callback

    async def connect_wifi(
        self, ssid: str = "TeddyBear_Network", password: str = "teddy123"
    ) -> bool:
        """Connect to WiFi network."""
        try:
            logger.info(f" Connecting to WiFi: {ssid}")

            self.network.wifi.connect(ssid, WiFiSecurityType.WPA2)

            # Simulate connection process
            await self._simulate_wifi_connection()

            if self.network.wifi.is_connected:
                logger.info(" WiFi connected successfully")
                self._notify_callbacks()

                # Auto-connect to server after WiFi
                await self.connect_server()

                return True
            else:
                logger.error(" WiFi connection failed")
                return False

        except Exception as e:
            logger.error(f" WiFi connection error: {e}")
            return False

    async def disconnect_wifi(self) -> None:
        """Disconnect from WiFi."""
        if self.network.wifi.is_connected:
            self.network.wifi.disconnect()
            await self.disconnect_server()  # Disconnect server when WiFi disconnects
            logger.info(" WiFi disconnected")
            self._notify_callbacks()

    async def connect_server(self) -> bool:
        """Connect to the server."""
        try:
            if not self.network.wifi.is_connected:
                logger.error(" Cannot connect to server: WiFi not connected")
                return False

            logger.info(f" Connecting to server: {self.network.server.server_url}")

            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.network.server.connect(session_id)

            # Simulate server connection
            success = await self._test_server_connection()

            if success:
                response_time = 150.0  # Mock response time
                self.network.server.connected(response_time)
                logger.info(" Server connected successfully")

                # Start monitoring
                self.start_monitoring()

                self._notify_callbacks()
                return True
            else:
                self.network.server.status = ConnectionStatus.ERROR
                logger.error(" Server connection failed")
                return False

        except Exception as e:
            logger.error(f" Server connection error: {e}")
            return False

    async def disconnect_server(self) -> None:
        """Disconnect from server."""
        if self.network.server.is_connected:
            self.stop_monitoring()
            self.network.server.disconnect()
            logger.info(" Server disconnected")
            self._notify_callbacks()

    async def send_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send message to server."""
        try:
            if not self.network.is_fully_connected:
                logger.error(" Cannot send message: Not fully connected")
                return None

            # Add metadata
            full_message = {
                **message,
                "device_id": "ESP32_DEVICE",
                "timestamp": datetime.now().isoformat(),
                "session_id": self.network.server.session_id,
            }

            logger.debug(f" Sending message: {message.get('type', 'unknown')}")

            # Simulate HTTP request
            response = await self._simulate_server_request(full_message)

            if response:
                self.network.server.ping_success(100.0)  # Mock response time
                logger.debug(f" Received response: {response.get('type', 'unknown')}")
                return response
            else:
                self.network.server.ping_failed()
                return None

        except Exception as e:
            logger.error(f" Message send error: {e}")
            self.network.server.ping_failed()
            return None

    async def register_device(self, device_info: Dict[str, Any]) -> bool:
        """Register device with server."""
        try:
            registration_message = {
                "type": "device_registration",
                "device_info": device_info,
            }

            response = await self.send_message(registration_message)

            if response and response.get("status") == "success":
                self.network.server.device_registered = True
                logger.info(" Device registered with server")
                return True
            else:
                logger.error(" Device registration failed")
                return False

        except Exception as e:
            logger.error(f" Device registration error: {e}")
            return False

    def get_network_status(self) -> Dict[str, Any]:
        """Get current network status."""
        return {
            "wifi": {
                "status": self.network.wifi.status.value,
                "ssid": self.network.wifi.ssid,
                "signal_strength": self.network.wifi.signal_strength,
                "signal_quality": self.network.wifi.signal_quality,
                "ip_address": self.network.wifi.ip_address,
                "connected_at": (
                    self.network.wifi.connected_at.isoformat()
                    if self.network.wifi.connected_at
                    else None
                ),
            },
            "server": {
                "status": self.network.server.status.value,
                "url": self.network.server.server_url,
                "session_id": self.network.server.session_id,
                "response_time": self.network.server.response_time,
                "is_healthy": self.network.server.is_healthy,
                "error_count": self.network.server.error_count,
                "last_ping": (
                    self.network.server.last_ping.isoformat()
                    if self.network.server.last_ping
                    else None
                ),
            },
            "overall": {
                "is_fully_connected": self.network.is_fully_connected,
                "connection_quality": self.network.connection_quality,
            },
        }

    def start_monitoring(self) -> None:
        """Start network monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_connections, daemon=True
            )
            self.monitor_thread.start()
            logger.info(" Network monitoring started")

    def stop_monitoring(self) -> None:
        """Stop network monitoring."""
        if self.monitoring_active:
            self.monitoring_active = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2)
            logger.info(" Network monitoring stopped")

    async def _simulate_wifi_connection(self) -> None:
        """Simulate WiFi connection process."""
        time.sleep(1)  # Simulate connection time

        # Mock successful connection
        self.network.wifi.connected(ip_address="192.168.1.100", signal_strength=85)

    async def _test_server_connection(self) -> bool:
        """Test server connectivity."""
        try:
            # Mock server test
            time.sleep(0.5)  # Simulate request time
            return True  # Mock successful connection

        except Exception as e:
            logger.error(f"Server test failed: {e}")
            return False

    async def _simulate_server_request(
        self, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Simulate server request for testing."""
        time.sleep(0.1)  # Simulate network latency

        # Mock responses based on message type
        message_type = message.get("type", "unknown")

        if message_type == "device_registration":
            return {
                "type": "registration_response",
                "status": "success",
                "device_id": message.get("device_id"),
                "session_id": message.get("session_id"),
            }
        elif message_type == "conversation":
            return {
                "type": "ai_response",
                "text": "مرحبا! كيف يمكنني مساعدتك اليوم",
                "audio_url": None,
                "emotion": "happy",
            }
        else:
            return {
                "type": "generic_response",
                "status": "received",
                "timestamp": datetime.now().isoformat(),
            }

    def _monitor_connections(self) -> None:
        """Monitor network connections health."""
        while self.monitoring_active:
            try:
                if self.network.server.is_connected:
                    # Send heartbeat
                    heartbeat_message = {"type": "heartbeat", "uptime": time.time()}

                    # In a real implementation, this would be async
                    # For now, just update ping time
                    self.network.server.ping_success(120.0)

                time.sleep(self.network.protocol.heartbeat_interval)

            except Exception as e:
                logger.error(f" Monitor error: {e}")
                self.network.server.ping_failed()
                time.sleep(10)  # Wait longer on error

    def _notify_callbacks(self) -> None:
        """Notify all connection callbacks."""
        for callback in self.connection_callbacks.values():
            try:
                callback(self.network)
            except Exception as e:
                logger.error(f"Connection callback error: {e}")

    def __del__(self):
        """Cleanup on destruction."""
        self.stop_monitoring()
