"""
Core plugin management implementation.
"""
import asyncio
import importlib
import inspect
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles

from .enums import PluginStatus
from .exceptions import PluginLoadError, PluginValidationError
from .interfaces import IPlugin, IPluginManager
from .models import PluginManifest, PluginMetadata
from .sandbox import PluginSandbox

logger = logging.getLogger(__name__)


class PluginManager(IPluginManager):
    """
    Manages the lifecycle of plugins, including discovery, loading,
    unloading, and execution within a secure sandbox.
    """

    def __init__(self, plugins_directory: str = "plugins"):
        self.plugins_directory = Path(plugins_directory).resolve()
        self.plugins_directory.mkdir(exist_ok=True, parents=True)

        self.loaded_plugins: Dict[str, IPlugin] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_status: Dict[str, PluginStatus] = {}

    async def discover_plugins(self) -> List[PluginMetadata]:
        """Discovers all valid plugins in the plugins directory."""
        discovered_plugins = []
        for item in self.plugins_directory.iterdir():
            if item.is_dir():
                try:
                    manifest = await self._load_plugin_manifest(item)
                    metadata = self._manifest_to_metadata(manifest)
                    discovered_plugins.append(metadata)
                    self.plugin_metadata[manifest.name] = metadata
                    if manifest.name not in self.plugin_status:
                        self.plugin_status[manifest.name] = PluginStatus.DISCOVERED
                except (PluginLoadError, PluginValidationError) as e:
                    logger.warning(
                        f"Could not load manifest for plugin in '{item.name}': {e}")

        logger.info(f"Discovered {len(discovered_plugins)} plugins.")
        return discovered_plugins

    async def load_plugin(self, plugin_name: str) -> IPlugin:
        """Loads, initializes, and returns a plugin instance by its name."""
        if plugin_name in self.loaded_plugins:
            logger.info(f"Plugin '{plugin_name}' is already loaded.")
            return self.loaded_plugins[plugin_name]

        plugin_dir = self.plugins_directory / plugin_name
        if not plugin_dir.is_dir():
            raise PluginLoadError(
                f"Plugin directory not found for '{plugin_name}'.")

        try:
            manifest = await self._load_plugin_manifest(plugin_dir)
            await self._validate_plugin(manifest)

            plugin_instance = self._create_plugin_instance(
                manifest, plugin_dir)

            config = await self._load_plugin_config(plugin_name)
            await plugin_instance.initialize(config, self)

            self.loaded_plugins[plugin_name] = plugin_instance
            self.plugin_status[plugin_name] = PluginStatus.LOADED
            logger.info(
                f"Successfully loaded plugin: {plugin_name} v{manifest.version}")
            return plugin_instance

        except (PluginLoadError, PluginValidationError, Exception) as e:
            self.plugin_status[plugin_name] = PluginStatus.ERROR
            logger.error(
                f"Failed to load plugin '{plugin_name}': {e}", exc_info=True)
            raise PluginLoadError(f"Failed to load plugin {plugin_name}: {e}")

    async def unload_plugin(self, plugin_name: str) -> None:
        """Stops, cleans up, and unloads a plugin."""
        if plugin_name not in self.loaded_plugins:
            logger.warning(
                f"Attempted to unload plugin '{plugin_name}', which is not loaded.")
            return

        plugin = self.loaded_plugins[plugin_name]
        try:
            await self.stop_plugin(plugin_name)
            await plugin.cleanup()

            del self.loaded_plugins[plugin_name]
            self.plugin_status[plugin_name] = PluginStatus.DISCOVERED
            logger.info(f"Successfully unloaded plugin: {plugin_name}")

        except Exception as e:
            self.plugin_status[plugin_name] = PluginStatus.ERROR
            logger.error(
                f"Error during unload of plugin '{plugin_name}': {e}", exc_info=True)

    async def get_plugin(self, plugin_name: str) -> Optional[IPlugin]:
        """Retrieves a loaded plugin instance."""
        return self.loaded_plugins.get(plugin_name)

    async def list_plugins(self) -> List[PluginMetadata]:
        """Lists metadata for all currently discovered plugins."""
        return list(self.plugin_metadata.values())

    async def start_plugin(self, plugin_name: str) -> None:
        """Starts a loaded plugin."""
        plugin = self.loaded_plugins.get(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_name}' is not loaded.")

        try:
            await plugin.start()
            self.plugin_status[plugin_name] = PluginStatus.ACTIVE
            logger.info(f"Plugin '{plugin_name}' started successfully.")
        except Exception as e:
            self.plugin_status[plugin_name] = PluginStatus.ERROR
            logger.error(
                f"Failed to start plugin '{plugin_name}': {e}", exc_info=True)
            raise

    async def stop_plugin(self, plugin_name: str) -> None:
        """Stops a running plugin."""
        plugin = self.loaded_plugins.get(plugin_name)
        if not plugin or self.plugin_status.get(plugin_name) != PluginStatus.ACTIVE:
            return

        try:
            await plugin.stop()
            self.plugin_status[plugin_name] = PluginStatus.INACTIVE
            logger.info(f"Plugin '{plugin_name}' stopped successfully.")
        except Exception as e:
            self.plugin_status[plugin_name] = PluginStatus.ERROR
            logger.error(
                f"Error stopping plugin '{plugin_name}': {e}", exc_info=True)
            raise

    async def _load_plugin_manifest(self, plugin_dir: Path) -> PluginManifest:
        """Loads and validates a plugin's manifest.json file."""
        manifest_path = plugin_dir / "manifest.json"
        if not manifest_path.exists():
            raise PluginLoadError(f"Manifest file not found in {plugin_dir}")

        async with aiofiles.open(manifest_path, "r", encoding="utf-8") as f:
            content = await f.read()
            return PluginManifest.parse_raw(content)

    def _manifest_to_metadata(self, manifest: PluginManifest) -> PluginMetadata:
        """Converts a PluginManifest to a PluginMetadata object."""
        return PluginMetadata(
            name=manifest.name,
            version=manifest.version,
            description=manifest.description,
            author=manifest.author,
            plugin_type=manifest.plugin_type,
            permissions=manifest.permissions,
            dependencies=manifest.dependencies,
            tags=set(manifest.tags),
            min_system_version=manifest.min_system_version,
            max_system_version=manifest.max_system_version,
            homepage=manifest.homepage,
            repository=manifest.repository,
            license=manifest.license,
        )

    def _create_plugin_instance(self, manifest: PluginManifest, plugin_dir: Path) -> IPlugin:
        """Dynamically imports and instantiates the main plugin class."""
        plugin_path_str = str(plugin_dir.resolve())
        if plugin_path_str not in sys.path:
            sys.path.insert(0, plugin_path_str)

        try:
            module = importlib.import_module(manifest.entry_point)
            importlib.reload(module)  # Ensure we get the latest version

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, IPlugin) and obj is not IPlugin:
                    return obj()

            raise PluginLoadError(
                f"No class inheriting from IPlugin found in '{manifest.entry_point}'.")
        finally:
            if plugin_path_str in sys.path:
                sys.path.remove(plugin_path_str)

    async def _validate_plugin(self, manifest: PluginManifest) -> None:
        """Validates a plugin's dependencies and system version compatibility."""
        # This is a placeholder for more advanced validation logic.
        # For example, checking against the current system version.
        pass

    async def _load_plugin_config(self, plugin_name: str) -> Dict:
        """Loads a plugin's configuration from config.json if it exists."""
        config_path = self.plugins_directory / plugin_name / "config.json"
        if not config_path.exists():
            return {}

        async with aiofiles.open(config_path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)
