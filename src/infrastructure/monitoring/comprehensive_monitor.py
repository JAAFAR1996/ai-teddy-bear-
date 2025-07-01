"""
Comprehensive Monitoring System - نظام المراقبة الشامل
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict, List, Optional

import structlog
from prometheus_client import Counter, Gauge, Histogram

from src.infrastructure.caching.redis_cache import get_redis_client
from src.infrastructure.external_services.openai_service import get_ai_service
from src.infrastructure.persistence.connection import get_db_session

logger = structlog.get_logger(__name__)

# Prometheus Metrics
error_counter = Counter(
    "teddy_bear_errors_total",
    "Total number of errors",
    ["error_type", "severity", "child_safety_related"],
)

response_time_histogram = Histogram(
    "teddy_bear_response_time_seconds",
    "Response time in seconds",
    ["endpoint", "method"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

active_children_gauge = Gauge(
    "teddy_bear_active_children", "Number of currently active children"
)

safety_violations_counter = Counter(
    "teddy_bear_safety_violations_total",
    "Total number of safety violations detected",
    ["violation_type", "age_group", "action_taken"],
)

websocket_connections_gauge = Gauge(
    "teddy_bear_websocket_connections", "Number of active WebSocket connections"
)

ai_requests_counter = Counter(
    "teddy_bear_ai_requests_total", "Total number of AI requests", ["model", "status"]
)

cache_operations_counter = Counter(
    "teddy_bear_cache_operations_total", "Cache operations", ["operation", "status"]
)


@dataclass
class HealthCheckResult:
    """Result of a health check"""

    service: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: float
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    checked_at: datetime = field(default_factory=datetime.utcnow)

    def is_healthy(self) -> bool:
        return self.status == "healthy"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "checked_at": self.checked_at.isoformat(),
        }


@dataclass
class Alert:
    """Alert configuration"""

    id: str
    type: str  # critical, warning, info
    title: str
    message: str
    service: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "service": self.service,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class MetricsAggregator:
    """Aggregates metrics for analysis"""

    def __init__(self):
        self.violations_buffer = []
        self.max_buffer_size = 10000

    async def record_violation(self, violation: Dict[str, Any]):
        """Record a safety violation"""
        self.violations_buffer.append({**violation, "timestamp": datetime.utcnow()})

        # Trim buffer if too large
        if len(self.violations_buffer) > self.max_buffer_size:
            self.violations_buffer = self.violations_buffer[-self.max_buffer_size :]

    async def get_recent_violations(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get violations from the last N minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [v for v in self.violations_buffer if v["timestamp"] > cutoff_time]

    async def get_violation_stats(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get violation statistics"""
        recent = await self.get_recent_violations(window_minutes)

        if not recent:
            return {"total": 0, "by_type": {}, "by_child": {}, "trend": "stable"}

        # Group by type
        by_type = {}
        by_child = {}

        for violation in recent:
            vtype = violation.get("type", "unknown")
            child_id = violation.get("child_id")

            by_type[vtype] = by_type.get(vtype, 0) + 1
            if child_id:
                by_child[child_id] = by_child.get(child_id, 0) + 1

        # Calculate trend
        half_window = window_minutes // 2
        cutoff = datetime.utcnow() - timedelta(minutes=half_window)
        recent_half = [v for v in recent if v["timestamp"] > cutoff]

        trend = "stable"
        if len(recent_half) > len(recent) * 0.6:
            trend = "increasing"
        elif len(recent_half) < len(recent) * 0.3:
            trend = "decreasing"

        return {
            "total": len(recent),
            "by_type": by_type,
            "by_child": by_child,
            "trend": trend,
            "window_minutes": window_minutes,
        }


