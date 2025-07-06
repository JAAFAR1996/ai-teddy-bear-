"""
Enhanced SQLAlchemy Base Repository
"""
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text


from src.infrastructure.persistence.base import BaseRepository
from .exceptions import (
    DatabaseOperationError,
    EntityNotFoundError,
    RepositoryError,
    ValidationError,
)
from .advanced_query import AdvancedQueryMixin
from .bulk_operations import BulkOperationsMixin
from .performance import PerformanceMixin

T = TypeVar("T")
ID = TypeVar("ID")
logger = logging.getLogger(__name__)


class SQLAlchemyBaseRepository(
    AdvancedQueryMixin,
    BulkOperationsMixin,
    PerformanceMixin,
    BaseRepository[T, ID],
):
    """
    An enhanced and modular base repository for SQLAlchemy, providing comprehensive
    CRUD, bulk, and advanced query operations through a clean, mixin-based architecture.
    """

    def __init__(
        self,
        session_factory: sessionmaker,
        model_class: Type[T],
        auto_commit: bool = True,
        enable_caching: bool = False,
    ):
        super().__init__(enable_caching=enable_caching, model_class=model_class)
        self.session_factory = session_factory
        self.model_class = model_class
        self.auto_commit = auto_commit

        logger.info(
            f"Initialized {self.__class__.__name__} for {model_class.__name__}",
            extra={"auto_commit": auto_commit,
                   "caching_enabled": self.enable_caching},
        )

    @contextmanager
    def get_session(self) -> Session:
        """Provides a transactional database session."""
        session = self.session_factory()
        try:
            yield session
            if self.auto_commit:
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(
                f"Database session error in {self.__class__.__name__}: {e}", exc_info=True)
            raise RepositoryError(f"Database operation failed: {e}")
        finally:
            session.close()

    def _validate_entity(self, entity: T) -> None:
        """Validates an entity before a database operation. Can be extended in subclasses."""
        if entity is None:
            raise ValidationError("Entity cannot be None.")
        # Subclasses can add more specific validation logic here.

    async def create(self, entity: T) -> T:
        """Creates a new entity in the database."""
        self._validate_entity(entity)
        try:
            with self.get_session() as session:
                session.add(entity)
                session.flush()  # Use flush to get the ID before commit
                self._cache_put(str(entity.id), entity)
                return entity
        except IntegrityError as e:
            raise ValidationError(
                f"Entity creation failed due to a constraint violation: {e}")
        except SQLAlchemyError as e:
            raise DatabaseOperationError("create", e)

    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Retrieves an entity by its ID, using the cache if enabled."""
        if cached_entity := self._cache_get(str(entity_id)):
            return cached_entity
        try:
            with self.get_session() as session:
                entity = session.query(self.model_class).get(entity_id)
                if entity:
                    self._cache_put(str(entity.id), entity)
                return entity
        except SQLAlchemyError as e:
            raise DatabaseOperationError("get_by_id", e)

    def _get_existing_entity(self, session: Session, entity_id: ID) -> Optional[T]:
        """Fetches an existing entity from the database within a session."""
        return session.query(self.model_class).get(entity_id)

    def _update_entity_fields(self, existing_entity: T, new_entity: T):
        """Updates the fields of an existing entity with new values."""
        for key, value in new_entity.__dict__.items():
            if not key.startswith("_"):
                setattr(existing_entity, key, value)

    async def update(self, entity: T) -> T:
        """Updates an existing entity in the database."""
        self._validate_entity(entity)
        entity_id = getattr(entity, "id", None)
        if not entity_id:
            raise ValidationError("Entity must have an ID for update.")

        try:
            with self.get_session() as session:
                existing_entity = self._get_existing_entity(session, entity_id)
                if not existing_entity:
                    raise EntityNotFoundError(
                        entity_id, self.model_class.__name__)

                # Update fields from the provided entity
                for key, value in entity.__dict__.items():
                    if not key.startswith('_'):
                        setattr(existing_entity, key, value)

                self._cache_put(str(entity_id), existing_entity)
                return existing_entity
        except SQLAlchemyError as e:
            raise DatabaseOperationError("update", e)

    async def delete(self, entity_id: ID) -> bool:
        """Deletes an entity from the database by its ID."""
        try:
            with self.get_session() as session:
                entity = self._get_existing_entity(session, entity_id)
                if not entity:
                    return False
                session.delete(entity)
                self._cache_remove(str(entity_id))
                return True
        except SQLAlchemyError as e:
            raise DatabaseOperationError("delete", e)

    async def list(self, options: Optional[QueryOptions] = None) -> List[T]:
        """Lists entities with optional filtering, sorting, and pagination."""
        try:
            with self.get_session() as session:
                query = self._build_query(session, options=options)
                return query.all()
        except SQLAlchemyError as e:
            raise DatabaseOperationError("list", e)

    async def execute_raw_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Executes a raw, parameterized SQL query safely."""
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                return result.fetchall()
        except SQLAlchemyError as e:
            logger.error(f"Error executing raw query: {e}", exc_info=True)
            raise RepositoryError(f"Raw query execution failed: {e}")
