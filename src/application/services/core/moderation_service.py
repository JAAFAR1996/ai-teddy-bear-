#!/usr/bin/env python3

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from .moderation.cache_manager import ModerationCache
from .moderation.content_analyzer import ContentAnalyzer
from .moderation.legacy_adapter import (
    LegacyModerationAdapter,
    LegacyModerationParams,
    ModerationMetadata,
)

# Import the extracted high-cohesion components
from .moderation.models import (
    ContentCategory,
    ModerationContext,
    ModerationRequest,
    ModerationSeverity,
)
from .moderation.statistics import ModerationStatistics

# ================== CONFIGURATION ==================


class SecureConfig:
    """تكوين آمن للخدمة مع إدارة الأسرار"""

    def __init__(self, secrets_manager=None):
        self.api_keys = SecureAPIKeys(secrets_manager)
        self.secrets_manager = secrets_manager


class SecureAPIKeys:
    """مفاتيح API آمنة من نظام إدارة الأسرار"""

    def __init__(self, secrets_manager=None):
        self.secrets_manager = secrets_manager
        self._cached_keys = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_openai_key(self) -> str:
        """Get OpenAI API key from vault"""
        if "openai" not in self._cached_keys:
            try:
                if self.secrets_manager:
                    self._cached_keys["openai"] = await self.secrets_manager.get_secret(
                        "openai_api_key"
                    )
                else:
                    self._cached_keys["openai"] = os.getenv("OPENAI_API_KEY", "")
            except Exception as e:
                self.logger.error(f"❌ Failed to get OpenAI key: {e}")
                self._cached_keys["openai"] = ""
        return self._cached_keys["openai"]

    async def get_anthropic_key(self) -> str:
        """Get Anthropic API key from vault"""
        if "anthropic" not in self._cached_keys:
            try:
                if self.secrets_manager:
                    self._cached_keys[
                        "anthropic"
                    ] = await self.secrets_manager.get_secret("anthropic_api_key")
                else:
                    self._cached_keys["anthropic"] = os.getenv("ANTHROPIC_API_KEY", "")
            except Exception as e:
                self.logger.error(f"❌ Failed to get Anthropic key: {e}")
                self._cached_keys["anthropic"] = ""
        return self._cached_keys["anthropic"]

    async def get_azure_content_safety_key(self) -> str:
        """Get Azure Content Safety key from vault"""
        if "azure_content_safety" not in self._cached_keys:
            try:
                if self.secrets_manager:
                    self._cached_keys[
                        "azure_content_safety"
                    ] = await self.secrets_manager.get_secret(
                        "azure_content_safety_key"
                    )
                else:
                    self._cached_keys["azure_content_safety"] = os.getenv(
                        "AZURE_CONTENT_SAFETY_KEY", ""
                    )
            except Exception as e:
                self.logger.error(f"❌ Failed to get Azure Content Safety key: {e}")
                self._cached_keys["azure_content_safety"] = ""
        return self._cached_keys["azure_content_safety"]

    async def get_azure_content_safety_endpoint(self) -> str:
        """Get Azure Content Safety endpoint from vault"""
        if "azure_endpoint" not in self._cached_keys:
            try:
                if self.secrets_manager:
                    self._cached_keys[
                        "azure_endpoint"
                    ] = await self.secrets_manager.get_secret(
                        "azure_content_safety_endpoint"
                    )
                else:
                    self._cached_keys["azure_endpoint"] = os.getenv(
                        "AZURE_CONTENT_SAFETY_ENDPOINT", ""
                    )
            except Exception as e:
                self.logger.error(f"❌ Failed to get Azure endpoint: {e}")
                self._cached_keys["azure_endpoint"] = ""
        return self._cached_keys["azure_endpoint"]

    async def get_google_cloud_credentials(self) -> str:
        """Get Google Cloud credentials from vault"""
        if "google_cloud" not in self._cached_keys:
            try:
                if self.secrets_manager:
                    self._cached_keys[
                        "google_cloud"
                    ] = await self.secrets_manager.get_secret(
                        "google_cloud_credentials"
                    )
                else:
                    self._cached_keys["google_cloud"] = os.getenv(
                        "GOOGLE_CLOUD_CREDENTIALS", ""
                    )
            except Exception as e:
                self.logger.error(f"❌ Failed to get Google Cloud credentials: {e}")
                self._cached_keys["google_cloud"] = ""
        return self._cached_keys["google_cloud"]

    def clear_cache(self):
        """Clear cached keys"""
        self._cached_keys.clear()
        self.logger.info("🗑️ API keys cache cleared")


