import pytest


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
