from typing import List

from .....domain.entities import Child
from .base_validator import ValidationStrategy


class UsageMetricsValidator(ValidationStrategy):
    """Validates the child's usage metrics."""

    def validate(self, child: Child) -> List[str]:
        """Validates that usage metrics are not negative."""
        violations = []
        if child.total_conversations_today < 0:
            violations.append("Daily conversation count cannot be negative")
        if child.daily_usage_minutes < 0:
            violations.append("Daily usage minutes cannot be negative")
        return violations
