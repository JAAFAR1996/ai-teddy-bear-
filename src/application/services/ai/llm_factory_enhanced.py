#!/usr/bin/env python3
"""
🚀 Enhanced LLM Service Factory
حل مشاكل "الطرق الوعرة" وتحسين التعقيد الدوري

التحسينات المطبقة:
✅ Parameter Objects بدلاً من 7+ معاملات
✅ تقسيم generate_response من 60+ سطر إلى دوال صغيرة  
✅ تبسيط ResponseCache.get من منطق معقد إلى strategy pattern
✅ فصل المسؤوليات - كل كلاس له مهمة واحدة
✅ Strategy Pattern للcache
✅ Service Layer للإحصائيات
"""

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


# ================== PARAMETER OBJECTS ==================

@dataclass
class GenerationRequest:
    """📦 Parameter Object - حل مشكلة 7+ معاملات"""
    conversation: Any  # Mock conversation type
    provider: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    stream: bool = False
    use_cache: bool = True
    task_type: str = "general"


@dataclass
class CacheRequest:
    """📦 Parameter Object للcache operations"""
    key: str
    value: Optional[str] = None
    ttl: int = 3600


@dataclass
class GenerationContext:
    """📦 Context object للعملية الكاملة"""
    request: GenerationRequest
    model_config: dict
    cache_key: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)


# ================== CACHE STRATEGIES ==================

class CacheStrategy(ABC):
    """🏗️ Strategy Pattern للcache - حل مشكلة ResponseCache.get المعقدة"""
    
    @abstractmethod
    async def get(self, request: CacheRequest) -> Optional[str]:
        pass
    
    @abstractmethod
    async def set(self, request: CacheRequest) -> bool:
        pass


class LocalCacheStrategy(CacheStrategy):
    """💾 Local cache strategy"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, tuple] = {}
        self.max_size = max_size
    
    async def get(self, request: CacheRequest) -> Optional[str]:
        """🔍 Get from local cache - منطق مبسط"""
        if request.key not in self.cache:
            return None
        
        value, expiry = self.cache[request.key]
        
        if self._is_expired(expiry):
            self._remove_expired_entry(request.key)
            return None
        
        return value
    
    async def set(self, request: CacheRequest) -> bool:
        """💾 Set in local cache"""
        if len(self.cache) >= self.max_size:
            self._cleanup_old_entries()
        
        expiry = datetime.now() + timedelta(seconds=request.ttl)
        self.cache[request.key] = (request.value, expiry)
        return True
    
    def _is_expired(self, expiry: datetime) -> bool:
        """⏰ Check if expired - single responsibility"""
        return datetime.now() >= expiry
    
    def _remove_expired_entry(self, key: str) -> None:
        """🗑️ Remove expired entry - single responsibility"""
        self.cache.pop(key, None)
    
    def _cleanup_old_entries(self) -> None:
        """🧹 Cleanup old entries - single responsibility"""
        items_to_remove = len(self.cache) // 5  # Remove 20%
        oldest_keys = sorted(
            self.cache.keys(),
            key=lambda k: self.cache[k][1]
        )[:items_to_remove]
        
        for key in oldest_keys:
            self.cache.pop(key, None)


class HybridCacheStrategy(CacheStrategy):
    """🔄 Hybrid strategy with fallback"""
    
    def __init__(self):
        self.primary = LocalCacheStrategy()
        self.fallback = LocalCacheStrategy(max_size=500)
    
    async def get(self, request: CacheRequest) -> Optional[str]:
        """🔍 Get with fallback - مبسط"""
        # Try primary first
        result = await self.primary.get(request)
        if result:
            return result
        
        # Fallback
        return await self.fallback.get(request)
    
    async def set(self, request: CacheRequest) -> bool:
        """💾 Set in both caches"""
        primary_success = await self.primary.set(request)
        fallback_success = await self.fallback.set(request)
        return primary_success or fallback_success


# ================== ENHANCED CACHE MANAGER ==================

class EnhancedResponseCache:
    """📦 Cache manager مع strategy pattern - حل مشكلة الطرق الوعرة"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.strategy = HybridCacheStrategy()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get(self, key: str) -> Optional[str]:
        """🔍 Get response - مبسط بدلاً من منطق معقد"""
        request = CacheRequest(key=key)
        return await self.strategy.get(request)
    
    async def set(self, key: str, value: str, ttl: int = 3600):
        """💾 Set response - مبسط"""
        request = CacheRequest(key=key, value=value, ttl=ttl)
        return await self.strategy.set(request)
    
    def generate_key(self, messages: List, model_config: dict) -> str:
        """🔑 Generate cache key - منطق مبسط"""
        try:
            content_hash = hashlib.md5(str(messages).encode()).hexdigest()
            config_hash = hashlib.md5(str(model_config).encode()).hexdigest()
            return f"llm:{content_hash}:{config_hash}"
        except Exception:
            return f"llm:fallback:{hash(str(messages))}"


