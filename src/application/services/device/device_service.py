"""
Device Registry Service - Manages ESP32 devices connected to cloud
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class DeviceStatus(str, Enum):
    """Device connection status"""

    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"
    ERROR = "error"


class ESP32Device:
    """ESP32 device model for cloud tracking"""

    def __init__(self, device_id: str, hardware_info: Dict[str, Any] = None):
        self.device_id = device_id
        self.hardware_info = hardware_info or {}
        self.status = DeviceStatus.OFFLINE
        self.registered_at = datetime.utcnow()
        self.last_seen = None
        self.child_profile_id = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "status": self.status.value,
            "hardware_info": self.hardware_info,
            "registered_at": self.registered_at.isoformat(),
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "child_profile_id": self.child_profile_id,
        }


class DeviceRegistryService:
    """Service for managing ESP32 devices connected to the cloud."""

    def __init__(self):
        self.devices: Dict[str, ESP32Device] = {}
        logger.info("DeviceRegistryService initialized")

    async def register_device(
        self,
        device_id: str,
        firmware_version: str,
        hardware_info: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Register a new ESP32 device

        Args:
            device_id: Unique ESP32 device identifier
            firmware_version: Device firmware version
            hardware_info: Additional hardware information

        Returns:
            Registration result
        """
        try:
            if not self._validate_device_id(device_id):
                raise ValueError(f"Invalid device ID format: {device_id}")

            # Create or update device
            if device_id in self.devices:
                device = self.devices[device_id]
                device.hardware_info.update(hardware_info or {})
                logger.info(f"Device updated: {device_id}")
            else:
                device = ESP32Device(device_id, hardware_info)
                self.devices[device_id] = device
                logger.info(f"New device registered: {device_id}")

            device.hardware_info["firmware_version"] = firmware_version
            device.status = DeviceStatus.ONLINE
            device.last_seen = datetime.utcnow()

            return {
                "status": "success",
                "device_id": device_id,
                "registration_id": f"REG_{device_id}_{datetime.utcnow().timestamp()}",
                "registered_at": device.registered_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Device registration failed: {str(e)}")
            raise

    async def update_device_status(
            self,
            device_id: str,
            status: DeviceStatus) -> bool:
        """Update device connection status"""
        try:
            if device_id not in self.devices:
                logger.warning(f"Unknown device status update: {device_id}")
                return False

            device = self.devices[device_id]
            device.status = status
            device.last_seen = datetime.utcnow()

            logger.info(f"Device {device_id} status updated to {status}")
            return True

        except Exception as e:
            logger.error(f"Status update failed for {device_id}: {str(e)}")
            return False

    async def get_device(self, device_id: str) -> Optional[ESP32Device]:
        """Get device by ID"""
        return self.devices.get(device_id)

    async def get_all_devices(self) -> List[ESP32Device]:
        """Get all registered devices"""
        return list(self.devices.values())

    async def get_online_devices(self) -> List[ESP32Device]:
        """Get only online devices"""
        return [
            device
            for device in self.devices.values()
            if device.status == DeviceStatus.ONLINE
        ]

    async def link_device_to_child(
            self,
            device_id: str,
            child_profile_id: str) -> bool:
        """Link device to a child profile"""
        try:
            if device_id not in self.devices:
                raise ValueError(f"Device not found: {device_id}")

            device = self.devices[device_id]
            device.child_profile_id = child_profile_id

            logger.info(
                f"Device {device_id} linked to child {child_profile_id}")
            return True

        except Exception as e:
            logger.error(f"Device linking failed: {str(e)}")
            return False

    async def cleanup_stale_devices(self, hours_threshold: int = 24) -> int:
        """Remove devices that haven't been seen for specified hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_threshold)
            stale_devices = []

            for device_id, device in self.devices.items():
                if device.last_seen and device.last_seen < cutoff_time:
                    stale_devices.append(device_id)

            for device_id in stale_devices:
                del self.devices[device_id]

            logger.info(f"Cleaned up {len(stale_devices)} stale devices")
            return len(stale_devices)

        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            return 0

    def _validate_device_id(self, device_id: str) -> bool:
        """Validate ESP32 device ID format"""
        return (
            device_id.startswith("ESP32_")
            and len(device_id) >= 8
            and device_id.replace("ESP32_", "").replace("_", "").isalnum()
        )

    async def get_device_stats(self) -> Dict[str, Any]:
        """Get device statistics"""
        total = len(self.devices)
        online = len([d for d in self.devices.values()
                      if d.status == DeviceStatus.ONLINE])
        offline = len([d for d in self.devices.values()
                       if d.status == DeviceStatus.OFFLINE])

        return {
            "total_devices": total,
            "online_devices": online,
            "offline_devices": offline,
            "connection_rate": (online / total * 100) if total > 0 else 0,
        }
