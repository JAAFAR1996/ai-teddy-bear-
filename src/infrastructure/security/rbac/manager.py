"""
The main RBAC manager class.
"""
import logging
from typing import Any, Dict, List, Optional, Set

from .access_checker import AccessCheckerMixin
from .models import Permission, UserProfile, UserRole
from .permissions import get_role_permissions

logger = logging.getLogger(__name__)


class TeddyBearRBACManager(AccessCheckerMixin):
    """
    The central manager for the Role-Based Access Control system, coordinating
    user profiles, roles, permissions, and access checks.
    """

    def __init__(self):
        self.users: Dict[str, UserProfile] = {}
        self.role_permissions: Dict[UserRole,
                                    Set[Permission]] = get_role_permissions()
        self.family_relationships: Dict[str, List[str]] = {}
        self.access_cache: Dict[str, 'AccessDecision'] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.time_restrictions: Dict[str, Dict] = {}
        self.emergency_contacts: Dict[str, List[str]] = {}

    async def create_user(self, user_data: Dict[str, Any]) -> UserProfile:
        """Creates a new user, assigns a role and default permissions, and stores them."""
        user_id = user_data.get("user_id")
        if not user_id:
            raise ValueError("user_id is required to create a user.")

        role = UserRole(user_data.get("role", "guest"))
        permissions = self.role_permissions.get(role, set()).copy()

        user = UserProfile(
            user_id=user_id,
            username=user_data.get("username", "Unknown"),
            role=role,
            permissions=permissions,
            family_id=user_data.get("family_id"),
            age=user_data.get("age"),
        )
        self.users[user_id] = user
        logger.info("User created", user_id=user_id, role=role.value)
        return user

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieves a user's profile by their ID."""
        return self.users.get(user_id)

    async def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Retrieves the set of permissions for a specific user."""
        user = await self.get_user_profile(user_id)
        return user.permissions if user else set()

    async def add_permission_to_user(self, user_id: str, permission: Permission):
        """Grants an additional permission to a user."""
        user = await self.get_user_profile(user_id)
        if user:
            user.permissions.add(permission)
            logger.info("Added permission", user_id=user_id,
                        permission=permission.value)

    async def remove_permission_from_user(self, user_id: str, permission: Permission):
        """Revokes a permission from a user."""
        user = await self.get_user_profile(user_id)
        if user and permission in user.permissions:
            user.permissions.remove(permission)
            logger.info("Removed permission", user_id=user_id,
                        permission=permission.value)

    async def set_time_restrictions(self, user_id: str, restrictions: Dict[str, Any]):
        """Sets time-based access restrictions for a user."""
        self.time_restrictions[user_id] = restrictions
        logger.info("Set time restrictions", user_id=user_id,
                    restrictions=restrictions)

    async def get_audit_log(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves the audit log, optionally filtered by user ID."""
        if user_id:
            return [entry for entry in self.audit_log if entry.get("request", {}).get("user_id") == user_id]
        return self.audit_log
