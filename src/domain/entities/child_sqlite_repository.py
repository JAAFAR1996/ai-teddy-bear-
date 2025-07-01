"""
Child SQLite Repository - Clean Architecture Implementation

This repository now delegates to specialized services following Clean Architecture principles.
Original God Class has been refactored into:
- Domain Services (business logic)
- Application Services (use cases)
- Infrastructure Services (external dependencies)
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.application.services.child.child_analytics_service import \
    ChildAnalyticsService
from src.application.services.child.child_bulk_operations_service import \
    ChildBulkOperationsService
from src.application.services.child.child_interaction_service import \
    ChildInteractionService
from src.application.services.child.child_search_service import \
    ChildSearchService
from src.core.domain.entities.child import Child
# Import refactored services
from src.domain.child.services.child_analytics_service import \
    ChildAnalyticsDomainService
from src.domain.child.services.child_family_service import \
    ChildFamilyDomainService
from src.domain.child.services.child_interaction_service import \
    ChildInteractionDomainService
from src.infrastructure.persistence.base import (QueryOptions, SearchCriteria,
                                                 SortOrder)
from src.infrastructure.persistence.base_sqlite_repository import \
    BaseSQLiteRepository
from src.infrastructure.persistence.child_repository import ChildRepository


class ChildSQLiteRepository(BaseSQLiteRepository[Child, int], ChildRepository):
    """
    Refactored SQLite implementation of Child Repository

    This class now coordinates between different services instead of handling
    all responsibilities itself, following Clean Architecture principles.
    """

    def __init__(
        self,
        session_factory,
        db_path: str = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "data", "teddyai.db"
        ),
    ):
        self.session_factory = session_factory

        # Ensure data directory exists
        data_dir = os.path.dirname(db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        # Create connection
        connection = sqlite3.connect(db_path, check_same_thread=False)

        super().__init__(
            connection=connection, table_name="children", entity_class=Child
        )

        # Initialize domain services
        self.analytics_domain_service = ChildAnalyticsDomainService()
        self.interaction_domain_service = ChildInteractionDomainService()
        self.family_domain_service = ChildFamilyDomainService()

        # Initialize application services
        self.search_service = ChildSearchService(self)
        self.analytics_service = ChildAnalyticsService(
            self, self.analytics_domain_service
        )
        self.interaction_service = ChildInteractionService(
            self, self.interaction_domain_service
        )
        self.bulk_operations_service = ChildBulkOperationsService(self)

    async def initialize(self):
        """Initialize repository"""
        pass

    def _get_table_schema(self) -> str:
        """Get the CREATE TABLE SQL statement for children table"""
        return """
            CREATE TABLE IF NOT EXISTS children (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                date_of_birth DATE,
                gender TEXT,
                interests TEXT,
                personality_traits TEXT,
                learning_preferences TEXT,
                communication_style TEXT,
                max_daily_interaction_time INTEGER DEFAULT 3600,
                allowed_topics TEXT,
                restricted_topics TEXT,
                language_preference TEXT DEFAULT 'en',
                cultural_background TEXT,
                parental_controls TEXT,
                emergency_contacts TEXT,
                medical_notes TEXT,
                educational_level TEXT,
                special_needs TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_interaction DATETIME,
                total_interaction_time INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                privacy_settings TEXT,
                custom_settings TEXT
            )
        """

    # ========== CORE CRUD OPERATIONS (Keep as-is) ==========

    async def create(self, child: Child) -> Child:
        """Create a new child profile"""
        try:
            with self.transaction() as cursor:
                data = self._serialize_child_for_db(child)

                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])
                sql = (
                    f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
                )

                cursor.execute(sql, list(data.values()))

                if not child.id:
                    child.id = data["id"]

                return child

        except sqlite3.Error as e:
            self.logger.error(f"Error creating child: {e}")
            raise

    async def get_by_id(self, child_id: str) -> Optional[Child]:
        """Retrieve child by ID"""
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE id = ? AND is_active = 1"
            cursor.execute(sql, (child_id,))

            row = cursor.fetchone()
            if row:
                return self._deserialize_child_from_db(dict(row))
            return None

        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving child {child_id}: {e}")
            raise

    async def update(self, child: Child) -> Child:
        """Update existing child profile"""
        try:
            with self.transaction() as cursor:
                data = self._serialize_child_for_db(child)

                if "id" not in data or not data["id"]:
                    raise ValueError("Child must have an ID for update")

                update_fields = [f"{k} = ?" for k in data.keys() if k != "id"]
                update_values = [v for k, v in data.items() if k != "id"]
                update_values.append(data["id"])

                sql = f"UPDATE {self.table_name} SET {', '.join(update_fields)} WHERE id = ?"

                cursor.execute(sql, update_values)

                if cursor.rowcount == 0:
                    raise ValueError(f"No child found with ID {data['id']}")

                return child

        except sqlite3.Error as e:
            self.logger.error(f"Error updating child: {e}")
            raise

    async def delete(self, child_id: str) -> bool:
        """Soft delete child (mark as inactive)"""
        try:
            with self.transaction() as cursor:
                sql = f"UPDATE {self.table_name} SET is_active = 0, updated_at = ? WHERE id = ?"
                cursor.execute(sql, (datetime.now().isoformat(), child_id))
                return cursor.rowcount > 0

        except sqlite3.Error as e:
            self.logger.error(f"Error deleting child {child_id}: {e}")
            raise

    async def list(self, options: Optional[QueryOptions] = None) -> List[Child]:
        """List active children with optional filtering and sorting"""
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE is_active = 1"
            params = []

            if options and hasattr(options, "sort_by") and options.sort_by:
                order = (
                    "DESC"
                    if hasattr(options, "sort_order")
                    and options.sort_order == SortOrder.DESC
                    else "ASC"
                )
                sql += f" ORDER BY {options.sort_by} {order}"

            if options and hasattr(options, "limit") and options.limit:
                sql += f" LIMIT {options.limit}"

            if options and hasattr(options, "offset") and options.offset:
                sql += f" OFFSET {options.offset}"

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [self._deserialize_child_from_db(dict(row)) for row in rows]

        except sqlite3.Error as e:
            self.logger.error(f"Error listing children: {e}")
            raise

    # ========== DELEGATED METHODS (Use Services) ==========

    # Analytics Operations - Delegate to Analytics Service
    async def get_engagement_insights(self, child_id: str) -> Dict[str, Any]:
        """Get engagement insights - delegated to analytics service"""
        insight = await self.analytics_service.get_child_engagement_insights(child_id)
        return {
            "child_id": insight.child_id,
            "engagement_level": insight.engagement_level.value,
            "days_since_last_interaction": insight.metrics.days_since_last_interaction,
            "total_interaction_time": insight.metrics.total_interaction_time,
            "daily_average_time": insight.metrics.daily_average_time,
            "time_utilization_percentage": insight.metrics.time_utilization_percentage,
            "interaction_streak": insight.metrics.interaction_streak,
            "recommendations": insight.recommendations,
            "last_analysis": insight.analysis_timestamp.isoformat(),
        }

    async def get_children_statistics(self) -> Dict[str, Any]:
        """Get system statistics - delegated to analytics service"""
        stats = await self.analytics_service.get_system_statistics()
        return {
            "total_children": stats.total_children,
            "age_statistics": {
                "min_age": stats.age_statistics.min_age,
                "max_age": stats.age_statistics.max_age,
                "average_age": stats.age_statistics.average_age,
            },
            "language_distribution": stats.language_distribution,
            "recent_activity": {
                "children_active_last_7_days": stats.activity_statistics.children_active_last_7_days,
                "activity_percentage": stats.activity_statistics.activity_percentage,
            },
        }

    # Search Operations - Delegate to Search Service
    async def find_by_name(self, name: str) -> Optional[Child]:
        """Find child by name - delegated to search service"""
        return await self.search_service.search_by_name(name)

    async def search_children(self, query: str) -> List[Child]:
        """Search children - delegated to search service"""
        return await self.search_service.full_text_search(query)

    # Interaction Operations - Delegate to Interaction Service
    async def update_interaction_time(
        self, child_id: str, additional_time: int
    ) -> bool:
        """Update interaction time - delegated to interaction service"""
        return await self.interaction_service.update_interaction_time(
            child_id, additional_time
        )

    async def get_children_over_time_limit(self) -> List[Child]:
        """Get children over time limit - delegated to interaction service"""
        return await self.interaction_service.get_children_over_limit()

    # Family Operations - Delegate to Family Service
    async def get_children_by_family(self, family_code: str) -> List[Child]:
        """Get children by family - delegated to search service"""
        return await self.search_service.search_by_family(family_code)

    async def get_children_needing_attention(self) -> List[Child]:
        """Get children needing attention - delegated to search service"""
        return await self.search_service.search_children_needing_attention()

    # Bulk Operations - Delegate to Bulk Operations Service
    async def bulk_update_settings(self, updates: List[Dict[str, Any]]):
        """Bulk update settings - delegated to bulk operations service"""
        return await self.bulk_operations_service.bulk_update_settings(updates)

    async def aggregate(
        self,
        field: str,
        operation: str,
        criteria: Optional[List[SearchCriteria]] = None,
    ) -> Any:
        """Aggregate data - delegated to bulk operations service"""
        return await self.bulk_operations_service.aggregate_data(
            field, operation, criteria
        )

    # ========== BACKWARD COMPATIBILITY METHODS ==========

    async def add(self, child: Child) -> Child:
        """Backward compatibility alias for create"""
        return await self.create(child)

    async def get(self, child_id: str) -> Optional[Child]:
        """Backward compatibility alias for get_by_id"""
        return await self.get_by_id(child_id)

    # ========== HELPER METHODS ==========

    def _serialize_child_for_db(self, child: Child) -> Dict[str, Any]:
        """Serialize child entity for database storage"""
        data = child.dict() if hasattr(child, "dict") else child.__dict__.copy()

        if not data.get("id"):
            data["id"] = str(uuid.uuid4())

        # Serialize complex fields to JSON
        json_fields = [
            "interests",
            "personality_traits",
            "learning_preferences",
            "allowed_topics",
            "restricted_topics",
            "parental_controls",
            "emergency_contacts",
            "privacy_settings",
            "custom_settings",
        ]

        for field in json_fields:
            if field in data and data[field] is not None:
                data[field] = json.dumps(data[field])

        # Handle datetime fields
        if "date_of_birth" in data and isinstance(data["date_of_birth"], datetime):
            data["date_of_birth"] = data["date_of_birth"].date().isoformat()

        # Set updated_at timestamp
        data["updated_at"] = datetime.now().isoformat()

        return data

    def _deserialize_child_from_db(self, data: Dict[str, Any]) -> Child:
        """Deserialize child data from database"""
        json_fields = [
            "interests",
            "personality_traits",
            "learning_preferences",
            "allowed_topics",
            "restricted_topics",
            "parental_controls",
            "emergency_contacts",
            "privacy_settings",
            "custom_settings",
        ]

        for field in json_fields:
            if field in data and data[field]:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = [] if field.endswith("s") else {}
            else:
                data[field] = [] if field.endswith("s") else {}

        # Parse datetime fields
        datetime_fields = ["created_at", "updated_at", "last_interaction"]
        for field in datetime_fields:
            if field in data and data[field]:
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except (ValueError, TypeError):
                    data[field] = None

        # Parse date fields
        if "date_of_birth" in data and data["date_of_birth"]:
            try:
                data["date_of_birth"] = datetime.fromisoformat(
                    data["date_of_birth"]
                ).date()
            except (ValueError, TypeError):
                data["date_of_birth"] = None

        # Convert boolean fields
        if "is_active" in data:
            data["is_active"] = bool(data["is_active"])

        return Child(**data)
