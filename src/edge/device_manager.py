import psutil
from typing import Dict, List, Optional
import platform
import asyncio
import structlog

logger = structlog.get_logger(__name__)


class DeviceManager:
    """Manage edge device capabilities and resources"""

    def __init__(self):
        self.device_info = {}
        self.capabilities = {}

    async def detect_capabilities(self) -> Dict[str, bool]:
        """Detect device capabilities for edge processing"""
        capabilities = {
            "neural_engine": False,
            "gpu_acceleration": False,
            "high_memory": False,
            "fast_cpu": False
        }

        # Check system specs
        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = psutil.cpu_count()

        capabilities["high_memory"] = memory_gb >= 8
        capabilities["fast_cpu"] = cpu_count >= 4

        # Check for GPU (simplified)
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            capabilities["gpu_acceleration"] = len(gpus) > 0
        except ImportError:
            pass

        # Check for Neural Engine (Apple devices)
        if platform.system() == "Darwin":
            capabilities["neural_engine"] = True

        self.capabilities = capabilities
        return capabilities

    def get_optimal_config(self) -> Dict[str, Any]:
        """Get optimal configuration based on device capabilities"""
        config = {
            "batch_size": 1,
            "model_precision": "float32",
            "max_concurrent_requests": 2
        }

        if self.capabilities.get("high_memory"):
            config["batch_size"] = 4
            config["max_concurrent_requests"] = 8

        if self.capabilities.get("neural_engine"):
            config["model_precision"] = "float16"

        if self.capabilities.get("fast_cpu"):
            config["max_concurrent_requests"] *= 2

        return config

    async def monitor_resources(self) -> Dict[str, float]:
        """Monitor device resources"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "temperature": self._get_temperature()
        }

    def _get_temperature(self) -> float:
        """Get device temperature (simplified)"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                return list(temps.values())[0][0].current
        except IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)ndexError as e:
    logger.warning(f"Ignoring error: {e}")
    return 0.0

    def should_throttle(self, resources: Dict[str, float]) -> bool:
        """Check if processing should be throttled"""
        return (
            resources["cpu_percent"] > 80 or
            resources["memory_percent"] > 85 or
            resources["temperature"] > 70
        )
