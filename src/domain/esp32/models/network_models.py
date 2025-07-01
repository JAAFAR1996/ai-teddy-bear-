"""ESP32 network domain models."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ConnectionStatus(Enum):
    """Network connection status."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    TIMEOUT = "timeout"


class WiFiSecurityType(Enum):
    """WiFi security types."""

    OPEN = "open"
    WEP = "wep"
    WPA = "wpa"
    WPA2 = "wpa2"
    WPA3 = "wpa3"


@dataclass
class WiFiStatus:
    """WiFi connection status."""

    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    ssid: Optional[str] = None
    signal_strength: int = 0  # 0-100
    security_type: Optional[WiFiSecurityType] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    connected_at: Optional[datetime] = None

    @property
    def is_connected(self) -> bool:
        """Check if WiFi is connected."""
        return self.status == ConnectionStatus.CONNECTED

    @property
    def signal_quality(self) -> str:
        """Get signal quality description."""
        if self.signal_strength >= 80:
            return "Excellent"
        elif self.signal_strength >= 60:
            return "Good"
        elif self.signal_strength >= 40:
            return "Fair"
        elif self.signal_strength >= 20:
            return "Poor"
        else:
            return "Very Poor"

    def connect(
        self, ssid: str, security_type: WiFiSecurityType = WiFiSecurityType.WPA2
    ) -> None:
        """Connect to WiFi network."""
        self.status = ConnectionStatus.CONNECTING
        self.ssid = ssid
        self.security_type = security_type

    def connected(self, ip_address: str, signal_strength: int = 80) -> None:
        """Set connected state."""
        self.status = ConnectionStatus.CONNECTED
        self.ip_address = ip_address
        self.signal_strength = signal_strength
        self.connected_at = datetime.now()

    def disconnect(self) -> None:
        """Disconnect from WiFi."""
        self.status = ConnectionStatus.DISCONNECTED
        self.ip_address = None
        self.connected_at = None


@dataclass
class ServerConnection:
    """Server connection status."""

    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    server_url: str = "http://127.0.0.1:8000"
    last_ping: Optional[datetime] = None
    response_time: Optional[float] = None  # milliseconds
    session_id: Optional[str] = None
    device_registered: bool = False
    error_count: int = 0

    @property
    def is_connected(self) -> bool:
        """Check if server is connected."""
        return self.status == ConnectionStatus.CONNECTED

    @property
    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        return (
            self.is_connected
            and self.error_count < 3
            and self.response_time
            and self.response_time < 5000
        )

    def connect(self, session_id: str) -> None:
        """Connect to server."""
        self.status = ConnectionStatus.CONNECTING
        self.session_id = session_id
        self.error_count = 0

    def connected(self, response_time: float) -> None:
        """Set connected state."""
        self.status = ConnectionStatus.CONNECTED
        self.last_ping = datetime.now()
        self.response_time = response_time
        self.device_registered = True

    def ping_success(self, response_time: float) -> None:
        """Record successful ping."""
        self.last_ping = datetime.now()
        self.response_time = response_time
        self.error_count = max(0, self.error_count - 1)

    def ping_failed(self) -> None:
        """Record failed ping."""
        self.error_count += 1
        if self.error_count >= 5:
            self.status = ConnectionStatus.ERROR

    def disconnect(self) -> None:
        """Disconnect from server."""
        self.status = ConnectionStatus.DISCONNECTED
        self.session_id = None
        self.device_registered = False


@dataclass
class CommunicationProtocol:
    """Communication protocol settings."""

    use_websocket: bool = True
    use_http: bool = True
    timeout_seconds: int = 30
    retry_attempts: int = 3
    heartbeat_interval: int = 60  # seconds

    @property
    def has_fallback(self) -> bool:
        """Check if fallback protocol is available."""
        return self.use_websocket and self.use_http


@dataclass
class NetworkConnection:
    """Complete network connection state."""

    wifi: WiFiStatus = None
    server: ServerConnection = None
    protocol: CommunicationProtocol = None

    def __post_init__(self):
        """Initialize components if not provided."""
        if self.wifi is None:
            self.wifi = WiFiStatus()
        if self.server is None:
            self.server = ServerConnection()
        if self.protocol is None:
            self.protocol = CommunicationProtocol()

    @property
    def is_fully_connected(self) -> bool:
        """Check if both WiFi and server are connected."""
        return self.wifi.is_connected and self.server.is_connected

    @property
    def connection_quality(self) -> str:
        """Get overall connection quality."""
        if not self.wifi.is_connected:
            return "No WiFi"
        elif not self.server.is_connected:
            return "No Server"
        elif self.server.is_healthy and self.wifi.signal_strength >= 60:
            return "Excellent"
        elif self.server.response_time and self.server.response_time < 3000:
            return "Good"
        else:
            return "Poor"
