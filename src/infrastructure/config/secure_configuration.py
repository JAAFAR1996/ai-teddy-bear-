"""
Secure Configuration Management System
Environment-specific configs with validation and audit logging
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import toml
import yaml
from cryptography.fernet import Fernet
from pydantic import BaseModel, Field, SecretStr, validator
from pydantic.types import confloat, conint

from ..security.secrets_manager import SecretsManager, SecretType

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Application environments"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ConfigSource(Enum):
    """Configuration sources"""

    FILE = auto()
    ENVIRONMENT = auto()
    SECRETS_MANAGER = auto()
    REMOTE = auto()


@dataclass
class ConfigAuditEntry:
    """Audit entry for configuration access"""

    timestamp: datetime
    config_key: str
    accessed_by: Optional[str]
    environment: Environment
    source: ConfigSource
    action: str  # read, write, delete
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "config_key": self.config_key,
            "accessed_by": self.accessed_by,
            "environment": self.environment.value,
            "source": self.source.name,
            "action": self.action,
            "old_value": str(self.old_value)[:100] if self.old_value else None,
            "new_value": str(self.new_value)[:100] if self.new_value else None,
        }


# Configuration Schemas with Pydantic


class DatabaseConfig(BaseModel):
    """Database configuration"""

    host: str = Field(..., description="Database host")
    port: conint(ge=1, le=65535) = Field(5432, description="Database port")
    name: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: SecretStr = Field(..., description="Database password")
    pool_size: conint(ge=1, le=100) = Field(10, description="Connection pool size")
    max_overflow: conint(ge=0, le=50) = Field(5, description="Max overflow connections")
    echo: bool = Field(False, description="Echo SQL statements")

    @validator("host")
    def validate_host(cls, v, values):
        """Validate database host"""
        if "production" in values.get("environment", "") and v == "localhost":
            raise ValueError("Cannot use localhost in production")
        return v


class RedisConfig(BaseModel):
    """Redis configuration"""

    host: str = Field("localhost", description="Redis host")
    port: conint(ge=1, le=65535) = Field(6379, description="Redis port")
    password: Optional[SecretStr] = Field(None, description="Redis password")
    db: conint(ge=0, le=15) = Field(0, description="Redis database number")
    decode_responses: bool = Field(True, description="Decode responses to strings")
    max_connections: conint(ge=1, le=1000) = Field(50, description="Max connections")
    socket_timeout: confloat(ge=0.1, le=60) = Field(5.0, description="Socket timeout")


class AIServiceConfig(BaseModel):
    """AI service configuration"""

    provider: str = Field(..., description="AI provider name")
    api_key: SecretStr = Field(..., description="API key")
    model_name: str = Field(..., description="Model name")
    temperature: confloat(ge=0, le=2) = Field(0.7, description="Temperature")
    max_tokens: conint(ge=1, le=32000) = Field(1000, description="Max tokens")
    timeout_seconds: confloat(ge=1, le=300) = Field(30.0, description="Timeout")
    retry_attempts: conint(ge=0, le=10) = Field(3, description="Retry attempts")

    @validator("provider")
    def validate_provider(cls, v):
        """Validate AI provider"""
        allowed = ["openai", "anthropic", "google", "azure", "local"]
        if v.lower() not in allowed:
            raise ValueError(f"Provider must be one of {allowed}")
        return v.lower()


class SecurityConfig(BaseModel):
    """Security configuration"""

    jwt_secret_key: SecretStr = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")
    jwt_expiration_minutes: conint(ge=1, le=1440) = Field(60, description="JWT expiration")
    encryption_key: SecretStr = Field(..., description="Encryption key")
    password_min_length: conint(ge=8, le=128) = Field(12, description="Min password length")
    password_require_uppercase: bool = Field(True, description="Require uppercase")
    password_require_lowercase: bool = Field(True, description="Require lowercase")
    password_require_numbers: bool = Field(True, description="Require numbers")
    password_require_special: bool = Field(True, description="Require special chars")
    max_login_attempts: conint(ge=1, le=10) = Field(5, description="Max login attempts")
    lockout_duration_minutes: conint(ge=1, le=1440) = Field(30, description="Lockout duration")
    session_timeout_minutes: conint(ge=1, le=1440) = Field(30, description="Session timeout")
    enable_2fa: bool = Field(True, description="Enable 2FA")


class ChildSafetyConfig(BaseModel):
    """Child safety configuration"""

    content_filter_level: str = Field("strict", description="Content filter level")
    age_verification_required: bool = Field(True, description="Require age verification")
    parental_consent_required: bool = Field(True, description="Require parental consent")
    data_retention_days: conint(ge=1, le=365) = Field(30, description="Data retention days")
    voice_recording_max_seconds: conint(ge=1, le=300) = Field(60, description="Max recording")
    inappropriate_content_threshold: confloat(ge=0, le=1) = Field(0.1, description="Content threshold")
    enable_content_moderation: bool = Field(True, description="Enable moderation")
    moderation_providers: List[str] = Field(["perspective", "azure", "custom"], description="Moderation providers")

    @validator("content_filter_level")
    def validate_filter_level(cls, v):
        """Validate content filter level"""
        allowed = ["strict", "moderate", "minimal"]
        if v not in allowed:
            raise ValueError(f"Filter level must be one of {allowed}")
        return v


class PerformanceConfig(BaseModel):
    """Performance configuration"""

    cache_ttl_seconds: conint(ge=1, le=86400) = Field(300, description="Cache TTL")
    request_timeout_seconds: confloat(ge=1, le=300) = Field(30.0, description="Request timeout")
    max_concurrent_requests: conint(ge=1, le=1000) = Field(100, description="Max concurrent")
    rate_limit_per_minute: conint(ge=1, le=10000) = Field(60, description="Rate limit")
    enable_caching: bool = Field(True, description="Enable caching")
    enable_compression: bool = Field(True, description="Enable compression")
    batch_size: conint(ge=1, le=1000) = Field(50, description="Batch size")
    worker_threads: conint(ge=1, le=100) = Field(10, description="Worker threads")


class LoggingConfig(BaseModel):
    """Logging configuration"""

    level: str = Field("INFO", description="Log level")
    format: str = Field("json", description="Log format")
    enable_structured_logging: bool = Field(True, description="Structured logging")
    log_sensitive_data: bool = Field(False, description="Log sensitive data")
    retention_days: conint(ge=1, le=365) = Field(30, description="Log retention")
    max_file_size_mb: conint(ge=1, le=1000) = Field(100, description="Max file size")
    backup_count: conint(ge=0, le=100) = Field(10, description="Backup count")

    @validator("level")
    def validate_level(cls, v):
        """Validate log level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()


