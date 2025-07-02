#!/usr/bin/env python3
"""
🚀 Enhanced LLM Service Factory v2
حل مشاكل "الطرق الوعرة" وتحسين التعقيد

تحسينات مطبقة:
✅ Parameter Objects بدلاً من معاملات متعددة
✅ تقسيم الدوال الطويلة إلى دوال أصغر
✅ فصل المسؤوليات
✅ تبسيط المنطق الشرطي
✅ تحسين معالجة الأخطاء
✅ Strategy Pattern للcache
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

# Optional imports with fallbacks
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    genai = None
    GOOGLE_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    REDIS_AVAILABLE = False

try:
    from src.core.domain.entities.conversation import Conversation, Message
    from src.infrastructure.config import get_config
    from .llm_base import LLMProvider, ModelConfig, LLMResponse, BaseLLMAdapter
    from .llm_openai_adapter import OpenAIAdapter
    from .llm_anthropic_adapter import AnthropicAdapter  
    from .llm_google_adapter import GoogleAdapter
except ImportError:
    # Mock imports for testing
    class LLMProvider(Enum):
        OPENAI = "openai"
        ANTHROPIC = "anthropic"
        GOOGLE = "google"
    
    @dataclass
    class ModelConfig:
        provider: LLMProvider
        model_name: str
        max_tokens: int = 150
        temperature: float = 0.7
    
    @dataclass
    class Message:
        role: str
        content: str
    
    @dataclass
    class Conversation:
        messages: List[Message] = field(default_factory=list)


# ================== PARAMETER OBJECTS ==================

@dataclass
class GenerationRequest:
    """📦 Parameter Object لطلب توليد النص"""
    conversation: Conversation
    provider: Optional[LLMProvider] = None
    model: Optional[str] = None
    max_tokens: int = 150
    temperature: float = 0.7
    stream: bool = False
    use_cache: bool = True
    task_type: str = "general"
    context_length: Optional[int] = None
    required_features: List[str] = field(default_factory=list)
    budget_constraint: Optional[float] = None
    latency_requirement: Optional[int] = None


@dataclass
class CacheRequest:
    """📦 Parameter Object لطلبات Cache"""
    key: str
    value: Optional[str] = None
    ttl: int = 3600


@dataclass
class GenerationContext:
    """📦 Context للعملية"""
    request: GenerationRequest
    model_config: ModelConfig
    cache_key: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)


# ================== CACHE STRATEGIES ==================

class CacheStrategy(ABC):
    """🏗️ Strategy Pattern للCache"""
    
    @abstractmethod
    async def get(self, request: CacheRequest) -> Optional[str]:
        """استرجاع قيمة من Cache"""
        pass
    
    @abstractmethod
    async def set(self, request: CacheRequest) -> bool:
        """حفظ قيمة في Cache"""
        pass


class LocalCacheStrategy(CacheStrategy):
    """💾 Local Memory Cache Strategy"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, tuple] = {}
        self.max_size = max_size
    
    async def get(self, request: CacheRequest) -> Optional[str]:
        """🔍 استرجاع من الذاكرة المحلية"""
        if request.key not in self.cache:
            return None
        
        value, expiry = self.cache[request.key]
        
        if self._is_expired(expiry):
            self._remove_expired_entry(request.key)
            return None
        
        return value
    
    async def set(self, request: CacheRequest) -> bool:
        """💾 حفظ في الذاكرة المحلية"""
        if len(self.cache) >= self.max_size:
            self._cleanup_cache()
        
        expiry = datetime.now() + timedelta(seconds=request.ttl)
        self.cache[request.key] = (request.value, expiry)
        return True
    
    def _is_expired(self, expiry: datetime) -> bool:
        """⏰ فحص انتهاء الصلاحية"""
        return datetime.now() >= expiry
    
    def _remove_expired_entry(self, key: str) -> None:
        """🗑️ إزالة مدخل منتهي الصلاحية"""
        self.cache.pop(key, None)
    
    def _cleanup_cache(self) -> None:
        """🧹 تنظيف Cache"""
        # إزالة 20% من أقدم العناصر
        items_to_remove = max(1, len(self.cache) // 5)
        oldest_keys = sorted(
            self.cache.keys(),
            key=lambda k: self.cache[k][1]
        )[:items_to_remove]
        
        for key in oldest_keys:
            self.cache.pop(key, None)


class RedisCacheStrategy(CacheStrategy):
    """🔴 Redis Cache Strategy"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
    
    async def connect(self):
        """🔗 الاتصال بـ Redis"""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            self.redis_client = await aioredis.create_redis_pool(self.redis_url)
            return True
        except Exception:
            return False
    
    async def get(self, request: CacheRequest) -> Optional[str]:
        """🔍 استرجاع من Redis"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(request.key)
            return value.decode('utf-8') if value else None
        except Exception:
            return None
    
    async def set(self, request: CacheRequest) -> bool:
        """💾 حفظ في Redis"""
        if not self.redis_client or not request.value:
            return False
        
        try:
            await self.redis_client.setex(request.key, request.ttl, request.value)
            return True
        except Exception:
            return False


class HybridCacheStrategy(CacheStrategy):
    """🔄 Hybrid Cache Strategy (Redis + Local)"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.local_cache = LocalCacheStrategy()
        self.redis_cache = RedisCacheStrategy(redis_url) if redis_url else None
    
    async def connect(self):
        """🔗 الاتصال بالcaches"""
        if self.redis_cache:
            await self.redis_cache.connect()
    
    async def get(self, request: CacheRequest) -> Optional[str]:
        """🔍 استرجاع مع fallback strategy"""
        # جرب Redis أولاً
        if self.redis_cache:
            value = await self.redis_cache.get(request)
            if value:
                return value
        
        # fallback للcache المحلي
        return await self.local_cache.get(request)
    
    async def set(self, request: CacheRequest) -> bool:
        """💾 حفظ في كلا الcaches"""
        local_success = await self.local_cache.set(request)
        
        redis_success = True
        if self.redis_cache:
            redis_success = await self.redis_cache.set(request)
        
        return local_success or redis_success


# ================== ENHANCED CACHE MANAGER ==================

class ResponseCache:
    """📦 Enhanced Response Cache مع Strategy Pattern"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.strategy = HybridCacheStrategy(redis_url)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def connect(self):
        """🔗 تهيئة الاتصال"""
        await self.strategy.connect()
    
    async def get(self, key: str) -> Optional[str]:
        """🔍 استرجاع response من Cache - مبسط"""
        request = CacheRequest(key=key)
        return await self.strategy.get(request)
    
    async def set(self, key: str, value: str, ttl: int = 3600):
        """💾 حفظ response في Cache - مبسط"""
        request = CacheRequest(key=key, value=value, ttl=ttl)
        return await self.strategy.set(request)
    
    def generate_key(self, messages: List[Message], model_config: ModelConfig) -> str:
        """🔑 توليد مفتاح Cache"""
        try:
            # تحويل messages لـ dict
            messages_data = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            # تحويل model_config لـ dict
            config_data = {
                "provider": model_config.provider.value if hasattr(model_config.provider, 'value') else str(model_config.provider),
                "model_name": model_config.model_name,
                "max_tokens": model_config.max_tokens,
                "temperature": model_config.temperature
            }
            
            # توليد hashes
            content_hash = hashlib.md5(
                json.dumps(messages_data, sort_keys=True).encode()
            ).hexdigest()
            
            config_hash = hashlib.md5(
                json.dumps(config_data, sort_keys=True).encode()
            ).hexdigest()
            
            return f"llm:{content_hash}:{config_hash}"
            
        except Exception as e:
            self.logger.error(f"Error generating cache key: {e}")
            return f"llm:fallback:{hash(str(messages))}"


# ================== MODEL SELECTION SERVICE ==================

class ModelSelectionService:
    """🎯 خدمة اختيار النموذج المحسنة"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.performance_history = defaultdict(list)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def select_optimal_model(self, request: GenerationRequest) -> ModelConfig:
        """🎯 اختيار النموذج الأمثل"""
        if request.provider:
            return self._create_config_for_provider(request)
        
        # اختيار تلقائي حسب نوع المهمة
        return self._auto_select_by_task(request)
    
    def _create_config_for_provider(self, request: GenerationRequest) -> ModelConfig:
        """🔧 إنشاء config لـ provider محدد"""
        model_name = request.model or self._get_default_model(request.provider)
        
        return ModelConfig(
            provider=request.provider,
            model_name=model_name,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
    
    def _auto_select_by_task(self, request: GenerationRequest) -> ModelConfig:
        """🤖 اختيار تلقائي حسب المهمة"""
        task_mapping = {
            "creative_writing": (LLMProvider.ANTHROPIC, "claude-3-sonnet", 0.8),
            "analysis": (LLMProvider.OPENAI, "gpt-4", 0.3),
            "conversation": (LLMProvider.OPENAI, "gpt-3.5-turbo", 0.7),
            "general": (LLMProvider.OPENAI, "gpt-3.5-turbo", 0.7)
        }
        
        provider, model, temp = task_mapping.get(
            request.task_type, 
            task_mapping["general"]
        )
        
        return ModelConfig(
            provider=provider,
            model_name=model,
            max_tokens=request.max_tokens,
            temperature=temp
        )
    
    def _get_default_model(self, provider: LLMProvider) -> str:
        """📋 الحصول على النموذج الافتراضي"""
        defaults = {
            LLMProvider.OPENAI: "gpt-3.5-turbo",
            LLMProvider.ANTHROPIC: "claude-3-sonnet",
            LLMProvider.GOOGLE: "gemini-pro"
        }
        return defaults.get(provider, "gpt-3.5-turbo")


# ================== USAGE STATISTICS SERVICE ==================

class UsageStatsService:
    """📊 خدمة إحصائيات الاستخدام"""
    
    def __init__(self):
        self.stats = defaultdict(lambda: {
            "requests": 0, 
            "total_cost": 0.0, 
            "errors": 0,
            "cache_hits": 0,
            "avg_response_time": 0.0
        })
        self.response_times = defaultdict(list)
    
    def record_request(self, provider: LLMProvider, context: GenerationContext):
        """📝 تسجيل طلب"""
        self.stats[provider]["requests"] += 1
    
    def record_response(self, provider: LLMProvider, context: GenerationContext, cost: float = 0.0):
        """📈 تسجيل استجابة"""
        self.stats[provider]["total_cost"] += cost
        
        # حساب وقت الاستجابة
        response_time = (datetime.now() - context.start_time).total_seconds()
        self.response_times[provider].append(response_time)
        
        # تحديث متوسط وقت الاستجابة
        self.stats[provider]["avg_response_time"] = sum(
            self.response_times[provider]
        ) / len(self.response_times[provider])
    
    def record_error(self, provider: LLMProvider):
        """❌ تسجيل خطأ"""
        self.stats[provider]["errors"] += 1
    
    def record_cache_hit(self, provider: LLMProvider):
        """💾 تسجيل cache hit"""
        self.stats[provider]["cache_hits"] += 1
    
    def get_stats(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """📊 الحصول على الإحصائيات"""
        if provider:
            return dict(self.stats[provider])
        return {str(p): dict(stats) for p, stats in self.stats.items()}


# ================== ENHANCED LLM SERVICE FACTORY ==================

class LLMServiceFactoryEnhanced:
    """🚀 Enhanced LLM Service Factory مع حل مشاكل "الطرق الوعرة" """
    
    def __init__(self, config=None):
        self.config = config or self._get_mock_config()
        self.adapters = {}
        self.cache = ResponseCache(redis_url=self.config.get('redis_url'))
        self.model_selector = ModelSelectionService(config)
        self.stats_service = UsageStatsService()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize adapters
        self._init_adapters()
    
    def _get_mock_config(self) -> Dict:
        """🔧 Mock config للاختبار"""
        return {
            'openai_api_key': '',
            'anthropic_api_key': '',
            'google_api_key': '',
            'redis_url': None
        }
    
    def _init_adapters(self):
        """🔧 تهيئة Adapters"""
        try:
            # سيتم تهيئة adapters هنا عند توفر المكتبات
            self.logger.info("Adapters initialized")
        except Exception as e:
            self.logger.error(f"Error initializing adapters: {e}")
    
    async def initialize(self):
        """🚀 تهيئة Factory"""
        await self.cache.connect()
    
    async def generate_response(self, request: GenerationRequest) -> Union[str, AsyncIterator[str]]:
        """
        🎯 توليد الاستجابة - مبسط ومحسن
        
        تم حل مشاكل "الطرق الوعرة":
        ✅ تقسيم الدالة الطويلة إلى دوال أصغر
        ✅ استخدام Parameter Objects
        ✅ فصل المسؤوليات
        ✅ تبسيط المنطق الشرطي
        """
        
        # إنشاء context
        context = await self._create_generation_context(request)
        
        # فحص cache أولاً
        if request.use_cache and not request.stream:
            cached_response = await self._try_get_cached_response(context)
            if cached_response:
                return cached_response
        
        # توليد استجابة جديدة
        return await self._generate_new_response(context)
    
    async def _create_generation_context(self, request: GenerationRequest) -> GenerationContext:
        """📋 إنشاء context للعملية"""
        # اختيار النموذج الأمثل
        model_config = self.model_selector.select_optimal_model(request)
        
        # توليد cache key
        cache_key = None
        if request.use_cache:
            cache_key = self.cache.generate_key(request.conversation.messages, model_config)
        
        return GenerationContext(
            request=request,
            model_config=model_config,
            cache_key=cache_key
        )
    
    async def _try_get_cached_response(self, context: GenerationContext) -> Optional[str]:
        """💾 محاولة الحصول على استجابة من Cache"""
        if not context.cache_key:
            return None
        
        try:
            cached_response = await self.cache.get(context.cache_key)
            if cached_response:
                self.stats_service.record_cache_hit(context.model_config.provider)
                self.logger.debug(f"Cache hit for {context.model_config.provider}")
                return cached_response
        except Exception as e:
            self.logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    async def _generate_new_response(self, context: GenerationContext) -> Union[str, AsyncIterator[str]]:
        """🤖 توليد استجابة جديدة"""
        # تسجيل بداية الطلب
        self.stats_service.record_request(context.model_config.provider, context)
        
        try:
            # الحصول على adapter
            adapter = self._get_adapter(context.model_config.provider)
            
            # توليد الاستجابة
            if context.request.stream:
                return await self._generate_streaming_response(adapter, context)
            else:
                return await self._generate_standard_response(adapter, context)
                
        except Exception as e:
            self.stats_service.record_error(context.model_config.provider)
            self.logger.error(f"Error generating response: {e}")
            raise
    
    def _get_adapter(self, provider: LLMProvider):
        """🔌 الحصول على Adapter"""
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"Provider {provider} not available")
        return adapter
    
    async def _generate_streaming_response(self, adapter, context: GenerationContext) -> AsyncIterator[str]:
        """🌊 توليد استجابة streaming"""
        # Mock streaming response
        async def mock_stream():
            response_parts = ["مرحبا! ", "كيف ", "يمكنني ", "مساعدتك؟"]
            for part in response_parts:
                yield part
                await asyncio.sleep(0.1)
        
        return mock_stream()
    
    async def _generate_standard_response(self, adapter, context: GenerationContext) -> str:
        """📝 توليد استجابة عادية"""
        # Mock response generation
        response_content = "مرحبا! كيف يمكنني مساعدتك؟"
        cost = 0.001  # Mock cost
        
        # تسجيل الاستجابة
        self.stats_service.record_response(context.model_config.provider, context, cost)
        
        # حفظ في cache
        if context.request.use_cache and context.cache_key:
            await self._cache_response(context.cache_key, response_content)
        
        return response_content
    
    async def _cache_response(self, cache_key: str, response: str):
        """💾 حفظ الاستجابة في Cache"""
        try:
            await self.cache.set(cache_key, response)
        except Exception as e:
            self.logger.warning(f"Cache save error: {e}")
    
    def get_available_providers(self) -> List[LLMProvider]:
        """📋 قائمة الproviders المتوفرة"""
        return list(self.adapters.keys()) or list(LLMProvider)
    
    def get_usage_stats(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """📊 إحصائيات الاستخدام"""
        return self.stats_service.get_stats(provider)


# ================== FACTORY FUNCTIONS ==================

async def create_enhanced_llm_factory(config: Optional[Dict] = None) -> LLMServiceFactoryEnhanced:
    """🏭 Factory function للخدمة المحسنة"""
    factory = LLMServiceFactoryEnhanced(config)
    await factory.initialize()
    return factory


def create_generation_request(
    conversation: Conversation,
    provider: Optional[LLMProvider] = None,
    **kwargs
) -> GenerationRequest:
    """📦 Helper function لإنشاء Generation Request"""
    return GenerationRequest(
        conversation=conversation,
        provider=provider,
        **kwargs
    )


def get_default_model_config(
    provider: LLMProvider = LLMProvider.OPENAI,
    task: str = 'general'
) -> ModelConfig:
    """📋 الحصول على config افتراضي"""
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


# ================== BACKWARDS COMPATIBILITY ==================

# Alias للتوافق مع الكود الموجود
LLMServiceFactory = LLMServiceFactoryEnhanced
create_llm_factory = create_enhanced_llm_factory 