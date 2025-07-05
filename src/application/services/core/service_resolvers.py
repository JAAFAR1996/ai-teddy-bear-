from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import strawberry
from strawberry.federation import Key

from .child_service_resolvers import Child, Conversation, ChildServiceResolvers, ContentFilterLevel, DifficultyLevel, SafetySettings, ChildPreferences
from .ai_service_resolvers import AIServiceResolvers, EmotionType, LearningStyle, PersonalityTrait, AIProfile, EmotionSnapshot, LearningProgress, ConversationAnalysis
from .monitoring_service_resolvers import MonitoringServiceResolvers, UsageStatistics, HealthMetrics, PerformanceMetrics
from .safety_service_resolvers import SafetyServiceResolvers, RiskLevel, SafetyProfile, RiskAssessment, SafetyCheck


class EntityResolver:
    @staticmethod
    def resolve_entities(representations: List[Dict[str, Any]]) -> List[Any]:
        entities = []
        for representation in representations:
            typename = representation.get("__typename")
            entity_id = representation.get("id")
            if typename == "Child":
                entities.append(Child.resolve_reference(entity_id))
            elif typename == "Conversation":
                entities.append(Conversation.resolve_reference(entity_id))
            else:
                entities.append(None)
        return entities


@strawberry.type
class Query:
    @strawberry.field
    async def child(self, id: strawberry.ID) -> Optional[Child]:
        return await ChildServiceResolvers.get_child(id)

    @strawberry.field
    async def children(self, parent_id: strawberry.ID) -> List[Child]:
        return await ChildServiceResolvers.get_children(parent_id)

    @strawberry.field
    async def ai_profile(self, child_id: strawberry.ID) -> Optional[AIProfile]:
        return await AIServiceResolvers.get_ai_profile(child_id)

    @strawberry.field
    async def usage_statistics(self, child_id: strawberry.ID, period: str) -> UsageStatistics:
        return await MonitoringServiceResolvers.get_usage_statistics(child_id, period)

    @strawberry.field
    async def safety_profile(self, child_id: strawberry.ID) -> SafetyProfile:
        return await SafetyServiceResolvers.get_safety_profile(child_id)


@strawberry.type
class Mutation:
    @strawberry.field
    async def update_child_preferences(self, child_id: strawberry.ID, preferences: Dict[str, Any]) -> bool:
        return True

    @strawberry.field
    async def record_emotion(self, child_id: strawberry.ID, emotion: EmotionType, intensity: float) -> EmotionSnapshot:
        return EmotionSnapshot(timestamp=datetime.now(), emotion=emotion, intensity=intensity, context="Manual recording")

    @strawberry.field
    async def perform_safety_check(self, child_id: strawberry.ID) -> SafetyCheck:
        return SafetyCheck(passed=True, score=0.96, timestamp=datetime.now(), review_required=False)


schema = strawberry.federation.Schema(
    query=Query, mutation=Mutation, enable_federation_2=True)
