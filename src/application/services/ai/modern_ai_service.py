"""
Modern AI Service - 2025 Enterprise Standards
Type-safe, async-first, with proper error handling and circuit breaker
"""

import asyncio
import base64
import logging
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Protocol, Union

import anthropic
import openai
import structlog
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel, Field, validator
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_exponential)

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from config.secure_config import AIServiceConfig

# from src.application.services.core.circuit_breaker import CircuitBreaker, CircuitBreakerError
from src.core.domain.entities.child import Child

# Metrics
ai_requests_total = Counter('ai_requests_total', 'Total AI requests', ['provider', 'model', 'status'])
ai_request_duration = Histogram('ai_request_duration_seconds', 'AI request duration', ['provider'])
ai_tokens_used = Counter('ai_tokens_used_total', 'Total tokens used', ['provider', 'type'])
ai_errors_total = Counter('ai_errors_total', 'Total AI errors', ['provider', 'error_type'])
active_ai_requests = Gauge('active_ai_requests', 'Active AI requests', ['provider'])


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


class AIModelType(Enum):
    """AI model types"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    MODERATION = "moderation"


class ResponseSafety(Enum):
    """Response safety levels"""
    SAFE = "safe"
    NEEDS_REVIEW = "needs_review"
    UNSAFE = "unsafe"


@dataclass
class AIRequest:
    """AI request data structure"""
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)
    max_tokens: int = 150
    temperature: float = 0.7
    child_id: Optional[str] = None
    session_id: Optional[str] = None
    require_safety_check: bool = True
    timeout: float = 30.0


@dataclass
class AIResponse:
    """AI response data structure"""
    content: str
    provider: AIProvider
    model: str
    tokens_used: int
    response_time: float
    safety_level: ResponseSafety
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class AIProviderProtocol(Protocol):
    """Protocol for AI providers"""
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate AI response"""
        ...
    
    async def check_safety(self, content: str) -> ResponseSafety:
        """Check content safety"""
        ...
    
    async def health_check(self) -> bool:
        """Check provider health"""
        ...


class OpenAIProvider:
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.provider = AIProvider.OPENAI
        self.logger = structlog.get_logger(f"{__name__}.OpenAI")
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=openai.APIError
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError))
    )
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using OpenAI"""
        start_time = time.time()
        active_ai_requests.labels(provider="openai").inc()
        
        try:
            # Prepare messages for child-safe conversation
            messages = [
                {
                    "role": "system", 
                    "content": self._get_child_safe_system_prompt(request.child_id)
                },
                {"role": "user", "content": request.prompt}
            ]
            
            # Add context if provided
            if request.context:
                context_msg = f"Context: {request.context}"
                messages.insert(-1, {"role": "assistant", "content": context_msg})
            
            # Make API call with circuit breaker
            async with self.circuit_breaker:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    timeout=request.timeout
                )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            response_time = time.time() - start_time
            
            # Safety check
            safety_level = await self.check_safety(content) if request.require_safety_check else ResponseSafety.SAFE
            
            # Create response
            ai_response = AIResponse(
                content=content,
                provider=self.provider,
                model=self.model,
                tokens_used=tokens_used,
                response_time=response_time,
                safety_level=safety_level,
                confidence_score=0.9,  # OpenAI generally high confidence
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "request_id": response.id
                }
            )
            
            # Update metrics
            ai_requests_total.labels(provider="openai", model=self.model, status="success").inc()
            ai_request_duration.labels(provider="openai").observe(response_time)
            ai_tokens_used.labels(provider="openai", type="total").inc(tokens_used)
            
            return ai_response
            
        except CircuitBreakerError:
            self.logger.error("OpenAI circuit breaker open")
            ai_errors_total.labels(provider="openai", error_type="circuit_breaker").inc()
            raise
            
        except openai.RateLimitError as e:
            self.logger.error(f"OpenAI rate limit exceeded: {e}")
            ai_errors_total.labels(provider="openai", error_type="rate_limit").inc()
            raise
            
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"OpenAI request failed: {e}")
            ai_requests_total.labels(provider="openai", model=self.model, status="error").inc()
            ai_errors_total.labels(provider="openai", error_type="unknown").inc()
            raise
            
        finally:
            active_ai_requests.labels(provider="openai").dec()
    
    async def check_safety(self, content: str) -> ResponseSafety:
        """Check content safety using OpenAI moderation"""
        try:
            moderation = await self.client.moderations.create(input=content)
            result = moderation.results[0]
            
            if result.flagged:
                return ResponseSafety.UNSAFE
            
            # Check specific categories for children
            high_risk_categories = ['violence', 'self-harm', 'sexual', 'hate']
            for category in high_risk_categories:
                if getattr(result.categories, category, False):
                    return ResponseSafety.UNSAFE
            
            return ResponseSafety.SAFE
            
        except Exception as e:
            self.logger.error(f"Safety check failed: {e}")
            return ResponseSafety.NEEDS_REVIEW
    
    async def health_check(self) -> bool:
        """Check OpenAI API health"""
        try:
            # Simple health check
            await self.client.models.list()
            return True
        except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)as e:
    logger.error(f"Error: {e}", exc_info=True)            return False
    
    def _get_child_safe_system_prompt(self, child_id: Optional[str] = None) -> str:
        """Get child-safe system prompt"""
        base_prompt = """You are Teddy, a friendly AI companion for children. You must:

