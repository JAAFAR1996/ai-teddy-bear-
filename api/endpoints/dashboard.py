"""
📊 Dashboard Analytics Endpoints
"""

import random
from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from infrastructure.dependencies import get_container

router = APIRouter()


@router.get("/stats/{child_id}")
async def get_child_stats(
    child_id: str, period: str = "week"  # week, month, year
) -> Dict[str, Any]:
    """Get child interaction statistics"""
    try:
        # Mock data - replace with real database queries
        stats = {
            "child_id": child_id,
            "period": period,
            "total_interactions": random.randint(10, 100),
            "learning_time_minutes": random.randint(60, 300),
            "favorite_topics": [
                {"topic": "قصص", "count": random.randint(5, 20)},
                {"topic": "رياضيات", "count": random.randint(3, 15)},
                {"topic": "علوم", "count": random.randint(2, 10)},
            ],
            "emotion_analysis": {
                "happy": random.randint(40, 60),
                "curious": random.randint(20, 40),
                "frustrated": random.randint(0, 10),
                "excited": random.randint(10, 30),
            },
            "daily_activity": [
                {
                    "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "interactions": random.randint(0, 10),
                    "learning_minutes": random.randint(0, 60),
                }
                for i in range(7)
            ],
        }

        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}",
        )


@router.get("/devices/status")
async def get_devices_status() -> Dict[str, Any]:
    """Get all devices status"""
    try:
        # Mock data
        devices = [
            {
                "device_id": "esp32_001",
                "child_name": "أحمد",
                "status": "online",
                "last_seen": datetime.now().isoformat(),
                "battery_level": random.randint(20, 100),
                "wifi_strength": random.randint(50, 100),
            },
            {
                "device_id": "esp32_002",
                "child_name": "فاطمة",
                "status": "offline",
                "last_seen": (datetime.now() - timedelta(hours=2)).isoformat(),
                "battery_level": random.randint(10, 50),
                "wifi_strength": 0,
            },
        ]

        return {
            "status": "success",
            "devices": devices,
            "summary": {
                "total": len(devices),
                "online": len([d for d in devices if d["status"] == "online"]),
                "offline": len([d for d in devices if d["status"] == "offline"]),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get devices status: {str(e)}",
        )


@router.get("/system/health")
async def get_system_health(container=Depends(get_container)) -> Dict[str, Any]:
    """Get system health metrics"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "ai_service": "healthy",
                "voice_service": "healthy",
                "database": "healthy",
                "redis": "healthy",
            },
            "metrics": {
                "response_time_ms": random.randint(100, 500),
                "active_connections": random.randint(5, 50),
                "cpu_usage": random.randint(20, 80),
                "memory_usage": random.randint(30, 70),
                "requests_per_minute": random.randint(10, 100),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}",
        )
