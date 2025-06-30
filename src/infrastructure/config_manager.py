"""
Enhanced Configuration Manager for AI Teddy Bear Project
Supports JSON, YAML, environment variables, and advanced validation
"""

from .config import AppConfig, VoiceSettings
from dotenv import load_dotenv
from jsonschema import validate, ValidationError
from typing import Dict, Any, Optional, Union
from pathlib import Path
import os
import json
import yaml
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Enhanced configuration manager with comprehensive functionality"""

    def __init__(self, config_path: Optional[str] = None, base_dir: Optional[str] = None):
        self.project_root = Path(__file__).parent.parent.parent
        
        # Set base directory for config files
        self.base_dir = Path(base_dir) if base_dir else (self.project_root / "config")
        self.base_dir.mkdir(exist_ok=True)

        # Load environment variables
        load_dotenv()

        # Determine config path
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to config directory
            possible_paths = [
                self.base_dir / "config.json",
                self.base_dir / "default_config.json",
                self.base_dir / "config.yaml",
                self.base_dir / "config.yml",
                Path("config/config.json"),
                Path("config/default_config.json"),
            ]

            for path in possible_paths:
                if path.exists():
                    self.config_path = path
                    logger.info(f"Found config file at: {path.absolute()}")
                    break

            if not hasattr(self, 'config_path'):
                raise FileNotFoundError(
                    "No config file found in any expected location")

        # Load schema
        self.schema_path = self.base_dir / 'default_schema.json'
        self.schema = self._load_schema()

        # Load and process configuration
        self._config = self.load_config()

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema for validation"""
        try:
            if self.schema_path.exists():
                with open(self.schema_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load schema: {e}")
        return {}

    def load_config(self, config_name: Optional[str] = None, config_type: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file with support for multiple formats"""
        try:
            # Determine which config to load
            if config_name:
                config_path = self.base_dir / f"{config_name}.{config_type or 'json'}"
            else:
                config_path = self.config_path

            # Determine file type from extension
            file_type = config_type or config_path.suffix.lstrip('.')
            
            # Load base configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                if file_type in ['yaml', 'yml']:
                    config = yaml.safe_load(f)
                elif file_type == 'json':
                    config = json.load(f)
                else:
                    raise ValueError(f"Unsupported config type: {file_type}")

            # Process environment variables
            config = self._process_env_vars(config)

            # Validate configuration
            if self.schema:
                self._validate_config(config)

            # Apply environment-specific overrides
            config = self._apply_environment_overrides(config)

            logger.info(f"Configuration loaded successfully from {config_path}")
            return config

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def save_config(self, config: Dict[str, Any], config_name: str, config_type: str = 'json') -> None:
        """Save configuration to file"""
        try:
            # Determine file path
            file_path = self.base_dir / f"{config_name}.{config_type}"
            
            # Write configuration file
            with open(file_path, 'w', encoding='utf-8') as config_file:
                if config_type == 'json':
                    json.dump(config, config_file, indent=4, ensure_ascii=False)
                elif config_type in ['yaml', 'yml']:
                    yaml.safe_dump(config, config_file, default_flow_style=False, allow_unicode=True)
                else:
                    raise ValueError(f"Unsupported config type: {config_type}")
            
            logger.info(f"Configuration saved to {file_path}")
        
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise

    def merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configuration dictionaries with deep merge"""
        return self._deep_merge(base_config.copy(), override_config)

    def _process_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Replace ${VAR} placeholders and $VAR references with environment variables"""
        def process_value(value) -> Any:
            if isinstance(value, str):
                # Handle ${VAR} pattern
                if value.startswith('${') and value.endswith('}'):
                    var_name = value[2:-1]
                    env_value = os.environ.get(var_name)
                    if env_value is not None:
                        return env_value
                    else:
                        logger.warning(f"Environment variable {var_name} not found")
                        return ""
                # Handle $VAR pattern  
                elif value.startswith('$') and len(value) > 1:
                    var_name = value[1:]
                    env_value = os.environ.get(var_name)
                    if env_value is not None:
                        return env_value
                    else:
                        logger.warning(f"Environment variable {var_name} not found")
                        return value
                return value
            elif isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_value(v) for v in value]
            return value

        return process_value(config)

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration against schema"""
        try:
            validate(config, self.schema)
            logger.info("Configuration validation passed")
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise

    def validate_config(self, config: Dict[str, Any], schema_name: str = 'default_schema') -> bool:
        """Validate configuration against a specific schema"""
        try:
            # Load JSON schema
            schema_path = self.base_dir / f"{schema_name}.json"
            
            if not schema_path.exists():
                logger.warning(f"Schema file not found: {schema_path}")
                return False
                
            with open(schema_path, 'r') as schema_file:
                schema = json.load(schema_file)
            
            # Validate using jsonschema
            validate(instance=config, schema=schema)
            return True
        
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False

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

    def reload(self) -> None:
        """Reload configuration"""
        self._config = self.load_config()

    def get_config(self) -> Dict[str, Any]:
        """إرجاع كل الإعدادات"""
        return self._config.copy()

    @staticmethod
    def load_app_config(path: str = "config/config.json") -> AppConfig:
        """Load AppConfig object from configuration file"""
        with open(path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
            # حمّل voice_settings من الدكت الفرعي الخاص به
            voice_settings = VoiceSettings(
                **config_dict.get("VOICE_SETTINGS", {}))
            # أنشئ AppConfig وأرسل له voice_settings
            app_config = AppConfig(
                environment=config_dict.get('APPLICATION', {}).get(
                    'ENVIRONMENT', 'development'),
                voice_settings=voice_settings,
                # Add other fields as needed
            )
        return app_config

    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create backup of current configuration"""
        from datetime import datetime
        
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"config_backup_{timestamp}"
        
        backup_path = self.base_dir / f"{backup_name}.json"
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Configuration backup created: {backup_path}")
            return str(backup_path)
        
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise

    def restore_from_backup(self, backup_path: str) -> None:
        """Restore configuration from backup"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_config = json.load(f)
            
            # Validate backup if schema exists
            if self.schema:
                validate(backup_config, self.schema)
            
            self._config = backup_config
            logger.info(f"Configuration restored from backup: {backup_path}")
        
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            raise


def main():
    """CLI for configuration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Teddy Bear Configuration Manager')
    parser.add_argument('--load', help='Load configuration file')
    parser.add_argument('--save', help='Save configuration')
    parser.add_argument('--type', choices=['json', 'yaml'], default='json', 
                        help='Configuration file type')
    parser.add_argument('--validate', help='Validate configuration file')
    parser.add_argument('--backup', action='store_true', help='Create configuration backup')
    
    args = parser.parse_args()
    
    try:
        config_manager = ConfigManager()
        
        if args.load:
            config = config_manager.load_config(args.load, args.type)
            print(json.dumps(config, indent=2, ensure_ascii=False))
        
        if args.save:
            # Example configuration (replace with actual configuration)
            sample_config = {
                'app_name': 'AI Teddy Bear',
                'version': '2025.1.0',
                'debug': False,
                'environment': '${ENVIRONMENT}'
            }
            config_manager.save_config(sample_config, args.save, args.type)
        
        if args.validate:
            config = config_manager.load_config(args.validate, args.type)
            is_valid = config_manager.validate_config(config)
            print(f"Configuration validation: {'PASSED' if is_valid else 'FAILED'}")
        
        if args.backup:
            backup_path = config_manager.create_backup()
            print(f"Backup created: {backup_path}")
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()