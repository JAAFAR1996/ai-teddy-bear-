"""
Mixin for bulk operations in SQLAlchemy repositories.
"""
import logging
from typing import List, TypeVar

from sqlalchemy.exc import SQLAlchemyError

from src.infrastructure.persistence.base import BulkOperationResult

from .exceptions import RepositoryError, ValidationError
from .query_builder import QueryBuilderMixin

T = TypeVar("T")
ID = TypeVar("ID")
logger = logging.getLogger(__name__)


class BulkOperationsMixin(QueryBuilderMixin):
    """A mixin to add efficient bulk create, update, and delete capabilities."""

    def _validate_entity(self, entity: T):
        """Placeholder for entity validation. To be implemented in the main class."""
        pass

    def _get_existing_entity(self, session, entity_id: ID):
        """Placeholder for getting an existing entity. To be implemented in the main class."""
        pass

    def _update_entity_fields(self, existing_entity, new_entity):
        """Placeholder for updating entity fields. To be implemented in the main class."""
        pass

    def _cache_put(self, key, entity):
        """Placeholder for caching. To be implemented in the caching mixin."""
        pass

    def _cache_remove(self, key):
        """Placeholder for cache removal. To be implemented in the caching mixin."""
        pass

    async def bulk_create(self, entities: List[T]) -> BulkOperationResult:
        """Creates multiple entities in a single transaction using `session.add_all`."""
        if not entities:
            return BulkOperationResult(success_count=0, failed_count=0, failed_ids=[])

        try:
            with self.get_session() as session:
                for entity in entities:
                    self._validate_entity(entity)
                session.add_all(entities)
                session.flush()  # Flush to get IDs
                for entity in entities:
                    if hasattr(entity, "id"):
                        self._cache_put(str(entity.id), entity)

                logger.info(
                    f"Bulk created {len(entities)} entities of type {self.model_class.__name__}.")
                return BulkOperationResult(success_count=len(entities), failed_count=0, failed_ids=[])
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during bulk create: {e}", exc_info=True)
            raise RepositoryError(f"Bulk create operation failed: {e}")

    def _update_one_in_bulk(self, session, entity_data: dict) -> bool:
        """Updates a single entity within a bulk update operation using a dictionary of values."""
        entity_id = entity_data.get("id")
        if not entity_id:
            raise ValidationError(
                "Each entity in a bulk update must have an ID.")

        existing = self._get_existing_entity(session, entity_id)
        if not existing:
            return False

        for key, value in entity_data.items():
            if key != "id":
                setattr(existing, key, value)

        self._cache_put(str(entity_id), existing)
        return True

    async def bulk_update(self, entities: List[T]) -> BulkOperationResult:
        """Updates multiple entities in a single transaction."""
        if not entities:
            return BulkOperationResult(success_count=0, failed_count=0, failed_ids=[])

        success_count = 0
        failed_ids = []
        try:
            with self.get_session() as session:
                # For ORM-based bulk updates, iterating is often necessary
                # to handle complex logic, but for simple updates,
                # session.bulk_update_mappings is more efficient.
                update_mappings = []
                for entity in entities:
                    self._validate_entity(entity)
                    if not hasattr(entity, "id") or not entity.id:
                        failed_ids.append("unknown_id")
                        continue
                    entity_dict = {c.key: getattr(
                        entity, c.key) for c in self.model_class.__table__.columns}
                    update_mappings.append(entity_dict)

                if update_mappings:
                    session.bulk_update_mappings(
                        self.model_class, update_mappings)
                    success_count = len(update_mappings)
                    for mapping in update_mappings:
                        # Attempt to cache the updated data. Note: this won't be the full entity object.
                        self._cache_put(str(mapping['id']), mapping)

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during bulk update: {e}", exc_info=True)
            raise RepositoryError(f"Bulk update operation failed: {e}")

        return BulkOperationResult(
            success_count=success_count,
            failed_count=len(failed_ids),
            failed_ids=failed_ids,
        )

    async def bulk_delete(self, entity_ids: List[ID]) -> BulkOperationResult:
        """Deletes multiple entities by their IDs in a single transaction."""
        if not entity_ids:
            return BulkOperationResult(success_count=0, failed_count=0, failed_ids=[])

        try:
            with self.get_session() as session:
                deleted_count = (
                    session.query(self.model_class)
                    .filter(self.model_class.id.in_(entity_ids))
                    .delete(synchronize_session=False)
                )

                for entity_id in entity_ids:
                    self._cache_remove(str(entity_id))

                failed_count = len(entity_ids) - deleted_count
                # A simple way to find failed IDs is to query which ones still exist,
                # but this is often too slow. We'll report the count.
                failed_ids = [] if failed_count == 0 else ["check_logs_for_failed_ids"]

                return BulkOperationResult(
                    success_count=deleted_count,
                    failed_count=failed_count,
                    failed_ids=failed_ids,
                )
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during bulk delete: {e}", exc_info=True)
            raise RepositoryError(f"Bulk delete operation failed: {e}")