class ApplicationConfig(BaseModel):
    """Main application configuration"""

    app_name: str = Field("AI Teddy Bear", description="Application name")
    version: str = Field("1.0.0", description="Application version")
    environment: Environment = Field(Environment.DEVELOPMENT, description="Environment")
    debug: bool = Field(False, description="Debug mode")
    timezone: str = Field("UTC", description="Timezone")

    # Sub-configurations
    database: DatabaseConfig
    redis: RedisConfig
    ai_services: Dict[str, AIServiceConfig]
    security: SecurityConfig
    child_safety: ChildSafetyConfig
    performance: PerformanceConfig
    logging: LoggingConfig

    # Feature flags
    features: Dict[str, bool] = Field(default_factory=dict, description="Feature flags")

    @validator("debug")
    def validate_debug(cls, v, values):
        """Ensure debug is False in production"""
        if values.get("environment") == Environment.PRODUCTION and v:
            raise ValueError("Debug cannot be True in production")
        return v

    class Config:
        use_enum_values = True


class IConfigLoader(ABC):
    """Interface for configuration loaders"""

    @abstractmethod
    async def load(self, key: str) -> Optional[Any]:
        """Load configuration value"""
        pass

    @abstractmethod
    async def save(self, key: str, value: Any) -> bool:
        """Save configuration value"""
        pass


