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
