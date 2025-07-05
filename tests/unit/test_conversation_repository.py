#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Conversation Repository
Tests all CRUD operations, analytics, search functionality, and advanced features
"""

import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from src.domain.entities.conversation import (
    ContentType,
    Conversation,
    EmotionalState,
    InteractionType,
    Message,
    MessageRole,
)

# Import our modules
from src.infrastructure.persistence.conversation_sqlite_repository import (
    ConversationSQLiteRepository,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def mock_session_factory():
    """Mock session factory for testing"""
    return Mock()


@pytest.fixture
def conversation_repository(temp_db, mock_session_factory):
    """Create a Conversation repository instance for testing"""
    repo = ConversationSQLiteRepository(mock_session_factory, temp_db)
    return repo


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing"""
    return {
        "id": "test-conv-001",
        "session_id": "session-123",
        "child_id": "child-456",
        "parent_id": "parent-789",
        "start_time": datetime.now() - timedelta(minutes=30),
        "end_time": datetime.now() - timedelta(minutes=15),
        "duration_seconds": 900,  # 15 minutes
        "interaction_type": InteractionType.LEARNING,
        "topics": ["math", "science", "problem_solving"],
        "primary_language": "en",
        "quality_score": 0.85,
        "safety_score": 1.0,
        "educational_score": 0.9,
        "engagement_score": 0.8,
        "llm_provider": "openai",
        "model_version": "gpt-4",
        "context_summary": "Educational conversation about basic math and science concepts",
        "metadata": {"user_agent": "TeddyBear/1.0", "ip_address": "192.168.1.1"},
        "total_messages": 12,
        "child_messages": 6,
        "assistant_messages": 6,
        "questions_asked": 3,
        "moderation_flags": 0,
        "parent_visible": True,
        "archived": False,
    }


@pytest.fixture
def sample_messages():
    """Sample messages for testing"""
    return [
        Message(
            id="msg-001",
            role=MessageRole.USER,
            content="Hi, can you help me with math?",
            content_type=ContentType.TEXT,
            sequence_number=0,
            timestamp=datetime.now() - timedelta(minutes=29),
            metadata={"input_method": "voice"},
        ),
        Message(
            id="msg-002",
            role=MessageRole.ASSISTANT,
            content="Of course! I'd love to help you with math. What would you like to learn about?",
            content_type=ContentType.TEXT,
            sequence_number=1,
            timestamp=datetime.now() - timedelta(minutes=28),
            sentiment_score=0.8,
            confidence_score=0.95,
        ),
        Message(
            id="msg-003",
            role=MessageRole.USER,
            content="I want to learn about addition",
            content_type=ContentType.TEXT,
            sequence_number=2,
            timestamp=datetime.now() - timedelta(minutes=27),
            metadata={"topic_detected": "addition"},
        ),
    ]


@pytest.fixture
def sample_emotional_states():
    """Sample emotional states for testing"""
    return [
        EmotionalState(
            id="emotion-001",
            primary_emotion="curious",
            confidence=0.85,
            secondary_emotions=[{"emotion": "excited", "confidence": 0.6}],
            arousal_level=0.6,
            valence_level=0.8,
            emotional_context="Child showing interest in learning",
            analysis_method="hume",
        ),
        EmotionalState(
            id="emotion-002",
            primary_emotion="happy",
            confidence=0.9,
            secondary_emotions=[{"emotion": "confident", "confidence": 0.7}],
            arousal_level=0.7,
            valence_level=0.9,
            emotional_context="Child excited about solving problems",
            analysis_method="hume",
        ),
    ]


@pytest.fixture
def sample_conversation(
    sample_conversation_data, sample_messages, sample_emotional_states
):
    """Create a sample Conversation entity"""
    conversation = Conversation(**sample_conversation_data)
    conversation.messages = sample_messages
    conversation.emotional_states = sample_emotional_states

    # Link messages and emotional states to conversation
    for msg in conversation.messages:
        msg.conversation_id = conversation.id
    for state in conversation.emotional_states:
        state.conversation_id = conversation.id

    return conversation


