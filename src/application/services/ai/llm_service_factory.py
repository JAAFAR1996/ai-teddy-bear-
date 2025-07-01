# Transformers imports patched for development
# llm_service_factory.py - Enhanced version with full adapter pattern

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


class LLMProvider(Enum):
    """Enumeration of supported Language Model Providers"""
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    GOOGLE = 'google'
    HUGGINGFACE = 'huggingface'
    LOCAL = 'local'
    AZURE_OPENAI = 'azure_openai'
    COHERE = 'cohere'
    REPLICATE = 'replicate'


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    provider: LLMProvider
    model_name: str
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    system_prompt: Optional[str] = None
    cost_per_1k_tokens: float = 0.0
    supports_streaming: bool = True
    supports_functions: bool = False
    context_window: int = 4096
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    provider: LLMProvider
    model: str
    usage: Dict[str, int]
    cost: float = 0.0
    latency_ms: int = 0
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseLLMAdapter(ABC):
    """Abstract base class for LLM adapters"""

    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        self.api_key = api_key
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        model_config: ModelConfig
    ) -> LLMResponse:
        """Generate response from LLM"""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        model_config: ModelConfig
    ) -> AsyncIterator[str]:
        """Generate streaming response from LLM"""
        pass

    @abstractmethod
    def validate_config(self, model_config: ModelConfig) -> bool:
        """Validate model configuration"""
        pass

    def calculate_cost(self, usage: Dict[str, int], model_config: ModelConfig) -> float:
        """Calculate cost based on usage"""
        total_tokens = usage.get('total_tokens', 0)
        return (total_tokens / 1000) * model_config.cost_per_1k_tokens


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI models"""

    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(api_key, config)
        if self.api_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = openai.AsyncOpenAI()

    async def generate(
        self,
        messages: List[Message],
        model_config: ModelConfig
    ) -> LLMResponse:
        """Generate response using OpenAI API"""
        start_time = asyncio.get_event_loop().time()

        try:
            response = await self.client.chat.completions.create(
                model=model_config.model_name,
                messages=[{"role": msg.role, "content": msg.content}
                          for msg in messages],
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
                frequency_penalty=model_config.frequency_penalty,
                presence_penalty=model_config.presence_penalty,
                stop=model_config.stop_sequences if model_config.stop_sequences else None
            )
            usage = response.usage.model_dump()
            content = response.choices[0].message.content
            latency_ms = int(
                (asyncio.get_event_loop().time() - start_time) * 1000)
            cost = self.calculate_cost(usage, model_config)

            return LLMResponse(
                content=content,
                provider=LLMProvider.OPENAI,
                model=model_config.model_name,
                usage=usage,
                cost=cost,
                latency_ms=latency_ms,
                metadata={'finish_reason': response.choices[0].finish_reason}
            )
        except Exception as e:
            self.logger.error(f"OpenAI generation error: {e}")
            raise

    async def generate_stream(
        self,
        messages: List[Message],
        model_config: ModelConfig
    ) -> AsyncIterator[str]:
        """Generate streaming response using OpenAI API"""
        try:
            stream = await self.client.chat.completions.create(
                model=model_config.model_name,
                messages=[{"role": msg.role, "content": msg.content}
                          for msg in messages],
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                stream=True
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and getattr(delta, "content", None):
                    yield delta.content
        except Exception as e:
            self.logger.error(f"OpenAI streaming error: {e}")
            raise

    def validate_config(self, model_config: ModelConfig) -> bool:
        """Validate OpenAI model configuration"""
        valid_models = [
            'gpt-4', 'gpt-4-turbo', 'gpt-4-32k',
            'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'
        ]
        return model_config.model_name in valid_models


class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic Claude models"""

    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(api_key, config)
        if self.api_key:
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def generate(
        self,
        messages: List[Message],
        model_config: ModelConfig
    ) -> LLMResponse:
        """Generate response using Anthropic API"""
        start_time = asyncio.get_event_loop().time()

        try:
            # Convert messages format
            system_message = next(
                (msg.content for msg in messages if msg.role == "system"), None)
            user_messages = [{"role": msg.role, "content": msg.content}
                             for msg in messages if msg.role != "system"]

            response = await self.client.messages.create(
                model=model_config.model_name,
                max_tokens=model_config.max_tokens,
                messages=user_messages,
                system=system_message,
                temperature=model_config.temperature
            )

            usage = {
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }

            latency_ms = int(
                (asyncio.get_event_loop().time() - start_time) * 1000)
            cost = self.calculate_cost(usage, model_config)

            return LLMResponse(
                content=response.content[0].text,
                provider=LLMProvider.ANTHROPIC,
                model=model_config.model_name,
                usage=usage,
                cost=cost,
                latency_ms=latency_ms
            )

        except Exception as e:
            self.logger.error(f"Anthropic generation error: {e}")
            raise

    async def generate_stream(
        self,
        messages: List[Message],
        model_config: ModelConfig
    ) -> AsyncIterator[str]:
        """Generate streaming response using Anthropic API"""
        try:
            system_message = next(
                (msg.content for msg in messages if msg.role == "system"), None)
            user_messages = [{"role": msg.role, "content": msg.content}
                             for msg in messages if msg.role != "system"]

            async with self.client.messages.stream(
                model=model_config.model_name,
                max_tokens=model_config.max_tokens,
                messages=user_messages,
                system=system_message,
                temperature=model_config.temperature
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            self.logger.error(f"Anthropic streaming error: {e}")
            raise

    def validate_config(self, model_config: ModelConfig) -> bool:
        """Validate Anthropic model configuration"""
        valid_models = [
            'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku',
            'claude-2.1', 'claude-2.0', 'claude-instant-1.2'
        ]
        return model_config.model_name in valid_models


class GoogleAdapter(BaseLLMAdapter):
    """Adapter for Google Generative AI models"""

    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(api_key, config)
        if self.api_key:
            genai.configure(api_key=self.api_key)

    async def generate(
        self,
        messages: List[Message],
        model_config: ModelConfig
    ) -> LLMResponse:
        """Generate response using Google Generative AI"""
        start_time = asyncio.get_event_loop().time()

        try:
            model = genai.GenerativeModel(model_config.model_name)

            # Convert messages to Google format
            chat = model.start_chat(history=[])
            for msg in messages[:-1]:
                if msg.role == 'user':
                    chat.send_message(msg.content)

            response = await model.generate_content_async(
                messages[-1].content,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=model_config.max_tokens,
                    temperature=model_config.temperature,
                    top_p=model_config.top_p,
                    stop_sequences=model_config.stop_sequences
                )
            )

            # Estimate token usage
            usage = {
                'prompt_tokens': len(messages[-1].content.split()) * 1.3,
                'completion_tokens': len(response.text.split()) * 1.3,
                'total_tokens': 0
            }
            usage['total_tokens'] = usage['prompt_tokens'] + \
                usage['completion_tokens']

            latency_ms = int(
                (asyncio.get_event_loop().time() - start_time) * 1000)
            cost = self.calculate_cost(usage, model_config)

            return LLMResponse(
                content=response.text,
                provider=LLMProvider.GOOGLE,
                model=model_config.model_name,
                usage={k: int(v) for k, v in usage.items()},
                cost=cost,
                latency_ms=latency_ms
            )

        except Exception as e:
            self.logger.error(f"Google generation error: {e}")
            raise

    async def generate_stream(
        self,
        messages: List[Message],
        model_config: ModelConfig
    ) -> AsyncIterator[str]:
        """Generate streaming response using Google API"""
        try:
            model = genai.GenerativeModel(model_config.model_name)
            response = await model.generate_content_async(
                messages[-1].content,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=model_config.max_tokens,
                    temperature=model_config.temperature
                ),
                stream=True
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            self.logger.error(f"Google streaming error: {e}")
            raise

    def validate_config(self, model_config: ModelConfig) -> bool:
        """Validate Google model configuration"""
        valid_models = ['gemini-pro', 'gemini-pro-vision', 'gemini-ultra']
        return model_config.model_name in valid_models