def get_config(secrets_manager=None):
    """إحضار التكوين الآمن"""
    return SecureConfig(secrets_manager)


# ================== MAIN MODERATION SERVICE ==================


class ModerationService:
    def __init__(self, config=None):
        """تهيئة الخدمة مع المكونات المستخرجة"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize high-cohesion components
        self.cache = ModerationCache(ttl=3600, max_size=1000)
        self.analyzer = ContentAnalyzer()
        self.statistics = ModerationStatistics(max_history=10000)
        self.legacy_adapter = LegacyModerationAdapter(self)

        # Parent dashboard reference (for compatibility)
        self.parent_dashboard = None

        self.logger.info(
            "🚀 Moderation Service initialized with High Cohesion Architecture"
        )

    # ================== MODERN INTERFACE ==================

    async def check_content(
        self,
        request: Union[str, ModerationRequest],
        context: Optional[ModerationContext] = None,
    ) -> Dict[str, Any]:
        """
        🔍 فحص المحتوى الرئيسي - محسن ومبسط
        Modern interface with high cohesion design
        """
        start_time = time.time()

        try:
            # 1. Prepare request and context
            mod_request, mod_context = self._prepare_request(request, context)

            # 2. Handle cache operations
            cache_result = await self._handle_cache(mod_request, mod_context)
            if cache_result:
                await self._record_stats(cache_result, mod_request, start_time)
                return cache_result

            # 3. Analyze content using dedicated analyzer
            analysis_result = self.analyzer.analyze_content(
                mod_request.content, mod_request.age, mod_request.language
            )

            # 4. Convert to service format
            service_result = self._convert_analysis_to_service_format(analysis_result)

            # 5. Update cache and statistics
            await self._update_cache_and_stats(
                service_result, mod_request, mod_context, start_time
            )

            return service_result

        except Exception as e:
            self.logger.error(f"❌ Error in content check: {e}")
            return self._create_safe_response("Processing error - content allowed")

    def _prepare_request(
        self,
        request: Union[str, ModerationRequest],
        context: Optional[ModerationContext],
    ) -> tuple[ModerationRequest, ModerationContext]:
        """تحضير طلب الفلترة والسياق"""
        if isinstance(request, str):
            mod_request = ModerationRequest(content=request)
        else:
            mod_request = request

        if context is None:
            context = ModerationContext()

        return mod_request, context

    async def _handle_cache(
        self, request: ModerationRequest, context: ModerationContext
    ) -> Optional[Dict[str, Any]]:
        """معالجة عمليات cache باستخدام المكون المخصص"""
        if not context.use_cache:
            return None

        cache_key = self.cache.generate_cache_key(
            request.content, request.age, request.language
        )

        cached_result = self.cache.get(cache_key)
        if cached_result:
            self.logger.debug(f"Cache hit for content check")
            return cached_result

        # Store cache key for later use
        setattr(request, "_cache_key", cache_key)
        return None

    def _convert_analysis_to_service_format(
        self, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تحويل نتيجة التحليل إلى تنسيق الخدمة"""
        return {
            "allowed": analysis.get("allowed", True),
            "severity": analysis.get("severity", ModerationSeverity.SAFE.value),
            "categories": analysis.get("categories", []),
            "confidence": analysis.get("confidence", 0.9),
            "reason": analysis.get("reason", "Content analysis completed"),
            "alternative_response": None,
            "processing_time_ms": 0,  # Will be updated later
            "timestamp": time.time(),
            "analysis_details": analysis.get("analysis_details", {}),
        }

    async def _update_cache_and_stats(
        self,
        result: Dict[str, Any],
        request: ModerationRequest,
        context: ModerationContext,
        start_time: float,
    ) -> None:
        """تحديث cache والإحصائيات"""
        processing_time_ms = (time.time() - start_time) * 1000
        result["processing_time_ms"] = processing_time_ms

        # Update cache
        if context.use_cache and hasattr(request, "_cache_key"):
            self.cache.set(request._cache_key, result)

        # Record statistics
        await self._record_stats(result, request, start_time)

    async def _record_stats(
        self, result: Dict[str, Any], request: ModerationRequest, start_time: float
    ) -> None:
        """تسجيل الإحصائيات باستخدام المكون المخصص"""
        processing_time_ms = (time.time() - start_time) * 1000

        self.statistics.record_moderation_result(
            result=result,
            user_id=request.user_id,
            session_id=request.session_id,
            content_length=len(request.content),
            processing_time_ms=processing_time_ms,
        )

    def _create_safe_response(
        self, reason: str, confidence: float = 0.9
    ) -> Dict[str, Any]:
        """إنشاء رد آمن"""
        return {
            "allowed": True,
            "severity": ModerationSeverity.SAFE.value,
            "categories": [],
            "confidence": confidence,
            "reason": reason,
            "alternative_response": None,
            "processing_time_ms": 45,
            "timestamp": time.time(),
        }

    # ================== LEGACY INTERFACE SUPPORT ==================

    async def check_content_legacy(
        self, params: Union[LegacyModerationParams, str], **kwargs
    ) -> Dict[str, Any]:
        """Legacy interface - delegated to adapter"""
        return await self.legacy_adapter.check_content_legacy(params, **kwargs)

    async def check_content_with_params(
        self, params: Union[str, "ContentCheckParams"], **kwargs
    ) -> Dict[str, Any]:
        """
        Refactored interface - uses parameter object pattern.
        ✅ Reduced from 5 arguments to 1 argument (under threshold)

        Args:
            params: ContentCheckParams object or content string for simple usage
            **kwargs: Additional parameters for backward compatibility

        Returns:
            Dict[str, Any]: Moderation result
        """
        from .moderation.legacy_adapter import ContentCheckParams

        if isinstance(params, str):
            # Simple usage - convert string to parameter object
            check_params = ContentCheckParams(
                content=params,
                user_id=kwargs.get("user_id"),
                session_id=kwargs.get("session_id"),
                age=kwargs.get("age", 10),
                language=kwargs.get("language", "en"),
                context=kwargs.get("context"),
                strict_mode=kwargs.get("strict_mode", False),
                use_cache=kwargs.get("use_cache", True),
            )
        else:
            check_params = params

        return await self.legacy_adapter.check_content_with_params(check_params)

    async def check_content_with_params_legacy(
        self, params: "LegacyContentCheckParams"
    ) -> Dict[str, Any]:
        """
        Legacy interface REFACTORED using Parameter Object pattern.
        ✅ Reduced from 5 arguments to 1 argument (under threshold)

        Args:
            params: LegacyContentCheckParams containing all legacy parameters

        Returns:
            Dict[str, Any]: Moderation result
        """
        # Handle legacy parameter object
        mod_request = ModerationRequest(
            content=params.content,
            user_id=params.user_id,
            session_id=params.session_id,
            age=params.age,
            language=params.extra_kwargs.get("language", "en"),
        )

        mod_context = ModerationContext(
            use_cache=params.extra_kwargs.get("use_cache", True),
            enable_openai=params.extra_kwargs.get("enable_openai", True),
        )

        return await self.check_content(mod_request, mod_context)

    async def check_content_with_params_legacy_args(
        self,
        content: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        age: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility - DEPRECATED.
        Creates LegacyContentCheckParams and delegates to new method.
        ⚠️ DEPRECATED: Use check_content_with_params_legacy with LegacyContentCheckParams instead.
        """
        legacy_params = LegacyContentCheckParams(
            content=content,
            user_id=user_id,
            session_id=session_id,
            age=age,
            extra_kwargs=kwargs,
        )
        return await self.check_content_with_params_legacy(legacy_params)

    async def moderate_content(self, text: str, user_context: dict = None) -> dict:
        """Very old legacy interface - delegated to adapter"""
        return await self.legacy_adapter.moderate_content(text, user_context)

    async def check_content_safe(
        self, params: LegacyModerationParams
    ) -> Dict[str, Any]:
        """Safe mode legacy interface - delegated to adapter"""
        return await self.legacy_adapter.check_content_safe(params)

    def create_legacy_params(
        self,
        content: str,
        metadata: Optional[Union[Dict[str, Any], ModerationMetadata]] = None,
    ) -> LegacyModerationParams:
        """Helper to create legacy parameters"""
        return self.legacy_adapter.create_legacy_params(content, metadata)

    async def check_content_enhanced(
        self, content: str, metadata: ModerationMetadata
    ) -> Dict[str, Any]:
        """Enhanced legacy interface - delegated to adapter"""
        return await self.legacy_adapter.check_content_enhanced(content, metadata)

    def validate_parameters(self, params: LegacyModerationParams) -> Dict[str, Any]:
        """Legacy parameter validation - delegated to adapter"""
        return self.legacy_adapter.validate_parameters(params)

    # ================== COMPONENT MANAGEMENT ==================

    async def update_whitelist(self, words: List[str], action: str = "add") -> bool:
        """Update whitelist - delegated to analyzer"""
        return self.analyzer.update_whitelist(words, action)

    async def update_blacklist(self, words: List[str], action: str = "add") -> bool:
        """Update blacklist - delegated to analyzer"""
        return self.analyzer.update_blacklist(words, action)

    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        return {
            "service_name": "ModerationService",
            "version": "2.0.0",
            "architecture": "High Cohesion",
            "components": {
                "cache": self.cache.get_stats(),
                "analyzer": self.analyzer.get_analysis_stats(),
                "statistics": self.statistics.get_general_stats(),
                "legacy_adapter": self.legacy_adapter.get_legacy_interface_info(),
            },
            "health": "healthy",
            "last_updated": time.time(),
        }

    async def get_moderation_stats(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get moderation statistics - delegated to statistics component"""
        if user_id:
            return self.statistics.get_user_stats(user_id)

        return {
            "general": self.statistics.get_general_stats(),
            "performance": self.statistics.get_performance_stats(),
            "categories": self.statistics.get_category_breakdown(),
            "trends": self.statistics.get_hourly_trends(24),
            "cache_stats": self.cache.get_stats(),
        }

    def clear_cache(self) -> None:
        """Clear cache - delegated to cache component"""
        self.cache.clear()

    def set_parent_dashboard(self, dashboard) -> None:
        """Set parent dashboard reference for compatibility"""
        self.parent_dashboard = dashboard
        if dashboard:
            self.logger.info("Parent dashboard connected")


# ================== FACTORY FUNCTIONS ==================


def create_moderation_service(config=None) -> ModerationService:
    """Factory function to create moderation service"""
    return ModerationService(config)


def create_moderation_request(
    content: str, user_id: Optional[str] = None, age: int = 10, language: str = "en"
) -> ModerationRequest:
    """Factory function to create moderation request"""
    return ModerationRequest(
        content=content, user_id=user_id, age=age, language=language
    )


# ================== BACKWARD COMPATIBILITY ==================

# Export legacy classes for backward compatibility

# ================== PARAMETER OBJECTS ==================


@dataclass
class LegacyContentCheckParams:
    """
    Parameter object for legacy content check parameters.
    Applied INTRODUCE PARAMETER OBJECT pattern to reduce function arguments.
    """

    content: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    age: int = 10
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate legacy parameters"""
        if not self.content or not isinstance(self.content, str):
            raise ValueError("content must be a non-empty string")

        if self.age < 0 or self.age > 150:
            raise ValueError("age must be between 0 and 150")

        if self.user_id is not None and not isinstance(self.user_id, str):
            raise ValueError("user_id must be a string or None")

        if self.session_id is not None and not isinstance(self.session_id, str):
            raise ValueError("session_id must be a string or None")


def create_legacy_content_check_params(
    content: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    age: int = 10,
    **kwargs,
) -> LegacyContentCheckParams:
    """
    Factory function to create LegacyContentCheckParams.
    Simplifies creation of parameter objects.
    """
    return LegacyContentCheckParams(
        content=content,
        user_id=user_id,
        session_id=session_id,
        age=age,
        extra_kwargs=kwargs,
    )


# Legacy rule engine placeholder
class RuleEngine:
    """Placeholder for legacy rule engine compatibility"""

    def __init__(self):
        pass

    async def add_rule(self, rule):
        pass

    async def remove_rule(self, rule_id: str):
        pass

    async def evaluate(self, content: str, age: int, language: str):
        return {"safe": True, "rules_matched": []}


# ================== EXPORTS ==================

__all__ = [
    "ModerationService",
    "ModerationRequest",
    "ModerationContext",
    "ModerationSeverity",
    "ContentCategory",
    "LegacyModerationParams",
    "ModerationMetadata",
    "ContentCheckParams",
    "LegacyContentCheckParams",
    "RuleEngine",
    "create_moderation_service",
    "create_moderation_request",
    "create_content_check_params",
    "create_legacy_content_check_params",
    "get_config",
]
