"""Performance metrics domain models for audio system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AudioSystemStatus(Enum):
    """Audio system health status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetrics:
    """Audio system performance metrics."""

    total_recordings: int = 0
    total_playbacks: int = 0
    total_errors: int = 0
    average_processing_time: float = 0.0
    last_error: Optional[str] = None
    uptime_start: datetime = field(default_factory=datetime.now)
    cloud_syncs: int = 0
    cache_hits: int = 0

    # Format-specific metrics
    formats_used: Dict[str, int] = field(default_factory=dict)

    # Session metrics
    sessions_created: int = 0
    sessions_completed: int = 0

    # System health
    status: AudioSystemStatus = AudioSystemStatus.HEALTHY
    last_health_check: datetime = field(default_factory=datetime.now)

    @property
    def uptime_seconds(self) -> float:
        """Calculate system uptime in seconds."""
        return (datetime.now() - self.uptime_start).total_seconds()

    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage."""
        total_operations = self.total_recordings + self.total_playbacks
        if total_operations == 0:
            return 0.0
        return (self.total_errors / total_operations) * 100

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        return 100.0 - self.error_rate

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        total_requests = self.total_playbacks + self.cache_hits
        if total_requests == 0:
            return 0.0
        return (self.cache_hits / total_requests) * 100

    def increment_recordings(self, processing_time: float = 0.0) -> None:
        """Increment recording count and update processing time."""
        self.total_recordings += 1
        self._update_processing_time(processing_time)

    def increment_playbacks(self) -> None:
        """Increment playback count."""
        self.total_playbacks += 1

    def increment_errors(self, error_message: str) -> None:
        """Increment error count and update last error."""
        self.total_errors += 1
        self.last_error = error_message
        self._update_status()

    def increment_cloud_syncs(self) -> None:
        """Increment cloud sync count."""
        self.cloud_syncs += 1

    def increment_cache_hits(self) -> None:
        """Increment cache hit count."""
        self.cache_hits += 1

    def record_format_usage(self, format_name: str) -> None:
        """Record usage of audio format."""
        if format_name not in self.formats_used:
            self.formats_used[format_name] = 0
        self.formats_used[format_name] += 1

    def start_session(self) -> None:
        """Record session start."""
        self.sessions_created += 1

    def complete_session(self) -> None:
        """Record session completion."""
        self.sessions_completed += 1

    def _update_processing_time(self, new_time: float) -> None:
        """Update average processing time."""
        if self.total_recordings == 1:
            self.average_processing_time = new_time
        else:
            # Running average
            old_total = self.average_processing_time * (self.total_recordings - 1)
            self.average_processing_time = (
                old_total + new_time
            ) / self.total_recordings

    def _update_status(self) -> None:
        """Update system status based on metrics."""
        if self.error_rate > 50:
            self.status = AudioSystemStatus.CRITICAL
        elif self.error_rate > 25:
            self.status = AudioSystemStatus.ERROR
        elif self.error_rate > 10:
            self.status = AudioSystemStatus.WARNING
        else:
            self.status = AudioSystemStatus.HEALTHY

        self.last_health_check = datetime.now()

    def update_health_check(self) -> None:
        """Update health check timestamp."""
        self.last_health_check = datetime.now()
        self._update_status()

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_recordings": self.total_recordings,
            "total_playbacks": self.total_playbacks,
            "total_errors": self.total_errors,
            "average_processing_time": self.average_processing_time,
            "last_error": self.last_error,
            "uptime_seconds": self.uptime_seconds,
            "cloud_syncs": self.cloud_syncs,
            "cache_hits": self.cache_hits,
            "formats_used": self.formats_used,
            "sessions_created": self.sessions_created,
            "sessions_completed": self.sessions_completed,
            "status": self.status.value,
            "error_rate": self.error_rate,
            "success_rate": self.success_rate,
            "cache_hit_rate": self.cache_hit_rate,
            "last_health_check": self.last_health_check.isoformat(),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.total_recordings = 0
        self.total_playbacks = 0
        self.total_errors = 0
        self.average_processing_time = 0.0
        self.last_error = None
        self.uptime_start = datetime.now()
        self.cloud_syncs = 0
        self.cache_hits = 0
        self.formats_used = {}
        self.sessions_created = 0
        self.sessions_completed = 0
        self.status = AudioSystemStatus.HEALTHY
        self.last_health_check = datetime.now()