class LocalLLMAdapter(BaseLLMAdapter):
    """Adapter for local LLM models (HuggingFace)"""

    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(api_key, config)
        self.models_cache = {}

    async def generate(
        self,
        messages: List[Message],
        model_config: ModelConfig
    ) -> LLMResponse:
        """Generate response using local model"""
        start_time = asyncio.get_event_loop().time()

        try:
            # Load model and tokenizer
            model, tokenizer = await self._load_model(model_config.model_name)

            # Format messages
            prompt = self._format_messages(messages, tokenizer)

            # Generate
            inputs = tokenizer(prompt, return_tensors="pt",
                               truncation=True, max_length=model_config.context_window)

            with torch.no_grad():
                outputs = model.generate(
                    inputs.input_ids,
                    max_new_tokens=model_config.max_tokens,
                    temperature=model_config.temperature,
                    top_p=model_config.top_p,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )

            response_text = tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

            # Calculate usage
            usage = {
                'prompt_tokens': inputs.input_ids.shape[1],
                'completion_tokens': outputs.shape[1] - inputs.input_ids.shape[1],
                'total_tokens': outputs.shape[1]
            }

            latency_ms = int(
                (asyncio.get_event_loop().time() - start_time) * 1000)

            return LLMResponse(
                content=response_text,
                provider=LLMProvider.LOCAL,
                model=model_config.model_name,
                usage=usage,
                cost=0.0,  # Local models have no API cost
                latency_ms=latency_ms
            )

        except Exception as e:
            self.logger.error(f"Local LLM generation error: {e}")
            raise

    async def generate_stream(
        self,
        messages: List[Message],
        model_config: ModelConfig
    ) -> AsyncIterator[str]:
        """Generate streaming response using local model"""
        # Simplified streaming for local models
        response = await self.generate(messages, model_config)

        # Simulate streaming by yielding words
        words = response.content.split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.01)  # Small delay to simulate streaming

    async def _load_model(self, model_name: str):
        """Load model and tokenizer with caching"""
        if model_name not in self.models_cache:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.models_cache[model_name] = (model, tokenizer)

        return self.models_cache[model_name]

    def _format_messages(self, messages: List[Message], tokenizer) -> str:
        """Format messages for the model"""
        formatted = ""
        for msg in messages:
            if msg.role == "system":
                formatted += f"System: {msg.content}\n"
            elif msg.role == "user":
                formatted += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                formatted += f"Assistant: {msg.content}\n"
        formatted += "Assistant: "
        return formatted

    def validate_config(self, model_config: ModelConfig) -> bool:
        """Validate local model configuration"""
        # Check if model exists on HuggingFace
        return True  # Simplified validation


