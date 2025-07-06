"""
Factory and utility functions for the plugin system.
"""
from typing import List

from .enums import PluginPermission, PluginType
from .interfaces import IPluginManager
from .manager import PluginManager
from .marketplace import PluginMarketplace
from .models import PluginManifest


def create_plugin_manager(plugins_directory: str = "plugins") -> IPluginManager:
    """Creates and returns a new instance of the default PluginManager."""
    return PluginManager(plugins_directory)


def create_plugin_marketplace(
    marketplace_url: str = "https://plugins.teddybear.ai/api/v1",
) -> PluginMarketplace:
    """Creates and returns a new instance of the PluginMarketplace client."""
    return PluginMarketplace(marketplace_url)


def create_plugin_manifest(
    name: str,
    version: str,
    description: str,
    author: str,
    plugin_type: PluginType,
    entry_point: str,
    **kwargs,
) -> PluginManifest:
    """A helper function to create a PluginManifest object programmatically."""
    return PluginManifest(
        name=name,
        version=version,
        description=description,
        author=author,
        plugin_type=plugin_type,
        entry_point=entry_point,
        **kwargs,
    )


def validate_plugin_permissions(permissions: List[PluginPermission]) -> bool:
    """
    Validates a list of plugin permissions to check for overly permissive or
    dangerous requests. Returns False if a dangerous permission is found.
    """
    dangerous_permissions = {PluginPermission.SYSTEM}
    requested_perms = set(permissions)

    intersection = requested_perms.intersection(dangerous_permissions)

    if intersection:
        # In a real application, you might want to log this or have a more
        # robust notification system.
        print(
            f"Warning: Plugin requests dangerous permissions: {intersection}")
        return False

    return True