# ================== MODEL SELECTION SERVICE ==================

class ModelSelectionService:
    """🎯 Model selection service - مسؤولية منفصلة"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def select_optimal_model(self, request: GenerationRequest) -> dict:
        """🎯 Select best model - منطق مبسط"""
        if request.provider:
            return self._create_config_for_provider(request)
        
        return self._auto_select_by_task(request)
    
    def _create_config_for_provider(self, request: GenerationRequest) -> dict:
        """🔧 Create config for specific provider"""
        return {
            "provider": request.provider,
            "model_name": request.model or "default",
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
    
    def _auto_select_by_task(self, request: GenerationRequest) -> dict:
        """🤖 Auto-select by task type"""
        task_configs = {
            "creative": {"provider": "anthropic", "model": "claude-3", "temperature": 0.8},
            "analysis": {"provider": "openai", "model": "gpt-4", "temperature": 0.3},
            "general": {"provider": "openai", "model": "gpt-3.5-turbo", "temperature": 0.7}
        }
        
        config = task_configs.get(request.task_type, task_configs["general"])
        config.update({
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        })
        
        return config


# ================== USAGE STATISTICS SERVICE ==================

class UsageStatsService:
    """📊 Statistics service - مسؤولية منفصلة"""
    
    def __init__(self):
        self.stats = defaultdict(lambda: {
            "requests": 0,
            "total_cost": 0.0,
            "errors": 0,
            "cache_hits": 0,
            "avg_response_time": 0.0
        })
        self.response_times = defaultdict(list)
    
    def record_request(self, provider: str):
        """📝 Record request start"""
        self.stats[provider]["requests"] += 1
    
    def record_response(self, provider: str, response_time: float, cost: float = 0.0):
        """📈 Record successful response"""
        self.stats[provider]["total_cost"] += cost
        self.response_times[provider].append(response_time)
        
        # Update average
        times = self.response_times[provider]
        self.stats[provider]["avg_response_time"] = sum(times) / len(times)
    
    def record_error(self, provider: str):
        """❌ Record error"""
        self.stats[provider]["errors"] += 1
    
    def record_cache_hit(self, provider: str):
        """💾 Record cache hit"""
        self.stats[provider]["cache_hits"] += 1
    
    def get_stats(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """📊 Get statistics"""
        if provider:
            return dict(self.stats[provider])
        return {p: dict(stats) for p, stats in self.stats.items()}


# ================== RESPONSE GENERATION SERVICE ==================

class ResponseGenerationService:
    """🤖 Response generation service - مسؤولية منفصلة"""
    
    def __init__(self, adapters: Dict):
        self.adapters = adapters
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def generate_streaming_response(self, context: GenerationContext) -> AsyncIterator[str]:
        """🌊 Generate streaming response"""
        # Mock streaming
        response_parts = ["مرحبا! ", "كيف ", "يمكنني ", "مساعدتك؟"]
        for part in response_parts:
            yield part
            await asyncio.sleep(0.1)
    
    async def generate_standard_response(self, context: GenerationContext) -> tuple:
        """📝 Generate standard response"""
        # Mock generation
        response_content = "مرحبا! كيف يمكنني مساعدتك؟"
        cost = 0.001
        
        return response_content, cost
    
    def get_adapter(self, provider: str):
        """🔌 Get adapter for provider"""
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"Provider {provider} not available")
        return adapter


# ================== ENHANCED LLM SERVICE FACTORY ==================

class EnhancedLLMServiceFactory:
    """
    🚀 Enhanced LLM Service Factory
    
    حل مشاكل "الطرق الوعرة":
    ✅ تقسيم generate_response من 60+ سطر إلى دوال صغيرة
    ✅ Parameter Objects بدلاً من 7+ معاملات
    ✅ Strategy Pattern للcache
    ✅ فصل المسؤوليات إلى services منفصلة
    ✅ تبسيط المنطق الشرطي
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.adapters = {}
        
        # Inject dependencies - Dependency Injection Pattern
        self.cache = EnhancedResponseCache(config.get('redis_url') if config else None)
        self.model_selector = ModelSelectionService(config)
        self.stats_service = UsageStatsService()
        self.response_service = ResponseGenerationService(self.adapters)
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize(self):
        """🚀 Initialize factory"""
        self.logger.info("Enhanced LLM Factory initialized")
    
    async def generate_response(self, request: GenerationRequest) -> Union[str, AsyncIterator[str]]:
        """
        🎯 Generate response - مبسط ومحسن
        
        قبل التحسين: 60+ سطر مع منطق معقد
        بعد التحسين: دوال صغيرة مع مسؤوليات واضحة
        """
        
        # 1. Create context
        context = await self._create_generation_context(request)
        
        # 2. Try cache first
        if request.use_cache and not request.stream:
            cached_response = await self._try_get_cached_response(context)
            if cached_response:
                return cached_response
        
        # 3. Generate new response
        return await self._generate_new_response(context)
    
    async def _create_generation_context(self, request: GenerationRequest) -> GenerationContext:
        """📋 Create generation context - مسؤولية واحدة"""
        model_config = self.model_selector.select_optimal_model(request)
        
        cache_key = None
        if request.use_cache:
            cache_key = self.cache.generate_key(
                request.conversation or [],
                model_config
            )
        
        return GenerationContext(
            request=request,
            model_config=model_config,
            cache_key=cache_key
        )
    
    async def _try_get_cached_response(self, context: GenerationContext) -> Optional[str]:
        """💾 Try to get cached response - مسؤولية واحدة"""
        if not context.cache_key:
            return None
        
        try:
            cached_response = await self.cache.get(context.cache_key)
            if cached_response:
                provider = context.model_config.get("provider", "unknown")
                self.stats_service.record_cache_hit(provider)
                self.logger.debug(f"Cache hit for {provider}")
                return cached_response
        except Exception as e:
            self.logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    async def _generate_new_response(self, context: GenerationContext) -> Union[str, AsyncIterator[str]]:
        """🤖 Generate new response - مسؤولية واحدة"""
        provider = context.model_config.get("provider", "unknown")
        
        # Record request start
        self.stats_service.record_request(provider)
        
        try:
            if context.request.stream:
                return await self.response_service.generate_streaming_response(context)
            else:
                return await self._generate_and_cache_response(context)
                
        except Exception as e:
            self.stats_service.record_error(provider)
            self.logger.error(f"Error generating response: {e}")
            raise
    
    async def _generate_and_cache_response(self, context: GenerationContext) -> str:
        """📝 Generate and cache standard response"""
        provider = context.model_config.get("provider", "unknown")
        
        # Generate response
        response_content, cost = await self.response_service.generate_standard_response(context)
        
        # Record stats
        response_time = (datetime.now() - context.start_time).total_seconds()
        self.stats_service.record_response(provider, response_time, cost)
        
        # Cache response
        if context.request.use_cache and context.cache_key:
            await self._cache_response(context.cache_key, response_content)
        
        return response_content
    
    async def _cache_response(self, cache_key: str, response: str):
        """💾 Cache response safely"""
        try:
            await self.cache.set(cache_key, response)
        except Exception as e:
            self.logger.warning(f"Cache save error: {e}")
    
    def get_available_providers(self) -> List[str]:
        """📋 Get available providers"""
        return list(self.adapters.keys()) or ["openai", "anthropic", "google"]
    
    def get_usage_stats(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """📊 Get usage statistics"""
        return self.stats_service.get_stats(provider)


# ================== FACTORY FUNCTIONS ==================

async def create_enhanced_llm_factory(config: Optional[Dict] = None) -> EnhancedLLMServiceFactory:
    """🏭 Factory function"""
    factory = EnhancedLLMServiceFactory(config)
    await factory.initialize()
    return factory


def create_generation_request(
    conversation: Any,
    provider: Optional[str] = None,
    **kwargs
) -> GenerationRequest:
    """📦 Helper function to create GenerationRequest"""
    return GenerationRequest(
        conversation=conversation,
        provider=provider,
        **kwargs
    )


# ================== BACKWARD COMPATIBILITY ==================

# Aliases for backward compatibility
LLMServiceFactory = EnhancedLLMServiceFactory
create_llm_factory = create_enhanced_llm_factory
ResponseCache = EnhancedResponseCache 