class FileConfigLoader(IConfigLoader):
    """Load configuration from files"""

    def __init__(self, config_dir: Path, environment: Environment):
        self.config_dir = config_dir
        self.environment = environment
        self.fernet = None
        self._init_encryption()

    def _init_encryption(self):
        """Initialize encryption for sensitive configs"""
        key_file = self.config_dir / ".config_key"
        if key_file.exists():
            with open(key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            os.chmod(key_file, 0o600)

        self.fernet = Fernet(key)

    async def load(self, key: str) -> Optional[Any]:
        """Load configuration from file"""
        # Try environment-specific file first
        env_file = self.config_dir / f"{self.environment.value}.yaml"
        if env_file.exists():
            with open(env_file, "r") as f:
                config = yaml.safe_load(f)
                return self._get_nested_value(config, key)

        # Fall back to default
        default_file = self.config_dir / "default.yaml"
        if default_file.exists():
            with open(default_file, "r") as f:
                config = yaml.safe_load(f)
                return self._get_nested_value(config, key)

        return None

    async def save(self, key: str, value: Any) -> bool:
        """Save configuration to file"""
        env_file = self.config_dir / f"{self.environment.value}.yaml"

        if env_file.exists():
            with open(env_file, "r") as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}

        self._set_nested_value(config, key, value)

        with open(env_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        return True

    def _get_nested_value(self, config: Dict, key: str) -> Any:
        """Get nested value from config"""
        keys = key.split(".")
        value = config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None

        # Decrypt if encrypted
        if isinstance(value, str) and value.startswith("ENC:"):
            encrypted_data = value[4:]
            return self.fernet.decrypt(encrypted_data.encode()).decode()

        return value

    def _set_nested_value(self, config: Dict, key: str, value: Any):
        """Set nested value in config"""
        keys = key.split(".")
        current = config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Encrypt sensitive values
        if self._is_sensitive_key(key) and isinstance(value, str):
            encrypted = self.fernet.encrypt(value.encode()).decode()
            value = f"ENC:{encrypted}"

        current[keys[-1]] = value

    def _is_sensitive_key(self, key: str) -> bool:
        """Check if key contains sensitive data"""
        sensitive_patterns = ["password", "secret", "key", "token", "credential", "private", "auth"]
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in sensitive_patterns)


class EnvironmentConfigLoader(IConfigLoader):
    """Load configuration from environment variables"""

    def __init__(self, prefix: str = "TEDDY_"):
        self.prefix = prefix

    async def load(self, key: str) -> Optional[Any]:
        """Load from environment variable"""
        env_key = f"{self.prefix}{key.upper().replace('.', '_')}"
        value = os.environ.get(env_key)

        if value:
            # Try to parse JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        return None

    async def save(self, key: str, value: Any) -> bool:
        """Cannot save to environment variables"""
        return False


