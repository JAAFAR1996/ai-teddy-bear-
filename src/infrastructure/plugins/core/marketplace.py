"""
Plugin marketplace for discovering and installing plugins.
"""
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from .enums import PluginType

logger = logging.getLogger(__name__)


class PluginMarketplace:
    """
    Provides an interface to a remote plugin marketplace for searching,
    viewing, and retrieving download URLs for plugins.
    """

    def __init__(self, marketplace_url: str = "https://plugins.teddybear.ai/api/v1"):
        self.marketplace_url = marketplace_url
        self.session = aiohttp.ClientSession()

    async def search_plugins(
        self, query: str, plugin_type: Optional[PluginType] = None
    ) -> List[Dict[str, Any]]:
        """Searches for plugins in the marketplace."""
        params = {"q": query}
        if plugin_type:
            params["type"] = plugin_type.value

        try:
            async with self.session.get(f"{self.marketplace_url}/search", params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Marketplace search failed: {e}", exc_info=True)
            return []

    async def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves detailed information about a specific plugin from the marketplace."""
        try:
            async with self.session.get(f"{self.marketplace_url}/plugins/{plugin_name}") as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(
                f"Failed to get plugin info for '{plugin_name}': {e}", exc_info=True)
            return None

    async def get_download_url(self, plugin_name: str, version: str) -> Optional[str]:
        """Gets the download URL for a specific version of a plugin."""
        try:
            plugin_info = await self.get_plugin_info(plugin_name)
            if plugin_info:
                for v_info in plugin_info.get("versions", []):
                    if v_info.get("version") == version:
                        return v_info.get("download_url")
            return None
        except Exception as e:
            logger.error(
                f"Failed to get download URL for {plugin_name} v{version}: {e}", exc_info=True)
            return None

    async def close(self):
        """Closes the aiohttp session."""
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
