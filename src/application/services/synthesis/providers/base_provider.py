#!/usr/bin/env python3
"""
🔌 Base Synthesis Provider
الفئة الأساسية لموفري خدمات تركيب الصوت
"""

import logging
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

from ..models import SynthesisContext

logger = logging.getLogger(__name__)


class BaseSynthesisProvider(ABC):
    """Abstract base class for all synthesis providers"""

    def __init__(self, provider_name: str):
        """Initialize the base provider"""
        self.provider_name = provider_name
        self.is_initialized = False

        logger.debug(f"Base provider initialized: {provider_name}")

    @abstractmethod
    async def initialize(self, credentials: dict) -> bool:
        """Initialize the provider with credentials"""
        pass

    @abstractmethod
    async def synthesize_audio(
            self, context: SynthesisContext) -> Optional[bytes]:
        """Synthesize complete audio"""
        pass

    @abstractmethod
    async def synthesize_stream(
        self, context: SynthesisContext
    ) -> AsyncIterator[bytes]:
        """Synthesize streaming audio"""
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        """Check provider health"""
        pass

    def is_available(self) -> bool:
        """Check if provider is available and initialized"""
        return self.is_initialized

    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.provider_name

    async def cleanup(self) -> None:
        """Cleanup provider resources"""
        logger.debug(f"Cleaning up provider: {self.provider_name}")
        self.is_initialized = False
