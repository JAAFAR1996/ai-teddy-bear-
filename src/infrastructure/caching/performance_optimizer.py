from typing import Any, Dict, List, Optional

"""
Performance Optimizer for Multi-Layer Caching System.

This module analyzes cache performance and provides optimization recommendations
for improving system performance.

Performance Team Implementation - Task 12
Author: Performance Team Lead
"""

import logging
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for cache analysis."""

    timestamp: datetime
    hit_rate: float
    miss_rate: float
    average_latency_ms: float
    throughput_ops_per_sec: float
    memory_usage_mb: float
    cache_size: int
    evictions_per_hour: int
    error_rate: float


@dataclass
class OptimizationRecommendation:
    """Cache optimization recommendation."""

    category: str
    priority: str  # HIGH, MEDIUM, LOW
    title: str
    description: str
    current_value: Any
    recommended_value: Any
    expected_improvement: str
    implementation_effort: str  # LOW, MEDIUM, HIGH


class PerformanceOptimizer:
    """Analyzes cache performance and provides optimization recommendations."""

    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.analysis_window_hours = 24
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    def record_metrics(self, cache_system) -> PerformanceMetrics:
        """Record current performance metrics."""
        try:
            metrics_data = cache_system.get_performance_metrics()

            # Calculate throughput
            total_ops = metrics_data.get("total_requests", 0)
            # Avoid division by zero
            time_span = max(1, len(self.metrics_history))
            throughput = total_ops / time_span

            # Create performance metrics
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                hit_rate=metrics_data.get("hit_rate", 0.0),
                miss_rate=1.0 - metrics_data.get("hit_rate", 0.0),
                average_latency_ms=metrics_data.get("average_latency_ms", 0.0),
                throughput_ops_per_sec=throughput,
                memory_usage_mb=metrics_data.get("memory_usage_mb", 0.0),
                cache_size=metrics_data.get("l1_stats", {}).get("size", 0),
                evictions_per_hour=metrics_data.get("evictions", 0),
                error_rate=metrics_data.get("cache_efficiency", {}).get(
                    "error_rate", 0.0
                ),
            )

            # Add to history
            self.metrics_history.append(metrics)

            # Keep only recent metrics
            cutoff_time = datetime.now() - timedelta(hours=self.analysis_window_hours)
            self.metrics_history = [
                m for m in self.metrics_history if m.timestamp > cutoff_time
            ]

            return metrics

        except Exception as e:
            self.logger.error(f"Error recording metrics: {e}")
            return None

    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        if len(self.metrics_history) < 2:
            return {"status": "insufficient_data"}

        # Extract time series data
        hit_rates = [m.hit_rate for m in self.metrics_history]
        latencies = [m.average_latency_ms for m in self.metrics_history]
        throughputs = [m.throughput_ops_per_sec for m in self.metrics_history]
        memory_usage = [m.memory_usage_mb for m in self.metrics_history]

        # Calculate trends
        trends = {
            "hit_rate": self._calculate_trend(hit_rates),
            "latency": self._calculate_trend(latencies),
            "throughput": self._calculate_trend(throughputs),
            "memory_usage": self._calculate_trend(memory_usage),
        }

        # Calculate statistics
        stats = {
            "hit_rate": {
                "current": hit_rates[-1],
                "average": statistics.mean(hit_rates),
                "min": min(hit_rates),
                "max": max(hit_rates),
                "std_dev": statistics.stdev(hit_rates) if len(hit_rates) > 1 else 0,
            },
            "latency": {
                "current": latencies[-1],
                "average": statistics.mean(latencies),
                "min": min(latencies),
                "max": max(latencies),
                "p95": self._percentile(latencies, 95),
            },
            "throughput": {
                "current": throughputs[-1],
                "average": statistics.mean(throughputs),
                "peak": max(throughputs),
            },
        }

        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "metrics_count": len(self.metrics_history),
            "time_window_hours": self.analysis_window_hours,
            "trends": trends,
            "statistics": stats,
            "performance_score": self._calculate_performance_score(stats),
        }

    def _analyze_hit_rate(self, latest_metrics, current_config) -> Optional[OptimizationRecommendation]:
        """Analyzes hit rate and suggests increasing cache size if it's too low."""
        if latest_metrics.hit_rate < 0.4:
            return OptimizationRecommendation(
                category="Cache Size",
                priority="HIGH",
                title="Increase L1 Cache Size",
                description="Hit rate is below 40%. Increasing L1 cache size will improve performance.",
                current_value=f"{current_config.l1_max_size_mb}MB",
                recommended_value=f"{current_config.l1_max_size_mb * 2}MB",
                expected_improvement="20-30% hit rate increase",
                implementation_effort="LOW",
            )
        return None

    def _analyze_latency(self, latest_metrics, current_config) -> Optional[OptimizationRecommendation]:
        """Analyzes latency and suggests enabling compression if it's too high."""
        if latest_metrics.average_latency_ms > 100:
            return OptimizationRecommendation(
                category="Latency",
                priority="HIGH",
                title="Enable Compression",
                description="High latency detected. Enable compression to reduce network overhead.",
                current_value=current_config.compression_enabled,
                recommended_value=True,
                expected_improvement="30-50% latency reduction",
                implementation_effort="LOW",
            )
        return None

    def _analyze_memory_usage(self, latest_metrics, current_config) -> Optional[OptimizationRecommendation]:
        """Analyzes memory usage and suggests optimizing TTL settings if it's too high."""
        memory_threshold = current_config.l1_max_size_mb * 0.8
        if latest_metrics.memory_usage_mb > memory_threshold:
            return OptimizationRecommendation(
                category="Memory Management",
                priority="MEDIUM",
                title="Optimize TTL Settings",
                description="Memory usage is high. Reducing TTL for less important content can help.",
                current_value="Current TTL values",
                recommended_value="Reduced TTL for transcriptions and emotions",
                expected_improvement="20-25% memory reduction",
                implementation_effort="MEDIUM",
            )
        return None

    def _analyze_eviction_rate(self, latest_metrics, current_config) -> Optional[OptimizationRecommendation]:
        """Analyzes eviction rate and suggests implementing a smart eviction policy if it's too high."""
        if latest_metrics.evictions_per_hour > 100:
            return OptimizationRecommendation(
                category="Cache Efficiency",
                priority="MEDIUM",
                title="Implement Smart Eviction",
                description="High eviction rate detected. Implement LFU or custom eviction policy.",
                current_value="LRU eviction",
                recommended_value="LFU or weighted eviction",
                expected_improvement="15-20% efficiency increase",
                implementation_effort="HIGH",
            )
        return None

    def _analyze_error_rate(self, latest_metrics, current_config) -> Optional[OptimizationRecommendation]:
        """Analyzes error rate and suggests improving error handling if it's too high."""
        if latest_metrics.error_rate > 0.05:
            return OptimizationRecommendation(
                category="Reliability",
                priority="HIGH",
                title="Improve Error Handling",
                description="Error rate is above 5%. Implement better fallback mechanisms.",
                current_value=f"{latest_metrics.error_rate:.2%}",
                recommended_value="<2%",
                expected_improvement="Better reliability and user experience",
                implementation_effort="MEDIUM",
            )
        return None

    def _analyze_hit_rate_trend(self, trends) -> Optional[OptimizationRecommendation]:
        """Analyzes hit rate trend and suggests an investigation if it's declining."""
        hit_rate_trend = trends.get("trends", {}).get("hit_rate", 0)
        if hit_rate_trend < -0.1:  # Declining hit rate
            return OptimizationRecommendation(
                category="Performance Degradation",
                priority="HIGH",
                title="Investigate Hit Rate Decline",
                description="Hit rate is declining over time. Review cache key generation and TTL settings.",
                current_value=f"Trending down {abs(hit_rate_trend):.1%}/hour",
                recommended_value="Stable or increasing",
                expected_improvement="Prevent further performance degradation",
                implementation_effort="MEDIUM",
            )
        return None

    def generate_optimization_recommendations(
        self, cache_system, current_config
    ) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on performance analysis."""
        if len(self.metrics_history) < 5:
            return []

        latest_metrics = self.metrics_history[-1]
        trends = self.analyze_performance_trends()

        potential_recommendations = [
            self._analyze_hit_rate(latest_metrics, current_config),
            self._analyze_latency(latest_metrics, current_config),
            self._analyze_memory_usage(latest_metrics, current_config),
            self._analyze_eviction_rate(latest_metrics, current_config),
            self._analyze_error_rate(latest_metrics, current_config),
            self._analyze_hit_rate_trend(trends),
        ]

        recommendations = [
            rec for rec in potential_recommendations if rec is not None]

        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        recommendations.sort(key=lambda x: priority_order[x.priority])

        return recommendations

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend using simple linear regression."""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x_values = list(range(n))

        # Calculate means
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n

        # Calculate slope
        numerator = sum((x - x_mean) * (y - y_mean)
                        for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        return numerator / denominator if denominator != 0 else 0.0

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)

        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def _calculate_performance_score(self, stats: Dict[str, Any]) -> float:
        """Calculate overall performance score (0-100)."""
        # Weight different metrics
        hit_rate_weight = 0.4
        latency_weight = 0.3
        throughput_weight = 0.3

        # Normalize hit rate (0-1 to 0-100)
        hit_rate_score = stats["hit_rate"]["current"] * 100

        # Normalize latency (lower is better, cap at 200ms)
        latency_ms = stats["latency"]["current"]
        latency_score = max(0, 100 - (latency_ms / 200) * 100)

        # Normalize throughput (relative to average)
        avg_throughput = stats["throughput"]["average"]
        current_throughput = stats["throughput"]["current"]
        throughput_score = min(
            100, (current_throughput / max(1, avg_throughput)) * 100)

        # Calculate weighted score
        total_score = (
            hit_rate_score * hit_rate_weight
            + latency_score * latency_weight
            + throughput_score * throughput_weight
        )

        return round(total_score, 1)

    def generate_performance_report(
        self, cache_system, current_config
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        # Record current metrics
        current_metrics = self.record_metrics(cache_system)

        # Analyze trends
        trends_analysis = self.analyze_performance_trends()

        # Generate recommendations
        recommendations = self.generate_optimization_recommendations(
            cache_system, current_config
        )

        # Create summary
        summary = {
            "overall_health": "GOOD",
            "critical_issues": 0,
            "optimization_opportunities": len(recommendations),
            "performance_score": trends_analysis.get("performance_score", 0),
        }

        # Determine health status
        if summary["performance_score"] < 50:
            summary["overall_health"] = "POOR"
        elif summary["performance_score"] < 75:
            summary["overall_health"] = "FAIR"

        # Count critical issues
        summary["critical_issues"] = len(
            [r for r in recommendations if r.priority == "HIGH"]
        )

        return {
            "report_timestamp": datetime.now().isoformat(),
            "summary": summary,
            "current_metrics": asdict(current_metrics) if current_metrics else None,
            "trends_analysis": trends_analysis,
            "recommendations": [asdict(r) for r in recommendations],
            "next_analysis_suggested": (
                datetime.now() + timedelta(hours=1)
            ).isoformat(),
        }

    def export_metrics_csv(self, filepath: str) -> bool:
        """Export metrics history to CSV file."""
        try:
            import csv

            with open(filepath, "w", newline="") as csvfile:
                if not self.metrics_history:
                    return False

                fieldnames = list(asdict(self.metrics_history[0]).keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for metrics in self.metrics_history:
                    row = asdict(metrics)
                    row["timestamp"] = row["timestamp"].isoformat()
                    writer.writerow(row)

            self.logger.info(f"Metrics exported to {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
            return False


class CacheHealthMonitor:
    """Monitors cache health and triggers alerts."""

    def __init__(self, optimizer: PerformanceOptimizer):
        self.optimizer = optimizer
        self.alert_thresholds = {
            "hit_rate_min": 0.3,
            "latency_max_ms": 200,
            "error_rate_max": 0.1,
            "memory_usage_max_pct": 90,
        }
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    def _check_metric(self, metric_name: str, current_value: float, threshold: float, is_max: bool) -> Optional[Dict]:
        """Checks a single metric against its threshold and returns an alert if triggered."""
        triggered = (current_value > threshold) if is_max else (
            current_value < threshold)
        if triggered:
            level = "CRITICAL" if metric_name == "error_rate" else "WARNING"
            comparison_text = "above" if is_max else "below"
            return {
                "level": level,
                "metric": metric_name,
                "message": f"{metric_name.replace('_', ' ').title()} ({current_value:.2% if '%' in str(threshold) else current_value}) {comparison_text} threshold ({threshold})",
                "timestamp": datetime.now().isoformat(),
            }
        return None

    async def check_health(self, cache_system, current_config) -> Dict[str, Any]:
        """Check cache health and generate alerts if needed."""
        if not self.optimizer.metrics_history:
            return {"status": "no_data"}

        latest_metrics = self.optimizer.metrics_history[-1]

        alerts = []

        # Check all metrics
        alerts.append(self._check_metric(
            "hit_rate", latest_metrics.hit_rate, self.alert_thresholds["hit_rate_min"], False))
        alerts.append(self._check_metric(
            "latency", latest_metrics.average_latency_ms, self.alert_thresholds["latency_max_ms"], True))
        alerts.append(self._check_metric(
            "error_rate", latest_metrics.error_rate, self.alert_thresholds["error_rate_max"], True))

        memory_pct = (latest_metrics.memory_usage_mb /
                      current_config.l1_max_size_mb) * 100
        alerts.append(self._check_metric("memory_usage", memory_pct,
                      self.alert_thresholds["memory_usage_max_pct"], True))

        valid_alerts = [alert for alert in alerts if alert]

        return {
            "health_check_timestamp": datetime.now().isoformat(),
            "overall_status": ("CRITICAL" if any(a["level"] == "CRITICAL" for a in valid_alerts) else "WARNING" if valid_alerts else "HEALTHY"),
            "alerts": valid_alerts,
            "metrics_summary": {
                "hit_rate": latest_metrics.hit_rate,
                "latency_ms": latest_metrics.average_latency_ms,
                "error_rate": latest_metrics.error_rate,
                "memory_usage_mb": latest_metrics.memory_usage_mb,
            },
        }

    def set_alert_threshold(self, metric: str, value: float) -> None:
        """Update alert threshold for specific metric."""
        if metric in self.alert_thresholds:
            self.alert_thresholds[metric] = value
            self.logger.info(
                f"Updated alert threshold for {metric} to {value}")
        else:
            self.logger.warning(
                f"Unknown metric for alert threshold: {metric}")


# Factory functions
def create_performance_optimizer() -> PerformanceOptimizer:
    """Create performance optimizer instance."""
    return PerformanceOptimizer()


def create_health_monitor(optimizer: PerformanceOptimizer) -> CacheHealthMonitor:
    """Create cache health monitor instance."""
    return CacheHealthMonitor(optimizer)
