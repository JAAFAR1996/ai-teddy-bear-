"""
Plugin Architecture System
Extensible plugin system with dynamic loading, sandboxing, and lifecycle management
"""

import asyncio
import importlib
import inspect
import json
import logging
import os
import sys
import tempfile
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union
from urllib.parse import urlparse

import aiofiles
import docker
from pydantic import BaseModel, Field, validator
from typing_extensions import Protocol

logger = logging.getLogger(__name__)

T = TypeVar('T')


class PluginStatus(Enum):
    """Plugin status enumeration"""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UPDATING = "updating"
    UNINSTALLING = "uninstalling"


class PluginType(Enum):
    """Plugin type enumeration"""
    AI_SERVICE = "ai_service"
    AUDIO_PROCESSOR = "audio_processor"
    SECURITY_MODULE = "security_module"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    CUSTOM = "custom"


class PluginPermission(Enum):
    """Plugin permission levels"""
    READ_ONLY = "read_only"
    BASIC = "basic"
    ELEVATED = "elevated"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class PluginMetadata:
    """Plugin metadata"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    permissions: List[PluginPermission] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    min_system_version: str = "1.0.0"
    max_system_version: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PluginManifest(BaseModel):
    """Plugin manifest schema"""
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")
    plugin_type: PluginType = Field(..., description="Plugin type")
    permissions: List[PluginPermission] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    min_system_version: str = "1.0.0"
    max_system_version: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: Optional[str] = None
    entry_point: str = Field(..., description="Main entry point")
    config_schema: Optional[Dict[str, Any]] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Plugin name must be alphanumeric with underscores or hyphens')
        return v
    
    @validator('version')
    def validate_version(cls, v):
        # Basic semver validation
        parts = v.split('.')
        if len(parts) != 3:
            raise ValueError('Version must be in semver format (x.y.z)')
        return v


class IPlugin(ABC):
    """Base plugin interface"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin"""
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """Start plugin"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop plugin"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Perform health check"""
        pass


class IPluginManager(ABC):
    """Plugin manager interface"""
    
    @abstractmethod
    async def discover_plugins(self) -> List[PluginMetadata]:
        """Discover available plugins"""
        pass
    
    @abstractmethod
    async def load_plugin(self, plugin_path: str) -> IPlugin:
        """Load plugin from path"""
        pass
    
    @abstractmethod
    async def unload_plugin(self, plugin_name: str) -> None:
        """Unload plugin"""
        pass
    
    @abstractmethod
    async def get_plugin(self, plugin_name: str) -> Optional[IPlugin]:
        """Get loaded plugin"""
        pass
    
    @abstractmethod
    async def list_plugins(self) -> List[PluginMetadata]:
        """List all plugins"""
        pass