1. Always use age-appropriate language and topics
2. Be encouraging, patient, and supportive
3. Avoid scary, violent, or inappropriate content
4. Focus on learning, creativity, and positive values
5. If asked about something inappropriate, gently redirect to a better topic
6. Keep responses concise and engaging for children
7. Use emojis occasionally to make conversations fun

Remember: Safety and child development are your top priorities."""

        if child_id:
            # Could customize based on child profile
            base_prompt += f"\n\nChild ID: {child_id} (customize responses accordingly)"
        
        return base_prompt


class AnthropicProvider:
    """Anthropic Claude provider implementation"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.provider = AIProvider.ANTHROPIC
        self.logger = structlog.get_logger(f"{__name__}.Anthropic")
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=anthropic.APIError
        )
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using Anthropic Claude"""
        start_time = time.time()
        active_ai_requests.labels(provider="anthropic").inc()
        
        try:
            # Prepare prompt for Claude
            system_prompt = self._get_child_safe_system_prompt()
            
            # Make API call with circuit breaker
            async with self.circuit_breaker:
                message = await self.client.messages.create(
                    model=self.model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": request.prompt}],
                    timeout=request.timeout
                )
            
            content = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens
            response_time = time.time() - start_time
            
            # Safety check
            safety_level = await self.check_safety(content) if request.require_safety_check else ResponseSafety.SAFE
            
            # Create response
            ai_response = AIResponse(
                content=content,
                provider=self.provider,
                model=self.model,
                tokens_used=tokens_used,
                response_time=response_time,
                safety_level=safety_level,
                confidence_score=0.85,  # Claude generally good confidence
                metadata={
                    "stop_reason": message.stop_reason,
                    "request_id": message.id
                }
            )
            
            # Update metrics
            ai_requests_total.labels(provider="anthropic", model=self.model, status="success").inc()
            ai_request_duration.labels(provider="anthropic").observe(response_time)
            ai_tokens_used.labels(provider="anthropic", type="total").inc(tokens_used)
            
            return ai_response
            
        except CircuitBreakerError:
            self.logger.error("Anthropic circuit breaker open")
            ai_errors_total.labels(provider="anthropic", error_type="circuit_breaker").inc()
            raise
            
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"Anthropic request failed: {e}")
            ai_requests_total.labels(provider="anthropic", model=self.model, status="error").inc()
            ai_errors_total.labels(provider="anthropic", error_type="unknown").inc()
            raise
            
        finally:
            active_ai_requests.labels(provider="anthropic").dec()
    
    async def check_safety(self, content: str) -> ResponseSafety:
        """Check content safety - basic implementation"""
        # Basic keyword filtering for child safety
        unsafe_keywords = ['violence', 'death', 'drugs', 'alcohol', 'weapon']
        content_lower = content.lower()
        
        for keyword in unsafe_keywords:
            if keyword in content_lower:
                return ResponseSafety.UNSAFE
        
        return ResponseSafety.SAFE
    
    async def health_check(self) -> bool:
        """Check Anthropic API health"""
        try:
            # Simple health check
            await self.client.messages.create(
                model=self.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "hi"}]
            )
            return True
        except Exception as e:
            return False
    
    def _get_child_safe_system_prompt(self) -> str:
        """Get child-safe system prompt for Claude"""
        return """You are Teddy, a friendly AI companion for children. Always be:
