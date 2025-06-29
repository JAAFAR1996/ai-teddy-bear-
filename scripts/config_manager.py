import os
import json
import yaml
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigurationManager:
    """
    Comprehensive configuration management utility
    """
    def __init__(self, base_dir: str = None):
        """
        Initialize configuration manager
        
        :param base_dir: Base directory for configuration files
        """
        self._logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # Set base directory
        self._base_dir = base_dir or os.path.join(os.getcwd(), 'config')
        
        # Ensure base directory exists
        os.makedirs(self._base_dir, exist_ok=True)
        
        # Load environment variables
        load_dotenv()

    def load_config(self, config_name: str, config_type: str = 'json') -> Dict[str, Any]:
        """
        Load configuration from file
        
        :param config_name: Name of the configuration file (without extension)
        :param config_type: Type of configuration file (json or yaml)
        :return: Configuration dictionary
        """
        try:
            # Determine file path
            file_path = os.path.join(
                self._base_dir, 
                f"{config_name}.{config_type}"
            )
            
            # Read configuration file
            with open(file_path, 'r') as config_file:
                if config_type == 'json':
                    config = json.load(config_file)
                elif config_type in ['yaml', 'yml']:
                    config = yaml.safe_load(config_file)
                else:
                    raise ValueError(f"Unsupported config type: {config_type}")
            
            # Resolve environment variables
            config = self._resolve_env_vars(config)
            
            return config
        
        except FileNotFoundError:
            self._logger.warning(f"Configuration file not found: {file_path}")
            return {}
        except Exception as e:
            self._logger.error(f"Error loading configuration: {e}")
            return {}

    def _resolve_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve environment variables in configuration
        
        :param config: Configuration dictionary
        :return: Configuration with resolved environment variables
        """
        def _resolve(value):
            if isinstance(value, str):
                # Check if value is an environment variable reference
                if value.startswith('$'):
                    env_var = value[1:]
                    return os.getenv(env_var, value)
            elif isinstance(value, dict):
                return {k: _resolve(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_resolve(item) for item in value]
            return value
        
        return _resolve(config)

    def save_config(
        self, 
        config: Dict[str, Any], 
        config_name: str, 
        config_type: str = 'json'
    ):
        """
        Save configuration to file
        
        :param config: Configuration dictionary
        :param config_name: Name of the configuration file
        :param config_type: Type of configuration file (json or yaml)
        """
        try:
            # Determine file path
            file_path = os.path.join(
                self._base_dir, 
                f"{config_name}.{config_type}"
            )
            
            # Write configuration file
            with open(file_path, 'w') as config_file:
                if config_type == 'json':
                    json.dump(config, config_file, indent=4)
                elif config_type in ['yaml', 'yml']:
                    yaml.safe_dump(config, config_file, default_flow_style=False)
                else:
                    raise ValueError(f"Unsupported config type: {config_type}")
            
            self._logger.info(f"Configuration saved to {file_path}")
        
        except Exception as e:
            self._logger.error(f"Error saving configuration: {e}")

    def merge_configs(
        self, 
        base_config: Dict[str, Any], 
        override_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries
        
        :param base_config: Base configuration
        :param override_config: Configuration to override base
        :return: Merged configuration
        """
        def _deep_merge(base, override):
            for key, value in override.items():
                if isinstance(value, dict):
                    base[key] = _deep_merge(base.get(key, {}), value)
                else:
                    base[key] = value
            return base
        
        return _deep_merge(base_config.copy(), override_config)

    def validate_config(
        self, 
        config: Dict[str, Any], 
        schema_name: str = 'default_schema'
    ) -> bool:
        """
        Validate configuration against a schema
        
        :param config: Configuration to validate
        :param schema_name: Name of the schema file
        :return: Whether configuration is valid
        """
        try:
            # Load JSON schema
            schema_path = os.path.join(
                self._base_dir, 
                f"{schema_name}_schema.json"
            )
            
            with open(schema_path, 'r') as schema_file:
                schema = json.load(schema_file)
            
            # Use jsonschema for validation
            import jsonschema
            jsonschema.validate(instance=config, schema=schema)
            
            return True
        
        except FileNotFoundError:
            self._logger.warning(f"Schema file not found: {schema_path}")
            return False
        except jsonschema.exceptions.ValidationError as e:
            self._logger.error(f"Configuration validation failed: {e}")
            return False
        except Exception as e:
            self._logger.error(f"Error validating configuration: {e}")
            return False

def main():
    """
    CLI for configuration management
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Teddy Bear Configuration Manager')
    parser.add_argument('--load', help='Load configuration file')
    parser.add_argument('--save', help='Save configuration')
    parser.add_argument('--type', choices=['json', 'yaml'], default='json', 
                        help='Configuration file type')
    
    args = parser.parse_args()
    
    config_manager = ConfigurationManager()
    
    if args.load:
        config = config_manager.load_config(args.load, args.type)
        print(json.dumps(config, indent=2))
    
    if args.save:
        # Example configuration (replace with actual configuration)
        sample_config = {
            'app_name': 'AI Teddy Bear',
            'version': '0.1.0',
            'debug': False
        }
        config_manager.save_config(sample_config, args.save, args.type)

if __name__ == "__main__":
    main()
