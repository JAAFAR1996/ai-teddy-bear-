#!/usr/bin/env python3
"""
Cleanup Report Entity
Comprehensive report for cleanup operations with tracking and metrics
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Set

from .retention_policy import DataRetentionPolicy


@dataclass
class CleanupReport:
    """تقرير شامل لعملية التنظيف"""

    # Basic info
    cleanup_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime = None
    status: str = "running"  # running, completed, failed, cancelled

    # Policy used
    policy: DataRetentionPolicy = field(default_factory=DataRetentionPolicy)

    # Statistics
    total_records_scanned: int = 0
    total_records_deleted: int = 0
    total_size_freed_bytes: int = 0

    # Detailed counts by type
    conversations_deleted: int = 0
    messages_deleted: int = 0
    emotional_states_deleted: int = 0
    audio_files_deleted: int = 0
    backup_files_created: int = 0

    # Children affected
    children_affected: Set[str] = field(default_factory=set)
    parents_notified: Set[str] = field(default_factory=set)

    # Errors and warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Performance metrics
    execution_time_seconds: float = 0.0
    database_operations_count: int = 0
    file_operations_count: int = 0

    def add_error(self, error: str):
        """إضافة خطأ للتقرير"""
        self.errors.append(f"{datetime.utcnow().isoformat()}: {error}")

    def add_warning(self, warning: str):
        """إضافة تحذير للتقرير"""
        self.warnings.append(f"{datetime.utcnow().isoformat()}: {warning}")

    def mark_completed(self):
        """تسجيل اكتمال العملية"""
        self.completed_at = datetime.utcnow()
        self.status = "completed"
        if self.started_at:
            self.execution_time_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()

    def mark_failed(self, error: str):
        """تسجيل فشل العملية"""
        self.completed_at = datetime.utcnow()
        self.status = "failed"
        self.add_error(f"Operation failed: {error}")

    def get_size_freed_mb(self) -> float:
        """Get freed size in megabytes"""
        return round(self.total_size_freed_bytes / 1024 / 1024, 2)

    def get_success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_records_scanned == 0:
            return 100.0
        return round(
            (self.total_records_deleted /
             self.total_records_scanned) *
            100,
            2)

    def has_errors(self) -> bool:
        """Check if report has any errors"""
        return len(self.errors) > 0

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        return {
            "execution_time_seconds": self.execution_time_seconds,
            "records_per_second": round(
                self.total_records_deleted / max(self.execution_time_seconds, 0.1), 2
            ),
            "database_operations": self.database_operations_count,
            "file_operations": self.file_operations_count,
            "size_freed_mb": self.get_size_freed_mb(),
        }

    def to_dict(self) -> Dict[str, Any]:
        """تحويل التقرير إلى dictionary"""
        data = asdict(self)
        # Convert sets to lists for JSON serialization
        data["children_affected"] = list(self.children_affected)
        data["parents_notified"] = list(self.parents_notified)
        # Convert datetime objects to ISO strings
        if self.started_at:
            data["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        return data
