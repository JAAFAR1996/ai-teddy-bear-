#!/usr/bin/env python3
"""
📦 Moderation Cache Manager
إدارة التخزين المؤقت للنتائج

المسؤوليات:
- تخزين نتائج الفحص مؤقتاً
- إدارة انتهاء الصلاحية
- منع تسرب الذاكرة
- تحسين الأداء
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple


class ModerationCacheManager:
    """📦 مدير التخزين المؤقت"""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cache: Dict[str, Tuple[Dict[str, Any], datetime]] = {}
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size

    def get(self, content: str, age: int, language: str) -> Optional[Dict[str, Any]]:
        """🔍 البحث في Cache"""
        cache_key = self._generate_key(content, age, language)

        if cache_key not in self.cache:
            return None

        cached_result, timestamp = self.cache[cache_key]

        # فحص انتهاء الصلاحية
        if self._is_expired(timestamp):
            del self.cache[cache_key]
            return None

        return cached_result

    def set(self, content: str, age: int, language: str, result: Dict[str, Any]) -> None:
        """💾 حفظ في Cache"""
        # تنظيف Cache إذا امتلأ
        if len(self.cache) >= self.max_size:
            self._cleanup_cache()

        cache_key = self._generate_key(content, age, language)
        self.cache[cache_key] = (result, datetime.now())

    def _generate_key(self, content: str, age: int, language: str) -> str:
        """🔑 توليد مفتاح Cache"""
        key_data = f"{content}:{age}:{language}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _is_expired(self, timestamp: datetime) -> bool:
        """⏰ فحص انتهاء الصلاحية"""
        elapsed = (datetime.now() - timestamp).total_seconds()
        return elapsed >= self.ttl_seconds

    def _cleanup_cache(self) -> None:
        """🧹 تنظيف Cache من العناصر القديمة"""
        # إزالة العناصر منتهية الصلاحية أولاً
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if self._is_expired(timestamp)
        ]

        for key in expired_keys:
            del self.cache[key]

        # إذا لا يزال ممتلئاً، أزل الأقدم
        if len(self.cache) >= self.max_size:
            oldest_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k][1]
            )[:200]  # أزل أقدم 200 عنصر

            for key in oldest_keys:
                del self.cache[key]

        self.logger.info(f"Cache cleaned, current size: {len(self.cache)}")

    def clear(self) -> None:
        """🗑️ مسح Cache بالكامل"""
        self.cache.clear()
        self.logger.info("Cache cleared completely")

    def get_stats(self) -> Dict[str, Any]:
        """📊 إحصائيات Cache"""
        return {
            "current_size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "usage_percentage": (len(self.cache) / self.max_size) * 100,
        }


def create_cache_manager(ttl_seconds: int = 3600, max_size: int = 1000) -> ModerationCacheManager:
    """🏭 Factory function"""
    return ModerationCacheManager(ttl_seconds, max_size)
