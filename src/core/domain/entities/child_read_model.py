from typing import Any, Dict, List, Optional

"""
📊 Child Read Model Implementation
=================================

CQRS Read Models for optimized child data queries.
Provides materialized views and projections from domain events.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...domain.events.child_events import ChildProfileUpdated, ChildRegistered, SafetyViolationDetected
from ...domain.events.conversation_events import ConversationEnded, ConversationStarted, MessageReceived
from ...shared.kernel import DomainEvent

logger = logging.getLogger(__name__)


@dataclass
class ChildReadModel:
    """Read model for child entity optimized for queries"""

    id: str
    parent_id: str
    device_id: str
    name: str
    age: int
    udid: str
    created_at: datetime
    updated_at: datetime

    # Computed fields for queries
    conversation_count: int = 0
    total_messages: int = 0
    safety_violations_count: int = 0
    last_interaction_at: Optional[datetime] = None
    safety_score: float = 100.0
    engagement_level: str = "new"

    # Profile completeness
    profile_completeness: float = 0.0
    preferences: Dict[str, Any] = field(default_factory=dict)
    learning_metrics: Dict[str, Any] = field(default_factory=dict)

    # Safety tracking
    last_safety_check: Optional[datetime] = None
    safety_status: str = "safe"
    flagged_content_count: int = 0


@dataclass
class ConversationSummaryReadModel:
    """Read model for conversation summaries"""

    id: str
    child_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    message_count: int = 0
    topic: Optional[str] = None
    engagement_score: float = 0.0
    flagged: bool = False
    safety_violations: List[str] = field(default_factory=list)


@dataclass
class SafetyMetricsReadModel:
    """Read model for safety metrics"""

    child_id: str
    total_violations: int = 0
    high_severity_violations: int = 0
    last_violation_date: Optional[datetime] = None
    violation_categories: Dict[str, int] = field(default_factory=dict)
    safety_trend: str = "stable"  # improving, stable, declining
    parent_notifications_sent: int = 0


class ChildProjectionManager:
    """Manages child-related projections from domain events"""

    def __init__(self):
        self.read_models: Dict[str, ChildReadModel] = {}
        self.conversation_summaries: Dict[str, ConversationSummaryReadModel] = {}
        self.safety_metrics: Dict[str, SafetyMetricsReadModel] = {}

    async def handle_event(self, event: DomainEvent) -> None:
        """Handle domain event and update read models"""

        if isinstance(event, ChildRegistered):
            await self._handle_child_registered(event)
        elif isinstance(event, ChildProfileUpdated):
            await self._handle_child_profile_updated(event)
        elif isinstance(event, SafetyViolationDetected):
            await self._handle_safety_violation(event)
        elif isinstance(event, ConversationStarted):
            await self._handle_conversation_started(event)
        elif isinstance(event, ConversationEnded):
            await self._handle_conversation_ended(event)
        elif isinstance(event, MessageReceived):
            await self._handle_message_received(event)

    async def _handle_child_registered(self, event: ChildRegistered) -> None:
        """Handle child registration event"""

        child_id = str(event.child_id)

        read_model = ChildReadModel(
            id=child_id,
            parent_id=str(event.parent_id),
            device_id=str(event.device_id),
            name=event.name,
            age=event.age,
            udid=event.udid,
            created_at=event.registered_at,
            updated_at=event.registered_at,
        )

        # Calculate initial profile completeness
        read_model.profile_completeness = self._calculate_profile_completeness(read_model)

        self.read_models[child_id] = read_model

        # Initialize safety metrics
        self.safety_metrics[child_id] = SafetyMetricsReadModel(child_id=child_id)

        logger.info(f"Child read model created for {child_id}")

    async def _handle_child_profile_updated(self, event: ChildProfileUpdated) -> None:
        """Handle profile update event"""

        child_id = str(event.child_id)
        read_model = self.read_models.get(child_id)

        if not read_model:
            logger.warning(f"Child read model not found: {child_id}")
            return

        # Apply changes
        for key, value in event.changes.items():
            if hasattr(read_model, key):
                setattr(read_model, key, value)

        read_model.updated_at = event.updated_at
        read_model.profile_completeness = self._calculate_profile_completeness(read_model)

        logger.info(f"Child read model updated for {child_id}")

    async def _handle_safety_violation(self, event: SafetyViolationDetected) -> None:
        """Handle safety violation event"""

        child_id = str(event.child_id)

        # Update child read model
        child_model = self.read_models.get(child_id)
        if child_model:
            child_model.safety_violations_count += 1
            child_model.safety_score = max(0, child_model.safety_score - 10)
            child_model.safety_status = self._calculate_safety_status(child_model.safety_score)
            child_model.last_safety_check = event.occurred_at

        # Update safety metrics
        safety_metrics = self.safety_metrics.get(child_id)
        if not safety_metrics:
            safety_metrics = SafetyMetricsReadModel(child_id=child_id)
            self.safety_metrics[child_id] = safety_metrics

        safety_metrics.total_violations += 1
        safety_metrics.last_violation_date = event.occurred_at

        if event.severity == "high":
            safety_metrics.high_severity_violations += 1

        # Update violation categories
        category = event.violation_type
        safety_metrics.violation_categories[category] = safety_metrics.violation_categories.get(category, 0) + 1

        logger.warning(f"Safety violation recorded for child {child_id}")

    async def _handle_conversation_started(self, event: ConversationStarted) -> None:
        """Handle conversation started event"""

        conversation_id = str(event.conversation_id)
        child_id = str(event.child_id)

        # Create conversation summary
        summary = ConversationSummaryReadModel(
            id=conversation_id, child_id=child_id, started_at=event.started_at, topic=event.initial_topic
        )

        self.conversation_summaries[conversation_id] = summary

        # Update child read model
        child_model = self.read_models.get(child_id)
        if child_model:
            child_model.conversation_count += 1
            child_model.last_interaction_at = event.started_at
            child_model.engagement_level = self._calculate_engagement_level(child_model)

        logger.info(f"Conversation started: {conversation_id}")

    async def _handle_conversation_ended(self, event) -> None:
        """Handle conversation ended event"""

        conversation_id = str(event.conversation_id)
        summary = self.conversation_summaries.get(conversation_id)

        if summary:
            summary.ended_at = event.ended_at
            if summary.started_at:
                duration = event.ended_at - summary.started_at
                summary.duration_minutes = duration.total_seconds() / 60

        logger.info(f"Conversation ended: {conversation_id}")

    async def _handle_message_received(self, event) -> None:
        """Handle message received event"""

        conversation_id = str(event.conversation_id)
        child_id = str(event.child_id)

        # Update conversation summary
        summary = self.conversation_summaries.get(conversation_id)
        if summary:
            summary.message_count += 1

        # Update child read model
        child_model = self.read_models.get(child_id)
        if child_model:
            child_model.total_messages += 1
            child_model.last_interaction_at = event.received_at

    def _calculate_profile_completeness(self, read_model: ChildReadModel) -> float:
        """Calculate profile completeness percentage"""

        required_fields = ["name", "age", "parent_id", "device_id"]
        optional_fields = ["preferences"]

        required_score = sum(1 for field in required_fields if getattr(read_model, field, None))
        optional_score = 1 if read_model.preferences else 0

        total_score = (required_score / len(required_fields)) * 0.8 + (optional_score / len(optional_fields)) * 0.2

        return round(total_score * 100, 1)

    def _calculate_safety_status(self, safety_score: float) -> str:
        """Calculate safety status from score"""

        if safety_score >= 90:
            return "safe"
        elif safety_score >= 70:
            return "caution"
        else:
            return "warning"

    def _calculate_engagement_level(self, read_model: ChildReadModel) -> str:
        """Calculate engagement level"""

        if read_model.conversation_count == 0:
            return "new"
        elif read_model.conversation_count < 5:
            return "learning"
        elif read_model.conversation_count < 20:
            return "engaged"
        else:
            return "active"

    # Query methods for read models
    def get_child_read_model(self, child_id: str) -> Optional[ChildReadModel]:
        """Get child read model by ID"""
        return self.read_models.get(child_id)

    def get_children_by_parent(self, parent_id: str) -> List[ChildReadModel]:
        """Get all children for a parent"""
        return [model for model in self.read_models.values() if model.parent_id == parent_id]

    def get_conversation_summary(self, conversation_id: str) -> Optional[ConversationSummaryReadModel]:
        """Get conversation summary by ID"""
        return self.conversation_summaries.get(conversation_id)

    def get_safety_metrics(self, child_id: str) -> Optional[SafetyMetricsReadModel]:
        """Get safety metrics for child"""
        return self.safety_metrics.get(child_id)

    def search_children(
        self, name_pattern: Optional[str] = None, age_range: Optional[tuple] = None, parent_id: Optional[str] = None
    ) -> List[ChildReadModel]:
        """Search children by criteria"""

        results = list(self.read_models.values())

        if name_pattern:
            results = [r for r in results if name_pattern.lower() in r.name.lower()]

        if age_range:
            min_age, max_age = age_range
            results = [r for r in results if min_age <= r.age <= max_age]

        if parent_id:
            results = [r for r in results if r.parent_id == parent_id]

        return results

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get overall analytics summary"""

        total_children = len(self.read_models)
        total_conversations = len(self.conversation_summaries)
        total_violations = sum(m.total_violations for m in self.safety_metrics.values())

        return {
            "total_children": total_children,
            "total_conversations": total_conversations,
            "total_safety_violations": total_violations,
            "average_engagement": self._calculate_average_engagement(),
            "safety_status_distribution": self._get_safety_status_distribution(),
        }

    def _calculate_average_engagement(self) -> float:
        """Calculate average engagement score"""

        if not self.read_models:
            return 0.0

        total_conversations = sum(m.conversation_count for m in self.read_models.values())
        return total_conversations / len(self.read_models)

    def _get_safety_status_distribution(self) -> Dict[str, int]:
        """Get distribution of safety statuses"""

        distribution = {"safe": 0, "caution": 0, "warning": 0}

        for model in self.read_models.values():
            status = model.safety_status
            if status in distribution:
                distribution[status] += 1

        return distribution


# Global projection manager instance
_projection_manager: Optional[ChildProjectionManager] = None


def get_child_projection_manager() -> ChildProjectionManager:
    """Get global child projection manager"""
    global _projection_manager
    if not _projection_manager:
        _projection_manager = ChildProjectionManager()
    return _projection_manager
