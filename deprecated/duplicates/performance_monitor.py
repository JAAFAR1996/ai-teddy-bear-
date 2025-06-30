"""
Performance Monitoring for GraphQL Federation.

This module provides comprehensive performance monitoring, metrics collection,
and query optimization for the federated GraphQL system.

API Team Implementation - Task 13
Author: API Team Lead
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import hashlib

# Monitoring and metrics
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# GraphQL query analysis
try:
    from graphql import parse, validate, execute
    from graphql.execution import ExecutionResult
    GRAPHQL_AVAILABLE = True
except ImportError:
    GRAPHQL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Metrics for a GraphQL query."""
    query_hash: str
    query_string: str
    operation_name: Optional[str]
    variables: Dict[str, Any]
    execution_time_ms: float
    fields_requested: List[str]
    services_involved: List[str]
    cache_hit: bool
    error_count: int
    timestamp: datetime
    user_id: Optional[str] = None
    client_info: Optional[str] = None


@dataclass
class ServiceMetrics:
    """Metrics for individual service calls."""
    service_name: str
    query_hash: str
    execution_time_ms: float
    response_size_bytes: int
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PerformanceAlert:
    """Performance alert definition."""
    alert_type: str
    message: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    metric_value: float
    threshold: float
    timestamp: datetime
    query_hash: Optional[str] = None
    service_name: Optional[str] = None