class TestConversationRepositoryBasicOperations:
    """Test basic CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_conversation(
        self, conversation_repository, sample_conversation
    ):
        """Test creating a new conversation"""
        # Act
        result = await conversation_repository.create(sample_conversation)

        # Assert
        pytest.assume(result is not None)
        pytest.assume(result.id is not None)
        pytest.assume(result.child_id == sample_conversation.child_id)
        pytest.assume(result.session_id == sample_conversation.session_id)
        pytest.assume(result.topics == sample_conversation.topics)

    @pytest.mark.asyncio
    async def test_get_conversation_by_id(
        self, conversation_repository, sample_conversation
    ):
        """Test retrieving a conversation by ID"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        retrieved_conversation = await conversation_repository.get_by_id(
            created_conversation.id
        )

        # Assert
        pytest.assume(retrieved_conversation is not None)
        pytest.assume(retrieved_conversation.id == created_conversation.id)
        pytest.assume(retrieved_conversation.child_id ==
                      sample_conversation.child_id)
        pytest.assume(len(retrieved_conversation.messages)
                      == len(sample_conversation.messages))
        pytest.assume(
            len(retrieved_conversation.emotional_states)
            == len(sample_conversation.emotional_states)
        )

    @pytest.mark.asyncio
    async def test_get_conversation_by_session_id(
        self, conversation_repository, sample_conversation
    ):
        """Test retrieving a conversation by session ID"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        retrieved_conversation = await conversation_repository.get_by_session_id(
            sample_conversation.session_id
        )

        # Assert
        pytest.assume(retrieved_conversation is not None)
        pytest.assume(
            retrieved_conversation.session_id == sample_conversation.session_id
        )
        pytest.assume(retrieved_conversation.id == created_conversation.id)

    @pytest.mark.asyncio
    async def test_update_conversation(
        self, conversation_repository, sample_conversation
    ):
        """Test updating an existing conversation"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)
        created_conversation.quality_score = 0.95
        created_conversation.context_summary = "Updated summary"
        created_conversation.topics.append("new_topic")

        # Act
        updated_conversation = await conversation_repository.update(
            created_conversation
        )

        # Assert
        pytest.assume(updated_conversation.quality_score == 0.95)
        pytest.assume(
            updated_conversation.context_summary == "Updated summary")
        pytest.assume("new_topic" in updated_conversation.topics)

    @pytest.mark.asyncio
    async def test_delete_conversation(
        self, conversation_repository, sample_conversation
    ):
        """Test archiving a conversation (soft delete)"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        delete_result = await conversation_repository.delete(created_conversation.id)

        # Assert
        pytest.assume(delete_result is True)

        # Verify conversation is archived
        retrieved_conversation = await conversation_repository.get_by_id(
            created_conversation.id
        )
        # Should not be found because it's archived
        pytest.assume(retrieved_conversation is None)


class TestConversationRepositoryMessaging:
    """Test message management functionality"""

    @pytest.mark.asyncio
    async def test_add_message_to_conversation(
        self, conversation_repository, sample_conversation
    ):
        """Test adding a single message to an existing conversation"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)
        initial_message_count = created_conversation.total_messages

        # Act
        success = await conversation_repository.add_message_to_conversation(
            created_conversation.id, "user", "This is a new message", {"test": True}
        )

        # Assert
        pytest.assume(success is True)

        # Verify message was added
        updated_conversation = await conversation_repository.get_by_id(
            created_conversation.id
        )
        pytest.assume(updated_conversation.total_messages ==
                      initial_message_count + 1)

    @pytest.mark.asyncio
    async def test_end_conversation(
            self,
            conversation_repository,
            sample_conversation):
        """Test ending a conversation"""
        # Arrange
        sample_conversation.end_time = None  # Make it an active conversation
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        success = await conversation_repository.end_conversation(
            created_conversation.id
        )

        # Assert
        pytest.assume(success is True)

        # Verify conversation was ended
        updated_conversation = await conversation_repository.get_by_id(
            created_conversation.id
        )
        pytest.assume(updated_conversation.end_time is not None)
        pytest.assume(updated_conversation.duration_seconds > 0)


