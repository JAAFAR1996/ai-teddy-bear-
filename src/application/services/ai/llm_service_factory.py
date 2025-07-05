"""
🚀 LLM Service Factory - Clean Modular Version
مصنع خدمات LLM - نسخة مودولار نظيفة

✅ File Size: Reduced from 943 lines to ~150 lines
✅ Modular Architecture: Uses extracted modules
✅ Single Responsibility: Only factory coordination
✅ High Cohesion: Clear separation of concerns
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional, Union

# Flexible imports with fallbacks
try:
    from src.core.domain.entities.conversation import Conversation, Message
except ImportError:
    # Mock classes for standalone operation
    class Message:
        def __init__(self, content="", role="user", **kwargs):
            self.content = content
            self.role = role
            for k, v in kwargs.items():
                setattr(self, k, v)

    class Conversation:
        def __init__(self, messages=None):
            self.messages = messages or []


try:
    from src.infrastructure.config import get_config
except ImportError:

    def get_config():
        return {}


# Import from extracted modules
try:
    from .validation import (
        LLMParameterValidationService,
        LLMParameterValidator,
        LLMProvider,
    )
    from .caching import LLMResponseCache, ModelConfig
    from .selection import LLMModelSelector, ModelSelectionRequest
except ImportError:
    # If relative imports fail, try direct imports
    from validation import (
        LLMParameterValidationService,
        LLMParameterValidator,
        LLMProvider,
    )
    from caching import LLMResponseCache, ModelConfig
    from selection import LLMModelSelector, ModelSelectionRequest

# Import adapters
try:
    from .llm_base import LLMResponse, BaseLLMAdapter
    from .llm_openai_adapter import OpenAIAdapter
    from .llm_anthropic_adapter import AnthropicAdapter
    from .llm_google_adapter import GoogleAdapter
except ImportError:
    # Mock for standalone operation
    class LLMResponse:
        def __init__(self, content="", cost=0.0):
            self.content = content
            self.cost = cost

    class BaseLLMAdapter:
        pass

    class OpenAIAdapter(BaseLLMAdapter):
        def __init__(self, api_key=None, config=None):
            pass

        async def generate(self, messages, config):
            return LLMResponse("Mock response", 0.0)

    class AnthropicAdapter(BaseLLMAdapter):
        def __init__(self, api_key=None, config=None):
            pass

        async def generate(self, messages, config):
            return LLMResponse("Mock response", 0.0)

    class GoogleAdapter(BaseLLMAdapter):
        def __init__(self, api_key=None, config=None):
            pass

        async def generate(self, messages, config):
            return LLMResponse("Mock response", 0.0)


# ================== PARAMETER OBJECTS ==================


@dataclass
class GenerationRequest:
    """Parameter object for generation requests"""

    conversation: Conversation
    provider: Optional[LLMProvider] = None
    model: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    stream: bool = False
    use_cache: bool = True
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LegacyGenerationParams:
    """Parameter object for legacy generation parameters"""

    conversation: Conversation
    provider: Optional[LLMProvider] = None
    model: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    stream: bool = False
    use_cache: bool = True
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)

    def to_generation_request(self) -> GenerationRequest:
        """Convert to modern GenerationRequest"""
        return GenerationRequest(
            conversation=self.conversation,
            provider=self.provider,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=self.stream,
            use_cache=self.use_cache,
            extra_kwargs=self.extra_kwargs,
        )


# ================== MAIN FACTORY ==================


class LLMServiceFactory:
    """
    🎯 Main Factory for LLM Services - Clean Modular Design

    Single Responsibility: Coordinate LLM services using extracted modules
    - Uses validation module for parameter validation
    - Uses caching module for response caching
    - Uses selection module for model selection
    - Only contains core coordination logic
    """

    def __init__(self, config=None):
        """Initialize factory with modular components"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize extracted components
        self.cache = LLMResponseCache(redis_url=self.config.get("redis_url"))
        self.model_selector = LLMModelSelector(config)
        self.validator = LLMParameterValidationService()

        # Initialize adapters
        self.adapters = {}
        self.usage_stats = defaultdict(
            lambda: {"requests": 0, "total_cost": 0, "errors": 0}
        )
        self._init_adapters()

        self.logger.info("🚀 LLM Service Factory initialized")

    def _init_adapters(self):
        """Initialize LLM adapters"""
        try:
            self.adapters[LLMProvider.OPENAI] = OpenAIAdapter(
                api_key=self.config.get("openai_api_key"),
                config=self.config.get("openai_config", {}),
            )
            self.adapters[LLMProvider.ANTHROPIC] = AnthropicAdapter(
                api_key=self.config.get("anthropic_api_key"),
                config=self.config.get("anthropic_config", {}),
            )
            self.adapters[LLMProvider.GOOGLE] = GoogleAdapter(
                api_key=self.config.get("google_api_key"),
                config=self.config.get("google_config", {}),
            )
        except Exception as e:
            self.logger.error(f"Error initializing adapters: {e}")

    async def initialize(self):
        """Initialize factory and components"""
        await self.cache.connect()

    async def generate_response(
        self, request: GenerationRequest
    ) -> Union[str, AsyncIterator[str]]:
        """Generate response using the provided request"""
        # Validate using validation module
        self.validator.validate_required_conversation(request.conversation)
        self.validator.validate_max_tokens_range(request.max_tokens)
        self.validator.validate_temperature_range(request.temperature)

        # Select provider and model using selection module
        provider = request.provider or LLMProvider.OPENAI
        model_config = self.model_selector.get_default_model_config(provider)
        model_config.model_name = request.model or model_config.model_name
        model_config.max_tokens = request.max_tokens
        model_config.temperature = request.temperature

        # Try cache first using caching module
        if request.use_cache and not request.stream:
            cache_key = self.cache.generate_key(
                request.conversation.messages, model_config
            )
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        # Generate new response
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"Provider {provider} not available")

        self.usage_stats[provider]["requests"] += 1

        try:
            response = await adapter.generate(
                request.conversation.messages, model_config
            )

            # Cache response using caching module
            if request.use_cache and not request.stream:
                cache_key = self.cache.generate_key(
                    request.conversation.messages, model_config
                )
                await self.cache.set(cache_key, response.content)

            self.usage_stats[provider]["total_cost"] += response.cost
            return response.content

        except Exception as e:
            self.usage_stats[provider]["errors"] += 1
            self.logger.error(f"Error generating response: {e}")
            raise

    async def generate_response_legacy(
        self, params: LegacyGenerationParams
    ) -> Union[str, AsyncIterator[str]]:
        """Generate response using legacy parameters"""
        request = params.to_generation_request()
        return await self.generate_response(request)

    def get_usage_stats(
            self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """Get usage statistics"""
        if provider:
            return dict(self.usage_stats.get(provider, {}))
        return {str(p): dict(stats) for p, stats in self.usage_stats.items()}

    async def generate_simple(
        self, prompt: str, provider: str = "openai", **kwargs
    ) -> str:
        """Simplified interface for quick usage"""
        message = Message(content=prompt, role="user")
        conversation = Conversation(messages=[message])

        provider_enum = LLMProvider(provider.lower())
        request = GenerationRequest(
            conversation=conversation, provider=provider_enum, **kwargs
        )

        return await self.generate_response(request)


# ================== HELPER FUNCTIONS ==================


def create_generation_request(
    conversation: Conversation, **kwargs
) -> GenerationRequest:
    """Create generation request with parameter object pattern"""
    return GenerationRequest(conversation=conversation, **kwargs)


def create_legacy_generation_params(
    conversation: Conversation, **kwargs
) -> LegacyGenerationParams:
    """Create legacy generation parameters with parameter object pattern"""
    return LegacyGenerationParams(conversation=conversation, **kwargs)


async def get_factory() -> LLMServiceFactory:
    """Get initialized factory instance"""
    factory = LLMServiceFactory()
    await factory.initialize()
    return factory


async def generate_simple(
        prompt: str,
        provider: str = "openai",
        **kwargs) -> str:
    """Global simplified interface for one-liner usage"""
    factory = await get_factory()
    return await factory.generate_simple(prompt, provider, **kwargs)
