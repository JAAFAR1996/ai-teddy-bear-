"""Conversation service implementing interaction business logic."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from ...domain.entities.child import Child
from ...domain.entities.conversation import (Content, ContentType,
                                             Conversation, InteractionType,
                                             Message)
from ...domain.repositories.conversation_repository import \
    ConversationRepository
from .base_service import BaseService


class ConversationService(BaseService[Conversation]):
    """Service for managing conversation interactions."""

    def __init__(
        self,
        repository: ConversationRepository,
        logger: logging.Logger = None,
        content_retention_days: int = 30,
        max_conversation_duration: int = 30,  # minutes
    ):
        """Initialize conversation service."""
        super().__init__(repository, logger)
        self._repository: ConversationRepository = repository
        self.content_retention_days = content_retention_days
        self.max_conversation_duration = max_conversation_duration

    async def start_conversation(
        self, child: Child, initial_message: Optional[str] = None
    ) -> Conversation:
        """Start a new conversation."""
        if not await self._validate_child_consent(child):
            raise ValueError("Child lacks necessary consent for interaction")

        conversation = Conversation(
            child_id=child.id,
            metadata={
                "language": child.preferences.language,
                "interaction_style": child.preferences.interaction_style,
            },
        )

        if initial_message:
            conversation.add_message(
                content=initial_message,
                content_type=ContentType.TEXT,
                interaction_type=InteractionType.CHILD_TO_AI,
            )

        await self._log_operation(
            "start_conversation", conversation.id, {"child_id": str(child.id)}
        )
        return await self.create(conversation)

    async def add_child_message(
        self,
        conversation_id: UUID,
        content: str,
        content_type: ContentType = ContentType.TEXT,
        emotion: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Conversation:
        """Add a child's message to the conversation."""
        conversation = await self.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")

        if not conversation.is_active:
            raise ValueError("Conversation has expired")

        await self._repository.add_message(
            conversation_id=conversation_id,
            content=content,
            content_type=content_type,
            interaction_type=InteractionType.CHILD_TO_AI,
            emotion=emotion,
            metadata=metadata,
        )

        await self._log_operation(
            "add_child_message",
            conversation_id,
            {"content_type": content_type.value, "emotion": emotion},
        )
        return await self.get(conversation_id)

    async def add_ai_response(
        self, conversation_id: UUID, response: str, metadata: Optional[dict] = None
    ) -> Conversation:
        """Add AI's response to the conversation."""
        conversation = await self.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")

        await self._repository.add_message(
            conversation_id=conversation_id,
            content=response,
            content_type=ContentType.TEXT,
            interaction_type=InteractionType.AI_TO_CHILD,
            metadata=metadata,
        )

        await self._log_operation("add_ai_response", conversation_id)
        return await self.get(conversation_id)

    async def get_conversation_context(
        self, conversation_id: UUID, message_limit: int = 5
    ) -> str:
        """Get recent conversation context for AI processing."""
        return await self._repository.get_conversation_context(
            conversation_id, message_limit
        )

    async def analyze_emotion_trends(
        self, conversation_id: UUID
    ) -> List[Tuple[datetime, str]]:
        """Analyze emotion trends in the conversation."""
        return await self._repository.get_emotion_timeline(conversation_id)

    async def get_child_conversations(
        self,
        child_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Conversation]:
        """Get conversations for a specific child."""
        return await self._repository.find_by_child(
            child_id, start_date, end_date, limit
        )

    async def archive_conversation(self, conversation_id: UUID, reason: str) -> bool:
        """Archive a conversation."""
        result = await self._repository.archive_conversation(conversation_id, reason)
        await self._log_operation(
            "archive_conversation", conversation_id, {"reason": reason}
        )
        return result

    async def get_flagged_content(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[dict]:
        """Get conversations with flagged content."""
        return await self._repository.get_flagged_content(start_date, end_date)

    async def search_conversations(
        self,
        keyword: str,
        content_type: Optional[ContentType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Conversation]:
        """Search conversations by content."""
        return await self._repository.find_by_content(
            keyword, content_type, start_date, end_date
        )

    async def get_conversation_metrics(self, conversation_id: UUID) -> dict:
        """Get interaction metrics for a conversation."""
        return await self._repository.get_interaction_metrics(conversation_id)

    async def clean_old_conversations(self) -> int:
        """Clean up conversations older than retention period."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.content_retention_days)
        count = 0

        # Get conversations older than cutoff date
        old_conversations = await self._repository.find_by_content(
            keyword="", end_date=cutoff_date
        )

        for conv in old_conversations:
            await self.archive_conversation(
                conv.id, f"Automated cleanup - Age > {self.content_retention_days} days"
            )
            count += 1

        await self._log_operation(
            "clean_old_conversations",
            details={"cleaned_count": count, "cutoff_date": cutoff_date.isoformat()},
        )
        return count

    async def get_similar_conversations(
        self, conversation_id: UUID, limit: int = 5
    ) -> List[Conversation]:
        """Find similar conversations based on content."""
        return await self._repository.get_similar_conversations(conversation_id, limit)