class AlertManager:
    """Manages system alerts"""

    def __init__(self):
        self.alerts = []
        self.alert_handlers = []

    def register_handler(self, handler: Callable[[Alert], Awaitable[None]]):
        """Register an alert handler"""
        self.alert_handlers.append(handler)

    async def send_alert(self, alert: Alert):
        """Send an alert through all handlers"""
        self.alerts.append(alert)

        # Execute all handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(
                    "Alert handler failed", handler=handler.__name__, error=str(e)
                )

    async def send_critical_alert(self, details: Dict[str, Any]):
        """Send a critical alert"""
        alert = Alert(
            id=f"critical_{datetime.utcnow().timestamp()}",
            type="critical",
            title="Critical System Issue",
            message=json.dumps(details),
            metadata=details,
        )
        await self.send_alert(alert)

    async def send_safety_alert(self, details: Dict[str, Any]):
        """Send a child safety alert"""
        alert = Alert(
            id=f"safety_{datetime.utcnow().timestamp()}",
            type="critical",
            title="Child Safety Alert",
            message=f"Safety violation detected: {details.get('type', 'unknown')}",
            metadata=details,
        )
        await self.send_alert(alert)

    async def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get alerts from the last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [a for a in self.alerts if a.created_at > cutoff]


class ComprehensiveMonitor:
    """نظام مراقبة شامل مع health checks و alerting"""

    def __init__(self):
        self.health_checks = {}
        self.alert_manager = AlertManager()
        self.metrics_aggregator = MetricsAggregator()
        self.monitoring_tasks = []

    def register_health_check(
        self,
        name: str,
        check_func: Callable[[], Awaitable[HealthCheckResult]],
        critical: bool = False,
        interval_seconds: int = 30,
    ):
        """تسجيل health check جديد"""
        self.health_checks[name] = {
            "func": check_func,
            "critical": critical,
            "interval": interval_seconds,
            "last_result": None,
            "consecutive_failures": 0,
        }

    async def run_health_checks(self) -> Dict[str, HealthCheckResult]:
        """تشغيل جميع health checks"""
        results = {}

        for name, check in self.health_checks.items():
            try:
                result = await asyncio.wait_for(
                    check["func"](), timeout=5.0
                )  # 5 second timeout
                results[name] = result

                # Update state
                if result.status == "healthy":
                    check["consecutive_failures"] = 0
                else:
                    check["consecutive_failures"] += 1

                check["last_result"] = result

                # Alert on critical service failure
                if check["critical"] and result.status == "unhealthy":
                    await self.alert_manager.send_critical_alert(
                        {
                            "service": name,
                            "status": result.status,
                            "error": result.error_message,
                            "consecutive_failures": check["consecutive_failures"],
                        }
                    )

            except asyncio.TimeoutError:
                results[name] = HealthCheckResult(
                    service=name,
                    status="unhealthy",
                    latency_ms=5000,
                    error_message="Health check timeout",
                )
                check["consecutive_failures"] += 1

            except Exception as e:
                results[name] = HealthCheckResult(
                    service=name, status="unhealthy", latency_ms=0, error_message=str(e)
                )
                check["consecutive_failures"] += 1

        return results

    async def monitor_child_safety_metrics(self):
        """مراقبة خاصة بمقاييس أمان الأطفال"""
        while True:
            try:
                # Get violation statistics
                stats = await self.metrics_aggregator.get_violation_stats(
                    window_minutes=5
                )

                # Alert on spike in violations
                if stats["total"] > 10:
                    await self.alert_manager.send_safety_alert(
                        {
                            "type": "violation_spike",
                            "count": stats["total"],
                            "timeframe": "5_minutes",
                            "by_type": stats["by_type"],
                        }
                    )

                # Check for repeated violations from same child
                for child_id, count in stats["by_child"].items():
                    if count > 3:
                        await self.alert_manager.send_safety_alert(
                            {
                                "type": "repeated_violations",
                                "child_id": child_id,
                                "violation_count": count,
                                "action": "notify_parent",
                            }
                        )

                # Update Prometheus metrics
                active_children_gauge.set(len(stats["by_child"]))

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error("Error in safety monitoring", error=str(e))
                await asyncio.sleep(60)

    async def start_monitoring(self):
        """Start all monitoring tasks"""

        # Start periodic health checks
        async def health_check_loop():
            while True:
                await self.run_health_checks()
                await asyncio.sleep(30)  # Run every 30 seconds

        # Start monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(health_check_loop()),
            asyncio.create_task(self.monitor_child_safety_metrics()),
        ]

        logger.info("Monitoring system started")

    async def stop_monitoring(self):
        """Stop all monitoring tasks"""
        for task in self.monitoring_tasks:
            task.cancel()

        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        logger.info("Monitoring system stopped")

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        # Run health checks
        health_results = await self.run_health_checks()

        # Get recent alerts
        recent_alerts = await self.alert_manager.get_recent_alerts(hours=1)

        # Get violation stats
        violation_stats = await self.metrics_aggregator.get_violation_stats()

        # Calculate overall health
        unhealthy_services = [
            name
            for name, result in health_results.items()
            if result.status == "unhealthy"
        ]

        overall_health = "healthy"
        if unhealthy_services:
            critical_unhealthy = [
                name
                for name in unhealthy_services
                if self.health_checks[name]["critical"]
            ]
            overall_health = "critical" if critical_unhealthy else "degraded"

        return {
            "overall_health": overall_health,
            "timestamp": datetime.utcnow().isoformat(),
            "health_checks": {
                name: result.to_dict() for name, result in health_results.items()
            },
            "recent_alerts": [a.to_dict() for a in recent_alerts],
            "safety_violations": violation_stats,
            "unhealthy_services": unhealthy_services,
        }


