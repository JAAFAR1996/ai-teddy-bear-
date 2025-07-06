"""
Configuration for the secrets management system.
"""
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel

from .models import SecretProvider


class SecretConfig(BaseModel):
    """Configuration for secrets management"""

    default_provider: SecretProvider = SecretProvider.HASHICORP_VAULT
    auto_rotation_enabled: bool = True
    rotation_check_interval_hours: int = 24
    encryption_key_path: Optional[Path] = None
    vault_config: Optional[Dict[str, Any]] = None
    aws_config: Optional[Dict[str, Any]] = None
    azure_config: Optional[Dict[str, Any]] = None
    cache_ttl_seconds: int = 300
    audit_enabled: bool = True
    secure_delete_enabled: bool = True
