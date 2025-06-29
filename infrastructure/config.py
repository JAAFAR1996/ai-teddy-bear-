"""
🧸 AI Teddy Bear - Configuration Management
إدارة التكوين والإعدادات بمعايير 2025
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import lru_cache
from pydantic import Field, SecretStr, validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
from enum import Enum


class Environment(str, Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    and validation
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="TEDDY_",
        case_sensitive=False,
        validate_default=True,
        extra="forbid"
    )
    
    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )
    
    # Application
    app_name: str = Field(default="AI Teddy Bear", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=4, ge=1, description="Number of workers")
    
    # Database
    database_url: str = Field(
        default="sqlite:///./teddy_bear.db",
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=10, ge=1)
    database_pool_timeout: int = Field(default=30, ge=1)
    
    # Redis
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection URL for caching/queuing"
    )
    redis_ttl: int = Field(default=3600, ge=60)
    
    # Security
    secret_key: SecretStr = Field(
        default=SecretStr("change-this-in-production"),
        description="Secret key for encryption"
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_minutes: int = Field(default=60, ge=1)
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    # API Keys (loaded from secure storage)
    openai_api_key: Optional[SecretStr] = Field(
        default=None,
        description="OpenAI API key"
    )
    hume_api_key: Optional[SecretStr] = Field(
        default=None,
        description="Hume AI API key"
    )
    elevenlabs_api_key: Optional[SecretStr] = Field(
        default=None,
        description="ElevenLabs API key"
    )
    azure_speech_key: Optional[SecretStr] = Field(
        default=None,
        description="Azure Speech Services key"
    )
    azure_speech_region: str = Field(
        default="eastus",
        description="Azure Speech region"
    )
    
    # Audio Processing
    audio_sample_rate: int = Field(default=16000, ge=8000)
    audio_chunk_size: int = Field(default=1024, ge=256)
    audio_format: str = Field(default="mp3")
    max_audio_duration_seconds: int = Field(default=60, ge=5)
    
    # AI Configuration
    ai_model: str = Field(default="gpt-4o-mini", description="OpenAI model")
    ai_temperature: float = Field(default=0.8, ge=0.0, le=2.0)
    ai_max_tokens: int = Field(default=150, ge=10)
    ai_timeout_seconds: int = Field(default=30, ge=5)
    
    # Voice Settings
    tts_voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM", description="ElevenLabs voice ID")
    tts_language: str = Field(default="ar", description="Default TTS language")
    stt_language: str = Field(default="ar", description="Default STT language")
    whisper_model: str = Field(default="base", description="Whisper model size")
    
    # WebSocket
    ws_heartbeat_interval: int = Field(default=30, ge=5)
    ws_max_connections: int = Field(default=1000, ge=10)
    ws_message_queue_size: int = Field(default=100, ge=10)
    
    # Monitoring
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090, ge=1, le=65535)
    log_level: LogLevel = Field(default=LogLevel.INFO)
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Storage
    upload_path: Path = Field(default=Path("./uploads"))
    cache_path: Path = Field(default=Path("./cache"))
    max_file_size_mb: int = Field(default=10, ge=1)
    
    # Feature Flags
    enable_emotion_analysis: bool = Field(default=True)
    enable_voice_games: bool = Field(default=True)
    enable_parent_dashboard: bool = Field(default=True)
    enable_offline_mode: bool = Field(default=False)
    
    @validator("environment", pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            v = v.lower()
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v, values):
        if values.get("environment") == Environment.PRODUCTION:
            if v.startswith("sqlite"):
                raise ValueError("SQLite not recommended for production")
        return v
    
    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        if values.get("environment") == Environment.PRODUCTION:
            if v.get_secret_value() == "change-this-in-production":
                raise ValueError("Must change secret key in production")
        return v
    
    @validator("upload_path", "cache_path")
    def create_directories(cls, v):
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    def load_api_keys_from_file(self, config_file: Path):
        """Load API keys from secure config file"""
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    api_keys = config_data.get("API_KEYS", {})
                    
                    if api_keys.get("OPENAI_API_KEY"):
                        self.openai_api_key = SecretStr(api_keys["OPENAI_API_KEY"])
                    if api_keys.get("HUME_API_KEY"):
                        self.hume_api_key = SecretStr(api_keys["HUME_API_KEY"])
                    if api_keys.get("ELEVENLABS_API_KEY"):
                        self.elevenlabs_api_key = SecretStr(api_keys["ELEVENLABS_API_KEY"])
                    if api_keys.get("AZURE_SPEECH_KEY"):
                        self.azure_speech_key = SecretStr(api_keys["AZURE_SPEECH_KEY"])
                        
                logging.info(f"API keys loaded from {config_file}")
        except Exception as e:
            logging.error(f"Failed to load API keys: {e}")
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "pool_timeout": self.database_pool_timeout,
            "echo": self.debug,
        }
    
    def get_redis_config(self) -> Optional[Dict[str, Any]]:
        """Get Redis configuration"""
        if self.redis_url:
            return {
                "url": self.redis_url,
                "decode_responses": True,
                "max_connections": 50,
            }
        return None
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration"""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
        }
    
    def configure_logging(self):
        """Configure application logging"""
        logging.basicConfig(
            level=self.log_level.value,
            format=self.log_format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f"logs/{self.environment.value}.log")
            ]
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings = Settings()
    
    # Load API keys from config file if in development
    if settings.environment == Environment.DEVELOPMENT:
        config_file = Path("config/config.json")
        settings.load_api_keys_from_file(config_file)
    
    # Configure logging
    settings.configure_logging()
    
    return settings


# Export settings instance
settings = get_settings() 