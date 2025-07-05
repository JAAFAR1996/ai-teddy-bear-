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
    from src.infrastructure.external_services.mock.transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
    )

import redis.asyncio as aioredis

from src.core.domain.entities.conversation import Conversation, Message
from src.infrastructure.config import get_config


from .llm_base import BaseLLMAdapter, LLMResponse, ModelConfig, LLMProvider, Message


class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic Claude models"""

    def __init__(
            self,
            api_key: Optional[str] = None,
            config: Optional[Dict] = None):
        super().__init__(api_key, config)
        if self.api_key:
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def generate(
        self, messages: List[Message], model_config: ModelConfig
    ) -> LLMResponse:
        """Generate response using Anthropic API"""
        start_time = asyncio.get_event_loop().time()

        try:
            # Convert messages format
            system_message = next(
                (msg.content for msg in messages if msg.role == "system"), None
            )
            user_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
                if msg.role != "system"
            ]

            response = await self.client.messages.create(
                model=model_config.model_name,
                max_tokens=model_config.max_tokens,
                messages=user_messages,
                system=system_message,
                temperature=model_config.temperature,
            )

            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens
                + response.usage.output_tokens,
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
                latency_ms=latency_ms,
            )

        except Exception as e:
            self.logger.error(f"Anthropic generation error: {e}")
            raise

    async def generate_stream(
        self, messages: List[Message], model_config: ModelConfig
    ) -> AsyncIterator[str]:
        """Generate streaming response using Anthropic API"""
        try:
            system_message = next(
                (msg.content for msg in messages if msg.role == "system"), None
            )
            user_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
                if msg.role != "system"
            ]

            async with self.client.messages.stream(
                model=model_config.model_name,
                max_tokens=model_config.max_tokens,
                messages=user_messages,
                system=system_message,
                temperature=model_config.temperature,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            self.logger.error(f"Anthropic streaming error: {e}")
            raise

    def validate_config(self, model_config: ModelConfig) -> bool:
        """Validate Anthropic model configuration"""
        valid_models = [
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2",
        ]
        return model_config.model_name in valid_models
