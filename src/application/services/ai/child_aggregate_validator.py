from typing import List, Type

from ....domain.entities import Child
from .validation_strategies import (
    AgeValidator,
    ConversationValidator,
    NameValidator,
    SafetySettingsValidator,
    UsageMetricsValidator,
    ValidationStrategy,
    VoiceProfileValidator,
)


class ChildAggregateValidator:
    """Validates the consistency of a Child aggregate using a set of strategies."""

    def __init__(self) -> None:
        self._validators: List[Type[ValidationStrategy]] = [
            NameValidator,
            AgeValidator,
            VoiceProfileValidator,
            SafetySettingsValidator,
            ConversationValidator,
            UsageMetricsValidator,
        ]

    def validate(self, child: Child) -> List[str]:
        """
        Validate the consistency of a Child aggregate by applying all registered
        validation strategies.

        Args:
            child: The Child aggregate to validate.

        Returns:
            A list of all validation violations. An empty list indicates a
            fully consistent aggregate.
        """
        violations = []
        for validator_class in self._validators:
            validator_instance = validator_class()
            violations.extend(validator_instance.validate(child))
        return violations
