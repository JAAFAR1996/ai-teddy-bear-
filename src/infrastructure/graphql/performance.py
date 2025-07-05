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
GRAPHQL_QUERIES = Counter('graphql_queries_total', 'Total GraphQL queries', ['operation_name', 'status'])
GRAPHQL_QUERY_DURATION = Histogram('graphql_query_duration_seconds', 'GraphQL query duration', ['operation_name'])
GRAPHQL_RESOLVER_DURATION = Histogram('graphql_resolver_duration_seconds', 'GraphQL resolver duration', ['resolver_name'])
GRAPHQL_DATALOADER_HITS = Counter('graphql_dataloader_hits_total', 'DataLoader cache hits', ['loader_name'])
GRAPHQL_DATALOADER_MISSES = Counter('graphql_dataloader_misses_total', 'DataLoader cache misses', ['loader_name'])
GRAPHQL_ACTIVE_QUERIES = Gauge('graphql_active_queries', 'Currently active GraphQL queries')
GRAPHQL_COMPLEXITY = Histogram('graphql_query_complexity', 'GraphQL query complexity score')


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
    
    def finish(self) -> Any:
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
    
    def __init__(self, config: PerformanceConfig = None):
        self.config = config or PerformanceConfig()
        self.active_queries: Dict[str, QueryMetrics] = {}
        self.query_history: List[QueryMetrics] = []
        self.resolver_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0})
        self.dataloader_stats = defaultdict(lambda: {"hits": 0, "misses": 0, "loads": 0})
        logger.info("📊 GraphQL Performance Monitor initialized")
    
    def start_query(
        self, 
        operation_name: str, 
        query: str, 
        variables: Dict[str, Any],
        query_id: str = None
    ) -> str:
        """Start monitoring a GraphQL query"""
        query_id = query_id or f"query_{int(time.time() * 1000000)}"
        
        metrics = QueryMetrics(
            operation_name=operation_name,
            query=query,
            variables=variables,
            start_time=time.time()
        )
        
        self.active_queries[query_id] = metrics
        GRAPHQL_ACTIVE_QUERIES.inc()
        
        logger.debug("🚀 Query started", 
                    operation_name=operation_name,
                    query_id=query_id)
        
        return query_id
    
    def finish_query(List[str] = None) -> None:
        """Finish monitoring a GraphQL query"""
        if query_id not in self.active_queries:
            logger.warning("Query not found in active queries", query_id=query_id)
            return
        
        metrics = self.active_queries[query_id]
        metrics.errors = errors or []
        metrics.finish()
        
        # Update Prometheus metrics
        GRAPHQL_QUERIES.labels(
            operation_name=metrics.operation_name,
            status=metrics.status
        ).inc()
        
        GRAPHQL_QUERY_DURATION.labels(
            operation_name=metrics.operation_name
        ).observe(metrics.duration)
        
        GRAPHQL_COMPLEXITY.observe(metrics.complexity)
        GRAPHQL_ACTIVE_QUERIES.dec()
        
        # Log slow queries
        if (self.config.enable_slow_query_logging and 
            metrics.duration > self.config.slow_query_threshold):
            logger.warning("🐌 Slow query detected",
                          operation_name=metrics.operation_name,
                          duration=metrics.duration,
                          complexity=metrics.complexity,
                          query_id=query_id)
        
        # Move to history
        self.query_history.append(metrics)
        del self.active_queries[query_id]
        
        # Cleanup old history
        self._cleanup_history()
        
        logger.debug("✅ Query finished",
                    operation_name=metrics.operation_name,
                    duration=metrics.duration,
                    status=metrics.status,
                    query_id=query_id)
    
    def record_resolver_call(float) -> None:
        """Record a resolver call"""
        if self.config.enable_resolver_timing:
            self.resolver_stats[resolver_name]["count"] += 1
            self.resolver_stats[resolver_name]["total_time"] += duration
            
            GRAPHQL_RESOLVER_DURATION.labels(
                resolver_name=resolver_name
            ).observe(duration)
    
    def record_dataloader_hit(str) -> None:
        """Record a DataLoader cache hit"""
        if self.config.enable_dataloader_monitoring:
            self.dataloader_stats[loader_name]["hits"] += 1
            GRAPHQL_DATALOADER_HITS.labels(loader_name=loader_name).inc()
    
    def record_dataloader_miss(str) -> None:
        """Record a DataLoader cache miss"""
        if self.config.enable_dataloader_monitoring:
            self.dataloader_stats[loader_name]["misses"] += 1
            GRAPHQL_DATALOADER_MISSES.labels(loader_name=loader_name).inc()
    
    def record_dataloader_load(int) -> None:
        """Record a DataLoader batch load"""
        if self.config.enable_dataloader_monitoring:
            self.dataloader_stats[loader_name]["loads"] += 1
    
    def set_query_complexity(int) -> None:
        """Set complexity score for a query"""
        if query_id in self.active_queries:
            self.active_queries[query_id].complexity = complexity
            
            if (self.config.enable_complexity_analysis and 
                complexity > self.config.max_query_complexity):
                logger.warning("⚠️ High complexity query",
                              query_id=query_id,
                              complexity=complexity,
                              max_allowed=self.config.max_query_complexity)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        now = datetime.utcnow()
        recent_queries = [
            q for q in self.query_history 
            if q.end_time and datetime.fromtimestamp(q.end_time) > now - timedelta(hours=1)
        ]
        
        total_queries = len(recent_queries)
        successful_queries = len([q for q in recent_queries if q.status == "success"])
        failed_queries = len([q for q in recent_queries if q.status == "error"])
        
        avg_duration = (
            sum(q.duration for q in recent_queries if q.duration) / total_queries
            if total_queries > 0 else 0
        )
        
        avg_complexity = (
            sum(q.complexity for q in recent_queries) / total_queries
            if total_queries > 0 else 0
        )
        
        # DataLoader statistics
        dataloader_summary = {}
        for loader_name, stats in self.dataloader_stats.items():
            total_requests = stats["hits"] + stats["misses"]
            hit_rate = stats["hits"] / total_requests if total_requests > 0 else 0
            
            dataloader_summary[loader_name] = {
                "hit_rate": hit_rate,
                "cache_hits": stats["hits"],
                "cache_misses": stats["misses"],
                "batch_loads": stats["loads"]
            }
        
        # Resolver statistics
        resolver_summary = {}
        for resolver_name, stats in self.resolver_stats.items():
            avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
            
            resolver_summary[resolver_name] = {
                "call_count": stats["count"],
                "total_time": stats["total_time"],
                "average_time": avg_time
            }
        
        return {
            "query_stats": {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "success_rate": successful_queries / total_queries if total_queries > 0 else 0,
                "average_duration": avg_duration,
                "average_complexity": avg_complexity,
                "active_queries": len(self.active_queries)
            },
            "dataloader_stats": dataloader_summary,
            "resolver_stats": resolver_summary,
            "timestamp": now.isoformat()
        }
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest queries from recent history"""
        recent_queries = [
            q for q in self.query_history 
            if q.duration and q.end_time
        ]
        
        # Sort by duration descending
        slow_queries = sorted(recent_queries, key=lambda q: q.duration, reverse=True)[:limit]
        
        return [
            {
                "operation_name": q.operation_name,
                "duration": q.duration,
                "complexity": q.complexity,
                "status": q.status,
                "errors": q.errors,
                "timestamp": datetime.fromtimestamp(q.end_time).isoformat()
            }
            for q in slow_queries
        ]
    
    def get_query_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        # Analyze DataLoader performance
        for loader_name, stats in self.dataloader_stats.items():
            total_requests = stats["hits"] + stats["misses"]
            if total_requests > 0:
                hit_rate = stats["hits"] / total_requests
                if hit_rate < 0.7:  # Less than 70% cache hit rate
                    recommendations.append(
                        f"Consider increasing cache TTL for {loader_name} DataLoader (hit rate: {hit_rate:.1%})"
                    )
        
        # Analyze resolver performance
        for resolver_name, stats in self.resolver_stats.items():
            if stats["count"] > 0:
                avg_time = stats["total_time"] / stats["count"]
                if avg_time > 0.5:  # Slower than 500ms
                    recommendations.append(
                        f"Optimize {resolver_name} resolver (avg time: {avg_time:.2f}s)"
                    )
        
        # Analyze query complexity
        recent_queries = self.query_history[-100:]  # Last 100 queries
        high_complexity_queries = [q for q in recent_queries if q.complexity > 500]
        if len(high_complexity_queries) > len(recent_queries) * 0.1:  # More than 10%
            recommendations.append(
                "Consider query complexity limits - many queries have high complexity"
            )
        
        return recommendations
    
    def _cleanup_history(self) -> Any:
        """Clean up old query history"""
        if not self.config.cache_performance_metrics:
            return
        
        cutoff_time = time.time() - (self.config.metrics_retention_hours * 3600)
        self.query_history = [
            q for q in self.query_history 
            if q.end_time and q.end_time > cutoff_time
        ]
    
    def reset_stats(self) -> Any:
        """Reset all performance statistics"""
        self.query_history.clear()
        self.resolver_stats.clear()
        self.dataloader_stats.clear()
        logger.info("📊 Performance statistics reset")


# Global performance monitor instance
performance_monitor = GraphQLPerformanceMonitor()


# Decorator for timing resolvers
def timed_resolver(str) -> None:
    """Decorator to time GraphQL resolvers"""
    def decorator(func) -> Any:
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_monitor.record_resolver_call(resolver_name, duration)
        return wrapper
    return decorator 