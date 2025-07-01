"""ESP32 device domain models."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class PowerState(Enum):
    """Device power states."""

    POWERED_OFF = "powered_off"
    POWERED_ON = "powered_on"
    STARTING_UP = "starting_up"
    SHUTTING_DOWN = "shutting_down"
    EMERGENCY_STOP = "emergency_stop"


class DeviceStatus(Enum):
    """Device operational status."""

    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


@dataclass
class HardwareState:
    """Hardware component states."""

    led_status: str = "red"  # red, green, blue, yellow
    volume_level: int = 50  # 0-100
    microphone_sensitivity: int = 300  # 100-1000
    audio_visualizer_active: bool = False
    wifi_signal_strength: int = 0  # 0-100

    def __post_init__(self):
        """Validate hardware state values."""
        if not 0 <= self.volume_level <= 100:
            raise ValueError("Volume level must be between 0 and 100")
        if not 100 <= self.microphone_sensitivity <= 1000:
            raise ValueError("Microphone sensitivity must be between 100 and 1000")


@dataclass
class ESP32Device:
    """ESP32 device representation."""

    device_id: str
    mac_address: str
    power_state: PowerState = PowerState.POWERED_OFF
    status: DeviceStatus = DeviceStatus.OFFLINE
    hardware_state: HardwareState = None
    last_heartbeat: Optional[datetime] = None
    firmware_version: str = "1.0.0"
    uptime_seconds: int = 0

    def __post_init__(self):
        """Initialize hardware state if not provided."""
        if self.hardware_state is None:
            self.hardware_state = HardwareState()

    @property
    def is_powered_on(self) -> bool:
        """Check if device is powered on."""
        return self.power_state == PowerState.POWERED_ON

    @property
    def is_ready(self) -> bool:
        """Check if device is ready for operation."""
        return self.is_powered_on and self.status == DeviceStatus.READY

    def power_on(self) -> None:
        """Power on the device."""
        if self.power_state == PowerState.POWERED_OFF:
            self.power_state = PowerState.STARTING_UP
            self.hardware_state.led_status = "yellow"
            self.uptime_seconds = 0

    def power_off(self) -> None:
        """Power off the device."""
        if self.power_state != PowerState.POWERED_OFF:
            self.power_state = PowerState.SHUTTING_DOWN
            self.hardware_state.led_status = "red"
            self.status = DeviceStatus.OFFLINE

    def set_ready(self) -> None:
        """Set device to ready state."""
        if self.power_state == PowerState.STARTING_UP:
            self.power_state = PowerState.POWERED_ON
            self.status = DeviceStatus.READY
            self.hardware_state.led_status = "green"
            self.last_heartbeat = datetime.now()

    def emergency_stop(self) -> None:
        """Emergency stop the device."""
        self.power_state = PowerState.EMERGENCY_STOP
        self.status = DeviceStatus.ERROR
        self.hardware_state.led_status = "red"

    def update_heartbeat(self) -> None:
        """Update device heartbeat."""
        if self.is_powered_on:
            self.last_heartbeat = datetime.now()
            self.uptime_seconds += 1
