from typing import List

from ....domain.entities import Child


class ChildAggregateValidator:
    """Validates the consistency of a Child aggregate."""

    def validate(self, child: Child) -> List[str]:
        """
        Validate the consistency of a Child aggregate and return any
        business rule violations or inconsistencies.
        """
        violations = []

        if not child.name or not child.name.strip():
            violations.append("Child name cannot be empty")
        if not 3 <= child.age <= 12:
            violations.append("Child age must be between 3 and 12")

        if child.voice_profile and not child.voice_profile.is_age_appropriate(child.age):
            violations.append(
                "Voice profile complexity not appropriate for child's age")

        if child.safety_settings:
            if child.safety_settings.max_session_minutes > child.safety_settings.max_daily_minutes:
                violations.append(
                    "Session time limit cannot exceed daily time limit")
            if child.daily_usage_minutes > child.safety_settings.max_daily_minutes:
                violations.append("Daily usage exceeds allowed limit")

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

        if child.total_conversations_today < 0:
            violations.append("Daily conversation count cannot be negative")
        if child.daily_usage_minutes < 0:
            violations.append("Daily usage minutes cannot be negative")

        return violations