class SecureConfigurationManager:
    """Main configuration manager with validation and audit"""

    def __init__(
        self,
        environment: Environment,
        config_dir: Optional[Path] = None,
        secrets_manager: Optional[SecretsManager] = None,
    ):
        self.environment = environment
        self.config_dir = config_dir or Path("config")
        self.secrets_manager = secrets_manager
        self.loaders: List[IConfigLoader] = []
        self.cache: Dict[str, Any] = {}
        self.audit_log: List[ConfigAuditEntry] = []
        self._config: Optional[ApplicationConfig] = None

        self._init_loaders()

    def _init_loaders(self):
        """Initialize configuration loaders in priority order"""
        # Environment variables have highest priority
        self.loaders.append(EnvironmentConfigLoader())

        # File-based configuration
        self.loaders.append(FileConfigLoader(self.config_dir, self.environment))

        # Add more loaders as needed

    async def load_configuration(self) -> ApplicationConfig:
        """Load and validate complete configuration"""
        raw_config = {}

        # Load from all sources
        for section in [
            "database",
            "redis",
            "security",
            "child_safety",
            "performance",
            "logging",
            "ai_services",
            "features",
        ]:
            raw_config[section] = await self._load_section(section)

        # Add metadata
        raw_config["environment"] = self.environment
        raw_config["app_name"] = await self._load_value("app.name", "AI Teddy Bear")
        raw_config["version"] = await self._load_value("app.version", "1.0.0")
        raw_config["debug"] = await self._load_value("app.debug", False)
        raw_config["timezone"] = await self._load_value("app.timezone", "UTC")

        # Load secrets from secrets manager if available
        if self.secrets_manager:
            await self._load_secrets(raw_config)

        # Validate and create config object
        try:
            self._config = ApplicationConfig(**raw_config)

            # Audit successful load
            await self._audit("load_configuration", "system", "full_config", action="read", new_value="<config loaded>")

            return self._config
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise

    async def _load_section(self, section: str) -> Dict[str, Any]:
        """Load a configuration section"""
        result = {}

        # Load each key in the section
        for loader in self.loaders:
            section_data = await loader.load(section)
            if section_data and isinstance(section_data, dict):
                result.update(section_data)

        return result

    async def _load_value(self, key: str, default: Any = None) -> Any:
        """Load a single configuration value"""
        # Check cache first
        if key in self.cache:
            return self.cache[key]

        # Try each loader
        for loader in self.loaders:
            value = await loader.load(key)
            if value is not None:
                self.cache[key] = value
                await self._audit("load_value", "system", key, action="read")
                return value

        return default

    async def _load_secrets(self, config: Dict[str, Any]):
        """Load secrets from secrets manager"""
        # Database password
        if "database" in config:
            password = await self.secrets_manager.get_secret("database_password")
            if password:
                config["database"]["password"] = password

        # Redis password
        if "redis" in config:
            password = await self.secrets_manager.get_secret("redis_password")
            if password:
                config["redis"]["password"] = password

        # AI API keys
        if "ai_services" in config:
            for provider, service_config in config["ai_services"].items():
                api_key = await self.secrets_manager.get_secret(f"{provider}_api_key")
                if api_key:
                    service_config["api_key"] = api_key

        # Security keys
        if "security" in config:
            jwt_secret = await self.secrets_manager.get_secret("jwt_secret_key")
            if jwt_secret:
                config["security"]["jwt_secret_key"] = jwt_secret

            encryption_key = await self.secrets_manager.get_secret("encryption_key")
            if encryption_key:
                config["security"]["encryption_key"] = encryption_key

    async def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        if not self._config:
            await self.load_configuration()

        # Navigate nested structure
        keys = key.split(".")
        value = self._config

        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            elif isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default

        await self._audit("get", "system", key, action="read")
        return value

    async def set(self, key: str, value: Any, persist: bool = False) -> bool:
        """Set configuration value"""
        # Update in memory
        self.cache[key] = value

        # Persist if requested
        if persist:
            for loader in self.loaders:
                if await loader.save(key, value):
                    await self._audit("set", "system", key, action="write", new_value=value)
                    return True

        return False

    async def reload(self):
        """Reload configuration"""
        self.cache.clear()
        self._config = None
        await self.load_configuration()

    async def validate(self) -> List[str]:
        """Validate current configuration"""
        errors = []

        if not self._config:
            errors.append("Configuration not loaded")
            return errors

        # Custom validation rules
        if self.environment == Environment.PRODUCTION:
            # Production-specific validations
            if self._config.debug:
                errors.append("Debug mode enabled in production")

            if not self._config.security.enable_2fa:
                errors.append("2FA disabled in production")

            if self._config.database.host == "localhost":
                errors.append("Database using localhost in production")

            if self._config.logging.level == "DEBUG":
                errors.append("Debug logging enabled in production")

        return errors

    async def _audit(
        self, accessed_by: str, source: str, key: str, action: str, old_value: Any = None, new_value: Any = None
    ):
        """Add audit entry"""
        entry = ConfigAuditEntry(
            timestamp=datetime.now(timezone.utc),
            config_key=key,
            accessed_by=accessed_by,
            environment=self.environment,
            source=ConfigSource.FILE,  # Determine dynamically
            action=action,
            old_value=old_value,
            new_value=new_value,
        )

        self.audit_log.append(entry)

        # Log audit entry
        logger.info(f"Config audit: {entry.to_dict()}")

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        return [entry.to_dict() for entry in self.audit_log[-limit:]]

    @property
    def config(self) -> ApplicationConfig:
        """Get validated configuration object"""
        if not self._config:
            raise RuntimeError("Configuration not loaded")
        return self._config


# Factory function
async def create_configuration_manager(environment: Optional[str] = None) -> SecureConfigurationManager:
    """Create and initialize configuration manager"""
    # Determine environment
    env_str = environment or os.environ.get("TEDDY_ENV", "development")
    try:
        env = Environment(env_str)
    except ValueError:
        env = Environment.DEVELOPMENT

    # Create manager
    manager = SecureConfigurationManager(environment=env)

    # Load configuration
    await manager.load_configuration()

    # Validate
    errors = await manager.validate()
    if errors:
        logger.warning(f"Configuration validation warnings: {errors}")

    return manager