class GraphQLPerformanceMonitor:
    """Performance monitoring for GraphQL Federation Gateway."""
    
    def __init__(self, enable_prometheus: bool = True):
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        
        # Query metrics storage
        self.query_metrics: deque = deque(maxlen=10000)
        self.service_metrics: deque = deque(maxlen=50000)
        
        # Performance counters
        self.query_counter = defaultdict(int)
        self.error_counter = defaultdict(int)
        self.latency_buckets = defaultdict(list)
        
        # Performance thresholds
        self.thresholds = {
            "slow_query_ms": 1000,
            "very_slow_query_ms": 5000,
            "high_error_rate": 0.05,
            "low_cache_hit_rate": 0.5,
            "max_concurrent_queries": 100
        }
        
        # Current performance state
        self.current_queries = 0
        self.peak_concurrent_queries = 0
        self.total_queries = 0
        self.total_errors = 0
        
        # Alerts
        self.alerts: List[PerformanceAlert] = []
        self.alert_callbacks: List[Callable] = []
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize Prometheus metrics if available
        if self.enable_prometheus:
            self._initialize_prometheus_metrics()
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        self.prom_query_counter = Counter(
            'graphql_queries_total',
            'Total GraphQL queries',
            ['operation_name', 'status']
        )
        
        self.prom_query_duration = Histogram(
            'graphql_query_duration_seconds',
            'GraphQL query duration',
            ['operation_name', 'service']
        )
        
        self.prom_service_duration = Histogram(
            'graphql_service_duration_seconds',
            'Service call duration',
            ['service_name', 'status']
        )
        
        self.prom_concurrent_queries = Gauge(
            'graphql_concurrent_queries',
            'Current concurrent queries'
        )
        
        self.prom_cache_hits = Counter(
            'graphql_cache_hits_total',
            'Cache hits',
            ['cache_type']
        )
        
        self.prom_errors = Counter(
            'graphql_errors_total',
            'GraphQL errors',
            ['error_type', 'service']
        )
    
    async def start_query_monitoring(
        self,
        query: str,
        variables: Dict[str, Any],
        operation_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Start monitoring a GraphQL query."""
        query_hash = self._generate_query_hash(query, variables)
        
        self.current_queries += 1
        self.total_queries += 1
        
        if self.current_queries > self.peak_concurrent_queries:
            self.peak_concurrent_queries = self.current_queries
        
        # Check for too many concurrent queries
        if self.current_queries > self.thresholds["max_concurrent_queries"]:
            await self._trigger_alert(
                "high_concurrency",
                f"High concurrent queries: {self.current_queries}",
                "HIGH",
                self.current_queries,
                self.thresholds["max_concurrent_queries"]
            )
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            self.prom_concurrent_queries.set(self.current_queries)
        
        self.logger.debug(f"Started monitoring query: {query_hash}")
        return query_hash
    
    async def finish_query_monitoring(
        self,
        query_hash: str,
        query: str,
        variables: Dict[str, Any],
        operation_name: Optional[str],
        execution_time_ms: float,
        fields_requested: List[str],
        services_involved: List[str],
        cache_hit: bool,
        error_count: int,
        user_id: Optional[str] = None
    ):
        """Finish monitoring a GraphQL query."""
        self.current_queries = max(0, self.current_queries - 1)
        
        # Create query metrics
        metrics = QueryMetrics(
            query_hash=query_hash,
            query_string=query,
            operation_name=operation_name,
            variables=variables,
            execution_time_ms=execution_time_ms,
            fields_requested=fields_requested,
            services_involved=services_involved,
            cache_hit=cache_hit,
            error_count=error_count,
            timestamp=datetime.now(),
            user_id=user_id
        )
        
        self.query_metrics.append(metrics)
        
        # Update counters
        self.query_counter[operation_name or "anonymous"] += 1
        if error_count > 0:
            self.error_counter[operation_name or "anonymous"] += error_count
            self.total_errors += error_count
        
        # Store latency
        self.latency_buckets[operation_name or "anonymous"].append(execution_time_ms)
        
        # Check performance thresholds
        await self._check_performance_thresholds(metrics)
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            status = "error" if error_count > 0 else "success"
            self.prom_query_counter.labels(
                operation_name=operation_name or "anonymous",
                status=status
            ).inc()
            
            self.prom_query_duration.labels(
                operation_name=operation_name or "anonymous",
                service="gateway"
            ).observe(execution_time_ms / 1000)
            
            self.prom_concurrent_queries.set(self.current_queries)
            
            if cache_hit:
                self.prom_cache_hits.labels(cache_type="graphql").inc()
            
            if error_count > 0:
                self.prom_errors.labels(
                    error_type="query_error",
                    service="gateway"
                ).inc(error_count)
        
        self.logger.debug(
            f"Finished monitoring query: {query_hash}, "
            f"time: {execution_time_ms:.2f}ms, "
            f"errors: {error_count}"
        )
    
    async def record_service_call(
        self,
        service_name: str,
        query_hash: str,
        execution_time_ms: float,
        response_size_bytes: int,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Record metrics for a service call."""
        metrics = ServiceMetrics(
            service_name=service_name,
            query_hash=query_hash,
            execution_time_ms=execution_time_ms,
            response_size_bytes=response_size_bytes,
            success=success,
            error_message=error_message
        )
        
        self.service_metrics.append(metrics)
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            status = "success" if success else "error"
            self.prom_service_duration.labels(
                service_name=service_name,
                status=status
            ).observe(execution_time_ms / 1000)
            
            if not success:
                self.prom_errors.labels(
                    error_type="service_error",
                    service=service_name
                ).inc()
        
        self.logger.debug(
            f"Service call recorded: {service_name}, "
            f"time: {execution_time_ms:.2f}ms, "
            f"success: {success}"
        )
    
    async def _check_performance_thresholds(self, metrics: QueryMetrics):
        """Check if query metrics exceed performance thresholds."""
        # Check slow queries
        if metrics.execution_time_ms > self.thresholds["very_slow_query_ms"]:
            await self._trigger_alert(
                "very_slow_query",
                f"Very slow query detected: {metrics.execution_time_ms:.2f}ms",
                "HIGH",
                metrics.execution_time_ms,
                self.thresholds["very_slow_query_ms"],
                query_hash=metrics.query_hash
            )
        elif metrics.execution_time_ms > self.thresholds["slow_query_ms"]:
            await self._trigger_alert(
                "slow_query",
                f"Slow query detected: {metrics.execution_time_ms:.2f}ms",
                "MEDIUM",
                metrics.execution_time_ms,
                self.thresholds["slow_query_ms"],
                query_hash=metrics.query_hash
            )
        
        # Check error rate
        if self.total_queries > 100:  # Only check after sufficient queries
            error_rate = self.total_errors / self.total_queries
            if error_rate > self.thresholds["high_error_rate"]:
                await self._trigger_alert(
                    "high_error_rate",
                    f"High error rate: {error_rate:.2%}",
                    "HIGH",
                    error_rate,
                    self.thresholds["high_error_rate"]
                )
    
    async def _trigger_alert(
        self,
        alert_type: str,
        message: str,
        severity: str,
        metric_value: float,
        threshold: float,
        query_hash: Optional[str] = None,
        service_name: Optional[str] = None
    ):
        """Trigger a performance alert."""
        alert = PerformanceAlert(
            alert_type=alert_type,
            message=message,
            severity=severity,
            metric_value=metric_value,
            threshold=threshold,
            timestamp=datetime.now(),
            query_hash=query_hash,
            service_name=service_name
        )
        
        self.alerts.append(alert)
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
        
        self.logger.warning(f"Performance alert: {alert_type} - {message}")
    
    def add_alert_callback(self, callback: Callable):
        """Add callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        current_time = datetime.now()
        recent_queries = [
            m for m in self.query_metrics
            if (current_time - m.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        if not recent_queries:
            return {"status": "no_recent_data"}
        
        # Calculate metrics
        total_queries = len(recent_queries)
        total_errors = sum(m.error_count for m in recent_queries)
        error_rate = total_errors / total_queries if total_queries > 0 else 0
        
        execution_times = [m.execution_time_ms for m in recent_queries]
        avg_latency = sum(execution_times) / len(execution_times) if execution_times else 0
        
        cache_hits = sum(1 for m in recent_queries if m.cache_hit)
        cache_hit_rate = cache_hits / total_queries if total_queries > 0 else 0
        
        # Service breakdown
        service_calls = defaultdict(list)
        for service_metric in self.service_metrics:
            if (current_time - service_metric.timestamp).total_seconds() < 3600:
                service_calls[service_metric.service_name].append(service_metric)
        
        service_stats = {}
        for service_name, calls in service_calls.items():
            success_count = sum(1 for c in calls if c.success)
            avg_time = sum(c.execution_time_ms for c in calls) / len(calls)
            
            service_stats[service_name] = {
                "total_calls": len(calls),
                "success_count": success_count,
                "success_rate": success_count / len(calls),
                "avg_latency_ms": avg_time,
                "total_response_size_mb": sum(c.response_size_bytes for c in calls) / (1024 * 1024)
            }
        
        # Top slow queries
        slow_queries = sorted(
            recent_queries,
            key=lambda m: m.execution_time_ms,
            reverse=True
        )[:10]
        
        return {
            "summary": {
                "total_queries": total_queries,
                "error_rate": error_rate,
                "avg_latency_ms": avg_latency,
                "cache_hit_rate": cache_hit_rate,
                "current_concurrent_queries": self.current_queries,
                "peak_concurrent_queries": self.peak_concurrent_queries
            },
            "service_stats": service_stats,
            "slow_queries": [
                {
                    "query_hash": q.query_hash,
                    "operation_name": q.operation_name,
                    "execution_time_ms": q.execution_time_ms,
                    "services_involved": q.services_involved,
                    "timestamp": q.timestamp.isoformat()
                }
                for q in slow_queries
            ],
            "recent_alerts": [
                asdict(alert) for alert in self.alerts[-10:]
            ],
            "timestamp": current_time.isoformat()
        }
    
    def get_query_analytics(self, query_hash: str) -> Dict[str, Any]:
        """Get detailed analytics for a specific query."""
        matching_queries = [
            m for m in self.query_metrics
            if m.query_hash == query_hash
        ]
        
        if not matching_queries:
            return {"status": "query_not_found"}
        
        execution_times = [m.execution_time_ms for m in matching_queries]
        error_counts = [m.error_count for m in matching_queries]
        
        return {
            "query_hash": query_hash,
            "total_executions": len(matching_queries),
            "avg_execution_time_ms": sum(execution_times) / len(execution_times),
            "min_execution_time_ms": min(execution_times),
            "max_execution_time_ms": max(execution_times),
            "total_errors": sum(error_counts),
            "error_rate": sum(error_counts) / len(matching_queries),
            "cache_hit_rate": sum(1 for m in matching_queries if m.cache_hit) / len(matching_queries),
            "services_involved": list(set().union(*(m.services_involved for m in matching_queries))),
            "first_seen": min(m.timestamp for m in matching_queries).isoformat(),
            "last_seen": max(m.timestamp for m in matching_queries).isoformat(),
            "sample_query": matching_queries[0].query_string
        }
    
    def optimize_query_suggestions(self, query_hash: str) -> List[str]:
        """Generate optimization suggestions for a query."""
        analytics = self.get_query_analytics(query_hash)
        
        if analytics.get("status") == "query_not_found":
            return []
        
        suggestions = []
        
        # High latency suggestions
        if analytics["avg_execution_time_ms"] > self.thresholds["slow_query_ms"]:
            suggestions.append("Consider adding field-level caching for frequently accessed data")
            suggestions.append("Review field selections to minimize over-fetching")
            
            if len(analytics["services_involved"]) > 3:
                suggestions.append("Query involves many services - consider denormalization or query splitting")
        
        # Low cache hit rate suggestions
        if analytics["cache_hit_rate"] < self.thresholds["low_cache_hit_rate"]:
            suggestions.append("Low cache hit rate - review caching strategy and TTL values")
            suggestions.append("Consider implementing query-level caching")
        
        # High error rate suggestions
        if analytics["error_rate"] > self.thresholds["high_error_rate"]:
            suggestions.append("High error rate detected - review error handling and validation")
            suggestions.append("Consider implementing circuit breaker pattern for service calls")
        
        return suggestions
    
    def _generate_query_hash(self, query: str, variables: Dict[str, Any]) -> str:
        """Generate hash for query identification."""
        # Normalize query by removing whitespace and comments
        normalized_query = " ".join(query.split())
        
        # Include variables in hash for uniqueness
        query_data = {
            "query": normalized_query,
            "variables": variables
        }
        
        return hashlib.sha256(
            json.dumps(query_data, sort_keys=True).encode()
        ).hexdigest()[:16]
    
    async def cleanup_old_metrics(self, hours: int = 24):
        """Cleanup metrics older than specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Clean query metrics
        original_query_count = len(self.query_metrics)
        self.query_metrics = deque(
            (m for m in self.query_metrics if m.timestamp > cutoff_time),
            maxlen=self.query_metrics.maxlen
        )
        
        # Clean service metrics
        original_service_count = len(self.service_metrics)
        self.service_metrics = deque(
            (m for m in self.service_metrics if m.timestamp > cutoff_time),
            maxlen=self.service_metrics.maxlen
        )
        
        # Clean alerts
        original_alerts_count = len(self.alerts)
        self.alerts = [
            alert for alert in self.alerts
            if (datetime.now() - alert.timestamp).total_seconds() < hours * 3600
        ]
        
        cleaned_queries = original_query_count - len(self.query_metrics)
        cleaned_services = original_service_count - len(self.service_metrics)
        cleaned_alerts = original_alerts_count - len(self.alerts)
        
        self.logger.info(
            f"Cleaned up metrics: {cleaned_queries} queries, "
            f"{cleaned_services} service calls, {cleaned_alerts} alerts"
        )


class QueryComplexityAnalyzer:
    """Analyze GraphQL query complexity for performance optimization."""
    
    def __init__(self, max_complexity: int = 1000):
        self.max_complexity = max_complexity
        self.field_costs = self._initialize_field_costs()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _initialize_field_costs(self) -> Dict[str, int]:
        """Initialize field cost mapping."""
        return {
            # Basic fields
            "id": 1,
            "name": 1,
            "email": 1,
            "createdAt": 1,
            
            # Complex fields
            "conversations": 10,
            "aiProfile": 15,
            "emotionHistory": 20,
            "usage": 25,
            "parentalReports": 30,
            
            # Very expensive fields
            "aiAnalysis": 50,
            "safetyCheck": 40,
            "performance": 35
        }
    
    def analyze_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query complexity."""
        if not GRAPHQL_AVAILABLE:
            return {"complexity": 0, "analysis": "GraphQL library not available"}
        
        try:
            # Parse query
            document = parse(query)
            
            # Calculate complexity
            complexity = self._calculate_complexity(document)
            
            # Generate analysis
            analysis = {
                "total_complexity": complexity,
                "max_allowed": self.max_complexity,
                "is_allowed": complexity <= self.max_complexity,
                "complexity_ratio": complexity / self.max_complexity,
                "recommendations": self._generate_complexity_recommendations(complexity)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Query complexity analysis failed: {e}")
            return {"complexity": float('inf'), "error": str(e)}
    
    def _calculate_complexity(self, document) -> int:
        """Calculate query complexity score."""
        # Simplified complexity calculation
        # In production, use a proper GraphQL complexity analyzer
        
        complexity = 0
        
        # Count field selections and apply costs
        for definition in document.definitions:
            if hasattr(definition, 'selection_set'):
                complexity += self._calculate_selection_complexity(definition.selection_set)
        
        return complexity
    
    def _calculate_selection_complexity(self, selection_set, depth: int = 0) -> int:
        """Calculate complexity for selection set."""
        if not selection_set or depth > 10:  # Prevent infinite recursion
            return 0
        
        complexity = 0
        depth_multiplier = 1 + (depth * 0.5)  # Increase cost with depth
        
        for selection in selection_set.selections:
            field_name = getattr(selection, 'name', {}).get('value', 'unknown')
            field_cost = self.field_costs.get(field_name, 5)  # Default cost
            
            complexity += field_cost * depth_multiplier
            
            # Add nested selection complexity
            if hasattr(selection, 'selection_set') and selection.selection_set:
                complexity += self._calculate_selection_complexity(
                    selection.selection_set, 
                    depth + 1
                )
        
        return int(complexity)
    
    def _generate_complexity_recommendations(self, complexity: int) -> List[str]:
        """Generate recommendations for complex queries."""
        recommendations = []
        
        if complexity > self.max_complexity:
            recommendations.append(
                f"Query complexity ({complexity}) exceeds limit ({self.max_complexity})"
            )
            recommendations.append("Consider breaking the query into smaller parts")
            recommendations.append("Use pagination for list fields")
            recommendations.append("Remove unnecessary fields from selection")
        
        elif complexity > self.max_complexity * 0.8:
            recommendations.append("Query is approaching complexity limit")
            recommendations.append("Consider optimizing field selections")
        
        return recommendations


# Factory function
def create_performance_monitor(enable_prometheus: bool = True) -> GraphQLPerformanceMonitor:
    """Create GraphQL performance monitor."""
    return GraphQLPerformanceMonitor(enable_prometheus) 