class ModelSelector:
    """Intelligent model selection based on various criteria"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.performance_history = defaultdict(list)

    def select_model(
        self,
        task_type: str,
        context_length: int,
        required_features: List[str],
        budget_constraint: Optional[float] = None,
        latency_requirement: Optional[int] = None
    ) -> ModelConfig:
        """Select best model based on requirements"""

        # Define model capabilities
        model_capabilities = {
            'gpt-4-turbo': {
                'context_window': 128000,
                'features': ['functions', 'vision', 'json_mode'],
                'cost_per_1k': 0.03,
                'avg_latency_ms': 2000,
                'quality_score': 0.95
            },
            'claude-3-opus': {
                'context_window': 200000,
                'features': ['long_context', 'coding'],
                'cost_per_1k': 0.075,
                'avg_latency_ms': 2500,
                'quality_score': 0.93
            },
            'gemini-pro': {
                'context_window': 32000,
                'features': ['multimodal', 'free_tier'],
                'cost_per_1k': 0.001,
                'avg_latency_ms': 1500,
                'quality_score': 0.85
            },
            'gpt-3.5-turbo': {
                'context_window': 16000,
                'features': ['functions', 'json_mode'],
                'cost_per_1k': 0.002,
                'avg_latency_ms': 800,
                'quality_score': 0.80
            }
        }

        # Score each model
        scores = {}
        for model_name, capabilities in model_capabilities.items():
            score = 0

            # Context window check
            if capabilities['context_window'] >= context_length:
                score += 20

            # Feature requirements
            matching_features = set(required_features) & set(
                capabilities['features'])
            score += len(matching_features) * 10

            # Budget constraint
            if budget_constraint:
                if capabilities['cost_per_1k'] <= budget_constraint:
                    score += 15

            # Latency requirement
            if latency_requirement:
                if capabilities['avg_latency_ms'] <= latency_requirement:
                    score += 15

            # Quality score
            score += capabilities['quality_score'] * 30

            # Historical performance
            if model_name in self.performance_history:
                avg_success_rate = sum(
                    self.performance_history[model_name]) / len(self.performance_history[model_name])
                score += avg_success_rate * 20

            scores[model_name] = score

        # Select best model
        best_model = max(scores, key=scores.get)

        # Map to provider
        provider_map = {
            'gpt-4-turbo': LLMProvider.OPENAI,
            'gpt-3.5-turbo': LLMProvider.OPENAI,
            'claude-3-opus': LLMProvider.ANTHROPIC,
            'gemini-pro': LLMProvider.GOOGLE
        }

        return ModelConfig(
            provider=provider_map[best_model],
            model_name=best_model,
            max_tokens=2048,
            temperature=0.7,
            cost_per_1k_tokens=model_capabilities[best_model]['cost_per_1k'],
            context_window=model_capabilities[best_model]['context_window']
        )

    def record_performance(int) -> None:
        """Record model performance for future selection"""
        self.performance_history[model_name].append(1.0 if success else 0.0)

        # Keep only last 100 records
        if len(self.performance_history[model_name]) > 100:
            self.performance_history[model_name].pop(0)


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
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    return value.decode('utf-8')
            except Exception as e:
    logger.warning(f"Ignored exception: {e}")

        # Fall back to local cache
        if key in self.local_cache:
            value, expiry = self.local_cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self.local_cache[key]

        return None

    async def set(self, key: str, value: str):
        """Set cached response"""
        # Set in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(key, self.except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)as e:
    logger.error(f"Error: {e}", exc_info=True)            except Exception as e:
    logger.warning(f"Ignored exception: {e}")

        # Set in local cache
        expiry = datetime.now() + timedelta(seconds=self.cache_ttl)
        self.local_cache[key] = (value, expiry)

    def generate_key(self, messages: List[Message], model_config: ModelConfig) -> str:
        """Generate cache key from messages and config"""
        content = json.dumps({
            'messages': [{'role': m.role, 'content': m.content} for m in messages],
            'model': model_config.model_name,
            'temperature': model_config.temperature,
            'max_tokens': model_config.max_tokens
        }, sort_keys=True)

        return hashlib.sha256(content.encode()).hexdigest()


class LLMServiceFactory:
    """
    Enhanced Factory for creating and managing Language Model services
    """

    def __init__(self, config=None):
        """Initialize LLM service factory"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize adapters
        self.adapters: Dict[LLMProvider, BaseLLMAdapter] = {}
        self._init_adapters()

        # Initialize components
        self.model_selector = ModelSelector(config)
        redis_url = None
        if hasattr(self.config, 'database'):
            redis_url = getattr(self.config.database, 'REDIS_URL', None)
        else:
            redis_url = getattr(self.config, 'REDIS_URL', None)
        self.cache = ResponseCache(redis_url)

        # Rate limiting
        self.rate_limits = defaultdict(
            lambda: {'requests': 0, 'reset_time': datetime.now()})
        self.rate_limit_config = {
            LLMProvider.OPENAI: {'requests_per_minute': 60},
            LLMProvider.ANTHROPIC: {'requests_per_minute': 50},
            LLMProvider.GOOGLE: {'requests_per_minute': 60}
        }

        # Usage tracking
        self.usage_stats = defaultdict(lambda: {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'total_latency_ms': 0
        })

    def _init_adapters(self) -> Any:
        """Initialize API adapters for different providers"""

        # OpenAI
        if getattr(self.config, "api_keys", None) and getattr(self.config.api_keys, "OPENAI_API_KEY", None):
            self.adapters[LLMProvider.OPENAI] = OpenAIAdapter(
                api_key=getattr(self.config.api_keys, "OPENAI_API_KEY"),
                config=self.config
            )

        # Anthropic
        if getattr(self.config, "api_keys", None) and getattr(self.config.api_keys, "ANTHROPIC_API_KEY", None):
            self.adapters[LLMProvider.ANTHROPIC] = AnthropicAdapter(
                api_key=getattr(self.config.api_keys, "ANTHROPIC_API_KEY"),
                config=self.config
            )

        # Google
        if getattr(self.config, "api_keys", None) and getattr(self.config.api_keys, "GOOGLE_GEMINI_API_KEY", None):
            self.adapters[LLMProvider.GOOGLE] = GoogleAdapter(
                api_key=getattr(self.config.api_keys, "GOOGLE_GEMINI_API_KEY"),
                config=self.config
            )
        # ملاحظة: إذا كان لديك FEATURE_FLAGS ضعها في config أو أزلها أو ضع قيمة ثابتة True مؤقتاً
        enable_local = True  # عدل حسب الحاجة
        if enable_local:
            self.adapters[LLMProvider.LOCAL] = LocalLLMAdapter(
                config=self.config)

    async def initialize(self):
        """Initialize async components"""
        await self.cache.connect()

    async def generate_response(
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
        """
        Generate a response using the specified or auto-selected LLM

        Args:
            conversation: Conversation context
            provider: LLM provider to use (auto-select if None)
            model: Specific model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            stream: Whether to stream the response
            use_cache: Whether to use response cache
            **kwargs: Additional model-specific parameters

        Returns:
            Generated response string or async iterator for streaming
        """

        # Auto-select provider and model if not specified
        if not provider or not model:
            # Calculate context length
            context_length = sum(len(msg.content)
                                 for msg in conversation.messages)

            # Determine required features
            required_features = []
            if stream:
                required_features.append('streaming')
            if 'functions' in kwargs:
                required_features.append('functions')

            # Select best model
            model_config = self.model_selector.select_model(
                task_type='conversation',
                context_length=context_length,
                required_features=required_features,
                budget_constraint=kwargs.get('budget_constraint'),
                latency_requirement=kwargs.get('latency_requirement')
            )

            provider = model_config.provider
            model = model_config.model_name
        else:
            # Create model config
            model_config = ModelConfig(
                provider=provider,
                model_name=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

        # Check rate limits
        if not await self._check_rate_limit(provider):
            raise Exception(f"Rate limit exceeded for {provider.value}")

        # Check cache
        if use_cache and not stream:
            cache_key = self.cache.generate_key(
                conversation.messages, model_config)
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                self.logger.info(f"Cache hit for {provider.value}/{model}")
                return cached_response

        # Get adapter
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"No adapter available for provider: {provider}")

        # Validate configuration
        if not adapter.validate_config(model_config):
            raise ValueError(
                f"Invalid configuration for {provider.value}: {model}")

        try:
            # Generate response
            if stream:
                return adapter.generate_stream(conversation.messages, model_config)
            else:
                response = await adapter.generate(conversation.messages, model_config)

                # Update statistics
                self._update_usage_stats(provider, response)

                # Record performance
                self.model_selector.record_performance(
                    model,
                    success=True,
                    latency_ms=response.latency_ms
                )

                # Cache response
                if use_cache:
                    await self.cache.set(cache_key, response.content)

                return response.content

        except Exception as e:
            self.logger.error(f"Generation error with {provider.value}: {e}")

            # Record failure
            self.model_selector.record_performance(
                model, success=False, latency_ms=0)

            # Try fallback if available
            if kwargs.get('enable_fallback', True):
                fallback_provider = self._get_fallback_provider(provider)
                if fallback_provider:
                    self.logger.info(
                        f"Falling back to {fallback_provider.value}")
                    # Prevent infinite recursion
                    kwargs['enable_fallback'] = False
                    return await self.generate_response(
                        conversation,
                        provider=fallback_provider,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=stream,
                        use_cache=use_cache,
                        **kwargs
                    )

            raise

    async def generate_with_retry(
        self,
        conversation: Conversation,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """Generate response with automatic retry on failure"""
        last_error = None

        for attempt in range(max_retries):
            try:
                return await self.generate_response(conversation, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)

        raise last_error

    async def generate_batch(
        self,
        conversations: List[Conversation],
        **kwargs
    ) -> List[str]:
        """Generate responses for multiple conversations in parallel"""
        tasks = [
            self.generate_response(conv, **kwargs)
            for conv in conversations
        ]

        return await asyncio.gather(*tasks, return_exceptions=True)

    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of available LLM providers"""
        return list(self.adapters.keys())

    def get_available_models(self, provider: LLMProvider) -> List[str]:
        """Get available models for a provider"""
        models_map = {
            LLMProvider.OPENAI: ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
            LLMProvider.ANTHROPIC: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
            LLMProvider.GOOGLE: ['gemini-pro', 'gemini-pro-vision'],
            LLMProvider.LOCAL: ['meta-llama/Llama-2-7b-chat-hf',
                                'mistralai/Mistral-7B-Instruct-v0.2']
        }

        return models_map.get(provider, [])

    def get_model_info(self, provider: LLMProvider, model: str) -> Dict[str, Any]:
        """Get detailed information about a model"""
        # This would typically fetch from a configuration or API
        return {
            'provider': provider.value,
            'model': model,
            'context_window': 4096,
            'max_tokens': 2048,
            'supports_streaming': True,
            'supports_functions': provider == LLMProvider.OPENAI,
            'cost_per_1k_tokens': 0.01
        }

    def get_usage_stats(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """Get usage statistics"""
        if provider:
            return dict(self.usage_stats[provider])
        else:
            # Aggregate stats for all providers
            total_stats = {
                'total_requests': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'total_latency_ms': 0,
                'by_provider': {}
            }

            for p, stats in self.usage_stats.items():
                total_stats['total_requests'] += stats['total_requests']
                total_stats['total_tokens'] += stats['total_tokens']
                total_stats['total_cost'] += stats['total_cost']
                total_stats['total_latency_ms'] += stats['total_latency_ms']
                total_stats['by_provider'][p.value] = dict(stats)

            return total_stats

    async def _check_rate_limit(self, provider: LLMProvider) -> bool:
        """Check if request is within rate limits"""
        if provider not in self.rate_limit_config:
            return True

        limit_config = self.rate_limit_config[provider]
        rate_data = self.rate_limits[provider]

        # Reset if time window has passed
        if datetime.now() >= rate_data['reset_time']:
            rate_data['requests'] = 0
            rate_data['reset_time'] = datetime.now() + timedelta(minutes=1)

        # Check limit
        if rate_data['requests'] >= limit_config['requests_per_minute']:
            return False

        rate_data['requests'] += 1
        return True

    def _update_usage_stats(LLMResponse) -> None:
        """Update usage statistics"""
        stats = self.usage_stats[provider]
        stats['total_requests'] += 1
        stats['total_tokens'] += response.usage.get('total_tokens', 0)
        stats['total_cost'] += response.cost
        stats['total_latency_ms'] += response.latency_ms

    def _get_fallback_provider(self, failed_provider: LLMProvider) -> Optional[LLMProvider]:
        """Get fallback provider for a failed provider"""
        fallback_map = {
            LLMProvider.OPENAI: LLMProvider.ANTHROPIC,
            LLMProvider.ANTHROPIC: LLMProvider.GOOGLE,
            LLMProvider.GOOGLE: LLMProvider.OPENAI
        }

        fallback = fallback_map.get(failed_provider)
        if fallback in self.adapters:
            return fallback

        # Return any available provider
        available = list(self.adapters.keys())
        available.remove(failed_provider)
        return available[0] if available else None

    async def test_provider(self, provider: LLMProvider) -> Dict[str, Any]:
        """Test a provider's availability and performance"""
        test_conversation = Conversation(messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user",
                    content="Say 'test successful' if you can read this.")
        ])

        try:
            start_time = asyncio.get_event_loop().time()
            response = await self.generate_response(
                test_conversation,
                provider=provider,
                max_tokens=20
            )

            latency_ms = int(
                (asyncio.get_event_loop().time() - start_time) * 1000)

            return {
                'provider': provider.value,
                'status': 'available',
                'latency_ms': latency_ms,
                'response': response,
                'models': self.get_available_models(provider)
            }

        except Exception as e:
            return {
                'provider': provider.value,
                'status': 'unavailable',
                'error': str(e),
                'models': []
            }

    async def optimize_for_task(
        self,
        task_description: str,
        sample_input: str,
        evaluation_criteria: List[str]
    ) -> ModelConfig:
        """
        Automatically optimize model selection for a specific task

        Args:
            task_description: Description of the task
            sample_input: Sample input for testing
            evaluation_criteria: List of criteria to optimize for

        Returns:
            Optimal ModelConfig for the task
        """

        test_conversation = Conversation(messages=[
            Message(role="system", content=f"Task: {task_description}"),
            Message(role="user", content=sample_input)
        ])

        results = []

        # Test each available provider/model combination
        for provider in self.get_available_providers():
            for model in self.get_available_models(provider):
                try:
                    start_time = asyncio.get_event_loop().time()

                    response = await self.generate_response(
                        test_conversation,
                        provider=provider,
                        model=model,
                        max_tokens=200
                    )

                    latency_ms = int(
                        (asyncio.get_event_loop().time() - start_time) * 1000)

                    # Simple scoring based on criteria
                    score = 0
                    if 'speed' in evaluation_criteria:
                        score += (5000 - latency_ms) / 5000  # Normalize to 0-1
                    if 'quality' in evaluation_criteria:
                        score += len(response) / 200  # Simple quality proxy
                    if 'cost' in evaluation_criteria:
                        model_info = self.get_model_info(provider, model)
                        # Normalize cost
                        score += 1 - (model_info['cost_per_1k_tokens'] / 0.1)

                    results.append({
                        'provider': provider,
                        'model': model,
                        'score': score / len(evaluation_criteria),
                        'latency_ms': latency_ms
                    })

                except Exception as e:
                    self.logger.warning(
                        f"Failed to test {provider.value}/{model}: {e}")

        # Select best model
        if results:
            best = max(results, key=lambda x: x['score'])
            return ModelConfig(
                provider=best['provider'],
                model_name=best['model'],
                max_tokens=200,
                temperature=0.7
            )
        else:
            # Default fallback
            return ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name='gpt-3.5-turbo',
                max_tokens=200,
                temperature=0.7
            )


