"""
Comprehensive Health Monitoring Service
Includes memory leak detection, performance monitoring, and system health checks
"""

import asyncio
import gc
import os
import sys
import tracemalloc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

import psutil
import structlog
from prometheus_client import Counter, Gauge, Histogram

# from src.application.services.core.service_registry import ServiceBase, ServiceState

logger = structlog.get_logger()

# Prometheus metrics
memory_usage_gauge = Gauge(
    "system_memory_usage_bytes", "Memory usage in bytes", ["type"]
)
cpu_usage_gauge = Gauge("system_cpu_usage_percent", "CPU usage percentage")
disk_usage_gauge = Gauge("system_disk_usage_percent", "Disk usage percentage", ["path"])
connection_count_gauge = Gauge(
    "system_connections_count", "Number of connections", ["type"]
)
memory_leak_counter = Counter(
    "memory_leak_detections_total", "Number of memory leak detections"
)
health_check_duration = Histogram(
    "health_check_duration_seconds", "Health check duration", ["service"]
)


@dataclass
class MemorySnapshot:
    """Memory usage snapshot"""

    timestamp: datetime
    rss: int  # Resident Set Size
    vms: int  # Virtual Memory Size
    heap_size: int
    heap_used: int
    objects_count: int
    gc_stats: Dict[str, int]
    top_types: List[Tuple[str, int, int]]  # (type, count, size)


@dataclass
class PerformanceMetrics:
    """System performance metrics"""

    cpu_percent: float
    cpu_count: int
    memory_percent: float
    disk_usage: Dict[str, float]
    network_io: Dict[str, int]
    open_files: int
    threads: int
    connections: int


@dataclass
class ServiceHealth:
    """Service health status"""

    service_name: str
    is_healthy: bool
    state: ServiceState
    last_check: datetime
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, bool] = field(default_factory=dict)


