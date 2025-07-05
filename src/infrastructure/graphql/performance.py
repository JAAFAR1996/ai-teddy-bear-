#!/usr/bin/env python3
"""
📊 GraphQL Performance Monitor
Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise performance monitoring and optimization for GraphQL
"""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from prometheus_client import Counter, Gauge, Histogram

logger = structlog.get_logger()

# Prometheus metrics
GRAPHQL_QUERIES = Counter(
    "graphql_queries_total", "Total GraphQL queries", [
        "operation_name", "status"])
GRAPHQL_QUERY_DURATION = Histogram(
    "graphql_query_duration_seconds",
    "GraphQL query duration",
    ["operation_name"])
GRAPHQL_RESOLVER_DURATION = Histogram(
    "graphql_resolver_duration_seconds",
    "GraphQL resolver duration",
    ["resolver_name"])
GRAPHQL_DATALOADER_HITS = Counter(
    "graphql_dataloader_hits_total", "DataLoader cache hits", ["loader_name"]
)
GRAPHQL_DATALOADER_MISSES = Counter(
    "graphql_dataloader_misses_total",
    "DataLoader cache misses",
    ["loader_name"])
GRAPHQL_ACTIVE_QUERIES = Gauge(
    "graphql_active_queries", "Currently active GraphQL queries"
)
GRAPHQL_COMPLEXITY = Histogram(
    "graphql_query_complexity", "GraphQL query complexity score"
)


