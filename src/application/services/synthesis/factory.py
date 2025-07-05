#!/usr/bin/env python3
"""
🏭 Synthesis Service Factory Functions
دوال إنشاء خدمات تركيب الصوت
"""

import logging
import warnings
from typing import Dict, Optional

from .models import SynthesisConfig, SynthesisServiceCredentials
from .synthesis_service import ModernSynthesisService

logger = logging.getLogger(__name__)


async def create_synthesis_service(
    config: Optional[SynthesisConfig] = None,
    credentials: Optional[SynthesisServiceCredentials] = None,
) -> ModernSynthesisService:
    """
    🏭 Factory function to create and initialize synthesis service

    Args:
        config: Optional synthesis configuration
        credentials: Optional service credentials for providers

    Returns:
        Initialized synthesis service

    Example:
        >>> credentials = SynthesisServiceCredentials(
        ...     elevenlabs_api_key="your_key",
        ...     openai_api_key="your_key"
        ... )
        >>> service = await create_synthesis_service(credentials=credentials)
    """
    try:
        service = ModernSynthesisService(config)
        await service.initialize(credentials=credentials)

        logger.info("✅ Synthesis service created successfully")
        return service

    except Exception as e:
        logger.error(f"❌ Failed to create synthesis service: {e}")
        raise


async def create_synthesis_service_legacy(
    config: Optional[SynthesisConfig] = None,
    api_keys: Optional[Dict[str, str]] = None,
    azure_region: str = "eastus",
) -> ModernSynthesisService:
    """
    🔄 Legacy factory function with reduced arguments

    ⚠️ DEPRECATED: Use create_synthesis_service with SynthesisServiceCredentials instead

    Args:
        config: Optional synthesis configuration
        api_keys: Dict with keys: 'elevenlabs', 'openai', 'azure'
        azure_region: Azure region for speech services

    Example:
        >>> await create_synthesis_service_legacy(
        ...     api_keys={'elevenlabs': 'key1', 'openai': 'key2'}
        ... )
    """
    warnings.warn(
        "create_synthesis_service_legacy is deprecated. "
        "Use create_synthesis_service with SynthesisServiceCredentials instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    api_keys = api_keys or {}

    credentials = SynthesisServiceCredentials(
        elevenlabs_api_key=api_keys.get("elevenlabs"),
        openai_api_key=api_keys.get("openai"),
        azure_speech_key=api_keys.get("azure"),
        azure_speech_region=azure_region,
    )

    return await create_synthesis_service(config=config, credentials=credentials)


async def create_synthesis_service_old(
    elevenlabs_key: Optional[str] = None,
    openai_key: Optional[str] = None,
    azure_key: Optional[str] = None,
    azure_region: str = "eastus",
) -> ModernSynthesisService:
    """
    🚨 ULTRA-DEPRECATED: Will be removed in v3.0
    Use create_synthesis_service instead
    """
    warnings.warn(
        "create_synthesis_service_old is deprecated and will be removed in v3.0. "
        "Use create_synthesis_service with SynthesisServiceCredentials instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    api_keys = {}
    if elevenlabs_key:
        api_keys["elevenlabs"] = elevenlabs_key
    if openai_key:
        api_keys["openai"] = openai_key
    if azure_key:
        api_keys["azure"] = azure_key

    return await create_synthesis_service_legacy(
        api_keys=api_keys, azure_region=azure_region
    )
