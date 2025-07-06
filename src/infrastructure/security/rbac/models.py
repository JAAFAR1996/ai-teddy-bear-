"""
Data models for the Role-Based Access Control (RBAC) system.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class UserRole(Enum):
    """Defines the roles a user can have within the system."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    PARENT = "parent"
    CHILD = "child"
    GUARDIAN = "guardian"
    EDUCATOR = "educator"
    THERAPIST = "therapist"
    SUPPORT = "support"
    GUEST = "guest"


class Permission(Enum):
    """Defines fine-grained permissions for actions within the system."""
    # Child Management
    CHILD_CREATE = "child:create"
    CHILD_READ = "child:read"
    CHILD_UPDATE = "child:update"
    CHILD_DELETE = "child:delete"
    CHILD_INTERACT = "child:interact"
    # Audio & Voice
    AUDIO_UPLOAD = "audio:upload"
    AUDIO_PLAYBACK = "audio:playback"
    # Settings & Configuration
    SETTINGS_VIEW = "settings:view"
    SETTINGS_UPDATE = "settings:update"
    # Parental Controls
    PARENTAL_CONTROLS_VIEW = "parental_controls:view"
    PARENTAL_CONTROLS_UPDATE = "parental_controls:update"
    # Reports & Analytics
    REPORTS_VIEW = "reports:view"
    # Family Management
    FAMILY_MANAGE = "family:manage"
    # System Administration
    SYSTEM_MONITOR = "system:monitor"
    USER_MANAGE = "user:manage"


class AccessContext(Enum):
    """Defines the context in which a permission is being requested."""
    DIRECT_INTERACTION = "direct_interaction"
    PARENTAL_SUPERVISION = "parental_supervision"
    EMERGENCY_OVERRIDE = "emergency_override"
    SCHEDULED_ACCESS = "scheduled_access"
    THERAPEUTIC_SESSION = "therapeutic_session"
    EDUCATIONAL_ACTIVITY = "educational_activity"


@dataclass
class AccessRequest:
    """Represents a request to perform an action that requires a permission check."""
    user_id: str
    user_role: UserRole
    permission: Permission
    resource_id: Optional[str] = None
    context: AccessContext = AccessContext.DIRECT_INTERACTION
    ip_address: Optional[str] = None
    # Add any other relevant context for the decision
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessDecision:
    """Represents the result of a permission check."""
    granted: bool
    reason: str
    conditions: List[str] = field(default_factory=list)
    audit_log_id: Optional[str] = None


@dataclass
class UserProfile:
    """Represents a user's profile, including their roles and permissions."""
    user_id: str
    username: str
    role: UserRole
    permissions: Set[Permission]
    family_id: Optional[str] = None
    is_active: bool = True
    # Other relevant user fields
    age: Optional[int] = None
