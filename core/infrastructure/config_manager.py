from .config import AppConfig, VoiceSettings
from dotenv import load_dotenv
from jsonschema import validate, ValidationError
from typing import Dict, Any, Optional
from pathlib import Path
import os
import json
import logging
logger = logging.getLogger(__name__)


class ConfigManager:
    """Enhanced configuration manager with environment variable support"""

    def __init__(self, config_path: Optional[str] = None):
        self.project_root = Path(__file__).parent.parent.parent

        # Load environment variables
        load_dotenv()

        # Determine config path
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to config directory
            possible_paths = [
                self.project_root / "config" / "config.json",
                self.project_root / "config" / "default_config.json",
                Path("config/config.json"),
                Path("config/default_config.json"),
                Path("./config/config.json"),
                Path("./config/default_config.json"),
            ]

            for path in possible_paths:
                if path.exists():
                    self.config_path = path
                    logger.info(f"Found config file at: {path.absolute()}")
                    break

            if self.config_path is None:
                raise FileNotFoundError(
                    "No config file found in any expected location")

        # Load schema
        self.schema_path = self.config_path.parent / 'default_schema.json'
        self.schema = self._load_schema()

        # Load and process configuration
        self._config = self.load_config()

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema for validation"""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load schema: {e}")
            return {}

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            # Load base configuration
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            # Process environment variables
            config = self._process_env_vars(config)

            # Validate configuration
            if self.schema:
                self._validate_config(config)

            # Apply environment-specific overrides
            config = self._apply_environment_overrides(config)

            logger.info("Configuration loaded successfully")
            return config

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def _process_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Replace ${VAR} placeholders with environment variables"""
        def process_value(value):
            if isinstance(value, str):
                # Check for ${VAR} pattern
                if value.startswith('${') and value.endswith('}'):
                    var_name = value[2:-1]
                    env_value = os.environ.get(var_name)
                    if env_value:
                        return env_value
                    else:
                        logger.warning(
                            f"Environment variable {var_name} not found")
                        return ""
                return value
            elif isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_value(v) for v in value]
            return value

        return process_value(config)

    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration against schema"""
        try:
            validate(config, self.schema)
            logger.info("Configuration validation passed")
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise

    def _apply_environment_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment-specific overrides"""
        env = os.environ.get('ENVIRONMENT', 'development')

        # Environment-specific settings
        env_overrides = {
            'production': {
                'APPLICATION': {'DEBUG': False},
                'LOGGING_CONFIG': {'LOG_LEVEL': 'WARNING'},
                'DEVELOPMENT': {'ENABLE_DEBUG_MODE': False}
            },
            'staging': {
                'APPLICATION': {'DEBUG': False},
                'LOGGING_CONFIG': {'LOG_LEVEL': 'INFO'}
            },
            'development': {
                'APPLICATION': {'DEBUG': True},
                'LOGGING_CONFIG': {'LOG_LEVEL': 'DEBUG'}
            }
        }

        if env in env_overrides:
            overrides = env_overrides[env]
            config = self._deep_merge(config, overrides)

        return config

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()

    def reload(self):
        """Reload configuration"""
        self._config = self.load_config()

    def get_config(self) -> Dict[str, Any]:
        """إرجاع كل الإعدادات"""
        return self._config.copy()

    def load_app_config(path="config/config.json"):
        with open(path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
            # حمّل voice_settings من الدكت الفرعي الخاص به
            voice_settings = VoiceSettings(
                **config_dict.get("VOICE_SETTINGS", {}))
            # أنشئ AppConfig وأرسل له voice_settings
            app_config = AppConfig(
                environment=config_dict.get('APPLICATION', {}).get(
                    'ENVIRONMENT', 'development'),
                # باقي القيم ...
                voice_settings=voice_settings,
                # الحقول الأخرى ...
            )
        return app_config