class PluginSandbox:
    """Plugin sandbox for security isolation"""
    
    def __init__(self, plugin_name: str, permissions: List[PluginPermission]):
        self.plugin_name = plugin_name
        self.permissions = set(permissions)
        self.allowed_modules = self._get_allowed_modules()
        self.allowed_functions = self._get_allowed_functions()
        self.resource_limits = self._get_resource_limits()
        self._original_import = __builtins__['__import__']
    
    def _get_allowed_modules(self) -> Set[str]:
        """Get allowed modules based on permissions"""
        base_modules = {
            'os', 'sys', 'json', 'datetime', 'logging', 'asyncio',
            'typing', 'pathlib', 'tempfile', 'uuid'
        }
        
        if PluginPermission.BASIC in self.permissions:
            base_modules.update({'requests', 'aiohttp', 'pydantic'})
        
        if PluginPermission.ELEVATED in self.permissions:
            base_modules.update({'redis', 'sqlalchemy', 'pandas'})
        
        if PluginPermission.ADMIN in self.permissions:
            base_modules.update({'docker', 'kubernetes', 'boto3'})
        
        return base_modules
    
    def _get_allowed_functions(self) -> Set[str]:
        """Get allowed functions based on permissions"""
        base_functions = {
            'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set',
            'max', 'min', 'sum', 'abs', 'round', 'sorted', 'reversed'
        }
        
        if PluginPermission.BASIC in self.permissions:
            base_functions.update({'open', 'read', 'write'})
        
        return base_functions
    
    def _get_resource_limits(self) -> Dict[str, Any]:
        """Get resource limits based on permissions"""
        limits = {
            'max_execution_time': 30,  # seconds
            'max_memory_mb': 100,
            'max_cpu_percent': 50,
            'max_network_requests': 10,
            'max_file_size_mb': 10
        }
        
        if PluginPermission.ELEVATED in self.permissions:
            limits.update({
                'max_execution_time': 300,
                'max_memory_mb': 500,
                'max_cpu_percent': 80,
                'max_network_requests': 100,
                'max_file_size_mb': 100
            })
        
        return limits
    
    def secure_import(self, name: str, *args, **kwargs):
        """Secure import function"""
        if name not in self.allowed_modules:
            raise SecurityError(f"Module {name} not allowed for plugin {self.plugin_name}")
        
        return self._original_import(name, *args, **kwargs)
    
    def secure_exec(self, code: str, globals_dict: Dict[str, Any], locals_dict: Dict[str, Any]):
        """Secure code execution"""
        # Check for dangerous operations
        dangerous_keywords = ['eval', 'exec', 'import', 'open', 'file', 'system', 'subprocess']
        for keyword in dangerous_keywords:
            if keyword in code.lower():
                raise SecurityError(f"Dangerous operation '{keyword}' not allowed")
        
        # Execute in restricted environment
        restricted_globals = {
            '__builtins__': {
                name: func for name, func in __builtins__.items()
                if name in self.allowed_functions
            }
        }
        restricted_globals.update(globals_dict)
        
        exec(code, restricted_globals, locals_dict)


class SecurityError(Exception):
    """Security violation exception"""
    pass


class PluginLoadError(Exception):
    """Plugin loading error"""
    pass


class PluginValidationError(Exception):
    """Plugin validation error"""
    pass


