"""
📊 Moderation Statistics Manager
Extracted statistics and monitoring functionality for better cohesion
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging


@dataclass
class ModerationStatsEntry:
    """Single moderation statistics entry"""

    timestamp: float
    user_id: Optional[str]
    session_id: Optional[str]
    content_length: int
    is_safe: bool
    severity: str
    categories: List[str]
    confidence: float
    processing_time_ms: float


class ModerationStatistics:
    """
    Dedicated statistics tracking and monitoring for moderation.
    High cohesion: all methods work with statistics data and analysis.
    """

    def __init__(self, max_history: int = 10000):
        """Initialize statistics manager"""
        self.logger = logging.getLogger(__name__)
        self.max_history = max_history

        # Core statistics
        self.stats = {
            "total_checks": 0,
            "safe_content": 0,
            "blocked_content": 0,
            "total_processing_time_ms": 0,
            "average_processing_time_ms": 0,
            "service_start_time": time.time(),
        }

        # Detailed tracking
        self.category_stats = {}
        self.severity_stats = {}
        self.user_stats = {}
        self.hourly_stats = {}

        # Recent activity history
        self.recent_entries: List[ModerationStatsEntry] = []

        # Performance tracking
        self.performance_metrics = {
            "min_processing_time_ms": float("inf"),
            "max_processing_time_ms": 0,
            "total_errors": 0,
            "uptime_seconds": 0,
        }

    def record_moderation_result(
        self,
        result: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        content_length: int = 0,
        processing_time_ms: float = 0,
    ) -> None:
        """Record a moderation result for statistics"""
        try:
            # Update core stats
            self.stats["total_checks"] += 1
            self.stats["total_processing_time_ms"] += processing_time_ms
            self.stats["average_processing_time_ms"] = (
                self.stats["total_processing_time_ms"] / self.stats["total_checks"])

            is_safe = result.get("allowed", True)
            if is_safe:
                self.stats["safe_content"] += 1
            else:
                self.stats["blocked_content"] += 1

            # Update performance metrics
            self._update_performance_metrics(processing_time_ms)

            # Track by categories
            categories = result.get("categories", [])
            for category in categories:
                self.category_stats[category] = self.category_stats.get(
                    category, 0) + 1

            # Track by severity
            severity = result.get("severity", "safe")
            self.severity_stats[severity] = self.severity_stats.get(
                severity, 0) + 1

            # Track by user
            if user_id:
                self._update_user_stats(user_id, is_safe, categories)

            # Track hourly stats
            self._update_hourly_stats(is_safe)

            # Add to recent history
            self._add_to_history(
                user_id,
                session_id,
                content_length,
                is_safe,
                severity,
                categories,
                result.get("confidence", 0.0),
                processing_time_ms,
            )

        except Exception as e:
            self.logger.error(f"Failed to record moderation result: {e}")
            self.performance_metrics["total_errors"] += 1

    def _update_performance_metrics(self, processing_time_ms: float) -> None:
        """Update performance tracking metrics"""
        if processing_time_ms < self.performance_metrics["min_processing_time_ms"]:
            self.performance_metrics["min_processing_time_ms"] = processing_time_ms

        if processing_time_ms > self.performance_metrics["max_processing_time_ms"]:
            self.performance_metrics["max_processing_time_ms"] = processing_time_ms

        # Update uptime
        self.performance_metrics["uptime_seconds"] = (
            time.time() - self.stats["service_start_time"]
        )

    def _update_user_stats(
        self, user_id: str, is_safe: bool, categories: List[str]
    ) -> None:
        """Update per-user statistics"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                "total_requests": 0,
                "safe_requests": 0,
                "blocked_requests": 0,
                "categories": {},
                "first_seen": time.time(),
                "last_seen": time.time(),
            }

        user_data = self.user_stats[user_id]
        user_data["total_requests"] += 1
        user_data["last_seen"] = time.time()

        if is_safe:
            user_data["safe_requests"] += 1
        else:
            user_data["blocked_requests"] += 1

        # Track categories for this user
        for category in categories:
            user_data["categories"][category] = (
                user_data["categories"].get(category, 0) + 1
            )

    def _update_hourly_stats(self, is_safe: bool) -> None:
        """Update hourly statistics"""
        current_hour = datetime.now().strftime("%Y-%m-%d %H:00")

        if current_hour not in self.hourly_stats:
            self.hourly_stats[current_hour] = {
                "total": 0,
                "safe": 0,
                "blocked": 0,
                "timestamp": time.time(),
            }

        hour_data = self.hourly_stats[current_hour]
        hour_data["total"] += 1

        if is_safe:
            hour_data["safe"] += 1
        else:
            hour_data["blocked"] += 1

    def _add_to_history(
        self,
        user_id: Optional[str],
        session_id: Optional[str],
        content_length: int,
        is_safe: bool,
        severity: str,
        categories: List[str],
        confidence: float,
        processing_time_ms: float,
    ) -> None:
        """Add entry to recent history"""
        entry = ModerationStatsEntry(
            timestamp=time.time(),
            user_id=user_id,
            session_id=session_id,
            content_length=content_length,
            is_safe=is_safe,
            severity=severity,
            categories=categories.copy(),
            confidence=confidence,
            processing_time_ms=processing_time_ms,
        )

        self.recent_entries.append(entry)

        # Maintain max history size
        if len(self.recent_entries) > self.max_history:
            self.recent_entries = self.recent_entries[-self.max_history:]

    def get_general_stats(self) -> Dict[str, Any]:
        """Get general moderation statistics"""
        total_requests = self.stats["total_checks"]
        safe_rate = (
            (self.stats["safe_content"] / total_requests * 100)
            if total_requests > 0
            else 0
        )

        return {
            "total_requests": total_requests,
            "safe_requests": self.stats["safe_content"],
            "blocked_requests": self.stats["blocked_content"],
            "safe_rate_percent": round(
                safe_rate,
                2),
            "average_processing_time_ms": round(
                self.stats["average_processing_time_ms"],
                2),
            "uptime_seconds": round(
                self.performance_metrics["uptime_seconds"],
                2),
            "uptime_hours": round(
                self.performance_metrics["uptime_seconds"] /
                3600,
                2),
            "service_health": self._calculate_service_health(),
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get detailed performance statistics"""
        return {
            "processing_time": {
                "average_ms": round(self.stats["average_processing_time_ms"], 2),
                "min_ms": round(self.performance_metrics["min_processing_time_ms"], 2),
                "max_ms": round(self.performance_metrics["max_processing_time_ms"], 2),
                "total_ms": round(self.stats["total_processing_time_ms"], 2),
            },
            "error_rate": {
                "total_errors": self.performance_metrics["total_errors"],
                "error_rate_percent": self._calculate_error_rate(),
            },
            "throughput": {
                "requests_per_hour": self._calculate_requests_per_hour(),
                "requests_per_minute": self._calculate_requests_per_minute(),
            },
        }

    def get_category_breakdown(self) -> Dict[str, Any]:
        """Get breakdown by content categories"""
        total_flagged = sum(self.category_stats.values())

        category_breakdown = {}
        for category, count in self.category_stats.items():
            percentage = (
                count /
                total_flagged *
                100) if total_flagged > 0 else 0
            category_breakdown[category] = {
                "count": count,
                "percentage": round(percentage, 2),
            }

        return {
            "total_flagged_content": total_flagged,
            "categories": category_breakdown,
            "most_common_category": (
                max(self.category_stats.items(), key=lambda x: x[1])[0]
                if self.category_stats
                else "none"
            ),
        }

    def get_user_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user-specific statistics"""
        if user_id:
            return self.user_stats.get(user_id, {})

        # Return summary of all users
        total_users = len(self.user_stats)
        most_active_user = None

        if self.user_stats:
            most_active_user = max(
                self.user_stats.items(), key=lambda x: x[1]["total_requests"]
            )[0]

        return {
            "total_users": total_users,
            "most_active_user": most_active_user,
            "users_with_blocked_content": sum(
                1
                for user_data in self.user_stats.values()
                if user_data["blocked_requests"] > 0
            ),
        }

    def get_hourly_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get hourly activity trends"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_hours = {}
        for hour, data in self.hourly_stats.items():
            hour_time = datetime.strptime(hour, "%Y-%m-%d %H:00")
            if hour_time >= cutoff_time:
                recent_hours[hour] = data

        return {
            "time_range_hours": hours,
            "hourly_data": recent_hours,
            "peak_hour": self._find_peak_hour(recent_hours),
            "total_requests_in_period": sum(
                data["total"] for data in recent_hours.values()
            ),
        }

    def get_recent_activity(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent moderation activity"""
        recent_entries = (
            self.recent_entries[-limit:] if limit > 0 else self.recent_entries
        )

        return [{"timestamp": entry.timestamp,
                 "datetime": datetime.fromtimestamp(entry.timestamp).isoformat(),
                 "user_id": entry.user_id,
                 "session_id": entry.session_id,
                 "content_length": entry.content_length,
                 "is_safe": entry.is_safe,
                 "severity": entry.severity,
                 "categories": entry.categories,
                 "confidence": entry.confidence,
                 "processing_time_ms": entry.processing_time_ms,
                 } for entry in reversed(recent_entries)]

    def _calculate_service_health(self) -> str:
        """Calculate overall service health"""
        total_requests = self.stats["total_checks"]
        if total_requests == 0:
            return "unknown"

        error_rate = self._calculate_error_rate()
        avg_processing_time = self.stats["average_processing_time_ms"]

        if error_rate > 5 or avg_processing_time > 1000:
            return "unhealthy"
        elif error_rate > 1 or avg_processing_time > 500:
            return "warning"
        else:
            return "healthy"

    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        total_requests = self.stats["total_checks"]
        if total_requests == 0:
            return 0.0

        return round(
            (self.performance_metrics["total_errors"] /
             total_requests) *
            100,
            2)

    def _calculate_requests_per_hour(self) -> float:
        """Calculate requests per hour"""
        uptime_hours = self.performance_metrics["uptime_seconds"] / 3600
        if uptime_hours == 0:
            return 0.0

        return round(self.stats["total_checks"] / uptime_hours, 2)

    def _calculate_requests_per_minute(self) -> float:
        """Calculate requests per minute"""
        uptime_minutes = self.performance_metrics["uptime_seconds"] / 60
        if uptime_minutes == 0:
            return 0.0

        return round(self.stats["total_checks"] / uptime_minutes, 2)

    def _find_peak_hour(self, hourly_data: Dict[str, Any]) -> Optional[str]:
        """Find the hour with most activity"""
        if not hourly_data:
            return None

        return max(hourly_data.items(), key=lambda x: x[1]["total"])[0]

    def reset_stats(self) -> None:
        """Reset all statistics"""
        self.stats = {
            "total_checks": 0,
            "safe_content": 0,
            "blocked_content": 0,
            "total_processing_time_ms": 0,
            "average_processing_time_ms": 0,
            "service_start_time": time.time(),
        }

        self.category_stats.clear()
        self.severity_stats.clear()
        self.user_stats.clear()
        self.hourly_stats.clear()
        self.recent_entries.clear()

        self.performance_metrics = {
            "min_processing_time_ms": float("inf"),
            "max_processing_time_ms": 0,
            "total_errors": 0,
            "uptime_seconds": 0,
        }

        self.logger.info("Statistics reset successfully")

    def export_stats(self) -> Dict[str, Any]:
        """Export comprehensive statistics"""
        return {
            "general": self.get_general_stats(),
            "performance": self.get_performance_stats(),
            "categories": self.get_category_breakdown(),
            "users": self.get_user_stats(),
            "trends": self.get_hourly_trends(24),
            "recent_activity": self.get_recent_activity(50),
            "export_timestamp": time.time(),
            "export_datetime": datetime.now().isoformat(),
        }
