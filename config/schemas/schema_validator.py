"""
Schema Validator Module

This module provides configuration validation functionality using the modular schemas.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft7Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    jsonschema = None
    Draft7Validator = None

from .schema_loader import SchemaLoader


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class SchemaValidator:
    """
    Validates configuration data against JSON schemas.
    
    This class provides:
    - Full configuration validation
    - Section-specific validation
    - Detailed error reporting
    - Custom validation rules
    """
    
    def __init__(self, schema_dir: Optional[str] = None):
        """
        Initialize the schema validator.
        
        Args:
            schema_dir: Directory containing schema files
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.warning(
                "jsonschema library not available. "
                "Install with: pip install jsonschema"
            )
        
        self.schema_loader = SchemaLoader(schema_dir)
        self._cached_master_schema = None
        
    def _get_master_schema(self) -> Dict[str, Any]:
        """Get the master schema, with caching."""
        if self._cached_master_schema is None:
            self._cached_master_schema = self.schema_loader.combine_schemas()
        return self._cached_master_schema
    
    def validate_complete_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a complete configuration against the master schema.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.error("Cannot validate: jsonschema library not available")
            return False, ["jsonschema library not installed"]
        
        try:
            master_schema = self._get_master_schema()
            validator = Draft7Validator(master_schema)
            
            errors = []
            for error in validator.iter_errors(config):
                error_msg = self._format_validation_error(error)
                errors.append(error_msg)
                logger.debug(f"Validation error: {error_msg}")
            
            is_valid = len(errors) == 0
            
            if is_valid:
                logger.info("Configuration validation successful")
            else:
                logger.warning(f"Configuration validation failed with {len(errors)} errors")
            
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"Validation failed with exception: {e}")
            return False, [f"Validation exception: {str(e)}"]
    
    def validate_section(self, section_name: str, section_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a specific configuration section.
        
        Args:
            section_name: Name of the section to validate (e.g., 'database', 'llm_settings')
            section_data: Section data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.error("Cannot validate: jsonschema library not available")
            return False, ["jsonschema library not installed"]
        
        try:
            # Load the specific schema for this section
            schema_content = self.schema_loader.load_individual_schema(section_name)
            validator = Draft7Validator(schema_content)
            
            # Wrap section data in the expected structure
            wrapped_data = {section_name.upper(): section_data}
            
            errors = []
            for error in validator.iter_errors(wrapped_data):
                error_msg = self._format_validation_error(error)
                errors.append(error_msg)
                logger.debug(f"Section validation error: {error_msg}")
            
            is_valid = len(errors) == 0
            
            if is_valid:
                logger.info(f"Section '{section_name}' validation successful")
            else:
                logger.warning(f"Section '{section_name}' validation failed with {len(errors)} errors")
            
            return is_valid, errors
            
        except FileNotFoundError:
            error_msg = f"Schema file not found for section: {section_name}"
            logger.error(error_msg)
            return False, [error_msg]
        except Exception as e:
            error_msg = f"Section validation failed with exception: {str(e)}"
            logger.error(error_msg)
            return False, [error_msg]
    
    def _format_validation_error(self, error) -> str:
        """
        Format a jsonschema validation error into a readable message.
        
        Args:
            error: jsonschema ValidationError object
            
        Returns:
            Formatted error message
        """
        path = " -> ".join(str(x) for x in error.absolute_path)
        if path:
            return f"Error at '{path}': {error.message}"
        else:
            return f"Error: {error.message}"
    
    def validate_required_sections(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if all required configuration sections are present.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (all_present, list_of_missing_sections)
        """
        try:
            master_schema = self._get_master_schema()
            required_sections = master_schema.get("required", [])
            
            missing_sections = []
            for section in required_sections:
                if section not in config:
                    missing_sections.append(section)
            
            all_present = len(missing_sections) == 0
            
            if all_present:
                logger.info("All required sections present")
            else:
                logger.warning(f"Missing required sections: {missing_sections}")
            
            return all_present, missing_sections
            
        except Exception as e:
            logger.error(f"Required sections check failed: {e}")
            return False, [f"Check failed: {str(e)}"]
    
    def get_validation_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a comprehensive validation summary.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Validation summary dictionary
        """
        summary = {
            "overall_valid": False,
            "total_errors": 0,
            "missing_required_sections": [],
            "section_results": {},
            "validation_errors": [],
            "schema_info": self.schema_loader.get_schema_info()
        }
        
        try:
            # Check required sections
            required_ok, missing_sections = self.validate_required_sections(config)
            summary["missing_required_sections"] = missing_sections
            
            # Full validation
            overall_valid, validation_errors = self.validate_complete_config(config)
            summary["overall_valid"] = overall_valid and required_ok
            summary["validation_errors"] = validation_errors
            summary["total_errors"] = len(validation_errors) + len(missing_sections)
            
            # Individual section validation
            available_schemas = summary["schema_info"]["available_schemas"]
            for schema_info in available_schemas:
                schema_name = schema_info["file"].replace(".json", "")
                section_key = schema_info["properties"][0] if schema_info["properties"] else None
                
                if section_key and section_key in config:
                    section_valid, section_errors = self.validate_section(
                        schema_name, config[section_key]
                    )
                    summary["section_results"][section_key] = {
                        "valid": section_valid,
                        "errors": section_errors
                    }
            
            logger.info(f"Validation summary complete: {summary['total_errors']} total issues")
            
        except Exception as e:
            logger.error(f"Validation summary failed: {e}")
            summary["validation_errors"] = [f"Summary generation failed: {str(e)}"]
        
        return summary
    
    def validate_json_file(self, config_file_path: str) -> Dict[str, Any]:
        """
        Validate a JSON configuration file.
        
        Args:
            config_file_path: Path to the JSON configuration file
            
        Returns:
            Validation summary dictionary
        """
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Validating configuration file: {config_file_path}")
            return self.get_validation_summary(config)
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_file_path}")
            return {
                "overall_valid": False,
                "total_errors": 1,
                "validation_errors": [f"File not found: {config_file_path}"],
                "section_results": {}
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            return {
                "overall_valid": False,
                "total_errors": 1,
                "validation_errors": [f"Invalid JSON: {str(e)}"],
                "section_results": {}
            }
        except Exception as e:
            logger.error(f"Configuration file validation failed: {e}")
            return {
                "overall_valid": False,
                "total_errors": 1,
                "validation_errors": [f"Validation failed: {str(e)}"],
                "section_results": {}
            }


# Convenience functions
def validate_config_dict(config: Dict[str, Any], schema_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to validate a configuration dictionary.
    
    Args:
        config: Configuration dictionary
        schema_dir: Directory containing schema files
        
    Returns:
        Validation summary
    """
    validator = SchemaValidator(schema_dir)
    return validator.get_validation_summary(config)


def validate_config_file(file_path: str, schema_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to validate a configuration file.
    
    Args:
        file_path: Path to configuration file
        schema_dir: Directory containing schema files
        
    Returns:
        Validation summary
    """
    validator = SchemaValidator(schema_dir)
    return validator.validate_json_file(file_path) 