class TestConversationRepositorySearch:
    """Test search and filtering functionality"""

    @pytest.mark.asyncio
    async def test_get_conversations_by_child(self, conversation_repository):
        """Test finding conversations by child ID"""
        # Arrange
        child_id = "test-child-123"
        conversations = []
        for i in range(3):
            conv = Conversation(
                child_id=child_id,
                session_id=f"session-{i}",
                start_time=datetime.now() - timedelta(hours=i),
                topics=[f"topic-{i}"],
                messages=[],
                emotional_states=[],
            )
            conversations.append(await conversation_repository.create(conv))

        # Act
        child_conversations = await conversation_repository.get_conversations_by_child(
            child_id
        )

        # Assert
        pytest.assume(len(child_conversations) >= 3)
        pytest.assume(
            all(conv.child_id == child_id for conv in child_conversations))

    @pytest.mark.asyncio
    async def test_get_conversations_by_topics(self, conversation_repository):
        """Test finding conversations by topics"""
        # Arrange
        conversations = [
            Conversation(
                child_id="child-1",
                topics=["math", "science"],
                messages=[],
                emotional_states=[],
            ),
            Conversation(
                child_id="child-2",
                topics=["art", "creativity"],
                messages=[],
                emotional_states=[],
            ),
            Conversation(
                child_id="child-3",
                topics=["math", "games"],
                messages=[],
                emotional_states=[],
            ),
        ]

        for conv in conversations:
            await conversation_repository.create(conv)

        # Act
        math_conversations = await conversation_repository.get_conversations_by_topics(
            ["math"]
        )

        # Assert
        pytest.assume(len(math_conversations) >= 2)
        for conv in math_conversations:
            pytest.assume("math" in conv.topics)

    @pytest.mark.asyncio
    async def test_find_conversations_with_emotion(
        self, conversation_repository, sample_conversation
    ):
        """Test finding conversations containing specific emotions"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        happy_conversations = (
            await conversation_repository.find_conversations_with_emotion(
                "happy", confidence_threshold=0.8
            )
        )

        # Assert
        pytest.assume(len(happy_conversations) >= 1)
        found_conversation = next(
            (
                conv
                for conv in happy_conversations
                if conv.id == created_conversation.id
            ),
            None,
        )
        pytest.assume(found_conversation is not None)

    @pytest.mark.asyncio
    async def test_search_conversation_content(
        self, conversation_repository, sample_conversation
    ):
        """Test full-text search in conversation messages"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        search_results = await conversation_repository.search_conversation_content(
            "math"
        )

        # Assert
        pytest.assume(len(search_results) >= 1)
        conversation, messages = search_results[0]
        pytest.assume(conversation.id == created_conversation.id)
        pytest.assume(any("math" in msg.content.lower() for msg in messages))