# Utility functions for easy factory usage

async def create_llm_factory(config: Optional[Dict] = None) -> LLMServiceFactory:
    """Create and initialize LLM factory"""
    factory = LLMServiceFactory(config)
    await factory.initialize()
    return factory


def get_default_model_config(
    provider: LLMProvider = LLMProvider.OPENAI,
    task: str = 'general'
) -> ModelConfig:
    """Get default model configuration for a provider and task"""

    configs = {
        'general': {
            LLMProvider.OPENAI: ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name='gpt-3.5-turbo',
                max_tokens=150,
                temperature=0.7
            ),
            LLMProvider.ANTHROPIC: ModelConfig(
                provider=LLMProvider.ANTHROPIC,
                model_name='claude-3-haiku',
                max_tokens=150,
                temperature=0.7
            ),
            LLMProvider.GOOGLE: ModelConfig(
                provider=LLMProvider.GOOGLE,
                model_name='gemini-pro',
                max_tokens=150,
                temperature=0.7
            )
        },
        'creative': {
            LLMProvider.OPENAI: ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name='gpt-4-turbo',
                max_tokens=500,
                temperature=0.9,
                top_p=0.95
            )
        },
        'code': {
            LLMProvider.OPENAI: ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name='gpt-4-turbo',
                max_tokens=1000,
                temperature=0.2,
                stop_sequences=['```']
            )
        }
    }

    return configs.get(task, configs['general']).get(provider, configs['general'][LLMProvider.OPENAI])