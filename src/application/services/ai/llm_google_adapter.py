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


class GoogleAdapter(BaseLLMAdapter):
    """Adapter for Google Generative AI models"""

    def __init__(
            self,
            api_key: Optional[str] = None,
            config: Optional[Dict] = None):
        super().__init__(api_key, config)
        if self.api_key:
            genai.configure(api_key=self.api_key)

    async def generate(
        self, messages: List[Message], model_config: ModelConfig
    ) -> LLMResponse:
        """Generate response using Google Generative AI"""
        start_time = asyncio.get_event_loop().time()

        try:
            model = genai.GenerativeModel(model_config.model_name)

            # Convert messages to Google format
            chat = model.start_chat(history=[])
            for msg in messages[:-1]:
                if msg.role == "user":
                    chat.send_message(msg.content)

            response = await model.generate_content_async(
                messages[-1].content,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=model_config.max_tokens,
                    temperature=model_config.temperature,
                    top_p=model_config.top_p,
                    stop_sequences=model_config.stop_sequences,
                ),
            )

            # Estimate token usage
            usage = {
                "prompt_tokens": len(messages[-1].content.split()) * 1.3,
                "completion_tokens": len(response.text.split()) * 1.3,
                "total_tokens": 0,
            }
            usage["total_tokens"] = usage["prompt_tokens"] + \
                usage["completion_tokens"]

            latency_ms = int(
                (asyncio.get_event_loop().time() - start_time) * 1000)
            cost = self.calculate_cost(usage, model_config)

            return LLMResponse(
                content=response.text,
                provider=LLMProvider.GOOGLE,
                model=model_config.model_name,
                usage={k: int(v) for k, v in usage.items()},
                cost=cost,
                latency_ms=latency_ms,
            )

        except Exception as e:
            self.logger.error(f"Google generation error: {e}")
            raise

    async def generate_stream(
        self, messages: List[Message], model_config: ModelConfig
    ) -> AsyncIterator[str]:
        """Generate streaming response using Google API"""
        try:
            model = genai.GenerativeModel(model_config.model_name)
            response = await model.generate_content_async(
                messages[-1].content,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=model_config.max_tokens,
                    temperature=model_config.temperature,
                ),
                stream=True,
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            self.logger.error(f"Google streaming error: {e}")
            raise

    def validate_config(self, model_config: ModelConfig) -> bool:
        """Validate Google model configuration"""
        valid_models = ["gemini-pro", "gemini-pro-vision", "gemini-ultra"]
        return model_config.model_name in valid_models
