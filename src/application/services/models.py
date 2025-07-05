"""Application Service Models"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ServiceRequest:
    id: str
    type: str
    timestamp: datetime
    child_id: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class ServiceResponse:
    id: str
    success: bool
    data: Dict[str, Any] = None
    error_message: Optional[str] = None


@dataclass
class ChildProfile:
    id: str
    name: str
    age: int
    language: str = "ar"
    preferences: Dict[str, Any] = None


@dataclass
class VoiceMessage:
    id: str
    audio_data: Optional[bytes] = None
    transcribed_text: Optional[str] = None
    duration_seconds: float = 0.0
    language: str = "ar"


def create_success_response(data: Dict[str, Any]) -> ServiceResponse:
    return ServiceResponse(id="", success=True, data=data)


def create_error_response(error: str) -> ServiceResponse:
    return ServiceResponse(id="", success=False, error_message=error)
