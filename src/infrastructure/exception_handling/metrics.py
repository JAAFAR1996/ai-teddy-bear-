"""
Metrics for exception handling.
"""

from prometheus_client import Counter, Gauge, Histogram

exception_counter = Counter(
    "app_exceptions_total",
    "Total number of exceptions",
    ["exception_type", "severity", "domain"],
)

exception_histogram = Histogram(
    "app_exception_handling_duration_seconds",
    "Exception handling duration",
    ["exception_type"],
)

active_circuit_breakers = Gauge(
    "app_circuit_breakers_active", "Number of active circuit breakers", [
        "service"]
)
