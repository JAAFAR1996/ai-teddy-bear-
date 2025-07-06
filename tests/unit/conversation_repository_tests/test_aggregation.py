import pytest

from src.domain.entities.conversation import Conversation


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
