from typing import List

from .....domain.entities import Child
from .base_validator import ValidationStrategy


class SafetySettingsValidator(ValidationStrategy):
    """Validates the child's safety settings."""

    def validate(self, child: Child) -> List[str]:
        """Validates safety settings like session time and daily usage."""
        violations = []
        if child.safety_settings:
            if child.safety_settings.max_session_minutes > child.safety_settings.max_daily_minutes:
                violations.append(
                    "Session time limit cannot exceed daily time limit")
            if child.daily_usage_minutes > child.safety_settings.max_daily_minutes:
                violations.append("Daily usage exceeds allowed limit")
        return violations
