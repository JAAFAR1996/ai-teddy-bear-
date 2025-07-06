"""
Mixin for bulk database operations in SQLite.
"""
import logging
import sqlite3
from typing import List, TypeVar

from src.infrastructure.persistence.base import BulkOperationResult

from .sqlite_query_builder import QueryBuilderMixin

T = TypeVar("T")
logger = logging.getLogger(__name__)


class SQLiteBulkOperationsMixin(QueryBuilderMixin):
    """A mixin to add bulk create, update, and delete capabilities."""

    def _create_entity_in_bulk(self, cursor, entity: T) -> bool:
        """Creates a single entity within a bulk transaction."""
        try:
            entity_dict = self._entity_to_dict(entity)
            sql, values = self._prepare_insert_sql(entity_dict)
            cursor.execute(sql, values)
            if hasattr(entity, "id") and not getattr(entity, "id", None):
                setattr(entity, "id", cursor.lastrowid)
            return True
        except Exception as e:
            entity_id = getattr(entity, "id", "unknown_id")
            logger.error(
                f"Failed to create entity {entity_id} in bulk operation: {e}", exc_info=True)
            return False

    async def bulk_create(self, entities: List[T]) -> BulkOperationResult:
        """Creates multiple entities in a single, efficient transaction."""
        success_count = 0
        failed_ids = []
        try:
            with self.transaction() as cursor:
                for entity in entities:
                    if self._create_entity_in_bulk(cursor, entity):
                        success_count += 1
                    else:
                        failed_ids.append(
                            str(getattr(entity, "id", "unknown_id")))
        except sqlite3.Error as e:
            logger.error(f"Bulk create transaction failed: {e}", exc_info=True)
            # All entities in the transaction are considered failed
            return BulkOperationResult(
                success_count=0,
                failed_count=len(entities),
                failed_ids=[str(getattr(e, "id", "unknown_id"))
                            for e in entities],
            )

        return BulkOperationResult(
            success_count=success_count,
            failed_count=len(failed_ids),
            failed_ids=failed_ids,
        )

    def _update_entity_in_bulk(self, cursor, entity: T) -> bool:
        """Updates a single entity within a bulk transaction."""
        try:
            entity_dict = self._entity_to_dict(entity)
            sql, values = self._prepare_update_sql(entity_dict)
            cursor.execute(sql, values)
            return cursor.rowcount > 0
        except Exception as e:
            entity_id = getattr(entity, "id", "unknown_id")
            logger.error(
                f"Failed to update entity {entity_id} in bulk operation: {e}", exc_info=True)
            return False

    async def bulk_update(self, entities: List[T]) -> BulkOperationResult:
        """Updates multiple entities in a single, efficient transaction."""
        success_count = 0
        failed_ids = []
        try:
            with self.transaction() as cursor:
                for entity in entities:
                    if self._update_entity_in_bulk(cursor, entity):
                        success_count += 1
                    else:
                        failed_ids.append(
                            str(getattr(entity, "id", "unknown_id")))
        except sqlite3.Error as e:
            logger.error(f"Bulk update transaction failed: {e}", exc_info=True)
            return BulkOperationResult(
                success_count=0,
                failed_count=len(entities),
                failed_ids=[str(getattr(e, "id", "unknown_id"))
                            for e in entities],
            )

        return BulkOperationResult(
            success_count=success_count,
            failed_count=len(failed_ids),
            failed_ids=failed_ids,
        )

    async def bulk_delete(self, entity_ids: List[str]) -> BulkOperationResult:
        """Deletes multiple entities in a single transaction by their IDs."""
        success_count = 0
        failed_ids = []
        try:
            with self.transaction() as cursor:
                for entity_id in entity_ids:
                    try:
                        self._validate_table_and_column(self.table_name)
                        sql = f"DELETE FROM {self.table_name} WHERE id = ?"
                        cursor.execute(sql, (entity_id,))
                        if cursor.rowcount > 0:
                            success_count += 1
                        else:
                            failed_ids.append(entity_id)
                    except Exception as e:
                        logger.error(
                            f"Failed to delete entity {entity_id} in bulk: {e}", exc_info=True)
                        failed_ids.append(entity_id)
        except sqlite3.Error as e:
            logger.error(f"Bulk delete transaction failed: {e}", exc_info=True)
            # If the transaction fails, all are considered failed
            return BulkOperationResult(
                success_count=0,
                failed_count=len(entity_ids),
                failed_ids=entity_ids,
            )

        return BulkOperationResult(
            success_count=success_count,
            failed_count=len(failed_ids),
            failed_ids=failed_ids,
        )
