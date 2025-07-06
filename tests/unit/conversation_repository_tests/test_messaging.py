import pytest


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
            created_conversation.id, "user", "This is a new message", {
                "test": True}
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
