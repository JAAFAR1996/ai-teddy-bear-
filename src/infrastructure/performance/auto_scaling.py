#!/usr/bin/env python3
"""
📈 Auto Scaling Infrastructure - AI Teddy Bear Project
نظام التوسع التلقائي مع Kubernetes و custom metrics

Features:
- Kubernetes Horizontal Pod Autoscaler
- Custom metrics-based scaling
- Load balancing with intelligent routing
- Geographic distribution and edge computing
- Cost optimization with spot instances
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Prometheus metrics
SCALING_EVENTS_TOTAL = Counter(
    "scaling_events_total", "Total scaling events", ["direction", "reason"]
)
CURRENT_REPLICAS = Gauge(
    "current_replicas", "Current number of replicas", ["deployment"]
)
TARGET_REPLICAS = Gauge(
    "target_replicas",
    "Target number of replicas",
    ["deployment"])
SCALING_DURATION = Histogram(
    "scaling_duration_seconds", "Time taken for scaling operation"
)


class ScalingPolicy:
    """Scaling policy configuration"""

    def __init__(self, config: Dict[str, Any]):
        self.min_replicas = config.get("min_replicas", 2)
        self.max_replicas = config.get("max_replicas", 20)
        self.target_cpu_utilization = config.get("target_cpu_utilization", 70)
        self.target_memory_utilization = config.get(
            "target_memory_utilization", 80)
        self.target_request_rate = config.get("target_request_rate", 1000)
        self.scale_up_cooldown_seconds = config.get(
            "scale_up_cooldown_seconds", 60)
        self.scale_down_cooldown_seconds = config.get(
            "scale_down_cooldown_seconds", 300
        )
        self.scale_up_threshold = config.get(
            "scale_up_threshold", 1.2
        )  # 20% above target
        self.scale_down_threshold = config.get(
            "scale_down_threshold", 0.8
        )  # 20% below target


class GeographicRegion:
    """Geographic region configuration"""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.location = config.get("location", "unknown")
        self.latency_ms = config.get("latency_ms", 100)
        self.capacity = config.get("capacity", 1000)
        self.current_load = 0
        self.is_healthy = True
        self.last_health_check = None


class AutoScalingSystem:
    """Advanced auto-scaling system with Kubernetes integration"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scaling_policy = ScalingPolicy(config.get("scaling_policy", {}))
        self.regions: List[GeographicRegion] = []
        self.current_replicas = self.scaling_policy.min_replicas
        self.target_replicas = self.scaling_policy.min_replicas
        self.last_scale_up = None
        self.last_scale_down = None
        self.metrics_history: List[Dict[str, Any]] = []
        self.scaling_enabled = config.get("scaling_enabled", True)

    async def initialize(self) -> None:
        """Initialize auto-scaling system"""
        logger.info("🚀 Initializing auto-scaling system...")

        try:
            # Setup geographic regions
            await self._setup_geographic_regions()

            # Initialize Kubernetes client (mock for now)
            await self._initialize_kubernetes_client()

            # Start monitoring tasks
            asyncio.create_task(self._monitor_metrics())
            asyncio.create_task(self._auto_scaling_loop())
            asyncio.create_task(self._geographic_load_balancing())

            logger.info("✅ Auto-scaling system initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize auto-scaling system: {e}")
            raise

    async def _setup_geographic_regions(self) -> None:
        """Setup geographic regions for edge computing"""
        region_configs = self.config.get(
            "geographic_regions",
            [
                {
                    "name": "us-east",
                    "location": "US East",
                    "latency_ms": 50,
                    "capacity": 2000,
                },
                {
                    "name": "us-west",
                    "location": "US West",
                    "latency_ms": 80,
                    "capacity": 1500,
                },
                {
                    "name": "eu-west",
                    "location": "Europe West",
                    "latency_ms": 120,
                    "capacity": 1800,
                },
                {
                    "name": "asia-east",
                    "location": "Asia East",
                    "latency_ms": 150,
                    "capacity": 1200,
                },
            ],
        )

        for region_config in region_configs:
            region = GeographicRegion(region_config["name"], region_config)
            self.regions.append(region)

        logger.info(f"✅ Setup {len(self.regions)} geographic regions")

    async def _initialize_kubernetes_client(self) -> None:
        """Initialize Kubernetes client for scaling operations"""
        # Mock Kubernetes client for demonstration
        # In production, use kubernetes-asyncio library
        logger.info("✅ Kubernetes client initialized (mock)")

    async def _monitor_metrics(self) -> None:
        """Monitor system metrics for scaling decisions"""
        while True:
            try:
                await asyncio.sleep(30)  # Every 30 seconds

                # Collect current metrics
                metrics = await self._collect_current_metrics()

                # Store in history
                self.metrics_history.append(
                    {"timestamp": datetime.now().isoformat(), **metrics}
                )

                # Keep only recent metrics (last hour)
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.metrics_history = [
                    m
                    for m in self.metrics_history
                    if datetime.fromisoformat(m["timestamp"]) > cutoff_time
                ]

                # Update Prometheus metrics
                CURRENT_REPLICAS.labels(deployment="ai-teddy-api").set(
                    self.current_replicas
                )
                TARGET_REPLICAS.labels(deployment="ai-teddy-api").set(
                    self.target_replicas
                )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics monitoring failed: {e}")

    async def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        # Mock metrics collection
        # In production, collect from Prometheus, Kubernetes, etc.
        return {
            "cpu_utilization": 65.0,  # Mock CPU usage
            "memory_utilization": 75.0,  # Mock memory usage
            "request_rate": 850,  # Mock requests per second
            "response_time_ms": 95,  # Mock response time
            "error_rate": 0.02,  # Mock error rate
            "active_connections": 1250,  # Mock active connections
        }

    async def _auto_scaling_loop(self) -> None:
        """Main auto-scaling decision loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute

                if not self.scaling_enabled:
                    continue

                # Get current metrics
                current_metrics = await self._collect_current_metrics()

                # Make scaling decision
                scaling_decision = await self._make_scaling_decision(current_metrics)

                if scaling_decision:
                    await self._execute_scaling_decision(scaling_decision)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-scaling loop failed: {e}")

    def _should_scale_up(
            self, metrics: Dict[str, Any], current_time: float) -> bool:
        """Checks if a scale-up action is warranted."""
        if self.current_replicas >= self.scaling_policy.max_replicas:
            return False

        if (
            self.last_scale_up
            and (current_time - self.last_scale_up)
            < self.scaling_policy.scale_up_cooldown_seconds
        ):
            return False

        return (
            metrics["cpu_utilization"]
            > self.scaling_policy.target_cpu_utilization
            * self.scaling_policy.scale_up_threshold
            or metrics["memory_utilization"]
            > self.scaling_policy.target_memory_utilization
            * self.scaling_policy.scale_up_threshold
            or metrics["request_rate"]
            > self.scaling_policy.target_request_rate
            * self.scaling_policy.scale_up_threshold
        )

    def _should_scale_down(
            self, metrics: Dict[str, Any], current_time: float) -> bool:
        """Checks if a scale-down action is warranted."""
        if self.current_replicas <= self.scaling_policy.min_replicas:
            return False

        if (
            self.last_scale_down
            and (current_time - self.last_scale_down)
            < self.scaling_policy.scale_down_cooldown_seconds
        ):
            return False

        return (
            metrics["cpu_utilization"]
            < self.scaling_policy.target_cpu_utilization
            * self.scaling_policy.scale_down_threshold
            and metrics["memory_utilization"]
            < self.scaling_policy.target_memory_utilization
            * self.scaling_policy.scale_down_threshold
            and metrics["request_rate"]
            < self.scaling_policy.target_request_rate
            * self.scaling_policy.scale_down_threshold
        )

    async def _make_scaling_decision(
        self, metrics: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Make scaling decision based on metrics"""
        current_time = time.time()

        if self._should_scale_up(metrics, current_time):
            return {
                "action": "scale_up",
                "reason": "high_utilization",
                "current_replicas": self.current_replicas,
                "target_replicas": min(
                    self.current_replicas + 1, self.scaling_policy.max_replicas
                ),
                "metrics": metrics,
            }

        if self._should_scale_down(metrics, current_time):
            return {
                "action": "scale_down",
                "reason": "low_utilization",
                "current_replicas": self.current_replicas,
                "target_replicas": max(
                    self.current_replicas - 1, self.scaling_policy.min_replicas
                ),
                "metrics": metrics,
            }

        return None

    async def _execute_scaling_decision(
            self, decision: Dict[str, Any]) -> None:
        """Execute scaling decision"""
        start_time = time.time()

        try:
            action = decision["action"]
            target_replicas = decision["target_replicas"]

            logger.info(
                f"🔄 Executing {action}: {self.current_replicas} -> {target_replicas} replicas"
            )

            # Update Kubernetes deployment
            await self._update_kubernetes_deployment(target_replicas)

            # Update local state
            self.current_replicas = target_replicas
            self.target_replicas = target_replicas

            # Update timestamps
            if action == "scale_up":
                self.last_scale_up = time.time()
            else:
                self.last_scale_down = time.time()

            # Record metrics
            duration = time.time() - start_time
            SCALING_DURATION.observe(duration)
            SCALING_EVENTS_TOTAL.labels(
                direction=action, reason=decision["reason"]
            ).inc()

            logger.info(f"✅ Scaling completed in {duration:.2f}s")

        except Exception as e:
            logger.error(f"❌ Scaling execution failed: {e}")

    async def _update_kubernetes_deployment(
            self, target_replicas: int) -> None:
        """Update Kubernetes deployment replicas"""
        # Mock Kubernetes API call
        # In production, use kubernetes-asyncio to update deployment
        logger.info(
            f"🔄 Updating Kubernetes deployment to {target_replicas} replicas")
        await asyncio.sleep(2)  # Simulate API call

    async def _geographic_load_balancing(self) -> None:
        """Geographic load balancing for edge computing"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                # Update region health status
                await self._update_region_health()

                # Optimize traffic distribution
                await self._optimize_traffic_distribution()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Geographic load balancing failed: {e}")

    async def _update_region_health(self) -> None:
        """Update health status of geographic regions"""
        for region in self.regions:
            try:
                # Mock health check
                region.is_healthy = True  # In production, check actual health
                region.last_health_check = datetime.now()

                # Simulate load variation
                region.current_load = min(
                    region.capacity,
                    region.current_load + (hash(region.name) % 100 - 50),
                )

            except Exception as e:
                region.is_healthy = False
                logger.warning(
                    f"Region {region.name} health check failed: {e}")

    async def _optimize_traffic_distribution(self) -> None:
        """Optimize traffic distribution across regions"""
        healthy_regions = [r for r in self.regions if r.is_healthy]

        if not healthy_regions:
            logger.warning("⚠️ No healthy regions available")
            return

        # Calculate optimal distribution based on capacity and latency
        total_capacity = sum(r.capacity for r in healthy_regions)

        for region in healthy_regions:
            # Weight by capacity and inverse latency
            weight = (region.capacity / total_capacity) * \
                (100 / region.latency_ms)
            region.traffic_weight = weight

        logger.info(
            f"✅ Traffic distribution optimized across {len(healthy_regions)} regions"
        )

    async def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status"""
        current_metrics = await self._collect_current_metrics()

        return {
            "auto_scaling": {
                "enabled": self.scaling_enabled,
                "current_replicas": self.current_replicas,
                "target_replicas": self.target_replicas,
                "min_replicas": self.scaling_policy.min_replicas,
                "max_replicas": self.scaling_policy.max_replicas,
                "last_scale_up": self.last_scale_up,
                "last_scale_down": self.last_scale_down,
            },
            "geographic_regions": {
                region.name: {
                    "location": region.location,
                    "latency_ms": region.latency_ms,
                    "capacity": region.capacity,
                    "current_load": region.current_load,
                    "is_healthy": region.is_healthy,
                    "traffic_weight": getattr(region, "traffic_weight", 0),
                }
                for region in self.regions
            },
            "current_metrics": current_metrics,
            "scaling_policy": {
                "target_cpu_utilization": self.scaling_policy.target_cpu_utilization,
                "target_memory_utilization": self.scaling_policy.target_memory_utilization,
                "target_request_rate": self.scaling_policy.target_request_rate,
                "scale_up_cooldown_seconds": self.scaling_policy.scale_up_cooldown_seconds,
                "scale_down_cooldown_seconds": self.scaling_policy.scale_down_cooldown_seconds,
            },
        }

    async def manual_scale(self, target_replicas: int) -> bool:
        """Manually scale to target replicas"""
        if not (
            self.scaling_policy.min_replicas
            <= target_replicas
            <= self.scaling_policy.max_replicas
        ):
            logger.error(
                f"Target replicas {target_replicas} outside allowed range")
            return False

        decision = {
            "action": (
                "scale_up" if target_replicas > self.current_replicas else "scale_down"
            ),
            "reason": "manual_scale",
            "current_replicas": self.current_replicas,
            "target_replicas": target_replicas,
            "metrics": await self._collect_current_metrics(),
        }

        await self._execute_scaling_decision(decision)
        return True

    async def enable_cost_optimization(self) -> None:
        """Enable cost optimization with spot instances"""
        logger.info("💰 Enabling cost optimization with spot instances")

        # In production, this would:
        # 1. Configure node selectors for spot instances
        # 2. Set up pod disruption budgets
        # 3. Configure graceful shutdown handling
        # 4. Monitor spot instance availability

        logger.info("✅ Cost optimization enabled")

    async def cleanup(self) -> None:
        """Cleanup auto-scaling system"""
        logger.info("🛑 Cleaning up auto-scaling system...")

        # Scale down to minimum replicas
        if self.current_replicas > self.scaling_policy.min_replicas:
            await self.manual_scale(self.scaling_policy.min_replicas)

        logger.info("✅ Auto-scaling system cleanup complete")


# Factory function
async def create_auto_scaling_system(
        config: Dict[str, Any]) -> AutoScalingSystem:
    """Create and initialize auto-scaling system"""
    scaling_system = AutoScalingSystem(config)
    await scaling_system.initialize()
    return scaling_system
