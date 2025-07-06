import pytest


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
