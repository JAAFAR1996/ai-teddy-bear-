"""
Data models for the API Gateway.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ThreatLevel(Enum):
    """Enumeration for classifying the severity of a detected threat."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RequestType(Enum):
    """Enumeration for classifying different types of incoming requests for rate limiting."""
    AUDIO_UPLOAD = "audio_upload"
    WEBSOCKET_CONNECTION = "websocket_connection"
    API_CALL = "api_call"
    AUTHENTICATION = "authentication"
    FILE_UPLOAD = "file_upload"
    BULK_OPERATION = "bulk_operation"


@dataclass
class RateLimitRule:
    """Represents a rule for rate limiting requests."""
    name: str
    requests: int
    window_seconds: int
    request_type: Optional[RequestType] = None
    user_role: Optional[str] = None
    endpoint_pattern: Optional[str] = None
    burst_multiplier: float = 1.5


@dataclass
class ThreatSignature:
    """Represents a signature used to detect a specific type of security threat."""
    name: str
    pattern: str
    threat_level: ThreatLevel
    action: str  # e.g., "block", "log", "rate_limit"
    description: str


@dataclass
class RequestAnalytics:
    """Represents the analytics data collected for a single request."""
    timestamp: datetime
    ip_address: str
    endpoint: str
    method: str
    response_time: float
    status_code: int
    user_agent: str
    threat_level: ThreatLevel
    user_id: Optional[str] = None
    blocked: bool = False
