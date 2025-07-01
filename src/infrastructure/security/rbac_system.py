"""
🔐 RBAC System for AI Teddy Bear - Parent-Child Access Control
============================================================

Author: Jaafar Adeeb - Security Lead
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set

import structlog

logger = structlog.get_logger(__name__)


class UserRole(Enum):
    """User roles in the system"""

    PARENT = "parent"
    CHILD = "child"
    GUARDIAN = "guardian"
    ADMIN = "admin"


class Permission(Enum):
    """System permissions"""

    CHILD_INTERACT = "child:interact"
    AUDIO_RECORD = "audio:record"
    AUDIO_PLAYBACK = "audio:playback"
    CONVERSATION_VIEW = "conversation:view"
    SETTINGS_UPDATE = "settings:update"
    PARENTAL_CONTROLS = "parental_controls"
    DEVICE_MANAGE = "device:manage"
    REPORTS_VIEW = "reports:view"


@dataclass
class UserProfile:
    """User profile with RBAC information"""

    user_id: str
    username: str
    role: UserRole
    permissions: Set[Permission]
    family_id: Optional[str] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = None
    is_active: bool = True

    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []


class RBACManager:
    """Role-Based Access Control Manager"""

    def __init__(self):
        self.users: Dict[str, UserProfile] = {}
        self.role_permissions = self._initialize_permissions()

    def _initialize_permissions(self) -> Dict[UserRole, Set[Permission]]:
        """Initialize default permissions for each role"""
        return {
            UserRole.PARENT: {
                Permission.CHILD_INTERACT,
                Permission.AUDIO_RECORD,
                Permission.AUDIO_PLAYBACK,
                Permission.CONVERSATION_VIEW,
                Permission.SETTINGS_UPDATE,
                Permission.PARENTAL_CONTROLS,
                Permission.DEVICE_MANAGE,
                Permission.REPORTS_VIEW,
            },
            UserRole.CHILD: {
                Permission.CHILD_INTERACT,
                Permission.AUDIO_RECORD,
                Permission.AUDIO_PLAYBACK,
            },
            UserRole.GUARDIAN: {
                Permission.CHILD_INTERACT,
                Permission.AUDIO_PLAYBACK,
                Permission.CONVERSATION_VIEW,
                Permission.REPORTS_VIEW,
            },
            UserRole.ADMIN: set(Permission),  # All permissions
        }

    async def check_permission(self, user_id: str, permission: Permission, resource_id: Optional[str] = None) -> bool:
        """Check if user has specific permission"""
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False

        # Check basic permission
        if permission not in user.permissions:
            return False

        # Resource-specific checks
        if resource_id and resource_id.startswith("child:"):
            child_id = resource_id.split(":")[1]

            # Parents can access their own children
            if user.role == UserRole.PARENT and child_id in user.children_ids:
                return True

            # Children can only access their own data
            if user.role == UserRole.CHILD and child_id == user.user_id:
                return True

            # Admins have full access
            if user.role == UserRole.ADMIN:
                return True

            return False

        return True

    async def create_user(
        self,
        user_id: str,
        username: str,
        role: UserRole,
        family_id: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> UserProfile:
        """Create a new user"""
        permissions = self.role_permissions[role].copy()

        user = UserProfile(
            user_id=user_id,
            username=username,
            role=role,
            permissions=permissions,
            family_id=family_id,
            parent_id=parent_id,
        )

        # Set up parent-child relationships
        if role == UserRole.CHILD and parent_id:
            parent = self.users.get(parent_id)
            if parent:
                parent.children_ids.append(user_id)

        self.users[user_id] = user
        logger.info("User created", user_id=user_id, role=role.value)
        return user

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        return self.users.get(user_id)


# Global instance
_rbac_manager: Optional[RBACManager] = None


def get_rbac_manager() -> RBACManager:
    """Get global RBAC manager instance"""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager()
    return _rbac_manager
