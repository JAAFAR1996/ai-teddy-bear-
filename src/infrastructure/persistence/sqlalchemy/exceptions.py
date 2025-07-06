"""
Custom exceptions for the SQLAlchemy repository layer.
"""
from typing import Any


class RepositoryError(Exception):
    """Base class for repository-related errors."""
    pass


class EntityNotFoundError(RepositoryError):
    """Raised when an entity is not found in the database."""

    def __init__(self, entity_id: Any, model_name: str):
        self.entity_id = entity_id
        self.model_name = model_name
        super().__init__(f"{model_name} with ID '{entity_id}' not found.")


class ValidationError(RepositoryError):
    """Raised when entity validation fails before a database operation."""
    pass


class DatabaseOperationError(RepositoryError):
    """Raised for general database errors during an operation, wrapping the original exception."""

    def __init__(self, operation: str, original_exception: Exception):
        self.operation = operation
        self.original_exception = original_exception
        super().__init__(
            f"Database error during '{operation}': {original_exception}")
