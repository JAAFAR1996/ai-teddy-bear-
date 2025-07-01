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


from .llm_base import (
    LLMProvider, ModelConfig, LLMResponse, BaseLLMAdapter
)
from .llm_openai_adapter import OpenAIAdapter
from .llm_anthropic_adapter import AnthropicAdapter  
from .llm_google_adapter import GoogleAdapter


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
        
        # Simple model selection logic
        if task_type == "creative_writing":
            return ModelConfig(
                provider=LLMProvider.ANTHROPIC,
                model_name="claude-3-sonnet",
                max_tokens=2048,
                temperature=0.8
            )
        elif task_type == "analysis":
            return ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name="gpt-4",
                max_tokens=1024,
                temperature=0.3
            )
        else:
            return ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                max_tokens=1024,
                temperature=0.7
            )


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
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    return value.decode('utf-8')
            except Exception:
                pass

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
        """Generate response using specified or auto-selected provider"""
        
        # Auto-select provider if not specified
        if provider is None:
            provider = LLMProvider.OPENAI  # Default

        # Get adapter
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"Provider {provider} not available")

        # Create model config
        model_config = ModelConfig(
            provider=provider,
            model_name=model or self._get_default_model(provider),
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        # Check cache if enabled
        cache_key = None
        if use_cache and not stream:
            cache_key = self.cache.generate_key(conversation.messages, model_config)
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                self.logger.debug(f"Cache hit for {provider}")
                return cached_response

        try:
            # Update stats
            self.usage_stats[provider]["requests"] += 1

            # Generate response
            if stream:
                return adapter.generate_stream(conversation.messages, model_config)
            else:
                response = await adapter.generate(conversation.messages, model_config)
                
                # Update cost stats
                self.usage_stats[provider]["total_cost"] += response.cost
                
                # Cache response
                if use_cache and cache_key:
                    await self.cache.set(cache_key, response.content)
                
                return response.content

        except Exception as e:
            self.usage_stats[provider]["errors"] += 1
            self.logger.error(f"Error generating response with {provider}: {e}")
            raise

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


async def create_llm_factory(config: Optional[Dict] = None) -> LLMServiceFactory:
    """Create and initialize LLM factory"""
    factory = LLMServiceFactory(config)
    await factory.initialize()
    return factory


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
