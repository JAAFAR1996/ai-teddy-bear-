"""
Core access checking logic for the RBAC system.
"""
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, List

from .models import (
    AccessContext,
    AccessDecision,
    AccessRequest,
    Permission,
    UserProfile,
    UserRole,
)

logger = logging.getLogger(__name__)


class AccessCheckerMixin:
    """A mixin that provides the core logic for checking access requests."""

    users: Dict[str, UserProfile]
    time_restrictions: Dict[str, Dict]
    emergency_contacts: Dict[str, List[str]]

    async def check_access(self, request: AccessRequest) -> AccessDecision:
        """Performs a comprehensive check to determine if a user has access."""
        user = self.users.get(request.user_id)
        if not user or not user.is_active:
            return AccessDecision(granted=False, reason="User not found or inactive.")

        # 1. Basic permission check based on role
        if request.permission not in user.permissions:
            return AccessDecision(granted=False, reason="Permission not granted to role.")

        # 2. Context-specific checks
        context_decision = await self._check_context(user, request)
        if not context_decision.granted:
            return context_decision

        # 3. Resource-specific checks
        resource_decision = await self._check_resource_ownership(user, request)
        if not resource_decision.granted:
            return resource_decision

        # 4. Time-based checks
        time_decision = await self._check_time_of_day(user, request)
        if not time_decision.granted:
            return time_decision

        return AccessDecision(granted=True, reason="Access granted.")

    async def _check_context(self, user: UserProfile, request: AccessRequest) -> AccessDecision:
        """Checks if the user's role is appropriate for the given access context."""
        # This is a simplified context check. A real system might have more complex rules.
        if request.context == AccessContext.PARENTAL_SUPERVISION and user.role not in [UserRole.PARENT, UserRole.GUARDIAN]:
            return AccessDecision(granted=False, reason="Context requires parental role.")
        return AccessDecision(granted=True, reason="Context check passed.")

    async def _check_resource_ownership(self, user: UserProfile, request: AccessRequest) -> AccessDecision:
        """Checks if the user has the required relationship to the resource."""
        if not request.resource_id:
            return AccessDecision(granted=True, reason="No resource to check.")

        # Example for child resources
        if request.resource_id.startswith("child:"):
            child_id = request.resource_id.split(":")[1]
            if user.role == UserRole.CHILD and user.user_id == child_id:
                return AccessDecision(granted=True, reason="Child accessing own resource.")
            # This would require loading the user's family data
            # if user.role == UserRole.PARENT and child_id in user.children_ids:
            #     return AccessDecision(granted=True, reason="Parent accessing own child's resource.")
            return AccessDecision(granted=False, reason="User does not have access to this child's resource.")

        return AccessDecision(granted=True, reason="Resource ownership check passed.")

    async def _check_time_of_day(self, user: UserProfile, request: AccessRequest) -> AccessDecision:
        """Checks if the request is being made within allowed time windows."""
        restrictions = self.time_restrictions.get(user.user_id)
        if not restrictions:
            return AccessDecision(granted=True, reason="No time restrictions.")

        now = datetime.utcnow()
        allowed_hours = restrictions.get("allowed_hours")
        if allowed_hours and now.hour not in range(allowed_hours[0], allowed_hours[1]):
            return AccessDecision(granted=False, reason="Access is outside of allowed hours.")

        return AccessDecision(granted=True, reason="Time of day check passed.")

    async def _log_access_attempt(self, request: AccessRequest, decision: AccessDecision) -> str:
        """Logs an access attempt for auditing purposes."""
        audit_id = f"audit_{len(self.audit_log) + 1}"
        log_entry = {
            "id": audit_id,
            "timestamp": datetime.utcnow().isoformat(),
            "request": request.__dict__,
            "decision": decision.__dict__,
        }
        self.audit_log.append(log_entry)
        logger.info("Access attempt logged", **log_entry)
        return audit_id