# Health Check Implementations
class HealthChecks:
    """مجموعة من health checks للخدمات المختلفة"""

    @staticmethod
    async def check_database() -> HealthCheckResult:
        """فحص صحة قاعدة البيانات"""
        start_time = datetime.utcnow()

        try:
            async with get_db_session() as session:
                # Simple query to check connectivity
                result = await session.execute("SELECT 1")
                result.scalar()

            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            return HealthCheckResult(
                service="database",
                status="healthy" if latency < 100 else "degraded",
                latency_ms=latency,
            )

        except Exception as e:
            return HealthCheckResult(
                service="database",
                status="unhealthy",
                latency_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                error_message=str(e),
            )

    @staticmethod
    async def check_redis() -> HealthCheckResult:
        """فحص صحة Redis"""
        start_time = datetime.utcnow()

        try:
            redis = get_redis_client()
            await redis.ping()

            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Check memory usage
            info = await redis.info("memory")
            used_memory_mb = info["used_memory"] / 1024 / 1024

            status = "healthy"
            if latency > 50:
                status = "degraded"
            elif used_memory_mb > 1024:  # 1GB
                status = "degraded"

            return HealthCheckResult(
                service="redis",
                status=status,
                latency_ms=latency,
                metadata={
                    "used_memory_mb": used_memory_mb,
                    "connected_clients": info.get("connected_clients", 0),
                },
            )

        except Exception as e:
            return HealthCheckResult(
                service="redis",
                status="unhealthy",
                latency_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                error_message=str(e),
            )

    @staticmethod
    async def check_ai_service() -> HealthCheckResult:
        """فحص صحة خدمة AI"""
        start_time = datetime.utcnow()

        try:
            ai_service = get_ai_service()

            # Test with safe prompt
            test_prompt = "Hello, can you hear me?"
            response = await ai_service.generate_response(test_prompt)

            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            if response and len(response) > 0:
                status = "healthy" if latency < 1000 else "degraded"
            else:
                status = "unhealthy"

            return HealthCheckResult(
                service="ai_service",
                status=status,
                latency_ms=latency,
                metadata={
                    "model": ai_service.model_name,
                    "response_length": len(response) if response else 0,
                },
            )

        except Exception as e:
            return HealthCheckResult(
                service="ai_service",
                status="unhealthy",
                latency_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                error_message=str(e),
            )
