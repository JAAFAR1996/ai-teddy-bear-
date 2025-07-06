"""
A comprehensive, modular Role-Based Access Control (RBAC) system.
"""

from .decorators import require_permission, require_role
from .factory import get_rbac_manager
from .manager import TeddyBearRBACManager
from .models import (
    AccessContext,
    AccessDecision,
    AccessRequest,
    Permission,
    UserProfile,
    UserRole,
)

__all__ = [
    # Main Manager and Factory
    "TeddyBearRBACManager",
    "get_rbac_manager",
    # Decorators
    "require_permission",
    "require_role",
    # Models
    "AccessContext",
    "AccessDecision",
    "AccessRequest",
    "Permission",
    "UserProfile",
    "UserRole",
]
