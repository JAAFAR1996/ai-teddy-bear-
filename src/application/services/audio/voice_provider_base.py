"""
Base Provider Service
Eliminates duplication between transcription and synthesis services
"""

import asyncio
import logging
from typing import Optional, List, Generic, TypeVar, Protocol
from abc import ABC, abstractmethod

from src.domain.audio.models import (
    ProviderConfig,
    ProviderResult,
    ProviderOperation,
    TranscriptionRequest,
    SynthesisRequest,
)
from .voice_cache_manager import VoiceCacheManager

# Mock metrics collector for now


class MockMetricsCollector:
    async def record_metric(self, name: str, value: float):
        pass


metrics_collector = MockMetricsCollector()

logger = logging.getLogger(__name__)

# Type variable for request types
RequestType = TypeVar("RequestType", TranscriptionRequest, SynthesisRequest)


class ProviderExecutor(Protocol):
    """Protocol for provider executors"""

    async def execute(
        self, provider: ProviderConfig, request: RequestType
    ) -> Optional[str]:
        """Execute provider operation"""
        ...


class BaseProviderService(ABC, Generic[RequestType]):
    """Base service for provider operations - eliminates duplication"""

    def __init__(
        self,
        operation_type: ProviderOperation,
        cache_manager: VoiceCacheManager,
        metric_name: str,
    ):
        self.operation_type = operation_type
        self.cache_manager = cache_manager
        self.metric_name = metric_name
        self.providers: List[ProviderConfig] = []

    def set_providers(self, providers: List[ProviderConfig]):
        """Set available providers for this operation"""
        self.providers = [
            p for p in providers if self.operation_type in p.supported_operations]
        # Sort by priority
        self.providers.sort(key=lambda x: x.priority, reverse=True)

    async def _process_with_single_provider(
        self, provider: ProviderConfig, request: RequestType, executor: ProviderExecutor
    ) -> Optional[str]:
        """Processes the request with a single provider."""
        try:
            result = await executor.execute(provider, request)
            if result:
                logger.info(
                    f"✅ {self.operation_type.value} successful with {provider.name}"
                )
                return result
            else:
                logger.debug(
                    f"❌ {self.operation_type.value} failed with {provider.name}"
                )
        except Exception as e:
            logger.error(
                f"Error in {provider.name} {self.operation_type.value}: {str(e)}"
            )
        return None

    async def process_with_providers(
        self, request: RequestType, executor: ProviderExecutor
    ) -> Optional[str]:
        """
        Generic provider processing logic - DRY implementation
        Replaces duplicated _try_*_providers methods
        """
        start_time = asyncio.get_event_loop().time()

        if hasattr(request, "cache_key") and request.cache_key:
            cached_result = await self.cache_manager.get(request.cache_key)
            if cached_result:
                logger.debug(f"Cache hit for {self.operation_type.value}")
                return cached_result

        available_providers = [p for p in self.providers if p.is_available]
        if not available_providers:
            logger.error(
                f"No available providers for {self.operation_type.value}")
            return None

        for provider in available_providers:
            result = await self._process_with_single_provider(provider, request, executor)
            if result:
                if hasattr(request, "cache_key") and request.cache_key:
                    await self.cache_manager.set(request.cache_key, result)

                processing_time = asyncio.get_event_loop().time() - start_time
                await metrics_collector.record_metric(
                    self.metric_name, processing_time
                )
                return result

        logger.warning(f"⚠️  All {self.operation_type.value} providers failed")
        return None

    def get_providers_status(self) -> List[dict]:
        """
        Get status of all providers for this operation
        Replaces duplicated get_*_providers_status methods
        """
        return [
            {
                "name": provider.name,
                "type": provider.provider_type.value,
                "available": provider.is_available,
                "priority": provider.priority,
                "operation": self.operation_type.value,
            }
            for provider in self.providers
        ]

    @abstractmethod
    async def process(self, *args, **kwargs) -> Optional[str]:
        """Process the request - to be implemented by subclasses"""
        pass
