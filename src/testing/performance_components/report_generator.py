import json
import statistics
import time
from typing import Any, Dict, List, Optional

from .models import PerformanceMetric, PerformanceReport, PerformanceResult


def _summarize_metrics(
    test_results: List[PerformanceResult]
) -> Dict[str, Any]:
    """Summarize performance metrics from a list of test results."""
    metrics_summary = {}
    for metric in PerformanceMetric:
        metric_results = [r for r in test_results if r.metric == metric]
        if metric_results:
            values = [r.value for r in metric_results]
            metrics_summary[metric.value] = {
                "count": len(metric_results),
                "average": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "passed": len([r for r in metric_results if r.success]),
            }
    return metrics_summary


def _check_metric_and_recommend(
    metric_summary: Dict[str, Any],
    metric_name: str,
    target: float,
    is_max_target: bool,
) -> Optional[str]:
    """Checks a single metric and returns a recommendation if it fails."""
    if metric_name not in metric_summary:
        return None

    summary = metric_summary[metric_name]
    value = summary["max"] if is_max_target else summary["min"]
    comparison_text = "exceeds" if is_max_target else "is below"
    unit = {"response_time": "ms", "memory_usage": "MB", "cpu_usage": "%",
            "throughput": "RPS", "error_rate": "%"}.get(metric_name, "")
    value_text = f"{value:.1f}{unit}" if unit != "%" else f"{value:.1f}%"
    target_text = f"{target}{unit}" if unit != "%" else f"{target}%"

    if (is_max_target and value > target) or (not is_max_target and value < target):
        return (
            f"Metric '{metric_name}' failed: value ({value_text}) "
            f"{comparison_text} target ({target_text}). "
            "Consider optimization and scaling."
        )
    return None


def _generate_performance_recommendations(
    metrics_summary: Dict[str, Any], performance_targets: dict
) -> List[str]:
    """Generate performance recommendations based on summarized metrics."""
    recommendations = []

    recommendation_strategies = [
        ("response_time",
         performance_targets["average_response_time_ms"], True),
        ("error_rate",
         performance_targets["max_error_rate"] * 100, True),
        ("memory_usage", performance_targets["max_memory_mb"], True),
        ("cpu_usage", performance_targets["max_cpu_percent"], True),
        ("throughput",
         performance_targets["min_throughput_rps"], False),
    ]

    for metric, target, is_max in recommendation_strategies:
        recommendation = _check_metric_and_recommend(
            metrics_summary, metric, target, is_max
        )
        if recommendation:
            recommendations.append(recommendation)

    # Child-specific recommendations
    recommendations.extend(
        [
            "Ensure response times remain under 500ms for optimal child engagement",
            "Monitor performance during peak usage times (after school, weekends)",
            "Implement progressive loading for story content to reduce perceived latency",
            "Consider edge computing for reduced latency in different geographic regions",
            "Implement performance monitoring and alerting for production environment",
        ]
    )

    return recommendations


async def generate_performance_report(
        test_results: List[PerformanceResult],
        start_time: float,
        end_time: float,
        performance_targets: dict) -> PerformanceReport:
    """Generate comprehensive performance report by orchestrating helper methods."""
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.success)
    pass_rate = passed_tests / total_tests if total_tests > 0 else 0

    metrics_summary = _summarize_metrics(test_results)
    recommendations = _generate_performance_recommendations(
        metrics_summary, performance_targets
    )
    overall_pass = pass_rate >= 0.8

    return PerformanceReport(
        test_suite_name="AI Teddy Bear Performance Test Suite",
        start_time=start_time,
        end_time=end_time,
        total_duration=end_time - start_time,
        results=test_results,
        summary_metrics={
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": pass_rate,
            "metrics_breakdown": metrics_summary,
        },
        recommendations=recommendations,
        pass_fail_status=overall_pass,
    )


async def export_performance_report(
    report: PerformanceReport, output_file: str
) -> bool:
    """Export performance report to file"""
    try:
        report_data = {
            "test_suite_name": report.test_suite_name,
            "timestamp": time.time(),
            "start_time": report.start_time,
            "end_time": report.end_time,
            "total_duration": report.total_duration,
            "summary_metrics": report.summary_metrics,
            "pass_fail_status": report.pass_fail_status,
            "recommendations": report.recommendations,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "test_type": r.test_type.value,
                    "metric": r.metric.value,
                    "value": r.value,
                    "unit": r.unit,
                    "success": r.success,
                    "error_message": r.error_message,
                }
                for r in report.results
            ],
        }

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        return True

    except Exception:
        return False
