"""
Prometheus Metrics - نظام metrics للـ monitoring
تتبع الأخطاء والأداء والاستخدام
"""

import asyncio
import time
from functools import wraps
from typing import Callable

import structlog
from prometheus_client import Counter, Gauge, Histogram, Info, Summary

logger = structlog.get_logger(__name__)

# Error Metrics
error_counter = Counter(
    "ai_teddy_errors_total",
    "Total number of errors",
    ["error_code", "category", "severity"],
)

exception_counter = Counter(
    "ai_teddy_exceptions_total",
    "Total number of exceptions",
    ["exception_type", "service", "method"],
)

# Performance Metrics
request_duration = Histogram(
    "ai_teddy_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint", "status"],
)

response_time = Summary(
    "ai_teddy_response_time_seconds", "Response time summary", ["service", "operation"]
)

# Business Metrics
active_children = Gauge(
    "ai_teddy_active_children", "Number of currently active children"
)

interactions_counter = Counter(
    "ai_teddy_interactions_total",
    "Total number of child interactions",
    ["interaction_type", "child_age_group"],
)

voice_messages_processed = Counter(
    "ai_teddy_voice_messages_total",
    "Total voice messages processed",
    ["status", "language"],
)

# Security Metrics
auth_attempts = Counter(
    "ai_teddy_auth_attempts_total", "Authentication attempts", ["method", "result"]
)

security_violations = Counter(
    "ai_teddy_security_violations_total",
    "Security violations detected",
    ["violation_type", "severity"],
)

# Infrastructure Metrics
database_connections = Gauge(
    "ai_teddy_database_connections",
    "Current database connections",
    ["database", "pool"],
)

cache_operations = Counter(
    "ai_teddy_cache_operations_total",
    "Cache operations",
    ["operation", "cache_name", "result"],
)

circuit_breaker_state = Gauge(
    "ai_teddy_circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half-open)",
    ["service"],
)

# Child Safety Metrics
content_filtered = Counter(
    "ai_teddy_content_filtered_total",
    "Content filtered for safety",
    ["filter_type", "reason"],
)

parental_consent_requests = Counter(
    "ai_teddy_parental_consent_requests_total",
    "Parental consent requests",
    ["action", "status"],
)

# System Info
system_info = Info("ai_teddy_system", "System information")

# Initialize system info
system_info.info(
    {"version": "2.0.0", "environment": "production", "region": "us-east-1"}
)


# Decorators for automatic metric collection
def track_request_duration(endpoint: str):
    """Decorator لتتبع مدة الـ requests"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            try:
                result = await func(*args, **kwargs)
                return result
            # FIXME: replace with specific exception
except Exception as exc:status = "error"
                raise
            finally:
                duration = time.time() - start_time
                request_duration.labels(
                    method=func.__name__, endpoint=endpoint, status=status
                ).observe(duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            try:
                result = func(*args, **kwargs)
                return result
            # FIXME: replace with specific exception
except Exception as exc:status = "error"
                raise
            finally:
                duration = time.time() - start_time
                request_duration.labels(
                    method=func.__name__, endpoint=endpoint, status=status
                ).observe(duration)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def track_exceptions(service: str):
    """Decorator لتتبع الـ exceptions"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                exception_counter.labels(
                    exception_type=type(e).__name__,
                    service=service,
                    method=func.__name__,
                ).inc()
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                exception_counter.labels(
                    exception_type=type(e).__name__,
                    service=service,
                    method=func.__name__,
                ).inc()
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class MetricsCollector:
    """جامع metrics مركزي"""

    @staticmethod
    def record_interaction(interaction_type: str, child_age: int) -> None:
        """تسجيل تفاعل طفل"""
        age_group = MetricsCollector._get_age_group(child_age)
        interactions_counter.labels(
            interaction_type=interaction_type, child_age_group=age_group
        ).inc()

    @staticmethod
    def record_voice_message(status: str, language: str = "ar") -> None:
        """تسجيل معالجة رسالة صوتية"""
        voice_messages_processed.labels(status=status, language=language).inc()

    @staticmethod
    def record_auth_attempt(method: str, success: bool) -> None:
        """تسجيل محاولة مصادقة"""
        result = "success" if success else "failure"
        auth_attempts.labels(method=method, result=result).inc()

    @staticmethod
    def record_security_violation(violation_type: str, severity: str) -> None:
        """تسجيل انتهاك أمني"""
        security_violations.labels(
            violation_type=violation_type, severity=severity
        ).inc()

    @staticmethod
    def update_database_connections(database: str, pool: str, count: int) -> None:
        """تحديث عدد اتصالات قاعدة البيانات"""
        database_connections.labels(database=database, pool=pool).set(count)

    @staticmethod
    def record_cache_operation(operation: str, cache_name: str, hit: bool) -> None:
        """تسجيل عملية cache"""
        result = "hit" if hit else "miss"
        cache_operations.labels(
            operation=operation, cache_name=cache_name, result=result
        ).inc()

    @staticmethod
    def update_circuit_breaker(service: str, state: str) -> None:
        """تحديث حالة circuit breaker"""
        state_map = {"CLOSED": 0, "OPEN": 1, "HALF_OPEN": 2}
        circuit_breaker_state.labels(service=service).set(state_map.get(state, -1))

    @staticmethod
    def record_content_filtered(filter_type: str, reason: str) -> None:
        """تسجيل محتوى تم تصفيته"""
        content_filtered.labels(filter_type=filter_type, reason=reason).inc()

    @staticmethod
    def record_parental_consent(action: str, status: str) -> None:
        """تسجيل طلب موافقة والدين"""
        parental_consent_requests.labels(action=action, status=status).inc()

    @staticmethod
    def _get_age_group(age: int) -> str:
        """تحديد الفئة العمرية"""
        if age < 3:
            return "0-2"
        elif age < 6:
            return "3-5"
        elif age < 9:
            return "6-8"
        elif age < 12:
            return "9-11"
        else:
            return "12+"


# Health check metrics
health_check_counter = Counter(
    "ai_teddy_health_checks_total", "Health check attempts", ["service", "result"]
)

last_successful_health_check = Gauge(
    "ai_teddy_last_successful_health_check_timestamp",
    "Timestamp of last successful health check",
    ["service"],
)


class HealthMetrics:
    """Metrics خاصة بـ health checks"""

    @staticmethod
    def record_health_check(service: str, healthy: bool) -> None:
        """تسجيل health check"""
        result = "healthy" if healthy else "unhealthy"
        health_check_counter.labels(service=service, result=result).inc()

        if healthy:
            last_successful_health_check.labels(service=service).set(time.time())


# Performance tracking
operation_latency = Histogram(
    "ai_teddy_operation_latency_seconds",
    "Operation latency",
    ["operation", "service"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)


class PerformanceTracker:
    """تتبع الأداء"""

    def __init__(self, operation: str, service: str):
        self.operation = operation
        self.service = service
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            operation_latency.labels(
                operation=self.operation, service=self.service
            ).observe(duration)


# Export all metrics
__all__ = [
    "error_counter",
    "exception_counter",
    "request_duration",
    "response_time",
    "active_children",
    "interactions_counter",
    "voice_messages_processed",
    "auth_attempts",
    "security_violations",
    "database_connections",
    "cache_operations",
    "circuit_breaker_state",
    "content_filtered",
    "parental_consent_requests",
    "system_info",
    "track_request_duration",
    "track_exceptions",
    "MetricsCollector",
    "HealthMetrics",
    "PerformanceTracker",
    "health_check_counter",
    "last_successful_health_check",
    "operation_latency",
]