class TestConversationRepositoryAnalytics:
    """Test analytics and insights functionality"""

    @pytest.mark.asyncio
    async def test_get_conversation_summary(
        self, conversation_repository, sample_conversation
    ):
        """Test generating conversation summary"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        summary = await conversation_repository.get_conversation_summary(
            created_conversation.id
        )

        # Assert
        pytest.assume(summary is not None)
        pytest.assume(summary["conversation_id"] == created_conversation.id)
        pytest.assume("quality_scores" in summary)
        pytest.assume("emotional_progression" in summary)
        pytest.assume("role_statistics" in summary)
        pytest.assume("dominant_emotions" in summary)

    @pytest.mark.asyncio
    async def test_get_conversation_analytics(
        self, conversation_repository, sample_conversation
    ):
        """Test generating conversation analytics"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        analytics = await conversation_repository.get_conversation_analytics(
            child_id=sample_conversation.child_id
        )

        # Assert
        pytest.assume(analytics is not None)
        pytest.assume("summary" in analytics)
        pytest.assume("topics" in analytics)
        pytest.assume("quality_metrics" in analytics)
        pytest.assume("safety" in analytics)

    @pytest.mark.asyncio
    async def test_get_conversation_patterns(self, conversation_repository):
        """Test analyzing conversation patterns"""
        # Arrange
        child_id = "pattern-test-child"
        for i in range(5):
            conv = Conversation(
                child_id=child_id,
                start_time=datetime.now() - timedelta(days=i),
                duration_seconds=600 + (i * 60),  # Varying durations
                topics=[f"topic-{i % 3}"],  # Cycling topics
                quality_score=0.7 + (i * 0.05),  # Improving quality
                engagement_score=0.6 + (i * 0.08),
                messages=[],
                emotional_states=[],
            )
            await conversation_repository.create(conv)

        # Act
        patterns = await conversation_repository.get_conversation_patterns(
            child_id, days_back=7
        )

        # Assert
        pytest.assume(patterns["status"] == "success")
        pytest.assume(patterns["total_conversations"] >= 5)
        pytest.assume("avg_duration_minutes" in patterns)
        pytest.assume("most_common_topics" in patterns)
        pytest.assume("conversation_frequency" in patterns)

    @pytest.mark.asyncio
    async def test_get_conversation_health_metrics(
        self, conversation_repository, sample_conversation
    ):
        """Test generating health metrics for a child's conversations"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        health_metrics = await conversation_repository.get_conversation_health_metrics(
            sample_conversation.child_id
        )

        # Assert
        pytest.assume(health_metrics["status"] == "success")
        pytest.assume("health_score" in health_metrics)
        pytest.assume("health_level" in health_metrics)
        pytest.assume("metrics" in health_metrics)
        pytest.assume("emotional_analysis" in health_metrics)
        pytest.assume("recommendations" in health_metrics)


class TestConversationRepositoryMaintenance:
    """Test maintenance and optimization functionality"""

    @pytest.mark.asyncio
    async def test_bulk_archive_old_conversations(
            self, conversation_repository):
        """Test archiving old conversations"""
        # Arrange
        old_conversations = []
        for i in range(3):
            conv = Conversation(
                child_id=f"child-{i}",
                start_time=datetime.now() - timedelta(days=100 + i),  # Very old
                messages=[],
                emotional_states=[],
            )
            old_conversations.append(await conversation_repository.create(conv))

        # Act
        archived_count = await conversation_repository.bulk_archive_old_conversations(
            days_old=90
        )

        # Assert
        pytest.assume(archived_count >= 3)

    @pytest.mark.asyncio
    async def test_get_conversation_metrics_summary(
        self, conversation_repository, sample_conversation
    ):
        """Test getting overall conversation metrics summary"""
        # Arrange
        await conversation_repository.create(sample_conversation)

        # Act
        metrics = await conversation_repository.get_conversation_metrics_summary()

        # Assert
        pytest.assume("total_conversations" in metrics)
        pytest.assume("unique_children_count" in metrics)
        pytest.assume("average_duration_minutes" in metrics)
        pytest.assume("average_quality_score" in metrics)
        pytest.assume("recent_activity_7_days" in metrics)
        pytest.assume("top_interaction_types" in metrics)

    @pytest.mark.asyncio
    async def test_optimize_conversation_performance(
            self, conversation_repository):
        """Test performance optimization analysis"""
        # Arrange - Create some conversations for analysis
        for i in range(5):
            conv = Conversation(
                child_id=f"child-{i}",
                start_time=datetime.now() - timedelta(days=i),
                duration_seconds=300 + (i * 100),
                total_messages=5 + i,
                quality_score=0.8 + (i * 0.02),
                safety_score=1.0,
                messages=[],
                emotional_states=[],
            )
            await conversation_repository.create(conv)

        # Act
        optimization = await conversation_repository.optimize_conversation_performance()

        # Assert
        pytest.assume("performance_score" in optimization)
        pytest.assume("performance_level" in optimization)
        pytest.assume("statistics" in optimization)
        pytest.assume("optimizations" in optimization)
        pytest.assume("recommendations" in optimization)

    @pytest.mark.asyncio
    async def test_find_conversations_requiring_review(
            self, conversation_repository):
        """Test finding conversations that require review"""
        # Arrange
        flagged_conv = Conversation(
            child_id="child-flagged",
            safety_score=0.7,  # Low safety score
            moderation_flags=3,  # High moderation flags
            messages=[],
            emotional_states=[],
        )
        await conversation_repository.create(flagged_conv)

        # Act
        review_conversations = (
            await conversation_repository.find_conversations_requiring_review()
        )

        # Assert
        pytest.assume(len(review_conversations) >= 1)
        flagged_found = any(
            conv.child_id == "child-flagged" for conv in review_conversations
        )
        pytest.assume(flagged_found)


class TestConversationRepositoryAggregation:
    """Test aggregation functionality"""

    @pytest.mark.asyncio
    async def test_aggregate_count(self, conversation_repository):
        """Test count aggregation"""
        # Arrange
        for i in range(3):
            conv = Conversation(
                child_id=f"child-{i}",
                duration_seconds=300 + (i * 100),
                messages=[],
                emotional_states=[],
            )
            await conversation_repository.create(conv)

        # Act
        count = await conversation_repository.aggregate("duration_seconds", "count")

        # Assert
        pytest.assume(count >= 3)

    @pytest.mark.asyncio
    async def test_aggregate_average_duration(self, conversation_repository):
        """Test average duration calculation"""
        # Arrange
        durations = [300, 600, 900]
        for i, duration in enumerate(durations):
            conv = Conversation(
                child_id=f"child-{i}",
                duration_seconds=duration,
                messages=[],
                emotional_states=[],
            )
            await conversation_repository.create(conv)

        # Act
        avg_duration = await conversation_repository.aggregate(
            "duration_seconds", "avg"
        )

        # Assert
        pytest.assume(avg_duration > 0)


class TestConversationRepositoryErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_get_nonexistent_conversation(self, conversation_repository):
        """Test retrieving a non-existent conversation"""
        # Act
        result = await conversation_repository.get_by_id("nonexistent-id")

        # Assert
        pytest.assume(result is None)

    @pytest.mark.asyncio
    async def test_update_nonexistent_conversation(
            self, conversation_repository):
        """Test updating a non-existent conversation"""
        # Arrange
        fake_conversation = Conversation(
            id="nonexistent-id",
            child_id="child-123",
            messages=[],
            emotional_states=[])

        # Act & Assert
        with pytest.raises(ValueError, match="No conversation found"):
            await conversation_repository.update(fake_conversation)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_conversation(
            self, conversation_repository):
        """Test deleting a non-existent conversation"""
        # Act
        result = await conversation_repository.delete("nonexistent-id")

        # Assert
        pytest.assume(result is False)

    @pytest.mark.asyncio
    async def test_add_message_to_nonexistent_conversation(
        self, conversation_repository
    ):
        """Test adding a message to a non-existent conversation"""
        # Act
        success = await conversation_repository.add_message_to_conversation(
            "nonexistent-id", "user", "test message"
        )

        # Assert
        pytest.assume(success is False)  # Should fail gracefully

    @pytest.mark.asyncio
    async def test_get_health_metrics_no_data(self, conversation_repository):
        """Test getting health metrics when no data exists"""
        # Act
        result = await conversation_repository.get_conversation_health_metrics(
            "nonexistent-child"
        )

        # Assert
        pytest.assume(result["status"] == "no_data")
        pytest.assume(result["child_id"] == "nonexistent-child")


class TestConversationRepositoryIntegration:
    """Integration tests with complete conversation lifecycle"""

    @pytest.mark.asyncio
    async def test_conversation_lifecycle(
        self, conversation_repository, sample_conversation
    ):
        """Test complete conversation lifecycle"""
        # Create
        created_conversation = await conversation_repository.create(sample_conversation)
        pytest.assume(created_conversation.id is not None)

        # Add messages
        success = await conversation_repository.add_message_to_conversation(
            created_conversation.id, "user", "Additional message"
        )
        pytest.assume(success is True)

        # Update
        created_conversation.quality_score = 0.95
        updated_conversation = await conversation_repository.update(
            created_conversation
        )
        pytest.assume(updated_conversation.quality_score == 0.95)

        # Get summary
        summary = await conversation_repository.get_conversation_summary(
            created_conversation.id
        )
        pytest.assume(summary is not None)

        # End conversation
        end_success = await conversation_repository.end_conversation(
            created_conversation.id
        )
        pytest.assume(end_success is True)

        # Archive (soft delete)
        delete_result = await conversation_repository.delete(created_conversation.id)
        pytest.assume(delete_result is True)

        # Verify archived
        archived_conversation = await conversation_repository.get_by_id(
            created_conversation.id
        )
        pytest.assume(archived_conversation is None)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
