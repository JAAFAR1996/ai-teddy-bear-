"""
Core data models for the secrets management system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, SecretStr


class SecretProvider(Enum):
    """Supported secret providers"""

    HASHICORP_VAULT = auto()
    AWS_SECRETS_MANAGER = auto()
    AZURE_KEY_VAULT = auto()
    LOCAL_ENCRYPTED = auto()


class SecretType(Enum):
    """Types of secrets"""

    API_KEY = auto()
    PASSWORD = auto()
    TOKEN = auto()
    CERTIFICATE = auto()
    ENCRYPTION_KEY = auto()
    CONNECTION_STRING = auto()


@dataclass
class SecretMetadata:
    """Metadata for a secret"""

    name: str
    provider: SecretProvider
    secret_type: SecretType
    created_at: datetime
    updated_at: datetime
    rotation_interval_days: int = 90
    last_rotated_at: Optional[datetime] = None
    version: int = 1
    tags: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None
    allowed_environments: List[str] = field(
        default_factory=lambda: ["production"])
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


class SecretValue(BaseModel):
    """Secure container for secret values"""

    value: SecretStr
    metadata: SecretMetadata
    encrypted: bool = False

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None}
