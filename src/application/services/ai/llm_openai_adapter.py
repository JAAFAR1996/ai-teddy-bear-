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


from .llm_base import BaseLLMAdapter, LLMResponse, ModelConfig, LLMProvider, Message


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
