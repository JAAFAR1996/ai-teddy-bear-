from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class PerformanceMetric(Enum):
    """Types of performance metrics"""

    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CONCURRENCY = "concurrency"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    RESOURCE_UTILIZATION = "resource_utilization"


class TestType(Enum):
    """Types of performance tests"""

    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"
    SPIKE_TEST = "spike_test"
    VOLUME_TEST = "volume_test"
    ENDURANCE_TEST = "endurance_test"
    SCALABILITY_TEST = "scalability_test"


@dataclass
class PerformanceResult:
    """Result from a performance test"""

    test_name: str
    test_type: TestType
    metric: PerformanceMetric
    value: float
    unit: str
    timestamp: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class LoadTestConfig:
    """Configuration for load testing"""

    concurrent_users: int = 10
    test_duration_seconds: int = 60
    ramp_up_time_seconds: int = 10
    target_rps: Optional[int] = None  # Requests per second
    max_response_time_ms: int = 500
    acceptable_error_rate: float = 0.01  # 1%


@dataclass
class PerformanceReport:
    """Comprehensive performance test report"""

    test_suite_name: str
    start_time: float
    end_time: float
    total_duration: float
    results: List[PerformanceResult]
    summary_metrics: Dict[str, Any]
    recommendations: List[str]
    pass_fail_status: bool
