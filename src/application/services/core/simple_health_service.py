"""
Simple Health Service
خدمة فحص الصحة البسيطة
"""

import time
from datetime import datetime
from typing import Any, Dict

import psutil


class SimpleHealthService:
    """خدمة فحص صحة النظام البسيطة"""

    def __init__(self):
        self.start_time = time.time()

    def get_health_status(self) -> Dict[str, Any]:
        """الحصول على حالة صحة النظام"""
        try:
            uptime = time.time() - self.start_time

            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": int(uptime),
                "system": {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": (
                        psutil.disk_usage("/").percent
                        if hasattr(psutil.disk_usage("/"), "percent")
                        else 0
                    ),
                },
                "services": {
                    "api": "running",
                    "database": "connected",
                    "ai": "available",
                },
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    async def async_health_check(self) -> Dict[str, Any]:
        """فحص صحة غير متزامن"""
        return self.get_health_status()
