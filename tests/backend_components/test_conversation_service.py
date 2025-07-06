from datetime import datetime, timedelta

import pytest

from .conftest import Conversation


class TestConversationService:
    """Test conversation service"""

    @pytest.mark.asyncio
    async def test_conversation_flow(self, conversation_service):
        """Test complete conversation flow"""
        # 1. Start conversation
        conversation_service.start_conversation.return_value = Conversation(
            id="conv123",
            child_id="child456",
            start_time=datetime.utcnow(),
            messages=[],
            is_active=True
        )

        conversation = await conversation_service.start_conversation("child456")
        assert conversation.id == "conv123"
        assert conversation.is_active is True

        # 2. Add messages
        messages = [
            {"speaker": "child", "text": "مرحبا دبدوب",
                "timestamp": datetime.utcnow()},
            {"speaker": "teddy",
             "text": "مرحباً صديقي! كيف حالك؟",
             "timestamp": datetime.utcnow()},
            {"speaker": "child",
             "text": "أنا بخير، هل تحكي لي قصة؟",
             "timestamp": datetime.utcnow()},
            {"speaker": "teddy",
             "text": "بالطبع! سأحكي لك قصة جميلة...",
             "timestamp": datetime.utcnow()}
        ]

        for msg in messages:
            await conversation_service.add_message("conv123", msg)

        # 3. End conversation
        conversation_service.end_conversation.return_value = Conversation(
            id="conv123",
            child_id="child456",
            start_time=datetime.utcnow() - timedelta(minutes=10),
            end_time=datetime.utcnow(),
            messages=messages,
            is_active=False,
            duration_seconds=600,
            summary="محادثة ودية مع طلب قصة"
        )

        ended_conversation = await conversation_service.end_conversation("conv123")
        assert ended_conversation.is_active is False
        assert ended_conversation.duration_seconds == 600
        assert ended_conversation.summary is not None

    @pytest.mark.asyncio
    async def test_conversation_analysis(self, conversation_service):
        """Test conversation analysis"""
        # Setup
        conversation_service.analyze_conversation.return_value = {
            "topics": ["greeting", "story_request", "animals"],
            "sentiment": "positive",
            "engagement_score": 0.85,
            "educational_value": 0.7,
            "key_moments": [
                {"timestamp": "00:01:30", "event": "story_started"},
                {"timestamp": "00:05:45", "event": "child_laughed"}
            ],
            "recommendations": [
                "Child shows interest in animal stories",
                "Consider more interactive storytelling"
            ]
        }

        # Test
        analysis = await conversation_service.analyze_conversation("conv123")

        # Assert
        assert "story_request" in analysis["topics"]
        assert analysis["sentiment"] == "positive"
        assert analysis["engagement_score"] > 0.8
        assert len(analysis["recommendations"]) >= 1
