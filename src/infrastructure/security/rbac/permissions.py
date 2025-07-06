"""
Defines the mapping of roles to their default permissions.
"""
from typing import Dict, Set

from .models import Permission, UserRole


def get_role_permissions() -> Dict[UserRole, Set[Permission]]:
    """
    Returns a dictionary that defines the default set of permissions for each
    user role in the system.
    """
    return {
        UserRole.SUPER_ADMIN: set(Permission),
        UserRole.ADMIN: {
            Permission.SYSTEM_MONITOR,
            Permission.USER_MANAGE,
            Permission.REPORTS_VIEW,
        },
        UserRole.PARENT: {
            Permission.CHILD_CREATE,
            Permission.CHILD_READ,
            Permission.CHILD_UPDATE,
            Permission.CHILD_DELETE,
            Permission.CHILD_INTERACT,
            Permission.AUDIO_UPLOAD,
            Permission.AUDIO_PLAYBACK,
            Permission.SETTINGS_VIEW,
            Permission.SETTINGS_UPDATE,
            Permission.PARENTAL_CONTROLS_VIEW,
            Permission.PARENTAL_CONTROLS_UPDATE,
            Permission.REPORTS_VIEW,
            Permission.FAMILY_MANAGE,
        },
        UserRole.CHILD: {
            Permission.CHILD_INTERACT,
            Permission.AUDIO_PLAYBACK,
            Permission.SETTINGS_VIEW,
        },
        UserRole.GUARDIAN: {
            Permission.CHILD_READ,
            Permission.CHILD_INTERACT,
            Permission.REPORTS_VIEW,
        },
        UserRole.EDUCATOR: {
            Permission.CHILD_INTERACT,
            Permission.REPORTS_VIEW,
        },
        UserRole.THERAPIST: {
            Permission.CHILD_INTERACT,
            Permission.REPORTS_VIEW,
        },
        UserRole.SUPPORT: {
            Permission.SYSTEM_MONITOR,
            Permission.USER_MANAGE,
        },
        UserRole.GUEST: {
            Permission.CHILD_INTERACT,
        },
    }