class PluginManager(IPluginManager):
    """Plugin manager implementation"""
    
    def __init__(self, plugins_directory: str = "plugins"):
        self.plugins_directory = Path(plugins_directory)
        self.plugins_directory.mkdir(exist_ok=True)
        
        self.loaded_plugins: Dict[str, IPlugin] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_sandboxes: Dict[str, PluginSandbox] = {}
        self.plugin_status: Dict[str, PluginStatus] = {}
        
        self._discovery_cache: Optional[List[PluginMetadata]] = None
        self._discovery_cache_time: Optional[datetime] = None
    
    async def discover_plugins(self) -> List[PluginMetadata]:
        """Discover available plugins"""
        # Check cache
        if (self._discovery_cache and self._discovery_cache_time and
            (datetime.now(timezone.utc) - self._discovery_cache_time).seconds < 300):
            return self._discovery_cache
        
        plugins = []
        
        for plugin_dir in self.plugins_directory.iterdir():
            if plugin_dir.is_dir():
                manifest_path = plugin_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        async with aiofiles.open(manifest_path, 'r') as f:
                            content = await f.read()
                            manifest_data = json.loads(content)
                            manifest = PluginManifest(**manifest_data)
                            
                            metadata = PluginMetadata(
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
                                license=manifest.license
                            )
                            
                            plugins.append(metadata)
                            
                    except Exception as e:
                        logger.error(f"❌ Error reading manifest for {plugin_dir.name}: {e}")
        
        # Update cache
        self._discovery_cache = plugins
        self._discovery_cache_time = datetime.now(timezone.utc)
        
        logger.info(f"🔍 Discovered {len(plugins)} plugins")
        return plugins
    
    async def load_plugin(self, plugin_path: str) -> IPlugin:
        """Load plugin from path"""
        plugin_dir = Path(plugin_path)
        manifest_path = plugin_dir / "manifest.json"
        
        if not manifest_path.exists():
            raise PluginLoadError(f"Manifest not found: {manifest_path}")
        
        # Load manifest
        async with aiofiles.open(manifest_path, 'r') as f:
            content = await f.read()
            manifest_data = json.loads(content)
            manifest = PluginManifest(**manifest_data)
        
        # Validate plugin
        await self._validate_plugin(manifest, plugin_dir)
        
        # Create sandbox
        sandbox = PluginSandbox(manifest.name, manifest.permissions)
        self.plugin_sandboxes[manifest.name] = sandbox
        
        # Load plugin module
        sys.path.insert(0, str(plugin_dir))
        try:
            module = importlib.import_module(manifest.entry_point)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, IPlugin) and 
                    obj != IPlugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                raise PluginLoadError(f"No plugin class found in {manifest.entry_point}")
            
            # Create plugin instance
            plugin = plugin_class()
            
            # Initialize plugin
            config = await self._load_plugin_config(manifest.name)
            await plugin.initialize(config)
            
            # Store plugin
            self.loaded_plugins[manifest.name] = plugin
            self.plugin_metadata[manifest.name] = PluginMetadata(
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
                license=manifest.license
            )
            self.plugin_status[manifest.name] = PluginStatus.LOADED
            
            logger.info(f"📦 Loaded plugin: {manifest.name} v{manifest.version}")
            return plugin
            
        except Exception as e:
            logger.error(f"❌ Failed to load plugin {manifest.name}: {e}")
            self.plugin_status[manifest.name] = PluginStatus.ERROR
            raise PluginLoadError(f"Failed to load plugin {manifest.name}: {e}")
        finally:
            sys.path.pop(0)
    
    async def unload_plugin(self, plugin_name: str) -> None:
        """Unload plugin"""
        if plugin_name not in self.loaded_plugins:
            return
        
        plugin = self.loaded_plugins[plugin_name]
        self.plugin_status[plugin_name] = PluginStatus.UNINSTALLING
        
        try:
            await plugin.stop()
            await plugin.cleanup()
            
            del self.loaded_plugins[plugin_name]
            del self.plugin_metadata[plugin_name]
            del self.plugin_sandboxes[plugin_name]
            del self.plugin_status[plugin_name]
            
            logger.info(f"🗑️ Unloaded plugin: {plugin_name}")
            
        except Exception as e:
            logger.error(f"❌ Error unloading plugin {plugin_name}: {e}")
            self.plugin_status[plugin_name] = PluginStatus.ERROR
    
    async def get_plugin(self, plugin_name: str) -> Optional[IPlugin]:
        """Get loaded plugin"""
        return self.loaded_plugins.get(plugin_name)
    
    async def list_plugins(self) -> List[PluginMetadata]:
        """List all plugins"""
        return list(self.plugin_metadata.values())
    
    async def start_plugin(self, plugin_name: str) -> None:
        """Start plugin"""
        if plugin_name not in self.loaded_plugins:
            raise ValueError(f"Plugin {plugin_name} not loaded")
        
        plugin = self.loaded_plugins[plugin_name]
        self.plugin_status[plugin_name] = PluginStatus.ACTIVE
        
        try:
            await plugin.start()
            logger.info(f"🚀 Started plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"❌ Failed to start plugin {plugin_name}: {e}")
            self.plugin_status[plugin_name] = PluginStatus.ERROR
    
    async def stop_plugin(self, plugin_name: str) -> None:
        """Stop plugin"""
        if plugin_name not in self.loaded_plugins:
            return
        
        plugin = self.loaded_plugins[plugin_name]
        self.plugin_status[plugin_name] = PluginStatus.INACTIVE
        
        try:
            await plugin.stop()
            logger.info(f"🛑 Stopped plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"❌ Error stopping plugin {plugin_name}: {e}")
    
    async def install_plugin(self, plugin_url: str) -> None:
        """Install plugin from URL"""
        # Download plugin
        plugin_zip = await self._download_plugin(plugin_url)
        
        # Extract plugin
        plugin_dir = await self._extract_plugin(plugin_zip)
        
        # Validate and load plugin
        await self.load_plugin(str(plugin_dir))
        
        logger.info(f"📦 Installed plugin from {plugin_url}")
    
    async def _validate_plugin(self, manifest: PluginManifest, plugin_dir: Path) -> None:
        """Validate plugin"""
        # Check system version compatibility
        current_version = "1.0.0"  # Get from system
        if manifest.min_system_version > current_version:
            raise PluginValidationError(
                f"Plugin requires system version {manifest.min_system_version}, "
                f"but current version is {current_version}"
            )
        
        # Check dependencies
        for dependency in manifest.dependencies:
            try:
                importlib.import_module(dependency)
            except ImportError:
                raise PluginValidationError(f"Missing dependency: {dependency}")
        
        # Check entry point exists
        entry_file = plugin_dir / f"{manifest.entry_point}.py"
        if not entry_file.exists():
            raise PluginValidationError(f"Entry point not found: {entry_file}")
    
    async def _load_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Load plugin configuration"""
        config_path = self.plugins_directory / plugin_name / "config.json"
        
        if config_path.exists():
            async with aiofiles.open(config_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
        
        return {}
    
    async def _download_plugin(self, plugin_url: str) -> Path:
        """Download plugin from URL"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(plugin_url) as response:
                if response.status != 200:
                    raise PluginLoadError(f"Failed to download plugin: {response.status}")
                
                # Save to temporary file
                temp_file = Path(tempfile.mktemp(suffix=".zip"))
                async with aiofiles.open(temp_file, 'wb') as f:
                    await f.write(await response.read())
                
                return temp_file
    
    async def _extract_plugin(self, plugin_zip: Path) -> Path:
        """Extract plugin archive"""
        plugin_name = plugin_zip.stem
        plugin_dir = self.plugins_directory / plugin_name
        
        with zipfile.ZipFile(plugin_zip, 'r') as zip_ref:
            zip_ref.extractall(plugin_dir)
        
        # Clean up temporary file
        plugin_zip.unlink()
        
        return plugin_dir


class PluginMarketplace:
    """Plugin marketplace for discovery and installation"""
    
    def __init__(self, marketplace_url: str = "https://plugins.teddybear.ai"):
        self.marketplace_url = marketplace_url
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour
    
    async def search_plugins(self, query: str, plugin_type: Optional[PluginType] = None) -> List[Dict[str, Any]]:
        """Search plugins in marketplace"""
        import aiohttp
        
        params = {"q": query}
        if plugin_type:
            params["type"] = plugin_type.value
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.marketplace_url}/search", params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"❌ Marketplace search failed: {response.status}")
                    return []
    
    async def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get plugin information from marketplace"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.marketplace_url}/plugin/{plugin_name}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
    
    async def get_download_url(self, plugin_name: str, version: str) -> Optional[str]:
        """Get plugin download URL"""
        plugin_info = await self.get_plugin_info(plugin_name)
        if plugin_info and version in plugin_info.get("versions", {}):
            return plugin_info["versions"][version]["download_url"]
        return None


# Factory functions
def create_plugin_manager(plugins_directory: str = "plugins") -> IPluginManager:
    """Create plugin manager"""
    return PluginManager(plugins_directory)


def create_plugin_marketplace(marketplace_url: str = "https://plugins.teddybear.ai") -> PluginMarketplace:
    """Create plugin marketplace"""
    return PluginMarketplace(marketplace_url)


# Utility functions
def create_plugin_manifest(
    name: str,
    version: str,
    description: str,
    author: str,
    plugin_type: PluginType,
    entry_point: str,
    **kwargs
) -> PluginManifest:
    """Create plugin manifest"""
    return PluginManifest(
        name=name,
        version=version,
        description=description,
        author=author,
        plugin_type=plugin_type,
        entry_point=entry_point,
        **kwargs
    )


def validate_plugin_permissions(plugin_name: str, permissions: List[PluginPermission]) -> bool:
    """Validate plugin permissions"""
    # Check for dangerous permissions
    dangerous_permissions = {PluginPermission.SYSTEM}
    
    for permission in permissions:
        if permission in dangerous_permissions:
            logger.warning(f"⚠️ Plugin {plugin_name} requests dangerous permission: {permission}")
            return False
    
    return True 