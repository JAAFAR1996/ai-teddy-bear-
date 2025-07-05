"""
🏗️ Child Domain Service
========================

Domain service for complex child-related business operations that don't
naturally belong to a single aggregate or entity.
"""

from typing import Any, Dict, List, Optional

from ....domain.entities import Child, Conversation
from ....domain.value_objects import VoiceProfile
from .conversation_compatibility_assessor import ConversationCompatibilityAssessor, ConversationCompatibilityResult
from .safety_assessor import SafetyAssessor, SafetyAssessmentResult
from .voice_profile_recommender import VoiceProfileRecommender
from .child_aggregate_validator import ChildAggregateValidator


class ChildDomainService:
    """
    Domain service providing complex business operations for Child management.
    This service delegates to specialized classes for each complex operation.
    """

    def __init__(self):
        self.compatibility_assessor = ConversationCompatibilityAssessor()
        self.safety_assessor = SafetyAssessor()
        self.voice_recommender = VoiceProfileRecommender()
        self.aggregate_validator = ChildAggregateValidator()

    def assess_conversation_compatibility(
        self,
        child: Child,
        proposed_topic: str,
        conversation_history: List[Conversation],
    ) -> ConversationCompatibilityResult:
        """
        Assess if a proposed conversation topic is compatible with the child's profile.
        Delegates to ConversationCompatibilityAssessor.
        """
        return self.compatibility_assessor.assess(child, proposed_topic, conversation_history)

    def conduct_comprehensive_safety_assessment(
        self,
        child: Child,
        recent_conversations: List[Conversation],
        parent_feedback: Optional[Dict[str, Any]] = None,
    ) -> SafetyAssessmentResult:
        """
        Conduct a comprehensive safety assessment for a child.
        Delegates to SafetyAssessor.
        """
        return self.safety_assessor.conduct_comprehensive_safety_assessment(
            child, recent_conversations, parent_feedback
        )

    def recommend_voice_profile_adjustments(
        self, child: Child, recent_conversations: List[Conversation]
    ) -> Optional[VoiceProfile]:
        """
        Recommend voice profile adjustments for better engagement.
        Delegates to VoiceProfileRecommender.
        """
        return self.voice_recommender.recommend_adjustments(child, recent_conversations)

    def validate_child_aggregate_consistency(self, child: Child) -> List[str]:
        """
        Validate the consistency of a Child aggregate.
        Delegates to ChildAggregateValidator.
        """
        return self.aggregate_validator.validate(child)