@dataclass
class QueryMetrics:
    """Metrics for a single GraphQL query"""

    operation_name: str
    query: str
    variables: Dict[str, Any]
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    complexity: int = 0
    resolver_calls: Dict[str, int] = field(default_factory=dict)
    dataloader_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)
    cache_hits: int = 0
    cache_misses: int = 0
    errors: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, success, error

    def finish(self):
        """Mark query as finished and calculate duration"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        if not self.errors:
            self.status = "success"
        else:
            self.status = "error"


@dataclass
class PerformanceConfig:
    """Configuration for GraphQL performance monitoring"""

    enable_complexity_analysis: bool = True
    max_query_complexity: int = 1000
    enable_slow_query_logging: bool = True
    slow_query_threshold: float = 2.0  # seconds
    enable_dataloader_monitoring: bool = True
    enable_resolver_timing: bool = True
    cache_performance_metrics: bool = True
    metrics_retention_hours: int = 24


class GraphQLPerformanceMonitor:
    """
    🏗️ GraphQL Performance Monitor
    Comprehensive monitoring and optimization for GraphQL operations
    """

    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or PerformanceConfig()
        self.active_queries: Dict[str, QueryMetrics] = {}
        self.query_history: List[QueryMetrics] = []
        self.resolver_stats = defaultdict(
            lambda: {"count": 0, "total_time": 0.0})
        self.dataloader_stats = defaultdict(
            lambda: {"hits": 0, "misses": 0, "loads": 0}
        )
        logger.info("📊 GraphQL Performance Monitor initialized")

    def start_query(
        self,
        operation_name: str,
        query: str,
        variables: Dict[str, Any],
        query_id: Optional[str] = None,
    ) -> str:
        """Start monitoring a GraphQL query"""
        query_id = query_id or f"query_{int(time.time() * 1000000)}"
        metrics = QueryMetrics(
            operation_name=operation_name,
            query=query,
            variables=variables,
            start_time=time.time(),
        )
        self.active_queries[query_id] = metrics
        GRAPHQL_ACTIVE_QUERIES.inc()
        logger.debug(
            "🚀 Query started", operation_name=operation_name, query_id=query_id
        )
        return query_id

    def finish_query(self, query_id: str, errors: Optional[List[str]] = None):
        """Finish monitoring a GraphQL query"""
        if query_id not in self.active_queries:
            logger.warning(
                "Query not found in active queries",
                query_id=query_id)
            return

        metrics = self.active_queries[query_id]
        metrics.errors = errors or []
        metrics.finish()

        GRAPHQL_QUERIES.labels(
            operation_name=metrics.operation_name, status=metrics.status
        ).inc()
        GRAPHQL_QUERY_DURATION.labels(
            operation_name=metrics.operation_name).observe(
            metrics.duration)
        GRAPHQL_COMPLEXITY.observe(metrics.complexity)
        GRAPHQL_ACTIVE_QUERIES.dec()

        if (
            self.config.enable_slow_query_logging
            and metrics.duration > self.config.slow_query_threshold
        ):
            logger.warning(
                "🐌 Slow query detected",
                operation_name=metrics.operation_name,
                duration=metrics.duration,
                complexity=metrics.complexity,
                query_id=query_id,
            )

        self.query_history.append(metrics)
        del self.active_queries[query_id]
        self._cleanup_history()
        logger.debug(
            "✅ Query finished",
            operation_name=metrics.operation_name,
            duration=metrics.duration,
            status=metrics.status,
            query_id=query_id,
        )

    def record_resolver_call(self, resolver_name: str, duration: float):
        """Record a resolver call"""
        if self.config.enable_resolver_timing:
            self.resolver_stats[resolver_name]["count"] += 1
            self.resolver_stats[resolver_name]["total_time"] += duration
            GRAPHQL_RESOLVER_DURATION.labels(
                resolver_name=resolver_name).observe(duration)

    def record_dataloader_hit(self, loader_name: str):
        """Record a DataLoader cache hit"""
        if self.config.enable_dataloader_monitoring:
            self.dataloader_stats[loader_name]["hits"] += 1
            GRAPHQL_DATALOADER_HITS.labels(loader_name=loader_name).inc()

    def record_dataloader_miss(self, loader_name: str):
        """Record a DataLoader cache miss"""
        if self.config.enable_dataloader_monitoring:
            self.dataloader_stats[loader_name]["misses"] += 1
            GRAPHQL_DATALOADER_MISSES.labels(loader_name=loader_name).inc()

    def record_dataloader_load(self, loader_name: str, batch_size: int):
        """Record a DataLoader batch load"""
        if self.config.enable_dataloader_monitoring:
            self.dataloader_stats[loader_name]["loads"] += 1

    def set_query_complexity(self, query_id: str, complexity: int):
        """Set complexity score for a query"""
        if query_id in self.active_queries:
            self.active_queries[query_id].complexity = complexity
            if (
                self.config.enable_complexity_analysis
                and complexity > self.config.max_query_complexity
            ):
                logger.warning(
                    "⚠️ High complexity query",
                    query_id=query_id,
                    complexity=complexity,
                    max_allowed=self.config.max_query_complexity,
                )

    def _get_query_stats(
            self, recent_queries: List[QueryMetrics]) -> Dict[str, Any]:
        """Calculates statistics for the provided queries."""
        total_queries = len(recent_queries)
        if total_queries == 0:
            return {
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "success_rate": 0,
                "average_duration": 0,
                "average_complexity": 0,
                "active_queries": len(self.active_queries),
            }

        successful_queries = len(
            [q for q in recent_queries if q.status == "success"])
        failed_queries = total_queries - successful_queries
        avg_duration = (
            sum(q.duration for q in recent_queries if q.duration) / total_queries
        )
        avg_complexity = sum(
            q.complexity for q in recent_queries) / total_queries

        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "success_rate": successful_queries / total_queries,
            "average_duration": avg_duration,
            "average_complexity": avg_complexity,
            "active_queries": len(self.active_queries),
        }

    def _get_dataloader_summary(self) -> Dict[str, Any]:
        """Generates a summary of dataloader performance."""
        summary = {}
        for loader_name, stats in self.dataloader_stats.items():
            total_requests = stats["hits"] + stats["misses"]
            summary[loader_name] = {
                "hit_rate": stats["hits"] /
                total_requests if total_requests > 0 else 0,
                "cache_hits": stats["hits"],
                "cache_misses": stats["misses"],
                "batch_loads": stats["loads"],
            }
        return summary

    def _get_resolver_summary(self) -> Dict[str, Any]:
        """Generates a summary of resolver performance."""
        summary = {}
        for resolver_name, stats in self.resolver_stats.items():
            summary[resolver_name] = {
                "call_count": stats["count"],
                "total_time": stats["total_time"],
                "average_time": (
                    stats["total_time"] /
                    stats["count"] if stats["count"] > 0 else 0),
            }
        return summary

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        now = datetime.utcnow()
        recent_queries = [
            q
            for q in self.query_history
            if q.end_time
            and datetime.fromtimestamp(q.end_time) > now - timedelta(hours=1)
        ]

        return {
            "query_stats": self._get_query_stats(recent_queries),
            "dataloader_stats": self._get_dataloader_summary(),
            "resolver_stats": self._get_resolver_summary(),
            "timestamp": now.isoformat(),
        }

    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest queries from recent history"""
        recent_queries = [
            q for q in self.query_history if q.duration and q.end_time]
        slow_queries = sorted(
            recent_queries,
            key=lambda q: q.duration,
            reverse=True)[
            :limit]

        return [
            {
                "operation_name": q.operation_name,
                "duration": q.duration,
                "complexity": q.complexity,
                "status": q.status,
                "errors": q.errors,
                "timestamp": datetime.fromtimestamp(q.end_time).isoformat(),
            }
            for q in slow_queries
        ]

    def _get_dataloader_recommendations(self) -> List[str]:
        """Analyzes DataLoader performance and returns recommendations."""
        recommendations = []
        for loader_name, stats in self.dataloader_stats.items():
            total_requests = stats["hits"] + stats["misses"]
            if total_requests > 0:
                hit_rate = stats["hits"] / total_requests
                if hit_rate < 0.7:
                    recommendations.append(
                        f"Consider increasing cache TTL for {loader_name} DataLoader (hit rate: {hit_rate:.1%})"
                    )
        return recommendations

    def _get_resolver_recommendations(self) -> List[str]:
        """Analyzes resolver performance and returns recommendations."""
        recommendations = []
        for resolver_name, stats in self.resolver_stats.items():
            if stats["count"] > 0 and (
                    stats["total_time"] / stats["count"]) > 0.5:
                avg_time = stats["total_time"] / stats["count"]
                recommendations.append(
                    f"Optimize {resolver_name} resolver (avg time: {avg_time:.2f}s)"
                )
        return recommendations

    def _get_complexity_recommendations(self) -> List[str]:
        """Analyzes query complexity and returns recommendations."""
        recent_queries = self.query_history[-100:]
        if not recent_queries:
            return []
        high_complexity_queries = [
            q for q in recent_queries if q.complexity > 500]
        if len(high_complexity_queries) > len(recent_queries) * 0.1:
            return [
                "Consider query complexity limits - many queries have high complexity"
            ]
        return []

    def get_query_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recs = self._get_dataloader_recommendations()
        recs.extend(self._get_resolver_recommendations())
        recs.extend(self._get_complexity_recommendations())
        return recs

    def _cleanup_history(self):
        """Clean up old query history"""
        if not self.config.cache_performance_metrics:
            return
        cutoff_time = time.time() - (self.config.metrics_retention_hours * 3600)
        self.query_history = [
            q for q in self.query_history if q.end_time and q.end_time > cutoff_time]

    def reset_stats(self):
        """Reset all performance statistics"""
        self.query_history.clear()
        self.resolver_stats.clear()
        self.dataloader_stats.clear()
        logger.info("📊 Performance statistics reset")


performance_monitor = GraphQLPerformanceMonitor()


def timed_resolver(resolver_name: str):
    """Decorator to time GraphQL resolvers"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                performance_monitor.record_resolver_call(
                    resolver_name, duration)

        return wrapper

    return decorator
