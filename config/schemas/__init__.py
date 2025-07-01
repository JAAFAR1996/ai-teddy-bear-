"""
Schema Management Package

This package provides modular JSON schema validation for the AI Teddy Bear configuration.
Each schema is separated into its own file for better organization and maintainability.
"""

from .schema_loader import SchemaLoader
from .schema_validator import SchemaValidator

__all__ = ['SchemaLoader', 'SchemaValidator']

# Version information
__version__ = '1.0.0'
__author__ = 'AI Teddy Bear Team' 