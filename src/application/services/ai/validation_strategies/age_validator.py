from typing import List

from .....domain.entities import Child
from .base_validator import ValidationStrategy


class AgeValidator(ValidationStrategy):
    """Validates the child's age."""

    def validate(self, child: Child) -> List[str]:
        """Validates that the child's age is within the allowed range."""
        violations = []
        if not 3 <= child.age <= 12:
            violations.append("Child age must be between 3 and 12")
        return violations
