from typing import Any, Dict, List, Optional

"""
👶 Child Queries Implementation
==============================

CQRS Queries for child-related read operations with optimized read models.
Handles child profile queries, safety reports, and analytics.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from .query_bus import Query, QueryHandler, QueryResult, get_query_bus

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetChildProfileQuery(Query):
    """Query to get child profile"""

    query_id: str
    timestamp: datetime
    child_id: str
    user_id: Optional[str] = None


@dataclass(frozen=True)
class GetChildrenByParentQuery(Query):
    """Query to get all children for a parent"""

    query_id: str
    timestamp: datetime
    parent_id: str
    page: int = 1
    page_size: int = 10
    user_id: Optional[str] = None


@dataclass(frozen=True)
class GetChildSafetyReportQuery(Query):
    """Query to get child safety report"""

    query_id: str
    timestamp: datetime
    child_id: str
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    user_id: Optional[str] = None


@dataclass(frozen=True)
class GetChildAnalyticsQuery(Query):
    """Query to get child analytics and insights"""

    query_id: str
    timestamp: datetime
    child_id: str
    period_days: int = 30
    user_id: Optional[str] = None


@dataclass(frozen=True)
class SearchChildrenQuery(Query):
    """Query to search children by criteria"""

    query_id: str
    timestamp: datetime
    search_term: Optional[str] = None
    age_range: Optional[tuple] = None
    parent_id: Optional[str] = None
    page: int = 1
    page_size: int = 20
    user_id: Optional[str] = None


class GetChildProfileQueryHandler(QueryHandler):
    """Handler for child profile query"""

    def __init__(self, read_model_db):
        self.db = read_model_db

    def get_cache_key(self, query: GetChildProfileQuery) -> str:
        """Generate cache key for child profile"""
        return f"child_profile:{query.child_id}"

    def get_cache_duration(self) -> timedelta:
        """Cache duration for child profiles"""
        return timedelta(minutes=30)

    async def handle(self, query: GetChildProfileQuery) -> QueryResult:
        """Handle child profile query"""

        try:
            # Get child profile from read model
            child_data = await self.db.get_by_id("children", query.child_id)

            if not child_data:
                return QueryResult(data=None, metadata={"message": "Child not found"})

            # Enrich with additional data
            enriched_data = await self._enrich_child_profile(child_data)

            return QueryResult(
                data=enriched_data,
                metadata={"cached": True, "query_time": datetime.utcnow().isoformat()},
            )

        except Exception as e:
            logger.error(f"Failed to get child profile: {e}")
            raise

    async def _enrich_child_profile(self, child_data: Dict) -> Dict:
        """Enrich child profile with additional information"""

        child_id = child_data["id"]

        # Get conversation count
        conversations = await self.db.find_many(
            "conversations", filters={"child_id": child_id}
        )

        # Get safety violations count
        violations = await self.db.find_many(
            "safety_violations", filters={"child_id": child_id}
        )

        # Get latest interaction
        interactions = await self.db.find_many(
            "interactions", filters={"child_id": child_id}, limit=1
        )

        enriched_data = child_data.copy()
        enriched_data.update(
            {
                "conversation_count": len(conversations),
                "safety_violations_count": len(violations),
                "last_interaction": interactions[0] if interactions else None,
                "profile_completeness": self._calculate_profile_completeness(
                    child_data
                ),
            }
        )

        return enriched_data

    def _calculate_profile_completeness(self, child_data: Dict) -> float:
        """Calculate profile completeness percentage"""

        required_fields = ["name", "age", "parent_id", "device_id"]
        optional_fields = ["preferences", "learning_style", "interests"]

        required_score = sum(1 for field in required_fields if child_data.get(field))
        optional_score = sum(1 for field in optional_fields if child_data.get(field))

        total_score = (required_score / len(required_fields)) * 0.7 + (
            optional_score / len(optional_fields)
        ) * 0.3

        return round(total_score * 100, 1)


class GetChildrenByParentQueryHandler(QueryHandler):
    """Handler for children by parent query"""

    def __init__(self, read_model_db):
        self.db = read_model_db

    def get_cache_key(self, query: GetChildrenByParentQuery) -> str:
        """Generate cache key for parent's children"""
        return f"parent_children:{query.parent_id}:{query.page}:{query.page_size}"

    def get_cache_duration(self) -> timedelta:
        """Cache duration for parent's children"""
        return timedelta(minutes=15)

    async def handle(self, query: GetChildrenByParentQuery) -> QueryResult:
        """Handle children by parent query"""

        try:
            offset = (query.page - 1) * query.page_size

            # Get children for parent
            children = await self.db.find_many(
                "children",
                filters={"parent_id": query.parent_id},
                limit=query.page_size,
                offset=offset,
            )

            # Get total count for pagination
            all_children = await self.db.find_many(
                "children", filters={"parent_id": query.parent_id}
            )

            # Enrich each child with summary data
            enriched_children = []
            for child in children:
                summary = await self._get_child_summary(child["id"])
                child_with_summary = child.copy()
                child_with_summary.update(summary)
                enriched_children.append(child_with_summary)

            return QueryResult(
                data=enriched_children,
                total_count=len(all_children),
                page=query.page,
                page_size=query.page_size,
                metadata={
                    "parent_id": query.parent_id,
                    "has_more": len(all_children) > offset + query.page_size,
                },
            )

        except Exception as e:
            logger.error(f"Failed to get children by parent: {e}")
            raise

    async def _get_child_summary(self, child_id: str) -> Dict:
        """Get summary information for child"""

        # Get recent conversations
        recent_conversations = await self.db.find_many(
            "conversations", filters={"child_id": child_id}, limit=5
        )

        # Get safety status
        recent_violations = await self.db.find_many(
            "safety_violations", filters={"child_id": child_id}, limit=1
        )

        return {
            "recent_conversations_count": len(recent_conversations),
            "safety_status": "warning" if recent_violations else "safe",
            "last_activity": (
                recent_conversations[0]["created_at"] if recent_conversations else None
            ),
        }


