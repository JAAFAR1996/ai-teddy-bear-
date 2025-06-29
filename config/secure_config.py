"""
Secure Configuration Management - 2025 Standards
Uses environment variables and secure patterns
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, field
from cryptography.fernet import Fernet
import secrets
import logging

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Configuration validation error"""
    pass


@dataclass
class SecurityConfig:
    """Security configuration with proper validation"""
    encryption_key: str = field(repr=False)  # Hide from repr
    jwt_secret: str = field(repr=False)
    token_expiry: int = 3600
    refresh_token_expiry: int = 2592000
    password_hash_rounds: int = 12
    max_login_attempts: int = 5
    session_timeout: int = 1800
    
    def __post_init__(self):
        # Validate encryption key
        if len(self.encryption_key) < 32:
            raise ConfigurationError("Encryption key must be at least 32 characters")
        
        # Validate JWT secret
        if len(self.jwt_secret) < 32:
            raise ConfigurationError("JWT secret must be at least 32 characters")


@dataclass 
class DatabaseConfig:
    """Database configuration"""
    url: str
    redis_url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    def __post_init__(self):
        if not self.url:
            raise ConfigurationError("Database URL is required")


@dataclass
class AIServiceConfig:
    """AI Service configuration with secure API key handling"""
    openai_api_key: Optional[str] = field(default=None, repr=False)
    anthropic_api_key: Optional[str] = field(default=None, repr=False)
    google_gemini_api_key: Optional[str] = field(default=None, repr=False)
    default_provider: str = "openai"
    default_model: str = "gpt-4"
    max_tokens: int = 150
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    
    def get_active_providers(self) -> List[str]:
        """Get list of providers with valid API keys"""
        providers = []
        if self.openai_api_key:
            providers.append("openai")
        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.google_gemini_api_key:
            providers.append("google")
        return providers


@dataclass
class VoiceServiceConfig:
    """Voice service configuration"""
    elevenlabs_api_key: Optional[str] = field(default=None, repr=False)
    azure_speech_key: Optional[str] = field(default=None, repr=False)
    azure_speech_region: str = "eastus"
    default_engine: str = "azure"
    default_voice_id: str = "en-US-JennyNeural"
    voice_speed: float = 1.0
    voice_volume: float = 0.8
    sample_rate: int = 24000


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    sentry_dsn: Optional[str] = field(default=None, repr=False)
    enable_prometheus: bool = True
    enable_tracing: bool = True
    log_level: str = "INFO"
    log_format: str = "structured"
    enable_audit_log: bool = True


class SecureConfigManager:
    """
    Secure configuration manager following 2025 best practices
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent
        self._encryption_cache: Dict[str, Fernet] = {}
        
    def load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        
        # Security configuration
        security = SecurityConfig(
            encryption_key=self._get_or_generate_key("ENCRYPTION_KEY"),
            jwt_secret=self._get_or_generate_key("JWT_SECRET"),
            token_expiry=int(os.getenv("TOKEN_EXPIRY", "3600")),
            refresh_token_expiry=int(os.getenv("REFRESH_TOKEN_EXPIRY", "2592000")),
            password_hash_rounds=int(os.getenv("PASSWORD_HASH_ROUNDS", "12"))
        )
        
        # Database configuration
        database = DatabaseConfig(
            url=os.getenv("DATABASE_URL", "sqlite:///data/teddy.db"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
        
        # AI Services configuration
        ai_services = AIServiceConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            google_gemini_api_key=os.getenv("GOOGLE_GEMINI_API_KEY"),
            default_provider=os.getenv("AI_DEFAULT_PROVIDER", "openai"),
            default_model=os.getenv("AI_DEFAULT_MODEL", "gpt-4"),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "150")),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7"))
        )
        
        # Voice Services configuration
        voice_services = VoiceServiceConfig(
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
            azure_speech_key=os.getenv("AZURE_SPEECH_KEY"),
            azure_speech_region=os.getenv("AZURE_SPEECH_REGION", "eastus"),
            default_engine=os.getenv("VOICE_DEFAULT_ENGINE", "azure")
        )
        
        # Monitoring configuration
        monitoring = MonitoringConfig(
            sentry_dsn=os.getenv("SENTRY_DSN"),
            enable_prometheus=os.getenv("ENABLE_PROMETHEUS", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            enable_audit_log=os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"
        )
        
        return {
            "security": security,
            "database": database,
            "ai_services": ai_services,
            "voice_services": voice_services,
            "monitoring": monitoring,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug": os.getenv("DEBUG", "false").lower() == "true"
        }
    
    def _get_or_generate_key(self, env_var: str) -> str:
        """Get key from environment or generate a secure one"""
        key = os.getenv(env_var)
        if not key:
            # Generate secure key
            key = secrets.token_urlsafe(32)
            logger.warning(
                f"No {env_var} found in environment. Generated secure key. "
                f"Add {env_var}={key} to your environment variables."
            )
        return key
    
    def encrypt_value(self, value: str, key_name: str = "ENCRYPTION_KEY") -> str:
        """Encrypt a sensitive value"""
        if key_name not in self._encryption_cache:
            encryption_key = os.getenv(key_name)
            if not encryption_key:
                raise ConfigurationError(f"Encryption key {key_name} not found")
            
            # Convert to Fernet key format
            key_bytes = encryption_key.encode()[:32].ljust(32, b'0')
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            self._encryption_cache[key_name] = Fernet(fernet_key)
        
        return self._encryption_cache[key_name].encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str, key_name: str = "ENCRYPTION_KEY") -> str:
        """Decrypt a sensitive value"""
        if key_name not in self._encryption_cache:
            encryption_key = os.getenv(key_name)
            if not encryption_key:
                raise ConfigurationError(f"Encryption key {key_name} not found")
            
            key_bytes = encryption_key.encode()[:32].ljust(32, b'0')
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            self._encryption_cache[key_name] = Fernet(fernet_key)
        
        return self._encryption_cache[key_name].decrypt(encrypted_value.encode()).decode()
    
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate the loaded configuration"""
        try:
            # Check required AI provider
            ai_config = config["ai_services"]
            if not ai_config.get_active_providers():
                raise ConfigurationError("At least one AI provider API key is required")
            
            # Validate database URLs
            db_config = config["database"]
            if not db_config.url:
                raise ConfigurationError("Database URL is required")
            
            # Security validation
            security_config = config["security"]
            if len(security_config.encryption_key) < 32:
                raise ConfigurationError("Encryption key too short")
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise


# Global instance
_config_manager = SecureConfigManager()

def get_secure_config() -> Dict[str, Any]:
    """Get secure configuration from environment"""
    config = _config_manager.load_from_env()
    _config_manager.validate_configuration(config)
    return config 