"""
A modular and secure plugin architecture for the AI Teddy Bear system.

This package provides the core components for discovering, loading, managing,
and sandboxing plugins.
"""

from .enums import PluginPermission, PluginStatus, PluginType
from .exceptions import (
    PluginError,
    PluginExecutionError,
    PluginLoadError,
    PluginValidationError,
    SecurityError,
)
from .factories import (
    create_plugin_manager,
    create_plugin_marketplace,
    create_plugin_manifest,
    validate_plugin_permissions,
)
from .interfaces import IPlugin, IPluginManager
from .manager import PluginManager
from .marketplace import PluginMarketplace
from .models import PluginManifest, PluginMetadata
from .sandbox import PluginSandbox

__all__ = [
    # Enums
    "PluginPermission",
    "PluginStatus",
    "PluginType",
    # Exceptions
    "PluginError",
    "PluginExecutionError",
    "PluginLoadError",
    "PluginValidationError",
    "SecurityError",
    # Factories
    "create_plugin_manager",
    "create_plugin_marketplace",
    "create_plugin_manifest",
    "validate_plugin_permissions",
    # Interfaces
    "IPlugin",
    "IPluginManager",
    # Implementations
    "PluginManager",
    "PluginMarketplace",
    "PluginSandbox",
    # Models
    "PluginManifest",
    "PluginMetadata",
]
