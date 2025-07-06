import pytest

from src.domain.entities.conversation import Conversation


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
