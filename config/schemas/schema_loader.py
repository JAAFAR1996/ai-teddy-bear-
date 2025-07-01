"""
Schema Loader Module

This module handles loading and combining all individual schema files
into a complete configuration schema for validation.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from functools import lru_cache


logger = logging.getLogger(__name__)


class SchemaLoader:
    """
    Handles loading and combining JSON schema files.
    
    This class provides functionality to:
    - Load individual schema files
    - Combine them into a master schema
    - Cache loaded schemas for performance
    - Validate schema file integrity
    """
    
    def __init__(self, schema_dir: Optional[str] = None):
        """
        Initialize the schema loader.
        
        Args:
            schema_dir: Directory containing schema files. 
                       Defaults to current directory/schemas
        """
        if schema_dir is None:
            schema_dir = Path(__file__).parent
        
        self.schema_dir = Path(schema_dir)
        self._validate_schema_directory()
        
    def _validate_schema_directory(self) -> None:
        """Validate that the schema directory exists and is accessible."""
        if not self.schema_dir.exists():
            raise FileNotFoundError(
                f"Schema directory not found: {self.schema_dir}"
            )
        
        if not self.schema_dir.is_dir():
            raise NotADirectoryError(
                f"Schema path is not a directory: {self.schema_dir}"
            )
    
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            logger.debug(f"Successfully loaded schema: {file_path.name}")
            return content
            
        except FileNotFoundError:
            logger.error(f"Schema file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading {file_path}: {e}")
            raise
    
    def get_schema_files(self) -> List[Path]:
        """Get list of all schema files in the directory."""
        schema_files = []
        
        for file_path in self.schema_dir.glob("*.json"):
            if file_path.name not in ['__init__.py', 'common_definitions.json']:
                schema_files.append(file_path)
        
        # Sort for consistent ordering
        schema_files.sort(key=lambda x: x.name)
        
        logger.debug(f"Found {len(schema_files)} schema files")
        return schema_files
    
    @lru_cache(maxsize=1)
    def load_common_definitions(self) -> Dict[str, Any]:
        """Load common schema definitions."""
        definitions_file = self.schema_dir / "common_definitions.json"
        
        if definitions_file.exists():
            return self._load_json_file(definitions_file)
        
        logger.warning("Common definitions file not found")
        return {"definitions": {}}
    
    def load_individual_schema(self, schema_name: str) -> Dict[str, Any]:
        """Load a specific schema file."""
        schema_file = self.schema_dir / f"{schema_name}.json"
        
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_name}.json")
        
        return self._load_json_file(schema_file)
    
    def combine_schemas(self) -> Dict[str, Any]:
        """Combine all individual schemas into a master schema."""
        logger.info("Combining all schema files into master schema")
        
        # Start with basic schema structure
        master_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "AI Teddy Bear Configuration Schema",
            "description": "Complete configuration schema for AI Teddy Bear application",
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
        
        # Load common definitions
        common_defs = self.load_common_definitions()
        if "definitions" in common_defs:
            master_schema["definitions"] = common_defs["definitions"]
        
        # Combine all individual schemas
        schema_files = self.get_schema_files()
        
        for schema_file in schema_files:
            try:
                schema_content = self._load_json_file(schema_file)
                
                # Extract properties and required fields from each schema
                if "properties" in schema_content:
                    master_schema["properties"].update(
                        schema_content["properties"]
                    )
                
                if "required" in schema_content:
                    master_schema["required"].extend(schema_content["required"])
                
                logger.debug(f"Added schema: {schema_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to process schema {schema_file}: {e}")
                raise
        
        # Remove duplicates from required fields
        master_schema["required"] = list(set(master_schema["required"]))
        
        logger.info(
            f"Successfully combined {len(schema_files)} schemas with "
            f"{len(master_schema['properties'])} main sections"
        )
        
        return master_schema
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about available schemas."""
        schema_files = self.get_schema_files()
        
        info = {
            "total_schemas": len(schema_files),
            "schema_directory": str(self.schema_dir),
            "available_schemas": []
        }
        
        for schema_file in schema_files:
            try:
                schema_content = self._load_json_file(schema_file)
                
                schema_info = {
                    "file": schema_file.name,
                    "title": schema_content.get("title", "Unknown"),
                    "description": schema_content.get("description", ""),
                    "properties": list(schema_content.get("properties", {}).keys())
                }
                
                info["available_schemas"].append(schema_info)
                
            except Exception as e:
                logger.warning(f"Could not get info for {schema_file}: {e}")
        
        return info


# Convenience functions for quick access
def load_complete_schema(schema_dir: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to load the complete combined schema."""
    loader = SchemaLoader(schema_dir)
    return loader.combine_schemas()


def get_available_schemas(schema_dir: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to get information about available schemas."""
    loader = SchemaLoader(schema_dir)
    return loader.get_schema_info()