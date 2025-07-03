#!/usr/bin/env python3
"""
🎯 مثال تطبيقي - كيف تعمل جميع الخدمات مع الأساس الجديد
يوضح حل مشاكل:
- cache_service: 137 ملف مكرر
- audio_service: 115 ملف مكرر  
- emotion_service: 117 ملف مكرر
- جميع الخدمات الأخرى
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio

# استيراد الأساس المعماري الجديد
from src.core.architecture.foundation import (
    IService, ServiceHealth, singleton, inject, container
)

# ===== 1. تعريف الواجهات الموحدة =====

class ICacheService(ABC):
    """واجهة موحدة للتخزين المؤقت"""
    @abstractmethod
    async def get(self, key: str) -> Any: pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool: pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool: pass


class IAudioService(ABC):
    """واجهة موحدة للصوت"""
    @abstractmethod
    async def process_audio(self, audio_data: bytes) -> Dict[str, Any]: pass
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str: pass


class IEmotionService(ABC):
    """واجهة موحدة لتحليل المشاعر"""
    @abstractmethod
    async def analyze_emotion(self, text: str) -> Dict[str, Any]: pass


class IDatabaseService(ABC):
    """واجهة موحدة لقاعدة البيانات"""
    @abstractmethod
    async def save(self, table: str, data: Dict) -> bool: pass
    
    @abstractmethod
    async def get(self, table: str, id: str) -> Optional[Dict]: pass


# ===== 2. تنفيذ الخدمات مع DI =====

@singleton(category="infrastructure")
class CacheService(IService):
    """
    خدمة التخزين المؤقت الموحدة
    ✅ بدلاً من 137 ملف مكرر - خدمة واحدة!
    """
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._is_healthy = True
    
    async def initialize(self) -> None:
        """تهيئة الخدمة"""
        print("🚀 تهيئة CacheService...")
        # تهيئة Redis connection مثلاً
        self._is_healthy = True
    
    async def get(self, key: str) -> Any:
        """الحصول على قيمة من التخزين المؤقت"""
        return self._cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """حفظ قيمة في التخزين المؤقت"""
        self._cache[key] = value
        return True
    
    async def delete(self, key: str) -> bool:
        """حذف قيمة من التخزين المؤقت"""
        return self._cache.pop(key, None) is not None
    
    async def health_check(self) -> ServiceHealth:
        """فحص صحة الخدمة"""
        return ServiceHealth.HEALTHY if self._is_healthy else ServiceHealth.UNHEALTHY
    
    async def cleanup(self) -> None:
        """تنظيف الموارد"""
        self._cache.clear()


@singleton(category="infrastructure")
class DatabaseService(IService):
    """
    خدمة قاعدة البيانات الموحدة
    ✅ بدلاً من 119 ملف مكرر - خدمة واحدة!
    """
    
    def __init__(self, cache_service: ICacheService):
        # ✅ Dependency Injection تلقائي!
        self.cache_service = cache_service
        self._connection = None
    
    async def initialize(self) -> None:
        """تهيئة الخدمة"""
        print("🚀 تهيئة DatabaseService...")
        # إنشاء اتصال قاعدة البيانات
    
    async def save(self, table: str, data: Dict) -> bool:
        """حفظ البيانات"""
        # حفظ في قاعدة البيانات
        print(f"💾 حفظ في {table}: {data}")
        
        # ✅ استخدام cache service تلقائياً
        cache_key = f"{table}:{data.get('id', 'unknown')}"
        await self.cache_service.set(cache_key, data)
        
        return True
    
    async def get(self, table: str, id: str) -> Optional[Dict]:
        """الحصول على البيانات"""
        cache_key = f"{table}:{id}"
        
        # ✅ فحص التخزين المؤقت أولاً
        cached = await self.cache_service.get(cache_key)
        if cached:
            print(f"📦 من التخزين المؤقت: {cache_key}")
            return cached
        
        # البحث في قاعدة البيانات
        print(f"🔍 من قاعدة البيانات: {table}:{id}")
        # ... query database
        
        return None
    
    async def health_check(self) -> ServiceHealth:
        return ServiceHealth.HEALTHY
    
    async def cleanup(self) -> None:
        """تنظيف الاتصالات"""
        if self._connection:
            # إغلاق اتصال قاعدة البيانات
            pass


@singleton(category="ai")
class AudioService(IService):
    """
    خدمة الصوت الموحدة
    ✅ بدلاً من 115 ملف مكرر - خدمة واحدة!
    """
    
    def __init__(self, cache_service: ICacheService, database_service: IDatabaseService):
        # ✅ حقن التبعيات تلقائياً - لا توجد تبعيات دائرية!
        self.cache_service = cache_service
        self.database_service = database_service
    
    async def initialize(self) -> None:
        print("🚀 تهيئة AudioService...")
        # تهيئة مكتبات معالجة الصوت
    
    async def process_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """معالجة الصوت"""
        # فحص التخزين المؤقت
        audio_hash = hash(audio_data)
        cache_key = f"audio_processed:{audio_hash}"
        
        cached_result = await self.cache_service.get(cache_key)
        if cached_result:
            return cached_result
        
        # معالجة الصوت
        result = {
            "transcription": "مرحباً تيدي!",
            "emotion": "happy",
            "confidence": 0.95
        }
        
        # حفظ في التخزين المؤقت وقاعدة البيانات
        await self.cache_service.set(cache_key, result)
        await self.database_service.save("audio_processing", {
            "id": str(audio_hash),
            "result": result,
            "timestamp": "2025-01-01"
        })
        
        return result
    
    async def transcribe(self, audio_data: bytes) -> str:
        """تحويل الصوت إلى نص"""
        result = await self.process_audio(audio_data)
        return result.get("transcription", "")
    
    async def health_check(self) -> ServiceHealth:
        return ServiceHealth.HEALTHY
    
    async def cleanup(self) -> None:
        """تنظيف الموارد"""
        pass


@singleton(category="ai")
class EmotionService(IService):
    """
    خدمة تحليل المشاعر الموحدة
    ✅ بدلاً من 117 ملف مكرر - خدمة واحدة!
    """
    
    def __init__(self, cache_service: ICacheService):
        self.cache_service = cache_service
    
    async def initialize(self) -> None:
        print("🚀 تهيئة EmotionService...")
    
    async def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """تحليل المشاعر"""
        cache_key = f"emotion:{hash(text)}"
        
        # فحص التخزين المؤقت
        cached = await self.cache_service.get(cache_key)
        if cached:
            return cached
        
        # تحليل المشاعر
        result = {
            "primary_emotion": "happy",
            "confidence": 0.85,
            "emotions": {"happy": 0.85, "excited": 0.15}
        }
        
        # حفظ في التخزين المؤقت
        await self.cache_service.set(cache_key, result)
        
        return result
    
    async def health_check(self) -> ServiceHealth:
        return ServiceHealth.HEALTHY
    
    async def cleanup(self) -> None:
        pass


# ===== 3. تسجيل الخدمات =====

def register_all_services():
    """تسجيل جميع الخدمات في الحاوية"""
    print("📋 تسجيل جميع الخدمات...")
    
    # تسجيل الواجهات مع التنفيذ
    container.register_singleton(ICacheService, CacheService)
    container.register_singleton(IDatabaseService, DatabaseService)
    container.register_singleton(IAudioService, AudioService)
    container.register_singleton(IEmotionService, EmotionService)
    
    print("✅ تم تسجيل جميع الخدمات!")


# ===== 4. مثال للاستخدام =====

async def demonstrate_unified_services():
    """عرض توضيحي للخدمات الموحدة"""
    print("\n🎯 عرض توضيحي للخدمات الموحدة")
    print("="*50)
    
    # تسجيل الخدمات
    register_all_services()
    
    # تهيئة جميع الخدمات
    await container.initialize_all()
    
    # استخدام الخدمات
    print("\n🎬 استخدام الخدمات:")
    
    # الحصول على الخدمات
    audio_service = await inject(IAudioService)
    emotion_service = await inject(IEmotionService)
    
    # معالجة صوت
    audio_data = "مرحباً تيدي، كيف حالك؟".encode('utf-8')
    audio_result = await audio_service.process_audio(audio_data)
    print(f"🎵 نتيجة معالجة الصوت: {audio_result}")
    
    # تحليل المشاعر
    text = "أنا سعيد جداً اليوم!"
    emotion_result = await emotion_service.analyze_emotion(text)
    print(f"😊 تحليل المشاعر: {emotion_result}")
    
    # فحص صحة الخدمات
    print("\n🏥 فحص صحة الخدمات:")
    health_status = await container.health_check_all()
    for service_name, health in health_status.items():
        print(f"  {service_name}: {health.value}")
    
    # معلومات الحاوية
    print("\n📊 معلومات الحاوية:")
    service_info = container.get_service_info()
    print(f"إجمالي الخدمات: {service_info['total_services']}")
    print(f"الخدمات المهيأة: {service_info['initialized_services']}")
    
    # تنظيف
    await container.cleanup()


if __name__ == "__main__":
    print("🏗️ مثال الخدمات الموحدة - الأساس المعماري الجديد")
    print("يحل مشاكل:")
    print("❌ 1,186 ملف مكرر → ✅ خدمات موحدة")
    print("❌ تبعيات دائرية → ✅ DI Container")
    print("❌ نسخ ولصق → ✅ إعادة استخدام")
    print("❌ عدم وضوح المعمارية → ✅ طبقات واضحة")
    
    asyncio.run(demonstrate_unified_services()) 