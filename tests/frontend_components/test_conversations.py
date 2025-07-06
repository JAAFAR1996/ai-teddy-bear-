import pytest


class TestConversations:
    """Test conversations functionality"""

    @pytest.mark.asyncio
    async def test_get_conversations(self, conversation_service):
        """Test fetching conversations list"""
        # Arrange
        conversations = [
            {
                "id": "conv1",
                "childId": "child1",
                "startTime": "2024-01-01T10:00:00Z",
                "duration": 300,
                "summary": "Story about animals",
            },
            {
                "id": "conv2",
                "childId": "child1",
                "startTime": "2024-01-01T14:00:00Z",
                "duration": 450,
                "summary": "Learning numbers",
            },
        ]
        conversation_service.get_conversations.return_value = {
            "conversations": conversations,
            "total": 2,
        }

        # Act
        result = await conversation_service.get_conversations("child1")

        # Assert
        assert result["total"] == 2
        assert len(result["conversations"]) == 2
        assert result["conversations"][0]["id"] == "conv1"

    @pytest.mark.asyncio
    async def test_conversation_details(self, conversation_service):
        """Test fetching conversation details"""
        # Arrange
        conversation_details = {
            "id": "conv1",
            "childId": "child1",
            "startTime": "2024-01-01T10:00:00Z",
            "endTime": "2024-01-01T10:05:00Z",
            "duration": 300,
            "transcript": [
                {
                    "speaker": "child",
                    "text": "Tell me a story",
                    "timestamp": "2024-01-01T10:00:10Z",
                },
                {
                    "speaker": "teddy",
                    "text": "Once upon a time...",
                    "timestamp": "2024-01-01T10:00:15Z",
                },
            ],
            "emotions": [
                {
                    "emotion": "happy",
                    "confidence": 0.85,
                    "timestamp": "2024-01-01T10:00:10Z",
                },
                {
                    "emotion": "excited",
                    "confidence": 0.75,
                    "timestamp": "2024-01-01T10:02:00Z",
                },
            ],
        }
        conversation_service.get_conversation_details.return_value = (
            conversation_details
        )

        # Act
        details = await conversation_service.get_conversation_details("conv1")

        # Assert
        assert details["id"] == "conv1"
        assert details["duration"] == 300
        assert len(details["transcript"]) == 2
        assert len(details["emotions"]) == 2
        assert details["transcript"][0]["speaker"] == "child"

    @pytest.mark.asyncio
    async def test_conversation_search(self, conversation_service):
        """Test conversation search functionality"""
        # Arrange
        search_results = [
            {"id": "conv1", "summary": "Story about cats", "relevance": 0.95},
            {"id": "conv3", "summary": "Cat sounds", "relevance": 0.80},
        ]
        conversation_service.search_conversations.return_value = search_results

        # Act
        results = await conversation_service.search_conversations("cat")

        # Assert
        assert len(results) == 2
        assert results[0]["relevance"] > results[1]["relevance"]
        assert "cat" in results[0]["summary"].lower()
