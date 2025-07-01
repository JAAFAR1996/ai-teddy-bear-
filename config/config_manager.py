"""
Configuration Manager

This module provides a unified interface for loading, validating, and managing
configuration settings using the modular schema system.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from functools import lru_cache

from .schemas import SchemaLoader, SchemaValidator, ValidationError

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass


class ConfigManager:
    """
    Main configuration manager that provides a unified interface to
    load, validate, and access configuration settings.
    """
    
    def __init__(self, config_dir: Optional[str] = None, schema_dir: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
            schema_dir: Directory containing schema files
        """
        if config_dir is None:
            config_dir = Path(__file__).parent
        
        self.config_dir = Path(config_dir)
        self.schema_loader = SchemaLoader(schema_dir)
        self.schema_validator = SchemaValidator(schema_dir)
        
        self._config_cache = {}
        self._validation_cache = {}
        
    def load_config_file(self, config_file: str, validate: bool = True) -> Dict[str, Any]:
        """
        Load a configuration file with optional validation.
        
        Args:
            config_file: Name or path of the configuration file
            validate: Whether to validate the configuration
            
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If file not found or validation fails
        """
        # Resolve file path
        if not os.path.isabs(config_file):
            config_path = self.config_dir / config_file
        else:
            config_path = Path(config_file)
        
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            # Load the JSON file
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Loaded configuration from: {config_path}")
            
            # Validate if requested
            if validate:
                validation_result = self.validate_config(config)
                if not validation_result['overall_valid']:
                    error_msg = f"Configuration validation failed with {validation_result['total_errors']} errors"
                    logger.error(error_msg)
                    
                    # Log first few errors for debugging
                    for error in validation_result['validation_errors'][:5]:
                        logger.error(f"  - {error}")
                    
                    if validation_result['total_errors'] > 5:
                        logger.error(f"  ... and {validation_result['total_errors'] - 5} more errors")
                    
                    raise ValidationError(error_msg, validation_result['validation_errors'])
                
                logger.info("Configuration validation passed")
            
            return config
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in configuration file {config_path}: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except Exception as e:
            error_msg = f"Failed to load configuration from {config_path}: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
    
    def load_environment_config(self, environment: str = None, validate: bool = True) -> Dict[str, Any]:
        """
        Load configuration for a specific environment.
        
        Args:
            environment: Environment name (development, staging, production)
            validate: Whether to validate the configuration
            
        Returns:
            Environment-specific configuration
        """
        if environment is None:
            environment = os.getenv('ENVIRONMENT', 'development')
        
        # Try different config file patterns
        config_patterns = [
            f"{environment}.json",
            f"{environment}_config.json",
            f"environments/{environment}.json",
            f"environments/{environment}_config.json"
        ]
        
        for pattern in config_patterns:
            config_path = self.config_dir / pattern
            if config_path.exists():
                logger.info(f"Loading {environment} configuration from: {pattern}")
                return self.load_config_file(str(config_path), validate=validate)
        
        # Fallback to default config
        logger.warning(f"No specific config found for environment '{environment}', trying default")
        
        default_patterns = ['config.json', 'default.json', 'default_config.json']
        for pattern in default_patterns:
            config_path = self.config_dir / pattern
            if config_path.exists():
                logger.info(f"Loading default configuration from: {pattern}")
                return self.load_config_file(str(config_path), validate=validate)
        
        raise ConfigurationError(f"No configuration found for environment: {environment}")
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a configuration dictionary.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Validation result dictionary
        """
        config_id = str(hash(str(sorted(config.items()))))
        
        # Check cache first
        if config_id in self._validation_cache:
            logger.debug("Using cached validation result")
            return self._validation_cache[config_id]
        
        # Perform validation
        logger.info("Validating configuration")
        result = self.schema_validator.get_validation_summary(config)
        
        # Cache the result
        self._validation_cache[config_id] = result
        
        return result
    
    def validate_config_section(self, section_name: str, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a specific configuration section.
        
        Args:
            section_name: Name of the section (e.g., 'database', 'llm_settings')
            section_data: Section data to validate
            
        Returns:
            Validation result
        """
        try:
            is_valid, errors = self.schema_validator.validate_section(section_name, section_data)
            return {
                'valid': is_valid,
                'errors': errors,
                'section': section_name
            }
        except Exception as e:
            logger.error(f"Section validation failed: {e}")
            return {
                'valid': False,
                'errors': [str(e)],
                'section': section_name
            }
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get information about available schemas.
        
        Returns:
            Schema information dictionary
        """
        return self.schema_loader.get_schema_info()
    
    def generate_sample_config(self, sections: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a sample configuration with default values.
        
        Args:
            sections: List of sections to include (None = all)
            
        Returns:
            Sample configuration dictionary
        """
        logger.info("Generating sample configuration")
        
        # Get schema info
        schema_info = self.get_schema_info()
        
        sample_config = {}
        
        for schema_data in schema_info['available_schemas']:
            section_name = schema_data['properties'][0] if schema_data['properties'] else None
            
            if section_name and (sections is None or section_name in sections):
                # Load the schema to get default values
                try:
                    schema_file_name = schema_data['file'].replace('.json', '')
                    schema_content = self.schema_loader.load_individual_schema(schema_file_name)
                    
                    # Extract default values from schema
                    section_defaults = self._extract_defaults_from_schema(
                        schema_content['properties'][section_name]
                    )
                    
                    if section_defaults:
                        sample_config[section_name] = section_defaults
                        logger.debug(f"Added sample data for section: {section_name}")
                
                except Exception as e:
                    logger.warning(f"Could not generate sample for {section_name}: {e}")
        
        return sample_config
    
    def _extract_defaults_from_schema(self, schema_section: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract default values from a schema section.
        
        Args:
            schema_section: Schema section dictionary
            
        Returns:
            Dictionary with default values
        """
        defaults = {}
        
        properties = schema_section.get('properties', {})
        
        for prop_name, prop_schema in properties.items():
            if 'default' in prop_schema:
                defaults[prop_name] = prop_schema['default']
            elif prop_schema.get('type') == 'string':
                if 'enum' in prop_schema:
                    defaults[prop_name] = prop_schema['enum'][0]
                else:
                    defaults[prop_name] = "CHANGE_ME"
            elif prop_schema.get('type') == 'integer':
                defaults[prop_name] = prop_schema.get('minimum', 0)
            elif prop_schema.get('type') == 'number':
                defaults[prop_name] = prop_schema.get('minimum', 0.0)
            elif prop_schema.get('type') == 'boolean':
                defaults[prop_name] = False
            elif prop_schema.get('type') == 'array':
                defaults[prop_name] = []
            elif prop_schema.get('type') == 'object':
                # Recursively process nested objects
                nested_defaults = self._extract_defaults_from_schema(prop_schema)
                if nested_defaults:
                    defaults[prop_name] = nested_defaults
        
        return defaults
    
    def merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries.
        
        Args:
            base_config: Base configuration
            override_config: Configuration to override base with
            
        Returns:
            Merged configuration
        """
        def deep_merge(base: Dict, override: Dict) -> Dict:
            """Recursively merge dictionaries."""
            merged = base.copy()
            
            for key, value in override.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = deep_merge(merged[key], value)
                else:
                    merged[key] = value
            
            return merged
        
        return deep_merge(base_config, override_config)
    
    @lru_cache(maxsize=3)
    def get_master_schema(self) -> Dict[str, Any]:
        """
        Get the combined master schema (cached).
        
        Returns:
            Master schema dictionary
        """
        return self.schema_loader.combine_schemas()
    
    def export_config_template(self, output_file: str, sections: Optional[List[str]] = None) -> None:
        """
        Export a configuration template file.
        
        Args:
            output_file: Path to output file
            sections: Sections to include (None = all)
        """
        sample_config = self.generate_sample_config(sections)
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Configuration template exported to: {output_path}")


# Global configuration manager instance
_config_manager = None


def get_config_manager(config_dir: Optional[str] = None, schema_dir: Optional[str] = None) -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Args:
        config_dir: Configuration directory (only used on first call)
        schema_dir: Schema directory (only used on first call)
        
    Returns:
        ConfigManager instance
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(config_dir, schema_dir)
    
    return _config_manager


# Convenience functions
def load_config(config_file: str = None, environment: str = None, validate: bool = True) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        config_file: Specific config file to load
        environment: Environment to load config for
        validate: Whether to validate configuration
        
    Returns:
        Configuration dictionary
    """
    manager = get_config_manager()
    
    if config_file:
        return manager.load_config_file(config_file, validate=validate)
    else:
        return manager.load_environment_config(environment, validate=validate)


def validate_configuration(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to validate configuration.
    
    Args:
        config: Configuration to validate
        
    Returns:
        Validation result
    """
    manager = get_config_manager()
    return manager.validate_config(config) 