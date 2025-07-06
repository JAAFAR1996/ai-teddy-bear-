"""
Data models for the Vault integration.
"""
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class SecretType(Enum):
    """Types of secrets managed by Vault"""

    API_KEY = os.getenv("API_KEY")
    DATABASE_CREDENTIAL = "database_credential"
    ENCRYPTION_KEY = "encryption_key"
    JWT_SECRET = os.getenv("SECRET_KEY_1")
    CERTIFICATE = "certificate"
    OAUTH_TOKEN = os.getenv("ACCESS_TOKEN_1")
    WEBHOOK_SECRET = os.getenv("SECRET_KEY_2")
    CHILD_DEVICE_KEY = "child_device_key"
    PARENT_AUTH_TOKEN = os.getenv("ACCESS_TOKEN_2")


class VaultEngine(Enum):
    """Vault secret engines"""

    KV_V2 = "kv-v2"
    DATABASE = "database"
    PKI = "pki"
    TRANSIT = "transit"
    TOTP = "totp"
    CUBBYHOLE = "cubbyhole"


@dataclass
class SecretMetadata:
    """Metadata for secrets stored in Vault"""

    secret_type: SecretType
    path: str
    engine: VaultEngine
    ttl: Optional[int] = None
    max_ttl: Optional[int] = None
    renewable: bool = True
    tags: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_accessed: Optional[datetime] = None
    rotation_schedule: Optional[str] = None
