"""Base service class implementing common service functionality."""

from abc import ABC
from typing import TypeVar, Generic, Type
from uuid import UUID
import logging
from datetime import datetime

from ...domain.repositories.base import BaseRepository
from ...domain.entities.child import Child

T = TypeVar('T')

class BaseService(ABC, Generic[T]):
    """Base service class with common functionality."""

    def __init__(
        self,
        repository: BaseRepository[T],
        logger: logging.Logger = None
    ):
        """Initialize base service with repository and logger."""
        self._repository = repository
        self._logger = logger or logging.getLogger(self.__class__.__name__)

    async def _log_operation(
        self,
        operation: str,
        entity_id: UUID = None,
        details: dict = None,
        level: int = logging.INFO
    ) -> None:
        """Log an operation with standardized format."""
        log_entry = {
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
            "entity_id": str(entity_id) if entity_id else None,
            "details": details or {}
        }
        self._logger.log(level, log_entry)

    async def _validate_child_consent(self, child: Child) -> bool:
        """Validate child has necessary consent for operations."""
        if not child.can_interact():
            self._logger.warning(f"Child {child.id} lacks necessary consent")
            return False
        return True

    async def _handle_transaction(self, operation):
        """Execute operation within a transaction."""
        transaction = await self._repository.begin_transaction()
        try:
            result = await operation()
            await self._repository.commit_transaction(transaction)
            return result
        except Exception as e:
            await self._repository.rollback_transaction(transaction)
            self._logger.error(f"Transaction failed: {str(e)}")
            raise

    async def get(self, id: UUID) -> T:
        """Get entity by ID with logging."""
        try:
            entity = await self._repository.get(id)
            await self._log_operation("get", id)
            return entity
        except Exception as e:
            await self._log_operation(
                "get_failed",
                id,
                {"error": str(e)},
                logging.ERROR
            )
            raise

    async def create(self, entity: T) -> T:
        """Create entity with logging."""
        try:
            created = await self._handle_transaction(
                lambda: self._repository.create(entity)
            )
            await self._log_operation(
                "create",
                getattr(created, 'id', None),
                {"type": type(entity).__name__}
            )
            return created
        except Exception as e:
            await self._log_operation(
                "create_failed",
                None,
                {
                    "type": type(entity).__name__,
                    "error": str(e)
                },
                logging.ERROR
            )
            raise

    async def update(self, entity: T) -> T:
        """Update entity with logging."""
        try:
            updated = await self._handle_transaction(
                lambda: self._repository.update(entity)
            )
            await self._log_operation(
                "update",
                getattr(updated, 'id', None),
                {"type": type(entity).__name__}
            )
            return updated
        except Exception as e:
            await self._log_operation(
                "update_failed",
                getattr(entity, 'id', None),
                {
                    "type": type(entity).__name__,
                    "error": str(e)
                },
                logging.ERROR
            )
            raise

    async def delete(self, id: UUID) -> bool:
        """Delete entity with logging."""
        try:
            result = await self._handle_transaction(
                lambda: self._repository.delete(id)
            )
            await self._log_operation("delete", id)
            return result
        except Exception as e:
            await self._log_operation(
                "delete_failed",
                id,
                {"error": str(e)},
                logging.ERROR
            )
            raise

    async def exists(self, id: UUID) -> bool:
        """Check if entity exists."""
        try:
            return await self._repository.exists(id)
        except Exception as e:
            await self._log_operation(
                "exists_check_failed",
                id,
                {"error": str(e)},
                logging.ERROR
            )
            raise

    async def list(self, filters: dict = None, limit: int = 100, offset: int = 0):
        """List entities with filtering and pagination."""
        try:
            entities = await self._repository.list(filters, limit, offset)
            await self._log_operation(
                "list",
                None,
                {
                    "filters": filters,
                    "limit": limit,
                    "offset": offset,
                    "count": len(entities)
                }
            )
            return entities
        except Exception as e:
            await self._log_operation(
                "list_failed",
                None,
                {
                    "filters": filters,
                    "error": str(e)
                },
                logging.ERROR
            )
            raise
