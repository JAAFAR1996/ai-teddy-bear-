"""
System-wide health and reliability metrics.
"""
import logging

from opentelemetry import metrics, trace

logger = logging.getLogger(__name__)


class SystemHealthMetrics:
    """
    System-wide health and reliability metrics.
    Tracks infrastructure health, SLIs/SLOs, and error budgets.
    """

    def __init__(self):
        self.meter = metrics.get_meter("ai.teddy.system", "1.0.0")
        self.tracer = trace.get_tracer("ai.teddy.system", "1.0.0")
        self._initialize_metrics()

    def _initialize_metrics(self):
        """Initializes all the Prometheus metrics for system health."""
        self.service_availability = self.meter.create_gauge(
            name="service_availability",
            description="Service availability percentage",
            unit="1",
        )
        self.error_rate = self.meter.create_gauge(
            name="service_error_rate", description="Service error rate", unit="1"
        )
        self.request_latency = self.meter.create_histogram(
            name="request_latency_ms",
            description="Request latency in milliseconds",
            unit="ms",
            boundaries=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000],
        )
        self.request_throughput = self.meter.create_counter(
            name="requests_total", description="Total number of requests", unit="1"
        )
        self.error_budget_consumption = self.meter.create_gauge(
            name="error_budget_consumption",
            description="Error budget consumption rate",
            unit="1",
        )
        self.slo_compliance = self.meter.create_gauge(
            name="slo_compliance", description="SLO compliance percentage", unit="1"
        )
        self.db_connection_health = self.meter.create_gauge(
            name="database_connection_health",
            description="Database connection health score",
            unit="1",
        )
        self.cache_hit_rate = self.meter.create_gauge(
            name="cache_hit_rate", description="Cache hit rate percentage", unit="1"
        )
        self.memory_usage = self.meter.create_gauge(
            name="memory_usage_bytes",
            description="Memory usage in bytes",
            unit="bytes",
        )
        self.cpu_utilization = self.meter.create_gauge(
            name="cpu_utilization", description="CPU utilization percentage", unit="1"
        )

    def record_request(
        self,
        latency_ms: float,
        status_code: int,
        service_name: str,
        endpoint: str,
        method: str,
    ):
        """Record request metrics"""
        with self.tracer.start_as_current_span("request") as span:
            span.set_attributes({
                "http.method": method,
                "http.status_code": status_code,
                "service.name": service_name,
                "endpoint": endpoint,
                "latency_ms": latency_ms,
            })

            self.request_latency.record(
                latency_ms,
                attributes={
                    "service": service_name,
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": str(status_code),
                    "status_class": f"{status_code // 100}xx",
                },
            )
            self.request_throughput.add(
                1,
                attributes={
                    "service": service_name,
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": str(status_code),
                },
            )

    def update_slo_metrics(self, service_name: str) -> None:
        """Update SLO compliance metrics"""
        # This would typically calculate from actual metrics
        # For demo purposes, using simulated values
        availability = 0.9995  # 99.95% availability
        error_rate = 0.0005  # 0.05% error rate
        error_budget_used = 0.25  # 25% of error budget consumed
        slo_compliance = 0.998  # 99.8% SLO compliance

        self.service_availability.set(availability, attributes={
                                      "service": service_name})
        self.error_rate.set(error_rate, attributes={"service": service_name})
        self.error_budget_consumption.set(
            error_budget_used,
            attributes={"service": service_name, "slo_type": "availability"},
        )
        self.slo_compliance.set(slo_compliance, attributes={
                                "service": service_name})
