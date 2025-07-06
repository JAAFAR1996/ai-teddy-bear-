"""
Serialization and deserialization logic for SQLite repositories.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Type, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


class SerializationMixin:
    """A mixin for handling entity serialization and deserialization."""

    _entity_class: Type[T]

    def _entity_to_dict(self, entity: T) -> Dict[str, Any]:
        """Convert entity to a dictionary for database storage."""
        if hasattr(entity, "dict"):
            return entity.dict()
        if hasattr(entity, "to_dict"):
            return entity.to_dict()
        if hasattr(entity, "__dict__"):
            return entity.__dict__.copy()
        raise ValueError(f"Cannot convert entity {type(entity)} to dictionary")

    def _dict_to_entity(self, data: Dict[str, Any]) -> T:
        """Convert a dictionary from the database to an entity."""
        if not self._entity_class:
            raise ValueError("Entity class not specified for deserialization")

        processed_data = self._process_datetime_fields(dict(data))
        processed_data = self._process_json_fields(processed_data)

        try:
            return self._entity_class(**processed_data)
        except Exception as e:
            logger.error(
                f"Error creating entity from data {processed_data}: {e}", exc_info=True)
            raise ValueError(f"Cannot create entity from dictionary: {e}")

    def _process_datetime_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process datetime fields from the database, converting them from strings."""
        datetime_fields = ["created_at", "updated_at",
                           "start_time", "end_time", "timestamp"]
        for field in datetime_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(
                        data[field].replace("Z", "+00:00"))
                except ValueError:
                    try:
                        data[field] = datetime.strptime(
                            data[field], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        logger.warning(
                            f"Could not parse datetime string '{data[field]}' for field '{field}'.")
        return data

    def _process_json_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process JSON string fields from the database, loading them into dicts/lists."""
        json_fields = ["metadata", "settings", "config",
                       "data", "topics", "emotional_states"]
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError:
                    logger.warning(
                        f"Could not parse JSON string for field '{field}'.")
        return data

    def _serialize_for_db(self, value: Any) -> Any:
        """Serialize complex Python types for database storage."""
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        if isinstance(value, bool):
            return 1 if value else 0
        return value
