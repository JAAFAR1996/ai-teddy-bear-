"""
Mixin for building SQLAlchemy queries.
"""
import logging
import re
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import and_, asc, desc
from sqlalchemy.orm.query import Query

from src.infrastructure.persistence.base import QueryOptions, SearchCriteria, SortOrder

logger = logging.getLogger(__name__)


class QueryBuilderMixin:
    """A mixin for dynamically building safe SQLAlchemy queries from abstract criteria."""

    model_class: Any

    def _validate_attribute_name(self, name: str) -> None:
        """Ensures the attribute name is safe and exists on the model."""
        if not re.match(r"^[a-zA-Z0-9_]+$", name) or not hasattr(self.model_class, name):
            raise ValueError(
                f"Invalid or non-existent model attribute: {name}")

    def _apply_search_criteria(self, query: Query, criteria: List[SearchCriteria]) -> Query:
        """Applies a list of SearchCriteria to the query."""
        if not criteria:
            return query

        conditions = []
        for c in criteria:
            condition = self._build_condition(c)
            if condition is not None:
                conditions.append(condition)

        return query.filter(and_(*conditions)) if conditions else query

    def _apply_filters(self, query: Query, filters: Dict[str, Any]) -> Query:
        """Applies simple equality filters to the query."""
        if not filters:
            return query

        for field, value in filters.items():
            self._validate_attribute_name(field)
            query = query.filter(getattr(self.model_class, field) == value)
        return query

    def _apply_sorting(self, query: Query, sort_by: str, sort_order: SortOrder) -> Query:
        """Applies sorting to the query."""
        if not sort_by:
            return query

        self._validate_attribute_name(sort_by)
        sort_column = getattr(self.model_class, sort_by)
        return query.order_by(desc(sort_column) if sort_order == SortOrder.DESC else asc(sort_column))

    def _apply_pagination(self, query: Query, offset: Optional[int], limit: Optional[int]) -> Query:
        """Applies pagination (limit and offset) to the query."""
        if offset is not None and offset > 0:
            query = query.offset(offset)
        if limit is not None and limit > 0:
            query = query.limit(limit)
        return query

    def _build_query(
        self, session, criteria: Optional[List[SearchCriteria]] = None, options: Optional[QueryOptions] = None
    ) -> Query:
        """Builds a complete SQLAlchemy query with criteria, filters, sorting, and pagination."""
        query = session.query(self.model_class)
        if hasattr(self, '_query_count'):  # For performance tracking
            self._query_count += 1

        if criteria:
            query = self._apply_search_criteria(query, criteria)
        if options:
            query = self._apply_filters(query, options.filters)
            query = self._apply_sorting(
                query, options.sort_by, options.sort_order)
            query = self._apply_pagination(
                query, options.offset, options.limit)

        return query

    def _get_operator_handler(self, operator: str) -> Optional[Callable]:
        """Returns the handler function for a given search operator."""
        op_map = {
            "eq": lambda f, v: f == v,
            "ne": lambda f, v: f != v,
            "gt": lambda f, v: f > v,
            "gte": lambda f, v: f >= v,
            "lt": lambda f, v: f < v,
            "lte": lambda f, v: f <= v,
            "like": lambda f, v: f.like(f"%{v}%"),
            "ilike": lambda f, v: f.ilike(f"%{v}%"),
            "in": lambda f, v: f.in_(v),
            "not_in": lambda f, v: ~f.in_(v),
            "is_null": lambda f, v: f.is_(None),
            "is_not_null": lambda f, v: f.isnot(None),
            "between": lambda f, v: f.between(v[0], v[1]),
            "starts_with": lambda f, v: f.startswith(v),
            "ends_with": lambda f, v: f.endswith(v),
        }
        return op_map.get(operator)

    def _build_condition(self, criterion: SearchCriteria) -> Optional[Any]:
        """Builds a single SQLAlchemy condition from a SearchCriteria object."""
        self._validate_attribute_name(criterion.field)
        field_attr = getattr(self.model_class, criterion.field)
        handler = self._get_operator_handler(criterion.operator.lower())

        if not handler:
            logger.warning(
                f"Unsupported search operator: {criterion.operator}")
            return None

        return handler(field_attr, criterion.value)
