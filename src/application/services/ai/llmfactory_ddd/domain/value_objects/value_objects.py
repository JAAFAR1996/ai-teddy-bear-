#!/usr/bin/env python3
"""
🏗️ Llmfactory Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

# Original imports
import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional, List, Union, Any, AsyncIterator

class LLMProvider(Enum):
    """Enumeration of supported Language Model Providers"""



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


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI models"""


class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic Claude models"""


class GoogleAdapter(BaseLLMAdapter):
    """Adapter for Google Generative AI models"""


class LocalLLMAdapter(BaseLLMAdapter):
    """Adapter for local LLM models (HuggingFace)"""


class ModelSelector:
    """Intelligent model selection based on various criteria"""


class ResponseCache:
    """Cache for LLM responses"""


class LLMServiceFactory:
    """
    Enhanced Factory for creating and managing Language Model services
    """