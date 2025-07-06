from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class QueryMetrics:
    """Metrics for a GraphQL query."""

    query_hash: str
    query_string: str
    operation_name: Optional[str]
    variables: Dict[str, Any]
    execution_time_ms: float
    fields_requested: List[str]
    services_involved: List[str]
    cache_hit: bool
    error_count: int
    timestamp: datetime
    user_id: Optional[str] = None
    client_info: Optional[str] = None


@dataclass
class QueryCompletionInfo:
    """Information required to finalize query monitoring."""

    query_hash: str
    query: str
    variables: Dict[str, Any]
    operation_name: Optional[str]
    execution_time_ms: float
    fields_requested: List[str]
    services_involved: List[str]
    cache_hit: bool
    error_count: int
    user_id: Optional[str] = None


@dataclass
class ServiceMetrics:
    """Metrics for individual service calls."""

    service_name: str
    query_hash: str
    execution_time_ms: float
    response_size_bytes: int
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PerformanceAlert:
    """Performance alert definition."""

    alert_type: str
    message: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    metric_value: float
    threshold: float
    timestamp: datetime
    query_hash: Optional[str] = None
    service_name: Optional[str] = None


@dataclass
class QueryAnalytics:
    """Detailed analytics for a specific query."""

    query_hash: str
    total_executions: int
    avg_execution_time_ms: float
    min_execution_time_ms: float
    max_execution_time_ms: float
    total_errors: int
    error_rate: float
    cache_hit_rate: float
    services_involved: List[str]
    first_seen: str
    last_seen: str
    sample_query: str
