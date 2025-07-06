"""
Core data models for the service orchestration layer.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ServiceStatus(Enum):
    """Service status enumeration"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    RANDOM = "random"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class ServiceInstance:
    """Service instance information"""

    id: str
    name: str
    host: str
    port: int
    protocol: str = "http"
    health_check_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    response_time: Optional[float] = None
    error_count: int = 0
    success_count: int = 0
    weight: int = 1
    tags: Set[str] = field(default_factory=set)


@dataclass
class ServiceDefinition:
    """Service definition"""

    name: str
    version: str
    instances: List[ServiceInstance] = field(default_factory=list)
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_check_interval: int = 30
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    retry_attempts: int = 3
    timeout: int = 30
    max_connections: int = 100
    tags: Set[str] = field(default_factory=set)
