"""
⚙️ Configuration Management - Enterprise Grade
Settings with environment variable support and validation
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pydantic import Field, validator
import yaml

logger = logging.getLogger(__name__)

# ================== CONFIGURATION MODELS ==================

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite+aiosqlite:///data/teddy_bear.db"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False

@dataclass
class RedisConfig:
    """Redis configuration"""
    url: Optional[str] = None
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    decode_responses: bool = True
    max_connections: int = 50

@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = field(default_factory=lambda: os.urandom(32).hex())
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    allowed_hosts: List[str] = field(default_factory=lambda: ["*"])
    enable_api_key: bool = True
    enable_rate_limiting: bool = True
    rate_limit_calls: int = 100
    rate_limit_period: int = 60

@dataclass
class AIConfig:
    """AI service configuration"""
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.8
    max_tokens: int = 200
    timeout: int = 30
    retry_attempts: int = 3
    cache_ttl: int = 3600

# ================== MAIN SETTINGS CLASS ==================

class Settings:
    """
    Enterprise application settings with validation
    Supports loading from:
    1. Environment variables (highest priority)
    2. .env file
    3. config.json
    4. config.yaml
    5. Default values (lowest priority)
    """
    
    def __init__(self):
        # Application
        self.app_name: str = os.getenv("APP_NAME", "AI Teddy Bear")
        self.app_version: str = os.getenv("APP_VERSION", "3.0.0")
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.debug_mode: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.enable_simulator: bool = os.getenv("ENABLE_SIMULATOR", "True").lower() == "true"
        
        # API Server
        self.api_host: str = os.getenv("API_HOST", "0.0.0.0")
        self.api_port: int = int(os.getenv("API_PORT", "8000"))
        self.api_workers: int = int(os.getenv("API_WORKERS", "4"))
        self.api_reload: bool = os.getenv("API_RELOAD", "False").lower() == "true"
        
        # Database
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "sqlite+aiosqlite:///data/teddy_bear.db"
        )
        self.database_pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
        self.database_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        
        # Redis
        self.redis_url: Optional[str] = os.getenv("REDIS_URL")
        self.redis_host: str = os.getenv("REDIS_HOST", "localhost")
        self.redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
        
        # Security
        self.secret_key: str = os.getenv("SECRET_KEY", os.urandom(32).hex())
        self.jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.cors_origins: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
        
        # AI Services
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        
        # Voice Services
        self.elevenlabs_api_key: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
        self.azure_speech_key: Optional[str] = os.getenv("AZURE_SPEECH_KEY")
        self.azure_speech_region: str = os.getenv("AZURE_SPEECH_REGION", "eastus")
        
        # Storage
        self.upload_dir: str = os.getenv("UPLOAD_DIR", "data/uploads")
        self.temp_dir: str = os.getenv("TEMP_DIR", "temp")
        self.max_upload_size: int = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))
        
        # Monitoring
        self.enable_metrics: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
        self.enable_tracing: bool = os.getenv("ENABLE_TRACING", "True").lower() == "true"
        self.jaeger_host: str = os.getenv("JAEGER_HOST", "localhost")
        self.jaeger_port: int = int(os.getenv("JAEGER_PORT", "6831"))
        
        # Feature Flags
        self.enable_voice_chat: bool = os.getenv("ENABLE_VOICE_CHAT", "True").lower() == "true"
        self.enable_emotion_analysis: bool = os.getenv("ENABLE_EMOTION_ANALYSIS", "True").lower() == "true"
        self.enable_content_moderation: bool = os.getenv("ENABLE_CONTENT_MODERATION", "True").lower() == "true"
        self.enable_analytics: bool = os.getenv("ENABLE_ANALYTICS", "True").lower() == "true"
    
    # ================== COMPUTED PROPERTIES ==================
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    @property
    def database_path(self) -> str:
        """Get database file path"""
        if self.database_url.startswith("sqlite"):
            return self.database_url.split("///")[-1]
        return ""
    
    @property
    def redis_enabled(self) -> bool:
        """Check if Redis is configured"""
        return bool(self.redis_url or self.redis_host)
    
    # ================== METHODS ==================
    
    async def load(self) -> None:
        """Load configuration from multiple sources"""
        # Try loading from config files
        await self._load_from_json()
        await self._load_from_yaml()
        
        # Validate configuration
        self._validate_config()
        
        # Log configuration (without secrets)
        self._log_configuration()
    
    async def _load_from_json(self) -> None:
        """Load configuration from JSON file"""
        config_files = [
            "config/config.json",
            "config/config.local.json",
            f"config/config.{self.environment}.json"
        ]
        
        for config_file in config_files:
            path = Path(config_file)
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                        
                    # Update settings with loaded data
                    for key, value in config_data.items():
                        if hasattr(self, key.lower()):
                            setattr(self, key.lower(), value)
                            
                    logger.info(f"Loaded configuration from {config_file}")
                    
                except Exception as e:
                    logger.error(f"Failed to load {config_file}: {str(e)}")
    
    async def _load_from_yaml(self) -> None:
        """Load configuration from YAML file"""
        config_files = [
            "config/config.yaml",
            "config/config.yml",
            f"config/config.{self.environment}.yaml"
        ]
        
        for config_file in config_files:
            path = Path(config_file)
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                        
                    # Update settings with loaded data
                    for key, value in config_data.items():
                        if hasattr(self, key.lower()):
                            setattr(self, key.lower(), value)
                            
                    logger.info(f"Loaded configuration from {config_file}")
                    
                except Exception as e:
                    logger.error(f"Failed to load {config_file}: {str(e)}")
    
    def _validate_config(self) -> None:
        """Validate configuration completeness"""
        # Check required API keys for production
        if self.is_production:
            if not self.openai_api_key and not self.anthropic_api_key:
                raise ValueError("At least one AI API key required in production")
            
            if not self.secret_key or self.secret_key == "changeme":
                raise ValueError("Secure secret key required in production")
        
        # Validate paths exist
        for path_attr in ["upload_dir", "temp_dir"]:
            path = Path(getattr(self, path_attr))
            path.mkdir(parents=True, exist_ok=True)
    
    def _log_configuration(self) -> None:
        """Log configuration (excluding sensitive data)"""
        safe_config = {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment,
            "debug_mode": self.debug_mode,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "database_url": self._mask_url(self.database_url),
            "redis_enabled": self.redis_enabled,
            "openai_configured": bool(self.openai_api_key),
            "elevenlabs_configured": bool(self.elevenlabs_api_key),
            "azure_speech_configured": bool(self.azure_speech_key),
        }
        
        logger.info("Configuration loaded", **safe_config)
    
    def _mask_url(self, url: str) -> str:
        """Mask sensitive parts of URLs"""
        if "@" in url:
            parts = url.split("@")
            return f"{parts[0].split('://')[0]}://***@{parts[1]}"
        return url
    
    def to_dict(self) -> Dict[str, Any]:
        """Export settings as dictionary"""
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_') and k not in [
                'openai_api_key', 'anthropic_api_key',
                'elevenlabs_api_key', 'azure_speech_key',
                'secret_key'
            ]
        }

# ================== FACTORY FUNCTIONS ==================

_settings_instance: Optional[Settings] = None

def get_settings() -> Settings:
    """Get cached settings instance"""
    global _settings_instance
    
    if _settings_instance is None:
        _settings_instance = Settings()
    
    return _settings_instance

def reset_settings() -> None:
    """Reset settings cache (mainly for testing)"""
    global _settings_instance
    _settings_instance = None

# ================== ENVIRONMENT HELPERS ==================

def is_production() -> bool:
    """Quick check if running in production"""
    return os.getenv("ENVIRONMENT", "development") == "production"

def is_development() -> bool:
    """Quick check if running in development"""
    return os.getenv("ENVIRONMENT", "development") == "development"

def require_env_var(name: str) -> str:
    """Require an environment variable to be set"""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Environment variable {name} is required but not set")
    return value 