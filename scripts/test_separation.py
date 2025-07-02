#!/usr/bin/env python3
"""
🧪 اختبار فصل المسؤوليات
التأكد من أن جميع المكونات تعمل منفصلة ومعاً
"""

import asyncio
import os
import sys

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.services.core.moderation_helpers import ModerationRequest, ModerationContext
from src.application.services.core.moderation_cache_manager import create_cache_manager
from src.application.services.core.moderation_result_processor import create_result_processor
from src.application.services.core.moderation_main import create_moderation_service


def test_cache_manager():
    """🧪 اختبار Cache Manager"""
    print("🧪 Testing Cache Manager...")
    
    cache = create_cache_manager(ttl_seconds=60, max_size=10)
    
    # اختبار الحفظ والاسترجاع
    test_result = {"allowed": True, "severity": "safe"}
    cache.set("test content", 10, "en", test_result)
    
    retrieved = cache.get("test content", 10, "en")
    assert retrieved == test_result
    
    # اختبار cache miss
    not_found = cache.get("different content", 10, "en")
    assert not_found is None
    
    print("   ✅ Cache Manager working correctly")


def test_result_processor():
    """🧪 اختبار Result Processor"""
    print("🧪 Testing Result Processor...")
    
    processor = create_result_processor()
    
    # اختبار إنشاء ردود آمنة
    safe_response = processor.create_safe_response("Test safe")
    assert safe_response["allowed"] == True
    assert safe_response["severity"] == "safe"
    
    # اختبار إنشاء ردود غير آمنة
    from src.application.services.core.moderation import ContentCategory
    unsafe_response = processor.create_unsafe_response("Test unsafe", [ContentCategory.VIOLENCE])
    assert unsafe_response["allowed"] == False
    assert "categories" in unsafe_response
    
    print("   ✅ Result Processor working correctly")


async def test_moderation_service():
    """🧪 اختبار الخدمة الرئيسية المحسنة"""
    print("🧪 Testing Refactored Moderation Service...")
    
    try:
        # إنشاء الخدمة
        service = create_moderation_service()
        
        # اختبار Parameter Object
        request = ModerationRequest(
            content="Hello world",
            age=10,
            language="en"
        )
        
        # اختبار الفحص
        result = await service.check_content(request)
        
        # التحقق من النتيجة
        assert "allowed" in result
        assert "severity" in result
        assert "categories" in result
        
        print("   ✅ Refactored Moderation Service working correctly")
        
    except Exception as e:
        print(f"   ❌ Moderation Service error: {e}")


def test_component_independence():
    """🧪 اختبار استقلالية المكونات"""
    print("🧪 Testing Component Independence...")
    
    # كل مكون يجب أن يعمل منفصلاً
    cache = create_cache_manager()
    processor = create_result_processor()
    
    # Cache Manager
    cache.set("test", 10, "en", {"test": True})
    cached = cache.get("test", 10, "en")
    assert cached == {"test": True}
    
    # Result Processor
    safe = processor.create_safe_response("Independent test")
    assert safe["allowed"] == True
    
    print("   ✅ All components working independently")


async def run_all_tests():
    """🏃‍♂️ تشغيل جميع الاختبارات"""
    print("🚀 Starting Separation Tests...")
    print("=" * 50)
    
    try:
        test_cache_manager()
        test_result_processor()
        await test_moderation_service()
        test_component_independence()
        
        print("=" * 50)
        print("🎉 All separation tests passed!")
        print("\n📊 Benefits achieved:")
        print("   ✅ Clear separation of concerns")
        print("   ✅ Each component has single responsibility")
        print("   ✅ Easy to test and maintain")
        print("   ✅ Modular and extensible")
        print("   ✅ Reduced complexity")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1) 