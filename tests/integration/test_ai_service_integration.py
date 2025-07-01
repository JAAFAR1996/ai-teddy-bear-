from unittest.mock import AsyncMock, Mock

import pytest

from src.core.application.services.modern_ai_service import AIServiceError, ModernAIService


@pytest.mark.asyncio
class TestAIServiceIntegration:
    """Test AI service integration"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_client = AsyncMock()
        self.ai_service = ModernAIService(
            openai_client=self.mock_client, default_model="gpt-4-turbo-preview", temperature=0.7
        )

    async def test_generate_educational_response(self):
        """Test generating educational response"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "The sun is a big star that gives us light and warmth!"

        self.mock_client.chat.completions.create.return_value = mock_response

        # Test the service
        response = await self.ai_service.generate_response(
            message="What is the sun?", context={"age": 6, "language": "en"}, response_type="educational"
        )

        assert response == "The sun is a big star that gives us light and warmth!"
        self.mock_client.chat.completions.create.assert_called_once()

    async def test_generate_playful_response(self):
        """Test generating playful response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hey there! The sun is like a giant glowing ball in the sky! ☀️"

        self.mock_client.chat.completions.create.return_value = mock_response

        response = await self.ai_service.generate_response(
            message="Tell me about the sun",
            context={"age": 5, "child_name": "Ahmed", "language": "en"},
            response_type="playful",
        )

        assert "sun" in response.lower()
        assert response == "Hey there! The sun is like a giant glowing ball in the sky! ☀️"

    async def test_ai_service_error_handling(self):
        """Test AI service error handling"""
        # Mock an exception
        self.mock_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(AIServiceError) as exc_info:
            await self.ai_service.generate_response(message="Hello", context={"age": 6}, response_type="general")

        assert "Failed to generate response" in str(exc_info.value)

    async def test_system_prompt_building(self):
        """Test system prompt building for different contexts"""
        # Test educational prompt
        prompt = self.ai_service._build_system_prompt({"age": 7, "language": "ar"}, "educational")

        assert "7-year-old" in prompt
        assert "ar" in prompt
        assert "educational" in prompt

        # Test playful prompt
        prompt = self.ai_service._build_system_prompt({"age": 5, "language": "en"}, "playful")

        assert "5-year-old" in prompt
        assert "playful" in prompt