- Age-appropriate and educational
- Kind, patient, and encouraging  
- Focused on creativity and learning
- Safe and positive in all responses
Avoid any scary, violent, or inappropriate content."""


class ModernAIService:
    """
    Modern AI Service with multiple providers and enterprise features
    """
    
    def __init__(self, config: AIServiceConfig):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        self.providers: Dict[AIProvider, AIProviderProtocol] = {}
        self.current_provider = AIProvider(config.default_provider)
        self._initialize_providers()
        
        # Performance tracking
        self.request_count = 0
        self.error_count = 0
        self.total_tokens_used = 0
        self.average_response_time = 0.0
    
    def _initialize_providers(self) -> Any:
        """Initialize available AI providers"""
        if self.config.openai_api_key:
            self.providers[AIProvider.OPENAI] = OpenAIProvider(
                api_key=self.config.openai_api_key,
                model=self.config.default_model
            )
            
        if self.config.anthropic_api_key:
            self.providers[AIProvider.ANTHROPIC] = AnthropicProvider(
                api_key=self.config.anthropic_api_key
            )
        
        if not self.providers:
            raise ValueError("No AI providers configured with valid API keys")
        
        self.logger.info(f"Initialized AI providers: {list(self.providers.keys())}")
    
    async def generate_response(
        self, 
        prompt: str, 
        child_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AIResponse:
        """Generate AI response with automatic fallback"""
        request = AIRequest(
            prompt=prompt,
            child_id=child_id,
            context=context or {},
            **kwargs
        )
        
        # Try current provider first
        try:
            response = await self._make_request(self.current_provider, request)
            self._update_metrics(response)
            return response
            
        except Exception as e:
            self.logger.warning(f"Primary provider {self.current_provider} failed: {e}")
            
            # Try fallback providers
            for provider in self.providers:
                if provider != self.current_provider:
                    try:
                        self.logger.info(f"Trying fallback provider: {provider}")
                        response = await self._make_request(provider, request)
                        self._update_metrics(response)
                        return response
                        
                    except Exception as fallback_error:
                        self.logger.warning(f"Fallback provider {provider} failed: {fallback_error}")
                        continue
            
            # All providers failed
            self.error_count += 1
            raise RuntimeError("All AI providers failed")
    
    async def _make_request(self, provider: AIProvider, request: AIRequest) -> AIResponse:
        """Make request to specific provider"""
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")
        
        provider_instance = self.providers[provider]
        return await provider_instance.generate_response(request)
    
    def _update_metrics(AIResponse) -> None:
        """Update internal metrics"""
        self.request_count += 1
        self.total_tokens_used += response.tokens_used
        
        # Update average response time
        self.average_response_time = (
            (self.average_response_time * (self.request_count - 1) + response.response_time) 
            / self.request_count
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
        health_status = {
            "healthy": False,
            "providers": {},
            "active_provider": self.current_provider.value,
            "total_requests": self.request_count,
            "error_rate": self.error_count / max(self.request_count, 1) * 100
        }
        
        healthy_providers = 0
        for provider, instance in self.providers.items():
            try:
                is_healthy = await instance.health_check()
                health_status["providers"][provider.value] = is_healthy
                if is_healthy:
                    healthy_providers += 1
            except Exception as e:
                self.logger.error(f"Health check failed for {provider}: {e}")
                health_status["providers"][provider.value] = False
        
        health_status["healthy"] = healthy_providers > 0
        return health_status
    
    async def switch_provider(self, provider: AIProvider) -> bool:
        """Switch to a different provider"""
        if provider in self.providers:
            self.current_provider = provider
            self.logger.info(f"Switched to provider: {provider}")
            return True
        return False
    
    def get_available_providers(self) -> List[AIProvider]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    async def cleanup(self):
        """Cleanup resources"""
        # Close any open connections
        for provider_instance in self.providers.values():
            if hasattr(provider_instance, 'cleanup'):
                await provider_instance.cleanup() 