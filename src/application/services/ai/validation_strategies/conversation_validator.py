from typing import List

from .....domain.entities import Child
from .base_validator import ValidationStrategy


class ConversationValidator(ValidationStrategy):
    """Validates the state of the child's conversations."""

    def validate(self, child: Child) -> List[str]:
        """
        Validates rules related to active conversations, ensuring consistency
        and integrity.
        """
        violations = []
        if len(child.active_conversations) > 1:
            violations.append(
                "Child cannot have more than one active conversation")
        for conversation in child.active_conversations:
            if conversation.child_id != child.id:
                violations.append(
                    "Active conversation belongs to different child")
            if conversation.status not in ["active", "paused"]:
                violations.append(
                    "Active conversation list contains non-active conversation")
        return violations
