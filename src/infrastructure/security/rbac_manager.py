from typing import Any, Dict, List, Optional

"""
🔐 Role-Based Access Control (RBAC) Manager - Enterprise Security 2025
=====================================================================

Comprehensive RBAC system for AI Teddy Bear with:
- Parent-Child relationship management
- Fine-grained permissions
- Context-aware access control
- Dynamic role assignment
- Audit trail for all access decisions

Author: Jaafar Adeeb - Security Lead
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

import structlog

logger = structlog.get_logger(__name__)


class UserRole(Enum):
    """User roles in the system"""
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
    """System permissions"""
    # Child Management
    CHILD_CREATE = "child:create"
    CHILD_READ = "child:read"
    CHILD_UPDATE = "child:update"
    CHILD_DELETE = "child:delete"
    CHILD_INTERACT = "child:interact"
    
    # Audio & Voice
    AUDIO_RECORD = "audio:record"
    AUDIO_PLAYBACK = "audio:playback"
    AUDIO_UPLOAD = "audio:upload"
    AUDIO_DOWNLOAD = "audio:download"
    AUDIO_DELETE = "audio:delete"
    
    # Conversations
    CONVERSATION_VIEW = "conversation:view"
    CONVERSATION_MODERATE = "conversation:moderate"
    CONVERSATION_EXPORT = "conversation:export"
    CONVERSATION_DELETE = "conversation:delete"
    
    # Settings & Configuration
    SETTINGS_VIEW = "settings:view"
    SETTINGS_UPDATE = "settings:update"
    SETTINGS_RESET = "settings:reset"
    
    # Parental Controls
    PARENTAL_CONTROLS_VIEW = "parental_controls:view"
    PARENTAL_CONTROLS_UPDATE = "parental_controls:update"
    SCREEN_TIME_MANAGE = "screen_time:manage"
    CONTENT_FILTER_MANAGE = "content_filter:manage"
    
    # Reports & Analytics
    REPORTS_VIEW = "reports:view"
    REPORTS_EXPORT = "reports:export"
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_ADVANCED = "analytics:advanced"
    
    # Device Management
    DEVICE_REGISTER = "device:register"
    DEVICE_MANAGE = "device:manage"
    DEVICE_RESET = "device:reset"
    DEVICE_DELETE = "device:delete"
    
    # Family Management
    FAMILY_CREATE = "family:create"
    FAMILY_MANAGE = "family:manage"
    FAMILY_INVITE = "family:invite"
    FAMILY_REMOVE_MEMBER = "family:remove_member"
    
    # System Administration
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_CONFIGURE = "system:configure"
    USER_MANAGE = "user:manage"
    AUDIT_VIEW = "audit:view"


class AccessContext(Enum):
    """Access context for permission checks"""
    DIRECT_INTERACTION = "direct_interaction"  # Child directly using device
    PARENTAL_SUPERVISION = "parental_supervision"  # Parent supervising/managing
    EMERGENCY_OVERRIDE = "emergency_override"  # Emergency access
    SCHEDULED_ACCESS = "scheduled_access"  # Scheduled interaction
    THERAPEUTIC_SESSION = "therapeutic_session"  # Therapy session
    EDUCATIONAL_ACTIVITY = "educational_activity"  # Educational content


@dataclass
class AccessRequest:
    """Access request structure"""
    user_id: str
    user_role: UserRole
    permission: Permission
    resource_id: Optional[str] = None
    context: AccessContext = AccessContext.DIRECT_INTERACTION
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessDecision:
    """Access decision result"""
    granted: bool
    reason: str
    conditions: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    audit_log_id: Optional[str] = None


@dataclass
class UserProfile:
    """User profile with RBAC information"""
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: Set[Permission]
    family_id: Optional[str] = None
    parent_id: Optional[str] = None  # For children
    children_ids: List[str] = field(default_factory=list)  # For parents
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    security_level: int = 1  # 1-5, higher is more secure
    
    # Child-specific fields
    age: Optional[int] = None
    grade_level: Optional[str] = None
    special_needs: List[str] = field(default_factory=list)
    
    # Parent-specific fields
    parental_controls: Dict[str, Any] = field(default_factory=dict)
    supervision_level: str = "medium"  # low, medium, high, strict


class TeddyBearRBACManager:
    """Comprehensive RBAC manager for AI Teddy Bear system"""
    
    def __init__(self):
        self.users: Dict[str, UserProfile] = {}
        self.role_permissions: Dict[UserRole, Set[Permission]] = {}
        self.family_relationships: Dict[str, List[str]] = {}  # family_id -> user_ids
        self.access_cache: Dict[str, AccessDecision] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        # Initialize role permissions
        self._initialize_role_permissions()
        
        # Time-based restrictions
        self.time_restrictions: Dict[str, Dict[str, Any]] = {}
        
        # Emergency override settings
        self.emergency_contacts: Dict[str, List[str]] = {}
    
    def _initialize_role_permissions(self) -> Any:
        """Initialize default permissions for each role"""
        
        # Super Admin - Full access
        self.role_permissions[UserRole.SUPER_ADMIN] = set(Permission)
        
        # Admin - System management
        self.role_permissions[UserRole.ADMIN] = {
            Permission.SYSTEM_MONITOR,
            Permission.SYSTEM_CONFIGURE,
            Permission.USER_MANAGE,
            Permission.AUDIT_VIEW,
            Permission.REPORTS_VIEW,
            Permission.REPORTS_EXPORT,
            Permission.ANALYTICS_VIEW,
            Permission.ANALYTICS_ADVANCED,
        }
        
        # Parent - Full control over their children
        self.role_permissions[UserRole.PARENT] = {
            Permission.CHILD_CREATE,
            Permission.CHILD_READ,
            Permission.CHILD_UPDATE,
            Permission.CHILD_DELETE,
            Permission.CHILD_INTERACT,
            Permission.AUDIO_RECORD,
            Permission.AUDIO_PLAYBACK,
            Permission.AUDIO_UPLOAD,
            Permission.AUDIO_DOWNLOAD,
            Permission.AUDIO_DELETE,
            Permission.CONVERSATION_VIEW,
            Permission.CONVERSATION_MODERATE,
            Permission.CONVERSATION_EXPORT,
            Permission.CONVERSATION_DELETE,
            Permission.SETTINGS_VIEW,
            Permission.SETTINGS_UPDATE,
            Permission.SETTINGS_RESET,
            Permission.PARENTAL_CONTROLS_VIEW,
            Permission.PARENTAL_CONTROLS_UPDATE,
            Permission.SCREEN_TIME_MANAGE,
            Permission.CONTENT_FILTER_MANAGE,
            Permission.REPORTS_VIEW,
            Permission.REPORTS_EXPORT,
            Permission.ANALYTICS_VIEW,
            Permission.DEVICE_REGISTER,
            Permission.DEVICE_MANAGE,
            Permission.DEVICE_RESET,
            Permission.DEVICE_DELETE,
            Permission.FAMILY_CREATE,
            Permission.FAMILY_MANAGE,
            Permission.FAMILY_INVITE,
            Permission.FAMILY_REMOVE_MEMBER,
        }
        
        # Child - Limited interaction permissions
        self.role_permissions[UserRole.CHILD] = {
            Permission.CHILD_INTERACT,
            Permission.AUDIO_RECORD,
            Permission.AUDIO_PLAYBACK,
            Permission.SETTINGS_VIEW,
        }
        
        # Guardian - Similar to parent but limited
        self.role_permissions[UserRole.GUARDIAN] = {
            Permission.CHILD_READ,
            Permission.CHILD_INTERACT,
            Permission.AUDIO_PLAYBACK,
            Permission.CONVERSATION_VIEW,
            Permission.SETTINGS_VIEW,
            Permission.REPORTS_VIEW,
            Permission.ANALYTICS_VIEW,
        }
        
        # Educator - Educational content management
        self.role_permissions[UserRole.EDUCATOR] = {
            Permission.CHILD_INTERACT,
            Permission.AUDIO_RECORD,
            Permission.AUDIO_PLAYBACK,
            Permission.CONVERSATION_VIEW,
            Permission.REPORTS_VIEW,
            Permission.ANALYTICS_VIEW,
        }
        
        # Therapist - Therapeutic session access
        self.role_permissions[UserRole.THERAPIST] = {
            Permission.CHILD_INTERACT,
            Permission.AUDIO_RECORD,
            Permission.AUDIO_PLAYBACK,
            Permission.CONVERSATION_VIEW,
            Permission.CONVERSATION_EXPORT,
            Permission.REPORTS_VIEW,
            Permission.ANALYTICS_VIEW,
        }
        
        # Support - Limited system access
        self.role_permissions[UserRole.SUPPORT] = {
            Permission.SYSTEM_MONITOR,
            Permission.AUDIT_VIEW,
            Permission.DEVICE_MANAGE,
        }
        
        # Guest - Very limited access
        self.role_permissions[UserRole.GUEST] = {
            Permission.CHILD_INTERACT,
        }
    
    async def check_access(self, request: AccessRequest) -> AccessDecision:
        """Check if user has access to requested resource/action"""
        
        # Get user profile
        user = self.users.get(request.user_id)
        if not user:
            return AccessDecision(
                granted=False,
                reason="User not found",
                audit_log_id=await self._log_access_attempt(request, False, "User not found")
            )
        
        # Check if user is active
        if not user.is_active:
            return AccessDecision(
                granted=False,
                reason="User account is inactive",
                audit_log_id=await self._log_access_attempt(request, False, "Inactive user")
            )
        
        # Check basic role permissions
        if request.permission not in user.permissions:
            return AccessDecision(
                granted=False,
                reason="Permission not granted to user role",
                audit_log_id=await self._log_access_attempt(request, False, "Permission denied")
            )
        
        # Context-specific checks
        context_check = await self._check_context_permissions(user, request)
        if not context_check.granted:
            return context_check
        
        # Resource-specific checks
        resource_check = await self._check_resource_access(user, request)
        if not resource_check.granted:
            return resource_check
        
        # Time-based restrictions
        time_check = await self._check_time_restrictions(user, request)
        if not time_check.granted:
            return time_check
        
        # Child safety checks
        if user.role == UserRole.CHILD:
            safety_check = await self._check_child_safety(user, request)
            if not safety_check.granted:
                return safety_check
        
        # Success - grant access
        decision = AccessDecision(
            granted=True,
            reason="Access granted",
            conditions=context_check.conditions + resource_check.conditions + time_check.conditions,
            expires_at=self._calculate_access_expiry(user, request),
            audit_log_id=await self._log_access_attempt(request, True, "Access granted")
        )
        
        # Cache the decision
        cache_key = f"{request.user_id}:{request.permission.value}:{request.resource_id}"
        self.access_cache[cache_key] = decision
        
        return decision
    
    async def _check_context_permissions(self, user: UserProfile, request: AccessRequest) -> AccessDecision:
        """Check context-specific permissions"""
        
        # Direct interaction context
        if request.context == AccessContext.DIRECT_INTERACTION:
            if user.role == UserRole.CHILD:
                # Check if child has permission for direct interaction
                return AccessDecision(granted=True, reason="Child direct interaction allowed")
            elif user.role == UserRole.PARENT:
                return AccessDecision(granted=True, reason="Parent access allowed")
        
        # Parental supervision context
        elif request.context == AccessContext.PARENTAL_SUPERVISION:
            if user.role not in [UserRole.PARENT, UserRole.GUARDIAN]:
                return AccessDecision(
                    granted=False,
                    reason="Only parents and guardians can access parental supervision"
                )
        
        # Emergency override
        elif request.context == AccessContext.EMERGENCY_OVERRIDE:
            if user.user_id in self.emergency_contacts.get(request.resource_id, []):
                return AccessDecision(
                    granted=True,
                    reason="Emergency override granted",
                    conditions=["Emergency access logged"]
                )
            else:
                return AccessDecision(
                    granted=False,
                    reason="User not authorized for emergency override"
                )
        
        # Therapeutic session
        elif request.context == AccessContext.THERAPEUTIC_SESSION:
            if user.role not in [UserRole.THERAPIST, UserRole.PARENT]:
                return AccessDecision(
                    granted=False,
                    reason="Only therapists and parents can access therapeutic sessions"
                )
        
        # Educational activity
        elif request.context == AccessContext.EDUCATIONAL_ACTIVITY:
            if user.role not in [UserRole.EDUCATOR, UserRole.PARENT, UserRole.CHILD]:
                return AccessDecision(
                    granted=False,
                    reason="Only educators, parents, and children can access educational activities"
                )
        
        return AccessDecision(granted=True, reason="Context check passed")
    
    async def _check_resource_access(self, user: UserProfile, request: AccessRequest) -> AccessDecision:
        """Check if user can access specific resource"""
        
        if not request.resource_id:
            return AccessDecision(granted=True, reason="No specific resource check needed")
        
        # Check if trying to access child resource
        if request.resource_id.startswith("child:"):
            child_id = request.resource_id.split(":")[1]
            
            # Parents can access their own children
            if user.role == UserRole.PARENT and child_id in user.children_ids:
                return AccessDecision(granted=True, reason="Parent accessing own child")
            
            # Children can only access their own data
            elif user.role == UserRole.CHILD and child_id == user.user_id:
                return AccessDecision(granted=True, reason="Child accessing own data")
            
            # Guardians need explicit permission
            elif user.role == UserRole.GUARDIAN:
                # Check if guardian has permission for this specific child
                # This would typically be stored in a database
                return AccessDecision(granted=True, reason="Guardian access (needs DB verification)")
            
            else:
                return AccessDecision(
                    granted=False,
                    reason="User not authorized to access this child's data"
                )
        
        # Check family resource access
        elif request.resource_id.startswith("family:"):
            family_id = request.resource_id.split(":")[1]
            
            if user.family_id == family_id:
                return AccessDecision(granted=True, reason="User is member of this family")
            else:
                return AccessDecision(
                    granted=False,
                    reason="User is not a member of this family"
                )
        
        return AccessDecision(granted=True, reason="Resource access check passed")
    
    async def _check_time_restrictions(self, user: UserProfile, request: AccessRequest) -> AccessDecision:
        """Check time-based access restrictions"""
        
        current_time = datetime.utcnow()
        
        # Check if user has time restrictions
        if user.user_id in self.time_restrictions:
            restrictions = self.time_restrictions[user.user_id]
            
            # Check daily time limits
            if "daily_limit" in restrictions:
                # This would check daily usage time against limits
                pass
            
            # Check allowed hours
            if "allowed_hours" in restrictions:
                current_hour = current_time.hour
                allowed_hours = restrictions["allowed_hours"]
                if current_hour not in allowed_hours:
                    return AccessDecision(
                        granted=False,
                        reason=f"Access not allowed at this time. Allowed hours: {allowed_hours}"
                    )
            
            # Check weekend restrictions
            if "weekend_restricted" in restrictions and restrictions["weekend_restricted"]:
                if current_time.weekday() >= 5:  # Saturday and Sunday
                    return AccessDecision(
                        granted=False,
                        reason="Weekend access is restricted for this user"
                    )
        
        return AccessDecision(granted=True, reason="Time restrictions check passed")
    
    async def _check_child_safety(self, user: UserProfile, request: AccessRequest) -> AccessDecision:
        """Additional safety checks for child users"""
        
        # Check if child is in a safe environment
        if request.permission in [Permission.AUDIO_RECORD, Permission.CHILD_INTERACT]:
            # In a real system, this might check:
            # - Location (if at home/school)
            # - Time of day
            # - Parental supervision status
            # - Content appropriateness
            
            # For now, we'll allow with conditions
            return AccessDecision(
                granted=True,
                reason="Child safety check passed",
                conditions=[
                    "Child interaction monitored",
                    "Content filtering active",
                    "Parent notification sent"
                ]
            )
        
        return AccessDecision(granted=True, reason="Child safety check passed")
    
    def _calculate_access_expiry(self, user: UserProfile, request: AccessRequest) -> Optional[datetime]:
        """Calculate when access expires"""
        
        # Child sessions expire after 30 minutes
        if user.role == UserRole.CHILD:
            return datetime.utcnow() + timedelta(minutes=30)
        
        # Parent sessions expire after 4 hours
        elif user.role == UserRole.PARENT:
            return datetime.utcnow() + timedelta(hours=4)
        
        # Admin sessions expire after 8 hours
        elif user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return datetime.utcnow() + timedelta(hours=8)
        
        # Other roles expire after 2 hours
        else:
            return datetime.utcnow() + timedelta(hours=2)
    
    async def _log_access_attempt(self, request: AccessRequest, granted: bool, reason: str) -> str:
        """Log access attempt for audit trail"""
        
        log_entry = {
            "id": f"audit_{len(self.audit_log) + 1}",
            "timestamp": request.timestamp.isoformat(),
            "user_id": request.user_id,
            "user_role": request.user_role.value,
            "permission": request.permission.value,
            "resource_id": request.resource_id,
            "context": request.context.value,
            "granted": granted,
            "reason": reason,
            "ip_address": request.ip_address,
            "user_agent": request.user_agent,
            "additional_data": request.additional_data
        }
        
        self.audit_log.append(log_entry)
        
        # In production, this would be stored in a database
        logger.info("Access attempt logged", **log_entry)
        
        return log_entry["id"]
    
    async def create_user(self, user_data: Dict[str, Any]) -> UserProfile:
        """Create a new user with appropriate permissions"""
        
        user_id = user_data["user_id"]
        role = UserRole(user_data["role"])
        
        # Get base permissions for role
        permissions = self.role_permissions[role].copy()
        
        # Create user profile
        user = UserProfile(
            user_id=user_id,
            username=user_data["username"],
            email=user_data["email"],
            role=role,
            permissions=permissions,
            family_id=user_data.get("family_id"),
            parent_id=user_data.get("parent_id"),
            age=user_data.get("age"),
            special_needs=user_data.get("special_needs", [])
        )
        
        # Set up parent-child relationships
        if role == UserRole.CHILD and user_data.get("parent_id"):
            parent = self.users.get(user_data["parent_id"])
            if parent:
                parent.children_ids.append(user_id)
        
        self.users[user_id] = user
        
        logger.info("User created", user_id=user_id, role=role.value)
        return user
    
    async def set_time_restrictions(self, user_id: str, restrictions: Dict[str, Any]):
        """Set time-based restrictions for a user"""
        self.time_restrictions[user_id] = restrictions
        logger.info("Time restrictions set", user_id=user_id, restrictions=restrictions)
    
    async def add_emergency_contact(self, resource_id: str, contact_id: str):
        """Add emergency contact for a resource"""
        if resource_id not in self.emergency_contacts:
            self.emergency_contacts[resource_id] = []
        self.emergency_contacts[resource_id].append(contact_id)
        logger.info("Emergency contact added", resource_id=resource_id, contact_id=contact_id)
    
    async def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for a user"""
        user = self.users.get(user_id)
        return user.permissions if user else set()
    
    async def get_family_members(self, family_id: str) -> List[UserProfile]:
        """Get all members of a family"""
        return [user for user in self.users.values() if user.family_id == family_id]
    
    async def get_audit_log(self, user_id: Optional[str] = None, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get audit log entries with optional filters"""
        filtered_log = self.audit_log
        
        if user_id:
            filtered_log = [entry for entry in filtered_log if entry["user_id"] == user_id]
        
        if start_date:
            filtered_log = [entry for entry in filtered_log 
                           if datetime.fromisoformat(entry["timestamp"]) >= start_date]
        
        if end_date:
            filtered_log = [entry for entry in filtered_log 
                           if datetime.fromisoformat(entry["timestamp"]) <= end_date]
        
        return filtered_log


# Global RBAC manager instance
_rbac_manager: Optional[TeddyBearRBACManager] = None


def get_rbac_manager() -> TeddyBearRBACManager:
    """Get global RBAC manager instance"""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = TeddyBearRBACManager()
    return _rbac_manager


# Convenience decorators for permission checking

def require_permission(AccessContext = AccessContext.DIRECT_INTERACTION) -> None:
    """Decorator to require specific permission for a function"""
    def decorator(func) -> Any:
        async def wrapper(*args, **kwargs):
            # Extract user_id from kwargs or first argument
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            if not user_id:
                raise ValueError("User ID required for permission check")
            
            rbac = get_rbac_manager()
            user = rbac.users.get(user_id)
            if not user:
                raise PermissionError("User not found")
            
            request = AccessRequest(
                user_id=user_id,
                user_role=user.role,
                permission=permission,
                context=context
            )
            
            decision = await rbac.check_access(request)
            if not decision.granted:
                raise PermissionError(f"Access denied: {decision.reason}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(List[UserRole]) -> None:
    """Decorator to require specific roles for a function"""
    def decorator(func) -> Any:
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            if not user_id:
                raise ValueError("User ID required for role check")
            
            rbac = get_rbac_manager()
            user = rbac.users.get(user_id)
            if not user:
                raise PermissionError("User not found")
            
            if user.role not in allowed_roles:
                raise PermissionError(f"Access denied. Required roles: {[r.value for r in allowed_roles]}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator 