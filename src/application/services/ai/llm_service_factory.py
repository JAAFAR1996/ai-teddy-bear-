import asyncio
import hashlib
import json
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import anthropic
import google.generativeai as genai
import openai
import torch

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ImportError:
    from src.infrastructure.external_services.mock.transformers import AutoModelForCausalLM, AutoTokenizer

import redis.asyncio as aioredis

from src.core.domain.entities.conversation import Conversation, Message
from src.infrastructure.config import get_config


from .llm_base import (
    LLMProvider, ModelConfig, LLMResponse, BaseLLMAdapter
)
from .llm_openai_adapter import OpenAIAdapter
from .llm_anthropic_adapter import AnthropicAdapter  
from .llm_google_adapter import GoogleAdapter


# ================== VALIDATION SERVICES ==================

class LLMParameterValidationService:
    """Validation service for LLM parameters"""
    
    @staticmethod
    def validate_required_conversation(conversation: Conversation) -> None:
        """Validate that conversation is provided and valid"""
        if not conversation:
            raise ValueError("Conversation is required")
    
    @staticmethod
    def validate_max_tokens_range(max_tokens: int) -> None:
        """Validate max_tokens parameter is within acceptable range"""
        if max_tokens < 1 or max_tokens > 8192:
            raise ValueError("max_tokens must be between 1 and 8192")
    
    @staticmethod
    def validate_temperature_range(temperature: float) -> None:
        """Validate temperature parameter is within acceptable range"""
        if temperature < 0.0 or temperature > 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
    
    @staticmethod
    def validate_provider_type(provider: Optional[LLMProvider]) -> None:
        """Validate provider parameter if provided"""
        if provider is not None and not isinstance(provider, LLMProvider):
            raise ValueError("provider must be a valid LLMProvider enum value")
    
    @staticmethod
    def validate_model_name(model: Optional[str]) -> None:
        """Validate model name if provided"""
        if model is not None and (not isinstance(model, str) or len(model.strip()) == 0):
            raise ValueError("model must be a non-empty string if provided")


class LLMParameterValidator:
    """Specialized validator for LLM parameter objects"""
    
    def __init__(self, validation_service: LLMParameterValidationService):
        self.validator = validation_service
    
    def validate_core_parameters(self, conversation: Conversation, max_tokens: int, temperature: float) -> None:
        """Validate core required parameters"""
        self.validator.validate_required_conversation(conversation)
        self.validator.validate_max_tokens_range(max_tokens)
        self.validator.validate_temperature_range(temperature)
    
    def validate_optional_parameters(self, provider: Optional[LLMProvider], model: Optional[str]) -> None:
        """Validate optional parameters"""
        self.validator.validate_provider_type(provider)
        self.validator.validate_model_name(model)
    
    def validate_all_parameters(self, conversation: Conversation, provider: Optional[LLMProvider], 
                              model: Optional[str], max_tokens: int, temperature: float) -> None:
        """Validate all parameters - single entry point"""
        self.validate_core_parameters(conversation, max_tokens, temperature)
        self.validate_optional_parameters(provider, model)


# ================== SHARED ABSTRACTIONS ==================

class ParameterConverter:
    """Shared logic for parameter conversions"""
    
    @staticmethod
    def legacy_args_to_factory_params(
        conversation: Conversation,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        max_tokens: int = 150,
        temperature: float = 0.7,
        stream: bool = False,
        use_cache: bool = True,
        **kwargs
    ) -> 'LegacyFactoryParams':
        """Convert individual arguments to LegacyFactoryParams"""
        return LegacyFactoryParams(
            conversation=conversation,
            provider=provider,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            use_cache=use_cache,
            extra_kwargs=kwargs
        )
    
    @staticmethod
    def legacy_args_to_generation_params(
        conversation: Conversation,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        max_tokens: int = 150,
        temperature: float = 0.7,
        stream: bool = False,
        use_cache: bool = True,
        **kwargs
    ) -> 'LegacyGenerationParams':
        """Convert individual arguments to LegacyGenerationParams"""
        return LegacyGenerationParams(
            conversation=conversation,
            provider=provider,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            use_cache=use_cache,
            extra_kwargs=kwargs
        )


class LegacyCompatibilityService:
    """Centralized legacy compatibility service"""
    
    def __init__(self, modern_service: 'LLMServiceFactory'):
        self.modern_service = modern_service
        self.converter = ParameterConverter()
    
    async def handle_legacy_compatible_request(self, params: 'LegacyGenerationParams') -> Union[str, AsyncIterator[str]]:
        """Common logic for legacy compatible requests"""
        return await self.modern_service.generate_response_legacy(params)
    
    async def handle_factory_compatible_request(self, params: 'LegacyFactoryParams') -> Union[str, AsyncIterator[str]]:
        """Common logic for factory compatible requests"""
        return await self.modern_service.generate_response_legacy_direct(params)


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
class ModelSelectionRequest:
    """Parameter object for model selection"""
    task_type: str
    context_length: int = 0
    required_features: List[str] = field(default_factory=list)
    budget_constraint: Optional[float] = None
    latency_requirement: Optional[int] = None

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
    
    def __post_init__(self):
        """Validate parameters"""
        validation_service = LLMParameterValidationService()
        parameter_validator = LLMParameterValidator(validation_service)
        
        parameter_validator.validate_all_parameters(
            self.conversation, self.provider, self.model, 
            self.max_tokens, self.temperature
        )
    
    def to_generation_request(self) -> GenerationRequest:
        """تحويل إلى GenerationRequest الحديث"""
        return GenerationRequest(
            conversation=self.conversation,
            provider=self.provider,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=self.stream,
            use_cache=self.use_cache,
            extra_kwargs=self.extra_kwargs
        )

@dataclass
class LegacyFactoryParams:
    """Parameter object for legacy factory parameters"""
    conversation: Conversation
    provider: Optional[LLMProvider] = None
    model: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    stream: bool = False
    use_cache: bool = True
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate factory parameters"""
        validation_service = LLMParameterValidationService()
        parameter_validator = LLMParameterValidator(validation_service)
        
        parameter_validator.validate_all_parameters(
            self.conversation, self.provider, self.model, 
            self.max_tokens, self.temperature
        )
    
    def to_legacy_generation_params(self) -> LegacyGenerationParams:
        """Convert to LegacyGenerationParams"""
        return LegacyGenerationParams(
            conversation=self.conversation,
            provider=self.provider,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=self.stream,
            use_cache=self.use_cache,
            extra_kwargs=self.extra_kwargs
        )

@dataclass
class LegacyCompatibilityParams:
    """Parameter object for legacy compatibility parameters"""
    conversation: Conversation
    provider: Optional[LLMProvider] = None
    model: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    stream: bool = False
    use_cache: bool = True
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate compatibility parameters"""
        validation_service = LLMParameterValidationService()
        parameter_validator = LLMParameterValidator(validation_service)
        
        parameter_validator.validate_all_parameters(
            self.conversation, self.provider, self.model, 
            self.max_tokens, self.temperature
        )
    
    def to_legacy_generation_params(self) -> LegacyGenerationParams:
        """Convert to LegacyGenerationParams"""
        return LegacyGenerationParams(
            conversation=self.conversation,
            provider=self.provider,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=self.stream,
            use_cache=self.use_cache,
            extra_kwargs=self.extra_kwargs
        )
    
    def to_legacy_factory_params(self) -> LegacyFactoryParams:
        """Convert to LegacyFactoryParams"""
        return LegacyFactoryParams(
            conversation=self.conversation,
            provider=self.provider,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=self.stream,
            use_cache=self.use_cache,
            extra_kwargs=self.extra_kwargs
        )


class ModelSelector:
    """Intelligent model selection based on various criteria"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.performance_history = defaultdict(list)

    def select_model(self, request: ModelSelectionRequest) -> ModelConfig:
        """Select best model for the given request"""
        return self._select_by_task_type(request.task_type)
    
    def _select_by_task_type(self, task_type: str) -> ModelConfig:
        """Select model based on task type"""
        task_configs = {
            "creative_writing": ModelConfig(
                provider=LLMProvider.ANTHROPIC,
                model_name="claude-3-sonnet", 
                max_tokens=2048,
                temperature=0.8
            ),
            "analysis": ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name="gpt-4",
                max_tokens=1024, 
                temperature=0.3
            )
        }
        
        return task_configs.get(task_type, ModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-3.5-turbo",
            max_tokens=1024,
            temperature=0.7
        ))


class ResponseCache:
    """Cache for LLM responses"""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.redis_client = None
        self.local_cache = {}
        self.cache_ttl = 3600  # 1 hour

    async def connect(self):
        """Connect to Redis if available"""
        if self.redis_url:
            try:
                self.redis_client = await aioredis.create_redis_pool(self.redis_url)
            except Exception as e:
                logging.warning(f"Failed to connect to Redis: {e}")

    async def get(self, key: str) -> Optional[str]:
        """Get cached response"""
        # Try Redis first
        redis_value = await self._try_redis_get(key)
        if redis_value:
            return redis_value
        
        # Fallback to local cache
        return self._try_local_get(key)
    
    async def _try_redis_get(self, key: str) -> Optional[str]:
        """Try to get value from Redis"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            return value.decode('utf-8') if value else None
        except Exception:
            return None
    
    def _try_local_get(self, key: str) -> Optional[str]:
        """Try to get value from local cache"""
        if key not in self.local_cache:
            return None
        
        value, expiry = self.local_cache[key]
        
        if self._is_cache_valid(expiry):
            return value
        else:
            self._remove_expired_cache(key)
            return None
    
    def _is_cache_valid(self, expiry: datetime) -> bool:
        """Check if cache entry is still valid"""
        return datetime.now() < expiry
    
    def _remove_expired_cache(self, key: str) -> None:
        """Remove expired cache entry"""
        self.local_cache.pop(key, None)

    async def set(self, key: str, value: str):
        """Set cached response"""
        if self.redis_client:
            try:
                await self.redis_client.setex(key, self.cache_ttl, value)
            except Exception:
                pass

        # Set in local cache
        expiry = datetime.now() + timedelta(seconds=self.cache_ttl)
        self.local_cache[key] = (value, expiry)

    def generate_key(self, messages: List[Message], model_config: ModelConfig) -> str:
        """Generate cache key for messages and config"""
        content = json.dumps([msg.__dict__ for msg in messages], sort_keys=True)
        config_hash = hashlib.md5(json.dumps(model_config.__dict__, sort_keys=True).encode()).hexdigest()
        return f"llm:{hashlib.md5(content.encode()).hexdigest()}:{config_hash}"


class LLMServiceFactory:
    """Main factory for LLM services with adapter pattern"""

    def __init__(self, config=None):
        self.config = config or get_config()
        self.adapters = {}
        self.cache = ResponseCache(redis_url=self.config.get('redis_url'))
        self.model_selector = ModelSelector(config)
        self.usage_stats = defaultdict(lambda: {"requests": 0, "total_cost": 0, "errors": 0})
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize services
        self.legacy_compatibility = LegacyCompatibilityService(self)
        
        # Initialize adapters
        self._init_adapters()

    def _init_adapters(self):
        """Initialize all LLM adapters"""
        try:
            self.adapters[LLMProvider.OPENAI] = OpenAIAdapter(
                api_key=self.config.get('openai_api_key'),
                config=self.config.get('openai_config', {})
            )
            self.adapters[LLMProvider.ANTHROPIC] = AnthropicAdapter(
                api_key=self.config.get('anthropic_api_key'),
                config=self.config.get('anthropic_config', {})
            )
            self.adapters[LLMProvider.GOOGLE] = GoogleAdapter(
                api_key=self.config.get('google_api_key'),
                config=self.config.get('google_config', {})
            )
            self.logger.info("All LLM adapters initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing adapters: {e}")

    async def initialize(self):
        """Initialize the factory and its components"""
        await self.cache.connect()

    async def generate_response(self, request: GenerationRequest) -> Union[str, AsyncIterator[str]]:
        """Generate response using the provided request"""
        
        # 1. Prepare generation context
        provider = self._select_provider(request.provider)
        model_config = self._create_model_config(request, provider)
        
        # 2. Try cache first
        if request.use_cache and not request.stream:
            cached = await self._try_get_cached_response(request.conversation, model_config, provider)
            if cached:
                return cached
        
        # 3. Generate new response
        return await self._generate_new_response(request, provider, model_config)
    
    def _select_provider(self, requested_provider: Optional[LLMProvider]) -> LLMProvider:
        """Select provider"""
        return requested_provider or LLMProvider.OPENAI
    
    def _create_model_config(self, request: GenerationRequest, provider: LLMProvider) -> ModelConfig:
        """Create model configuration"""
        return ModelConfig(
            provider=provider,
            model_name=request.model or self._get_default_model(provider),
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            **request.extra_kwargs
        )
    
    async def _try_get_cached_response(self, conversation: Conversation, model_config: ModelConfig, provider: LLMProvider) -> Optional[str]:
        """Try to get cached response"""
        try:
            cache_key = self.cache.generate_key(conversation.messages, model_config)
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                self.logger.debug(f"Cache hit for {provider}")
                return cached_response
        except Exception as e:
            self.logger.warning(f"Cache error: {e}")
        return None
    
    async def _generate_new_response(self, request: GenerationRequest, provider: LLMProvider, model_config: ModelConfig) -> Union[str, AsyncIterator[str]]:
        """Generate new response"""
        # Get adapter
        adapter = self._get_adapter(provider)
        
        # Update stats
        self.usage_stats[provider]["requests"] += 1
        
        try:
            if request.stream:
                return adapter.generate_stream(request.conversation.messages, model_config)
            else:
                response = await adapter.generate(request.conversation.messages, model_config)
                
                # Update stats and cache
                await self._handle_response_success(request, provider, model_config, response)
                return response.content
                
        except Exception as e:
            self.usage_stats[provider]["errors"] += 1
            self.logger.error(f"Error generating response with {provider}: {e}")
            raise
    
    def _get_adapter(self, provider: LLMProvider):
        """Get adapter for provider"""
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"Provider {provider} not available")
        return adapter
    
    async def _handle_response_success(self, request: GenerationRequest, provider: LLMProvider, model_config: ModelConfig, response):
        """Handle successful response"""
        # Update cost stats
        self.usage_stats[provider]["total_cost"] += response.cost
        
        # Cache response if enabled
        if request.use_cache:
            try:
                cache_key = self.cache.generate_key(request.conversation.messages, model_config)
                await self.cache.set(cache_key, response.content)
            except Exception as e:
                self.logger.warning(f"Cache save error: {e}")

    def _get_default_model(self, provider: LLMProvider) -> str:
        """Get default model for provider"""
        defaults = {
            LLMProvider.OPENAI: "gpt-3.5-turbo",
            LLMProvider.ANTHROPIC: "claude-3-sonnet",
            LLMProvider.GOOGLE: "gemini-pro"
        }
        return defaults.get(provider, "default")

    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of available providers"""
        return list(self.adapters.keys())

    def get_usage_stats(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """Get usage statistics"""
        if provider:
            return dict(self.usage_stats[provider])
        return {str(p): dict(stats) for p, stats in self.usage_stats.items()}
    
    # ================== MODERN INTERFACE ==================
    
    async def generate_response_legacy(
        self, params: LegacyGenerationParams
    ) -> Union[str, AsyncIterator[str]]:
        """Generate response using legacy parameters"""
        request = params.to_generation_request()
        return await self.generate_response(request)
    
    async def generate_response_legacy_direct(
        self, params: LegacyFactoryParams
    ) -> Union[str, AsyncIterator[str]]:
        """Generate response using legacy factory parameters"""
        legacy_params = params.to_legacy_generation_params()
        return await self.generate_response_legacy(legacy_params)
    
    # ================== BACKWARD COMPATIBILITY METHODS ==================
    
    async def generate_response_legacy_compatible(
        self, params: LegacyCompatibilityParams
    ) -> Union[str, AsyncIterator[str]]:
        """Generate response using legacy compatibility parameters"""
        legacy_params = params.to_legacy_generation_params()
        return await self.legacy_compatibility.handle_legacy_compatible_request(legacy_params)
    
    async def generate_response_factory_compatible(
        self, params: LegacyCompatibilityParams
    ) -> Union[str, AsyncIterator[str]]:
        """Generate response using factory compatibility parameters"""
        factory_params = params.to_legacy_factory_params()
        return await self.legacy_compatibility.handle_factory_compatible_request(factory_params)
    
    # ================== DEPRECATED LEGACY METHODS ==================
    
    async def generate_response_legacy_compatible_args(
        self,
        conversation: Conversation,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        max_tokens: int = 150,
        temperature: float = 0.7,
        stream: bool = False,
        use_cache: bool = True,
        **kwargs
    ) -> Union[str, AsyncIterator[str]]:
        """Legacy method for backward compatibility - DEPRECATED"""
        params = LegacyCompatibilityParams(
            conversation=conversation,
            provider=provider,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            use_cache=use_cache,
            extra_kwargs=kwargs
        )
        return await self.generate_response_legacy_compatible(params)
    
    async def generate_response_factory_compatible_args(
        self,
        conversation: Conversation,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        max_tokens: int = 150,
        temperature: float = 0.7,
        stream: bool = False,
        use_cache: bool = True,
        **kwargs
    ) -> Union[str, AsyncIterator[str]]:
        """Factory legacy method for backward compatibility - DEPRECATED"""
        params = LegacyCompatibilityParams(
            conversation=conversation,
            provider=provider,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            use_cache=use_cache,
            extra_kwargs=kwargs
        )
        return await self.generate_response_factory_compatible(params)


# ================== FACTORY & HELPER FUNCTIONS ==================

async def create_llm_factory(config: Optional[Dict] = None) -> LLMServiceFactory:
    """Create and initialize LLM factory"""
    factory = LLMServiceFactory(config)
    await factory.initialize()
    return factory


def create_generation_request(
    conversation: Conversation,
    provider: Optional[LLMProvider] = None,
    **kwargs
) -> GenerationRequest:
    """Helper function to create GenerationRequest"""
    return GenerationRequest(
        conversation=conversation,
        provider=provider,
        **kwargs
    )


def create_model_selection_request(
    task_type: str,
    **kwargs
) -> ModelSelectionRequest:
    """Helper function to create ModelSelectionRequest"""
    return ModelSelectionRequest(
        task_type=task_type,
        **kwargs
    )


def create_legacy_generation_params(
    conversation: Conversation,
    **kwargs
) -> LegacyGenerationParams:
    """Helper function to create LegacyGenerationParams"""
    return LegacyGenerationParams(
        conversation=conversation,
        **kwargs
    )


def create_legacy_factory_params(
    conversation: Conversation,
    **kwargs
) -> LegacyFactoryParams:
    """Helper function to create LegacyFactoryParams"""
    return LegacyFactoryParams(
        conversation=conversation,
        **kwargs
    )


def create_legacy_compatibility_params(
    conversation: Conversation,
    **kwargs
) -> LegacyCompatibilityParams:
    """Helper function to create LegacyCompatibilityParams"""
    return LegacyCompatibilityParams(
        conversation=conversation,
        **kwargs
    )


def create_legacy_params_from_args(
    conversation: Conversation,
    provider: Optional[LLMProvider] = None,
    model: Optional[str] = None,
    max_tokens: int = 150,
    temperature: float = 0.7,
    stream: bool = False,
    use_cache: bool = True,
    **kwargs
) -> LegacyCompatibilityParams:
    """Unified factory function to create legacy parameter object"""
    return LegacyCompatibilityParams(
        conversation=conversation,
        provider=provider,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=stream,
        use_cache=use_cache,
        extra_kwargs=kwargs
    )


def from_legacy_args(params: LegacyFactoryParams) -> LegacyGenerationParams:
    """Convert LegacyFactoryParams to LegacyGenerationParams"""
    return params.to_legacy_generation_params()


def from_legacy_args_compatible(params: LegacyCompatibilityParams) -> LegacyGenerationParams:
    """Convert LegacyCompatibilityParams to LegacyGenerationParams"""
    return params.to_legacy_generation_params()


def from_legacy_args_compatible_individual(
    conversation: Conversation,
    provider: Optional[LLMProvider] = None,
    model: Optional[str] = None,
    max_tokens: int = 150,
    temperature: float = 0.7,
    stream: bool = False,
    use_cache: bool = True,
    **kwargs
) -> LegacyGenerationParams:
    """Legacy function for backward compatibility - DEPRECATED"""
    compatibility_params = LegacyCompatibilityParams(
        conversation=conversation,
        provider=provider,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=stream,
        use_cache=use_cache,
        extra_kwargs=kwargs
    )
    return from_legacy_args_compatible(compatibility_params)


def get_default_model_config(
    provider: LLMProvider = LLMProvider.OPENAI,
    task: str = 'general'
) -> ModelConfig:
    """Get default model configuration for provider and task"""
    
    configs = {
        LLMProvider.OPENAI: {
            'general': ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name='gpt-3.5-turbo',
                max_tokens=150,
                temperature=0.7
            ),
            'creative': ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name='gpt-4',
                max_tokens=500,
                temperature=0.9
            )
        },
        LLMProvider.ANTHROPIC: {
            'general': ModelConfig(
                provider=LLMProvider.ANTHROPIC,
                model_name='claude-3-sonnet',
                max_tokens=150,
                temperature=0.7
            )
        }
    }
    
    return configs.get(provider, {}).get(task, configs[LLMProvider.OPENAI]['general'])


# ================== EXPORTS ==================

__all__ = [
    # Main service classes
    "LLMServiceFactory",
    "ModelSelector",
    "ResponseCache",
    
    # Parameter objects
    "GenerationRequest",
    "ModelSelectionRequest", 
    "LegacyGenerationParams",
    "LegacyFactoryParams",
    "LegacyCompatibilityParams",
    
    # Validation services
    "LLMParameterValidationService",
    "LLMParameterValidator",
    
    # Shared abstractions
    "ParameterConverter",
    "LegacyCompatibilityService",
    
    # Factory functions
    "create_llm_factory",
    "create_generation_request",
    "create_model_selection_request",
    "create_legacy_generation_params",
    "create_legacy_factory_params",
    "create_legacy_compatibility_params",
    "create_legacy_params_from_args",
    
    # Conversion functions
    "from_legacy_args",
    "from_legacy_args_compatible",
    "from_legacy_args_compatible_individual",
    
    # Utility functions
    "get_default_model_config"
]
