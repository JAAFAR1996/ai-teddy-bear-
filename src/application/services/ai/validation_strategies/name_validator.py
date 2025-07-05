from typing import List

from .....domain.entities import Child
from .base_validator import ValidationStrategy


class NameValidator(ValidationStrategy):
    """Validates the child's name."""

    def validate(self, child: Child) -> List[str]:
        """Validates that the child has a non-empty name."""
        violations = []
        if not child.name or not child.name.strip():
            violations.append("Child name cannot be empty")
        return violations
