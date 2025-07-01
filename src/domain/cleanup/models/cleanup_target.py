#!/usr/bin/env python3
"""
Cleanup Target Entity
Represents a specific target for data cleanup operations
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class CleanupTarget:
    """هدف التنظيف مع التفاصيل"""

    table_name: str
    record_id: str
    child_id: Optional[str] = None
    created_at: Optional[datetime] = None
    data_type: str = "unknown"
    size_bytes: int = 0
    related_files: List[str] = field(default_factory=list)
    foreign_key_refs: List[str] = field(default_factory=list)

    def is_database_record(self) -> bool:
        """Check if target is a database record"""
        return self.table_name not in ["files", "cache"]

    def is_file_target(self) -> bool:
        """Check if target is a file"""
        return self.table_name in ["files", "cache"] or self.data_type.endswith("_file")

    def get_size_mb(self) -> float:
        """Get size in megabytes"""
        return round(self.size_bytes / 1024 / 1024, 2)

    def has_related_data(self) -> bool:
        """Check if target has related data that needs cleanup"""
        return bool(self.foreign_key_refs or self.related_files)

    def get_age_days(self) -> int:
        """Get age of target in days"""
        if not self.created_at:
            return 0

        age_delta = datetime.utcnow() - self.created_at
        return age_delta.days
