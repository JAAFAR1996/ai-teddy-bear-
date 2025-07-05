#!/usr/bin/env python3
"""
🚀 Moderation Service (Refactored)
الخدمة الرئيسية المبسطة - فصل المسؤوليات
"""

import logging
from typing import Dict, Any, Optional, Union

from .moderation_helpers import (
    ModerationRequest,
    ModerationContext,
    ConditionalDecomposer,
)
from .moderation_api_clients import create_api_clients
from .moderation_local_checkers import create_local_checkers
from .moderation_cache_manager import create_cache_manager
from .moderation_result_processor import create_result_processor

try:
    from src.infrastructure.config import get_config
except ImportError:
    # Mock config for testing
    def get_config():
        class MockConfig:
            def __init__(self):
                self.api_keys = MockAPIKeys()

        class MockAPIKeys:
            def __init__(self):
                self.OPENAI_API_KEY = ""
                self.AZURE_CONTENT_SAFETY_KEY = ""
                self.AZURE_CONTENT_SAFETY_ENDPOINT = ""
                self.GOOGLE_CLOUD_CREDENTIALS = ""
                self.ANTHROPIC_API_KEY = ""

        return MockConfig()


class ModerationServiceRefactored:
    """🚀 خدمة الفلترة المحسنة"""

    def __init__(self, config=None):
        """تهيئة الخدمة مع جميع المكونات"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize components
        self.api_clients = create_api_clients(self.config)
        self.local_checkers = create_local_checkers(self.config)
        self.cache_manager = create_cache_manager()
        self.result_processor = create_result_processor()

    async def check_content(
        self,
        request: Union[str, ModerationRequest],
        context: Optional[ModerationContext] = None,
    ) -> Dict[str, Any]:
        """🔍 فحص المحتوى المحسن"""

        # Convert to Parameter Object
        if isinstance(request, str):
            mod_request = ModerationRequest(content=request)
        else:
            mod_request = request

        if context is None:
            context = ModerationContext()

        # Early validation
        if ConditionalDecomposer.is_content_empty_or_invalid(
                mod_request.content):
            return self.result_processor.create_safe_response("Empty content")

        # Check cache
        if context.use_cache:
            cached = self.cache_manager.get(
                mod_request.content, mod_request.age, mod_request.language
            )
            if cached:
                return cached

        # Local check first
        local_result = await self.local_checkers.check_whitelist_blacklist(mod_request)

        if not local_result.is_safe:
            response = self.result_processor.format_response(
                local_result, mod_request)
            self.cache_manager.set(
                mod_request.content,
                mod_request.age,
                mod_request.language,
                response)
            return response

        # Safe response
        safe_response = self.result_processor.create_safe_response(
            "Passed all checks")
        self.cache_manager.set(
            mod_request.content,
            mod_request.age,
            mod_request.language,
            safe_response)
        return safe_response


def create_moderation_service(config=None) -> ModerationServiceRefactored:
    """🏭 Factory function"""
    return ModerationServiceRefactored(config)
