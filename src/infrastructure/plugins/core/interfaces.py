"""
Interfaces for the plugin system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .models import PluginMetadata


# Forward declaration for type hinting
class IPlugin(ABC):
    pass


class IPluginManager(ABC):
    """Defines the contract for a plugin manager."""

    @abstractmethod
    async def discover_plugins(self) -> List[PluginMetadata]:
        """Discovers available plugins from the plugin directory."""
        pass

    @abstractmethod
    async def load_plugin(self, plugin_name: str) -> IPlugin:
        """Loads a specific plugin by its name."""
        pass

    @abstractmethod
    async def unload_plugin(self, plugin_name: str) -> None:
        """Unloads a currently loaded plugin."""
        pass

    @abstractmethod
    async def get_plugin(self, plugin_name: str) -> Optional[IPlugin]:
        """Retrieves a loaded plugin instance by its name."""
        pass

    @abstractmethod
    async def list_plugins(self) -> List[PluginMetadata]:
        """Lists metadata for all discovered plugins."""
        pass

    @abstractmethod
    async def start_plugin(self, plugin_name: str) -> None:
        """Starts a loaded plugin."""
        pass

    @abstractmethod
    async def stop_plugin(self, plugin_name: str) -> None:
        """Stops a running plugin."""
        pass


class IPlugin(ABC):
    """The base interface that all plugins must implement."""

    @abstractmethod
    async def initialize(self, config: Dict[str, Any], manager: IPluginManager) -> None:
        """
        Initializes the plugin with its configuration and a reference to the manager.
        This is called once when the plugin is loaded.
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """
        Starts the plugin's operations. This can be called after initialization.
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Stops the plugin's operations gracefully.
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Cleans up any resources used by the plugin before it is unloaded.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Returns the metadata for this plugin."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Performs a health check and returns True if the plugin is healthy, False otherwise.
        """
        pass
