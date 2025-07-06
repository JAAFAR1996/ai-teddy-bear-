"""
Custom Metrics for AI Teddy Bear Observability
==============================================

This module provides a central aggregator for all observability metrics,
offering a unified interface for metric collection and analysis.

Integrated with enterprise_observability.py and comprehensive_monitor.py for unified observability.
"""

import asyncio
import logging

from .metrics import (
    AIPerformanceMetrics,
    ChildSafetyMetrics,
    SystemHealthMetrics,
)

logger = logging.getLogger(__name__)


class ObservabilityAggregator:
    """
    Central aggregator for all observability metrics.
    Provides a unified interface for metric collection and analysis.
    """

    def __init__(self):
        self.child_safety_metrics = ChildSafetyMetrics()
        self.ai_performance_metrics = AIPerformanceMetrics()
        self.system_health_metrics = SystemHealthMetrics()

        # Start background tasks
        asyncio.create_task(self._periodic_compliance_update())
        asyncio.create_task(self._periodic_health_check())

    async def _periodic_compliance_update(self):
        """Periodically update compliance metrics"""
        while True:
            try:
                self.child_safety_metrics.update_compliance_metrics()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(
                    f"Error updating compliance metrics: {e}", exc_info=True)
                await asyncio.sleep(60)

    async def _periodic_health_check(self):
        """Periodically update system health metrics"""
        while True:
            try:
                # Assuming 'ai-teddy-core' is a valid service name for SLO metrics
                self.system_health_metrics.update_slo_metrics("ai-teddy-core")
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(
                    f"Error updating health metrics: {e}", exc_info=True)
                await asyncio.sleep(30)

    def get_safety_metrics(self) -> ChildSafetyMetrics:
        """Get child safety metrics instance"""
        return self.child_safety_metrics

    def get_performance_metrics(self) -> AIPerformanceMetrics:
        """Get AI performance metrics instance"""
        return self.ai_performance_metrics

    def get_health_metrics(self) -> SystemHealthMetrics:
        """Get system health metrics instance"""
        return self.system_health_metrics


# Global metrics instance, provides a singleton-like access pattern
observability = ObservabilityAggregator()