class HealthService(ServiceBase):
    """
    Comprehensive health monitoring service with memory leak detection
    """

    def __init__(self, registry, config: Dict[str, Any]):
        super().__init__(registry, config)
        self.check_interval = config.get("health_check_interval", 60)
        self.memory_leak_threshold = config.get(
            "memory_leak_threshold", 100 * 1024 * 1024
        )  # 100MB
        self.memory_snapshots: List[MemorySnapshot] = []
        self.max_snapshots = 60  # Keep 1 hour of snapshots
        self._monitor_task: Optional[asyncio.Task] = None
        self._tracemalloc_started = False

        # WebSocket connection tracking
        self._websocket_connections: Set[str] = set()
        self._connection_memory: Dict[str, int] = {}

    async def initialize(self) -> None:
        """Initialize health monitoring"""
        self.logger.info("Initializing health service")

        # Start memory tracking
        if not self._tracemalloc_started:
            tracemalloc.start(10)  # Keep top 10 frames
            self._tracemalloc_started = True

        # Start monitoring task
        self._monitor_task = asyncio.create_task(self._monitor_loop())

        self._state = ServiceState.READY

    async def shutdown(self) -> None:
        """Shutdown health monitoring"""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        if self._tracemalloc_started:
            tracemalloc.stop()

        self._state = ServiceState.STOPPED

    async def health_check(self) -> Dict[str, Any]:
        """Perform self health check"""
        return {
            "healthy": True,
            "monitoring_active": self._monitor_task and not self._monitor_task.done(),
            "snapshots_collected": len(self.memory_snapshots),
            "services_monitored": len(self.registry._services),
        }

    async def check_all(self) -> Dict[str, Any]:
        """Check health of all services and system"""
        start_time = asyncio.get_event_loop().time()

        # System health
        system_health = await self._check_system_health()

        # Service health
        service_health = await self._check_all_services()

        # Memory health
        memory_health = await self._check_memory_health()

        # WebSocket health
        websocket_health = self._check_websocket_health()

        # Overall health
        all_healthy = (
            system_health["healthy"]
            and all(s["is_healthy"] for s in service_health.values())
            and memory_health["healthy"]
            and websocket_health["healthy"]
        )

        duration = asyncio.get_event_loop().time() - start_time
        health_check_duration.labels(service="all").observe(duration)

        return {
            "healthy": all_healthy,
            "timestamp": datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "system": system_health,
            "services": service_health,
            "memory": memory_health,
            "websockets": websocket_health,
        }

    async def _monitor_loop(self) -> None:
        """Background monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)

                # Take memory snapshot
                snapshot = await self._take_memory_snapshot()
                self._add_snapshot(snapshot)

                # Update metrics
                self._update_prometheus_metrics(snapshot)

                # Check for memory leaks
                if self._detect_memory_leak():
                    memory_leak_counter.inc()
                    await self._handle_memory_leak()

                # Perform health checks
                health_status = await self.check_all()

                if not health_status["healthy"]:
                    self.logger.warning("System unhealthy", details=health_status)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Monitor loop error", error=str(e))

    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system resource health"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_healthy = cpu_percent < 80

            # Memory usage
            memory = psutil.virtual_memory()
            memory_healthy = memory.percent < 85

            # Disk usage
            disk_usage = {}
            disk_healthy = True
            for partition in psutil.disk_partitions():
                if partition.mountpoint:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = usage.percent
                    if usage.percent > 90:
                        disk_healthy = False

            # Network
            net_io = psutil.net_io_counters()

            # Process specific
            process = psutil.Process(os.getpid())
            open_files = len(process.open_files())
            threads = process.num_threads()
            connections = len(process.connections())

            metrics = PerformanceMetrics(
                cpu_percent=cpu_percent,
                cpu_count=psutil.cpu_count(),
                memory_percent=memory.percent,
                disk_usage=disk_usage,
                network_io={
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                },
                open_files=open_files,
                threads=threads,
                connections=connections,
            )

            return {
                "healthy": cpu_healthy and memory_healthy and disk_healthy,
                "cpu_healthy": cpu_healthy,
                "memory_healthy": memory_healthy,
                "disk_healthy": disk_healthy,
                "metrics": metrics.__dict__,
            }

        except Exception as e:
            self.logger.error("System health check failed", error=str(e))
            return {"healthy": False, "error": str(e)}

    async def _check_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all registered services"""
        results = {}

        for name, info in self.registry._services.items():
            if info.state != ServiceState.READY:
                results[name] = {
                    "is_healthy": False,
                    "state": info.state.value,
                    "error": "Service not ready",
                }
                continue

            try:
                start_time = asyncio.get_event_loop().time()
                health = await info.instance.health_check()
                duration = asyncio.get_event_loop().time() - start_time

                health_check_duration.labels(service=name).observe(duration)

                results[name] = {
                    "is_healthy": health.get("healthy", True),
                    "state": info.state.value,
                    "last_check": datetime.utcnow().isoformat(),
                    "check_duration": duration,
                    "details": health,
                }

            except Exception as e:
                results[name] = {
                    "is_healthy": False,
                    "state": info.state.value,
                    "error": str(e),
                }

        return results

    async def _take_memory_snapshot(self) -> MemorySnapshot:
        """Take a snapshot of current memory usage"""
        # Process memory
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        # Python heap
        gc_stats = {
            f"generation_{i}": len(gc.get_objects(i))
            for i in range(gc.get_count().__len__())
        }

        # Top memory consumers
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics("lineno")[:10]

        top_types = []
        for stat in top_stats:
            top_types.append((stat.traceback.format()[0], stat.count, stat.size))

        return MemorySnapshot(
            timestamp=datetime.utcnow(),
            rss=memory_info.rss,
            vms=memory_info.vms,
            heap_size=sys.getsizeof(gc.get_objects()),
            heap_used=sum(sys.getsizeof(obj) for obj in gc.get_objects()),
            objects_count=len(gc.get_objects()),
            gc_stats=gc_stats,
            top_types=top_types,
        )

    def _add_snapshot(self, snapshot: MemorySnapshot) -> None:
        """Add snapshot to history"""
        self.memory_snapshots.append(snapshot)

        # Keep only recent snapshots
        if len(self.memory_snapshots) > self.max_snapshots:
            self.memory_snapshots.pop(0)

    def _detect_memory_leak(self) -> bool:
        """Detect potential memory leaks"""
        if len(self.memory_snapshots) < 10:
            return False

        # Check RSS growth over last 10 snapshots
        recent_snapshots = self.memory_snapshots[-10:]
        rss_values = [s.rss for s in recent_snapshots]

        # Calculate growth rate
        growth = rss_values[-1] - rss_values[0]
        growth_rate = growth / (len(rss_values) - 1)

        # Check if consistently growing
        increasing_count = sum(
            1 for i in range(1, len(rss_values)) if rss_values[i] > rss_values[i - 1]
        )

        # Leak detected if:
        # 1. Memory grew more than threshold
        # 2. Memory increased in at least 70% of samples
        if growth > self.memory_leak_threshold and increasing_count >= 7:
            self.logger.warning(
                "Memory leak detected",
                growth_bytes=growth,
                growth_rate=growth_rate,
                current_rss=rss_values[-1],
            )
            return True

        return False

    async def _handle_memory_leak(self) -> None:
        """Handle detected memory leak"""
        # Force garbage collection
        gc.collect()

        # Log memory profile
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics("lineno")[:20]

        self.logger.error(
            "Memory leak details",
            top_consumers=[
                {
                    "file": stat.traceback.format()[0],
                    "size": stat.size,
                    "count": stat.count,
                }
                for stat in top_stats
            ],
        )

        # Check WebSocket connections for leaks
        await self._check_websocket_memory_leaks()

    def track_websocket_connection(self, session_id: str) -> None:
        """Track WebSocket connection"""
        self._websocket_connections.add(session_id)

        # Track initial memory
        process = psutil.Process(os.getpid())
        self._connection_memory[session_id] = process.memory_info().rss

    def untrack_websocket_connection(self, session_id: str) -> None:
        """Untrack WebSocket connection"""
        self._websocket_connections.discard(session_id)
        self._connection_memory.pop(session_id, None)

    def _check_websocket_health(self) -> Dict[str, Any]:
        """Check WebSocket connection health"""
        active_connections = len(self._websocket_connections)

        # Check for zombie connections
        zombie_connections = []
        for session_id in list(self._websocket_connections):
            # Check if connection is actually alive
            # This would need actual WebSocket checking logic
            pass

        return {
            "healthy": active_connections < 1000,  # Max connections
            "active_connections": active_connections,
            "zombie_connections": len(zombie_connections),
            "connection_ids": list(self._websocket_connections)[:10],  # First 10
        }

    async def _check_websocket_memory_leaks(self) -> None:
        """Check for WebSocket-related memory leaks"""
        current_memory = psutil.Process(os.getpid()).memory_info().rss

        for session_id, initial_memory in list(self._connection_memory.items()):
            if session_id not in self._websocket_connections:
                # Connection closed but memory not released
                memory_diff = current_memory - initial_memory
                if memory_diff > 10 * 1024 * 1024:  # 10MB
                    self.logger.warning(
                        "Potential WebSocket memory leak",
                        session_id=session_id,
                        memory_diff=memory_diff,
                    )

    async def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory health"""
        if not self.memory_snapshots:
            return {"healthy": True, "message": "No snapshots yet"}

        latest = self.memory_snapshots[-1]

        # Check thresholds
        memory_percent = psutil.virtual_memory().percent
        heap_size_mb = latest.heap_size / (1024 * 1024)
        objects_count = latest.objects_count

        healthy = (
            memory_percent < 85 and heap_size_mb < 1000 and objects_count < 1000000
        )  # 1GB heap  # 1M objects

        return {
            "healthy": healthy,
            "memory_percent": memory_percent,
            "heap_size_mb": heap_size_mb,
            "objects_count": objects_count,
            "gc_stats": latest.gc_stats,
            "top_consumers": [
                {"location": t[0], "count": t[1], "size": t[2]}
                for t in latest.top_types[:5]
            ],
        }

    def _update_prometheus_metrics(self, snapshot: MemorySnapshot) -> None:
        """Update Prometheus metrics"""
        # Memory metrics
        memory_usage_gauge.labels(type="rss").set(snapshot.rss)
        memory_usage_gauge.labels(type="vms").set(snapshot.vms)
        memory_usage_gauge.labels(type="heap").set(snapshot.heap_size)

        # CPU metrics
        cpu_usage_gauge.set(psutil.cpu_percent())

        # Disk metrics
        for partition in psutil.disk_partitions():
            if partition.mountpoint:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage_gauge.labels(path=partition.mountpoint).set(usage.percent)

        # Connection metrics
        connection_count_gauge.labels(type="websocket").set(
            len(self._websocket_connections)
        )
        connection_count_gauge.labels(type="total").set(
            len(psutil.Process(os.getpid()).connections())
        )

    def get_memory_report(self) -> Dict[str, Any]:
        """Generate memory usage report"""
        if not self.memory_snapshots:
            return {"message": "No memory data available"}

        # Analyze trends
        rss_values = [s.rss for s in self.memory_snapshots]

        return {
            "current_rss_mb": rss_values[-1] / (1024 * 1024),
            "min_rss_mb": min(rss_values) / (1024 * 1024),
            "max_rss_mb": max(rss_values) / (1024 * 1024),
            "avg_rss_mb": sum(rss_values) / len(rss_values) / (1024 * 1024),
            "trend": "increasing" if rss_values[-1] > rss_values[0] else "stable",
            "samples": len(self.memory_snapshots),
            "monitoring_duration_minutes": len(self.memory_snapshots)
            * self.check_interval
            / 60,
        }
