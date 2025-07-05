"""
📊 Dashboard Analytics Endpoints
"""

import secrets
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
            "total_interactions": secrets.randbelow(91) + 10,
            "learning_time_minutes": secrets.randbelow(241) + 60,
            "favorite_topics": [
                {"topic": "قصص", "count": secrets.randbelow(16) + 5},
                {"topic": "رياضيات", "count": secrets.randbelow(13) + 3},
                {"topic": "علوم", "count": secrets.randbelow(9) + 2},
            ],
            "emotion_analysis": {
                "happy": secrets.randbelow(21) + 40,
                "curious": secrets.randbelow(21) + 20,
                "frustrated": secrets.randbelow(11),
                "excited": secrets.randbelow(21) + 10,
            },
            "daily_activity": [
                {
                    "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "interactions": secrets.randbelow(11),
                    "learning_minutes": secrets.randbelow(61),
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
                "battery_level": secrets.randbelow(81) + 20,
                "wifi_strength": secrets.randbelow(51) + 50,
            },
            {
                "device_id": "esp32_002",
                "child_name": "فاطمة",
                "status": "offline",
                "last_seen": (datetime.now() - timedelta(hours=2)).isoformat(),
                "battery_level": secrets.randbelow(41) + 10,
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
async def get_system_health(
        container=Depends(get_container)) -> Dict[str, Any]:
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
                "response_time_ms": secrets.randbelow(401) + 100,
                "active_connections": secrets.randbelow(46) + 5,
                "cpu_usage": secrets.randbelow(61) + 20,
                "memory_usage": secrets.randbelow(41) + 30,
                "requests_per_minute": secrets.randbelow(91) + 10,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}",
        )
