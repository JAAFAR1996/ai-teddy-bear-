"""
Data models for plugin metadata and manifests.
"""
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, validator

from .enums import PluginPermission, PluginType


@dataclass
class PluginMetadata:
    """Represents the metadata of a discovered or loaded plugin."""
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
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))


class PluginManifest(BaseModel):
    """
    Defines the schema for the plugin's manifest.json file,
    used for validation and metadata extraction.
    """
    name: str = Field(..., description="Unique name of the plugin.")
    version: str = Field(..., description="Plugin version, following SemVer.")
    description: str = Field(...,
                             description="A brief description of what the plugin does.")
    author: str = Field(...,
                        description="Name of the plugin author or organization.")
    plugin_type: PluginType = Field(...,
                                    description="The functional category of the plugin.")
    entry_point: str = Field(
        ..., description="The main module to load for the plugin (e.g., 'main').")
    permissions: List[PluginPermission] = Field(
        default_factory=list, description="List of permissions required by the plugin.")
    dependencies: List[str] = Field(
        default_factory=list, description="List of external Python package dependencies.")
    tags: List[str] = Field(default_factory=list,
                            description="Tags for categorization and search.")
    min_system_version: str = Field(
        "1.0.0", description="The minimum system version required to run this plugin.")
    max_system_version: Optional[str] = Field(
        None, description="The maximum compatible system version.")
    homepage: Optional[str] = Field(
        None, description="URL to the plugin's homepage.")
    repository: Optional[str] = Field(
        None, description="URL to the source code repository.")
    license: Optional[str] = Field(
        None, description="The license under which the plugin is distributed.")
    config_schema: Optional[Dict[str, Any]] = Field(
        None, description="A JSON schema for the plugin's configuration.")

    @validator("name")
    def validate_name_format(cls, v):
        if not re.match(r"^[a-zA-Z0-9_.-]+$", v):
            raise ValueError(
                "Plugin name must contain only alphanumeric characters, underscores, hyphens, or dots.")
        return v

    @validator("version")
    def validate_version_format(cls, v):
        # Basic Semantic Versioning check
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError(
                "Version must be in the format X.Y.Z (e.g., 1.0.0).")
        return v
