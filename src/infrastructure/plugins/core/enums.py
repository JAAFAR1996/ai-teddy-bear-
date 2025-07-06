"""
Enumerations for the plugin system.
"""
from enum import Enum


class PluginStatus(Enum):
    """Defines the lifecycle status of a plugin."""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UPDATING = "updating"
    UNINSTALLING = "uninstalling"


class PluginType(Enum):
    """Categorizes plugins by their primary function."""
    AI_SERVICE = "ai_service"
    AUDIO_PROCESSOR = "audio_processor"
    SECURITY_MODULE = "security_module"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    CUSTOM = "custom"


class PluginPermission(Enum):
    """Defines the permission levels that can be granted to a plugin."""
    READ_ONLY = "read_only"  # Can only read data, no modifications.
    BASIC = "basic"          # Basic operations, limited API access.
    # More extensive API access, potential for some modifications.
    ELEVATED = "elevated"
    # High-level access, significant modification capabilities.
    ADMIN = "admin"
    SYSTEM = "system"        # Full system access, reserved for core plugins.
