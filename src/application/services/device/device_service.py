"""Device management service for ESP32 teddy bear."""

import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import structlog

from ....domain.esp32.models import (DeviceStatus, ESP32Device, HardwareState,
                                     PowerState)

logger = structlog.get_logger(__name__)


class DeviceManagementService:
    """Service for managing ESP32 device lifecycle and hardware."""

    def __init__(self, device_id: str, mac_address: str):
        self.device = ESP32Device(device_id=device_id, mac_address=mac_address)
        self.power_callbacks: Dict[str, Callable] = {}
        self.status_callbacks: Dict[str, Callable] = {}
        self.monitoring_active = False
        self.monitor_thread = None

        logger.info(f" Device service initialized: {device_id}")

    def register_power_callback(
        self, name: str, callback: Callable[[PowerState], None]
    ) -> None:
        """Register callback for power state changes."""
        self.power_callbacks[name] = callback

    def register_status_callback(
        self, name: str, callback: Callable[[DeviceStatus], None]
    ) -> None:
        """Register callback for status changes."""
        self.status_callbacks[name] = callback

    async def power_on(self) -> bool:
        """Power on the device."""
        try:
            if self.device.is_powered_on:
                logger.warning("Device already powered on")
                return True

            logger.info(" Powering on device...")
            self.device.power_on()

            # Notify callbacks
            for callback in self.power_callbacks.values():
                try:
                    callback(self.device.power_state)
                except Exception as e:
                    logger.error(f"Power callback error: {e}")

            # Simulate startup sequence
            await self._startup_sequence()

            # Start monitoring
            self.start_monitoring()

            return True

        except Exception as e:
            logger.error(f" Power on failed: {e}")
            return False

    async def power_off(self) -> bool:
        """Power off the device."""
        try:
            if not self.device.is_powered_on:
                logger.warning("Device already powered off")
                return True

            logger.info(" Powering off device...")

            # Stop monitoring
            self.stop_monitoring()

            self.device.power_off()

            # Notify callbacks
            for callback in self.power_callbacks.values():
                try:
                    callback(self.device.power_state)
                except Exception as e:
                    logger.error(f"Power callback error: {e}")

            return True

        except Exception as e:
            logger.error(f" Power off failed: {e}")
            return False

    async def emergency_stop(self) -> None:
        """Emergency stop the device."""
        logger.warning(" EMERGENCY STOP activated")

        self.stop_monitoring()
        self.device.emergency_stop()

        # Notify all callbacks
        for callback in self.power_callbacks.values():
            try:
                callback(self.device.power_state)
            except Exception as e:
                logger.error(f"Emergency callback error: {e}")

    async def restart(self) -> bool:
        """Restart the device."""
        logger.info(" Restarting device...")

        success = await self.power_off()
        if success:
            time.sleep(2)  # Wait for complete shutdown
            success = await self.power_on()

        return success

    def update_volume(self, volume: int) -> bool:
        """Update device volume."""
        try:
            if not 0 <= volume <= 100:
                raise ValueError("Volume must be between 0 and 100")

            self.device.hardware_state.volume_level = volume
            logger.debug(f" Volume updated to {volume}%")
            return True

        except Exception as e:
            logger.error(f" Volume update failed: {e}")
            return False

    def update_microphone_sensitivity(self, sensitivity: int) -> bool:
        """Update microphone sensitivity."""
        try:
            if not 100 <= sensitivity <= 1000:
                raise ValueError("Sensitivity must be between 100 and 1000")

            self.device.hardware_state.microphone_sensitivity = sensitivity
            logger.debug(f" Microphone sensitivity updated to {sensitivity}")
            return True

        except Exception as e:
            logger.error(f" Sensitivity update failed: {e}")
            return False

    def get_device_status(self) -> Dict[str, Any]:
        """Get current device status."""
        return {
            "device_id": self.device.device_id,
            "mac_address": self.device.mac_address,
            "power_state": self.device.power_state.value,
            "status": self.device.status.value,
            "is_powered_on": self.device.is_powered_on,
            "is_ready": self.device.is_ready,
            "uptime_seconds": self.device.uptime_seconds,
            "last_heartbeat": (
                self.device.last_heartbeat.isoformat()
                if self.device.last_heartbeat
                else None
            ),
            "hardware": {
                "led_status": self.device.hardware_state.led_status,
                "volume_level": self.device.hardware_state.volume_level,
                "microphone_sensitivity": self.device.hardware_state.microphone_sensitivity,
                "audio_visualizer_active": self.device.hardware_state.audio_visualizer_active,
                "wifi_signal_strength": self.device.hardware_state.wifi_signal_strength,
            },
        }

    def start_monitoring(self) -> None:
        """Start device monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_device, daemon=True
            )
            self.monitor_thread.start()
            logger.info(" Device monitoring started")

    def stop_monitoring(self) -> None:
        """Stop device monitoring."""
        if self.monitoring_active:
            self.monitoring_active = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2)
            logger.info(" Device monitoring stopped")

    async def _startup_sequence(self) -> None:
        """Execute device startup sequence."""
        try:
            # Simulate hardware initialization
            time.sleep(1)

            # Set device ready
            self.device.set_ready()

            # Notify status callbacks
            for callback in self.status_callbacks.values():
                try:
                    callback(self.device.status)
                except Exception as e:
                    logger.error(f"Status callback error: {e}")

            logger.info(" Device startup sequence completed")

        except Exception as e:
            logger.error(f" Startup sequence failed: {e}")
            self.device.status = DeviceStatus.ERROR

    def _monitor_device(self) -> None:
        """Monitor device health and update heartbeat."""
        while self.monitoring_active:
            try:
                if self.device.is_powered_on:
                    self.device.update_heartbeat()

                time.sleep(1)  # Monitor every second

            except Exception as e:
                logger.error(f" Monitor error: {e}")
                time.sleep(5)  # Wait longer on error

    def __del__(self):
        """Cleanup on destruction."""
        self.stop_monitoring()