class GetChildSafetyReportQueryHandler(QueryHandler):
    """Handler for child safety report query"""

    def __init__(self, read_model_db):
        self.db = read_model_db

    def get_cache_key(self, query: GetChildSafetyReportQuery) -> str:
        """Generate cache key for safety report"""
        from_date = query.from_date.isoformat() if query.from_date else "all"
        to_date = query.to_date.isoformat() if query.to_date else "all"
        return f"safety_report:{query.child_id}:{from_date}:{to_date}"

    def get_cache_duration(self) -> timedelta:
        """Cache duration for safety reports"""
        return timedelta(hours=1)

    async def handle(self, query: GetChildSafetyReportQuery) -> QueryResult:
        """Handle safety report query"""

        try:
            # Build date filters
            filters = {"child_id": query.child_id}

            if query.from_date:
                filters["created_at__gte"] = query.from_date
            if query.to_date:
                filters["created_at__lte"] = query.to_date

            # Get safety violations
            violations = await self.db.find_many("safety_violations", filters=filters)

            # Get flagged conversations
            flagged_conversations = await self.db.find_many(
                "conversations", filters={**filters, "flagged": True}
            )

            # Generate safety report
            report = self._generate_safety_report(violations, flagged_conversations)

            return QueryResult(
                data=report,
                metadata={
                    "child_id": query.child_id,
                    "report_period": {
                        "from": (
                            query.from_date.isoformat() if query.from_date else None
                        ),
                        "to": query.to_date.isoformat() if query.to_date else None,
                    },
                },
            )

        except Exception as e:
            logger.error(f"Failed to generate safety report: {e}")
            raise

    def _generate_safety_report(
        self, violations: List[Dict], flagged_conversations: List[Dict]
    ) -> Dict:
        """Generate comprehensive safety report"""

        # Categorize violations
        violation_categories = {}
        for violation in violations:
            category = violation.get("violation_type", "unknown")
            if category not in violation_categories:
                violation_categories[category] = []
            violation_categories[category].append(violation)

        # Calculate safety score
        total_interactions = (
            len(flagged_conversations) + 100
        )  # Assume 100 normal interactions
        safety_score = max(0, 100 - (len(violations) * 10))

        return {
            "summary": {
                "total_violations": len(violations),
                "flagged_conversations": len(flagged_conversations),
                "safety_score": safety_score,
                "status": self._get_safety_status(safety_score),
            },
            "violations_by_category": violation_categories,
            "recent_violations": violations[-5:] if violations else [],
            "recommendations": self._get_safety_recommendations(violations),
        }

    def _get_safety_status(self, score: int) -> str:
        """Determine safety status from score"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        else:
            return "needs_attention"

    def _get_safety_recommendations(self, violations: List[Dict]) -> List[str]:
        """Generate safety recommendations"""

        recommendations = []

        if len(violations) > 5:
            recommendations.append(
                "Consider reviewing conversation topics and setting stricter content filters."
            )

        if any(v.get("severity") == "high" for v in violations):
            recommendations.append(
                "High-severity violations detected. Enable immediate parent notifications."
            )

        if not recommendations:
            recommendations.append(
                "Safety status is good. Continue monitoring interactions."
            )

        return recommendations


def register_child_query_handlers() -> Any:
    """Register all child query handlers"""

    query_bus = get_query_bus()

    # Get read model database
    read_model_db = query_bus._db

    # Register handlers
    query_bus.register_handler(
        GetChildProfileQuery, GetChildProfileQueryHandler(read_model_db)
    )

    query_bus.register_handler(
        GetChildrenByParentQuery, GetChildrenByParentQueryHandler(read_model_db)
    )

    query_bus.register_handler(
        GetChildSafetyReportQuery, GetChildSafetyReportQueryHandler(read_model_db)
    )

    logger.info("Child query handlers registered successfully")
