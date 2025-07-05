from typing import List

from .....domain.entities import Child
from .base_validator import ValidationStrategy


class VoiceProfileValidator(ValidationStrategy):
    """Validates the child's voice profile."""

    def validate(self, child: Child) -> List[str]:
        """Validates the appropriateness of the voice profile for the child's age."""
        violations = []
        if child.voice_profile and not child.voice_profile.is_age_appropriate(child.age):
            violations.append(
                "Voice profile complexity not appropriate for child's age")
        return violations
