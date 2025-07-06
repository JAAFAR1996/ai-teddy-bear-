"""
SQL query building logic for SQLite repositories.
"""
import logging
import re
from typing import Any, Callable, Dict, List, Tuple

from src.infrastructure.persistence.base import QueryOptions, SearchCriteria, SortOrder

from .serialization import SerializationMixin

logger = logging.getLogger(__name__)


class QueryBuilderMixin(SerializationMixin):
    """A mixin for building safe and robust SQL queries."""

    table_name: str

    def _validate_table_and_column(self, name: str) -> None:
        """Ensure table/column name is safe (alphanumeric/underscore only)."""
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            logger.error(
                f"Invalid or unsafe table or column name detected: {name}")
            raise ValueError(f"Invalid table or column name: {name}")

    def _prepare_insert_sql(self, entity_dict: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Prepares the SQL INSERT statement and values from an entity dictionary."""
        serialized_dict = {k: self._serialize_for_db(
            v) for k, v in entity_dict.items()}

        if "id" in serialized_dict and not serialized_dict["id"]:
            del serialized_dict["id"]

        for col in serialized_dict.keys():
            self._validate_table_and_column(col)

        columns = ", ".join(serialized_dict.keys())
        placeholders = ", ".join(["?" for _ in serialized_dict])
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        return sql, list(serialized_dict.values())

    def _prepare_update_sql(self, entity_dict: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Prepares the SQL UPDATE statement and values from an entity dictionary."""
        if "id" not in entity_dict or not entity_dict["id"]:
            raise ValueError("Entity must have an ID for an update operation.")

        serialized_dict = {k: self._serialize_for_db(
            v) for k, v in entity_dict.items()}
        update_fields = []
        update_values = []

        for k, v in serialized_dict.items():
            if k != "id":
                self._validate_table_and_column(k)
                update_fields.append(f"{k} = ?")
                update_values.append(v)

        if not update_fields:
            raise ValueError("No fields to update for the entity.")

        update_values.append(serialized_dict["id"])
        sql = f"UPDATE {self.table_name} SET {', '.join(update_fields)} WHERE id = ?"
        return sql, update_values

    def _build_list_query(self, options: QueryOptions) -> Tuple[str, List[Any]]:
        """Builds the SQL query for the list method based on query options."""
        self._validate_table_and_column(self.table_name)
        sql = f"SELECT * FROM {self.table_name}"
        params: List[Any] = []

        if options and options.filters:
            filter_clauses = []
            for key, value in options.filters.items():
                self._validate_table_and_column(key)
                filter_clauses.append(f"{key} = ?")
                params.append(self._serialize_for_db(value))
            if filter_clauses:
                sql += " WHERE " + " AND ".join(filter_clauses)

        return self._apply_options_to_query(sql, params, options)

    def _build_search_query(
        self, criteria: List[SearchCriteria], options: QueryOptions
    ) -> Tuple[str, List[Any]]:
        """Builds a comprehensive SQL query for searching with multiple criteria."""
        self._validate_table_and_column(self.table_name)
        sql = f"SELECT * FROM {self.table_name}"
        params: List[Any] = []

        sql, params = self._apply_criteria_to_query(sql, params, criteria)
        sql, params = self._apply_options_to_query(sql, params, options)

        return sql, params

    def _apply_criteria_to_query(
        self, sql: str, params: List[Any], criteria: List[SearchCriteria]
    ) -> Tuple[str, List[Any]]:
        """Applies a list of search criteria to the SQL query as WHERE clauses."""
        if not criteria:
            return sql, params

        conditions = []
        for criterion in criteria:
            condition, param = self._build_search_condition(criterion)
            conditions.append(condition)
            if isinstance(param, list):
                params.extend(param)
            elif param is not None:
                params.append(param)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        return sql, params

    def _apply_options_to_query(
        self, sql: str, params: List[Any], options: QueryOptions
    ) -> Tuple[str, List[Any]]:
        """Applies sorting and pagination options to the SQL query."""
        if options and options.sort_by:
            self._validate_table_and_column(options.sort_by)
            order = "DESC" if options.sort_order == SortOrder.DESC else "ASC"
            sql += f" ORDER BY {options.sort_by} {order}"

        if options and options.limit:
            sql += " LIMIT ?"
            params.append(options.limit)

        if options and options.offset:
            sql += " OFFSET ?"
            params.append(options.offset)

        return sql, params

    def _get_condition_handlers(self) -> Dict[str, Callable]:
        """Returns a dictionary of handlers for different search condition operators."""
        return {
            "eq": lambda f, v: (f"{f} = ?", v),
            "ne": lambda f, v: (f"{f} != ?", v),
            "gt": lambda f, v: (f"{f} > ?", v),
            "gte": lambda f, v: (f"{f} >= ?", v),
            "lt": lambda f, v: (f"{f} < ?", v),
            "lte": lambda f, v: (f"{f} <= ?", v),
            "like": lambda f, v: (f"{f} LIKE ?", f"%{v}%"),
            "ilike": lambda f, v: (f"LOWER({f}) LIKE LOWER(?)", f"%{v}%"),
            "in": self._handle_in_operator,
            "is_null": lambda f, v: (f"{f} IS NULL", None),
            "is_not_null": lambda f, v: (f"{f} IS NOT NULL", None),
        }

    def _handle_in_operator(self, field: str, value: Any) -> Tuple[str, Any]:
        """Handles the 'IN' operator by generating appropriate placeholders."""
        if isinstance(value, (list, tuple)):
            if not value:
                return "1=0", []
            placeholders = ", ".join(["?" for _ in value])
            return f"{field} IN ({placeholders})", value
        return f"{field} = ?", value

    def _build_search_condition(self, criterion: SearchCriteria) -> Tuple[str, Any]:
        """Builds a single SQL condition from a SearchCriteria object."""
        self._validate_table_and_column(criterion.field)
        handlers = self._get_condition_handlers()
        handler = handlers.get(criterion.operator)

        if handler:
            return handler(criterion.field, self._serialize_for_db(criterion.value))

        raise ValueError(f"Unsupported search operator: {criterion.operator}")

    def _build_aggregation_function(self, operation: str, field: str) -> str:
        """Builds a safe SQL aggregation function string."""
        self._validate_table_and_column(field)
        op = operation.lower()
        if op not in ["count", "sum", "avg", "max", "min"]:
            raise ValueError(f"Unsupported aggregation operation: {operation}")
        return f"{op.upper()}({field})"
