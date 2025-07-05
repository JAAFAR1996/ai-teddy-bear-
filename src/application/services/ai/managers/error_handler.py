import logging
from typing import Any, Dict

from openai import APIError, APITimeoutError, RateLimitError

from src.application.services.ai.fallback_response_service import FallbackResponseService
from src.application.services.ai.models.ai_response_models import AIResponseModel
from src.core.domain.entities.child import Child

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Handles errors from the OpenAI API."""

    def __init__(self, fallback_service: FallbackResponseService):
        self.fallback_service = fallback_service
        self.rate_limit_count = 0
        self.error_count = 0

    async def handle_api_errors(
        self, error: Exception, message: str, child: Child, session_id: str
    ) -> AIResponseModel:
        """Handle different types of API errors with appropriate fallbacks"""
        if isinstance(error, RateLimitError):
            self.rate_limit_count += 1
            logger.warning(
                f"⚠️ OpenAI rate limit hit (#{self.rate_limit_count})")
            return await self.fallback_service.create_rate_limit_fallback(
                message, child, session_id
            )
        elif isinstance(error, APITimeoutError):
            self.error_count += 1
            logger.error(f"⏰ OpenAI API timeout: {str(error)}")
            return await self.fallback_service.create_timeout_fallback(
                message, child, session_id
            )
        elif isinstance(error, APIError):
            self.error_count += 1
            logger.error(f"🚫 OpenAI API error: {str(error)}", exc_info=True)
            return await self.fallback_service.create_api_error_fallback(
                message, child, session_id, str(error)
            )
        else:
            self.error_count += 1
            logger.error(
                f"💥 Unexpected AI service error: {str(error)}", exc_info=True)
            return await self.fallback_service.create_generic_fallback(
                message, child, session_id, str(error)
            )
