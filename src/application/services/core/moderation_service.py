#!/usr/bin/env python3
"""
🚀 Moderation Service (Refactored)
الخدمة الرئيسية المبسطة باستخدام المكونات المنفصلة

تحسينات مطبقة:
✅ فصل المسؤوليات
✅ Parameter Objects
✅ State Machine
✅ Lookup Tables
✅ Memory Management
✅ Clean Architecture
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Union

from .moderation import ContentCategory, ModerationSeverity
from .moderation_helpers import (
    ModerationRequest,
    ModerationContext,
    ModerationStateMachine,
    ModerationEvent,
    ConditionalDecomposer,
)
from .moderation_api_clients import create_api_clients
from .moderation_local_checkers import create_local_checkers
from .moderation_cache_manager import create_cache_manager
from .moderation_result_processor import create_result_processor
from src.infrastructure.config import get_config


class ModerationServiceRefactored:
    """🚀 خدمة الفلترة المحسنة"""
    
    def __init__(self, config=None):
        """تهيئة الخدمة مع جميع المكونات"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components using factory functions
        self.api_clients = create_api_clients(self.config)
        self.local_checkers = create_local_checkers(self.config)
        self.cache_manager = create_cache_manager()
        self.result_processor = create_result_processor()
        
        self.logger.info("Moderation service initialized with separated components")
    
    async def check_content(
        self,
        request: Union[str, ModerationRequest],
        context: Optional[ModerationContext] = None,
    ) -> Dict[str, Any]:
        """
        🔍 فحص المحتوى الرئيسي - محسن ومبسط
        
        استخدام جميع التحسينات:
        - Parameter Objects
        - State Machine
        - Lookup Tables
        - Decomposed Conditionals
        """
        
        # 📦 Convert to Parameter Object
        if isinstance(request, str):
            mod_request = ModerationRequest(content=request)
        else:
            mod_request = request
        
        if context is None:
            context = ModerationContext()
        
        # ✅ Early validation using Decomposed Conditionals
        if ConditionalDecomposer.is_content_empty_or_invalid(mod_request.content):
            return self.result_processor.create_safe_response("Empty or invalid content")
        
        if ConditionalDecomposer.is_content_too_long(mod_request.content):
            return self.result_processor.create_unsafe_response(
                "Content too long", 
                [ContentCategory.AGE_INAPPROPRIATE]
            )
        
        # 🔄 Use State Machine for flow control
        state_machine = ModerationStateMachine()
        state_machine.transition(ModerationEvent.START)
        
        # 📦 Check cache first
        if context.use_cache:
            cached_result = self.cache_manager.get(
                mod_request.content, 
                mod_request.age, 
                mod_request.language
            )
            if cached_result:
                return cached_result
        
        # 🏠 Local check first (fast path)
        local_result = await self.local_checkers.check_whitelist_blacklist(mod_request)
        
        # Short-circuit if local check finds unsafe content
        if not local_result.is_safe:
            response = self.result_processor.format_response(local_result, mod_request)
            self._cache_result(mod_request, response)
            return response
        
        # 🤖 AI check if needed and available
        if self._should_use_ai_check(mod_request, local_result, context):
            ai_result = await self.api_clients.check_with_openai(mod_request)
            
            if not ai_result.is_safe:
                response = self.result_processor.format_response(ai_result, mod_request)
                self._cache_result(mod_request, response)
                return response
        
        # ✅ Content is safe
        safe_response = self.result_processor.create_safe_response("Passed all checks")
        self._cache_result(mod_request, safe_response)
        return safe_response
    
    async def check_content_comprehensive(
        self,
        request: Union[str, ModerationRequest],
        context: Optional[ModerationContext] = None,
    ) -> Dict[str, Any]:
        """
        🔍 فحص شامل مع جميع الخدمات
        
        للاستخدام عند الحاجة لفحص دقيق جداً
        """
        
        # تحويل لـ Parameter Object
        if isinstance(request, str):
            mod_request = ModerationRequest(content=request)
        else:
            mod_request = request
        
        if context is None:
            context = ModerationContext()
        
        # تجميع النتائج من جميع المصادر
        results = []
        
        # 1. الفحص المحلي
        local_result = await self.local_checkers.check_whitelist_blacklist(mod_request)
        results.append(local_result)
        
        # 2. فحص APIs الخارجية (parallel)
        api_tasks = []
        
        if context.enable_openai and self.api_clients.openai_client:
            api_tasks.append(self.api_clients.check_with_openai(mod_request))
        
        if context.enable_azure and self.api_clients.azure_client:
            api_tasks.append(self.api_clients.check_with_azure(mod_request))
        
        if context.enable_google and self.api_clients.google_client:
            api_tasks.append(self.api_clients.check_with_google(mod_request))
        
        # تشغيل فحوصات APIs بالتوازي
        if api_tasks:
            api_results = await asyncio.gather(*api_tasks, return_exceptions=True)
            
            # إضافة النتائج الصالحة فقط
            for result in api_results:
                if not isinstance(result, Exception):
                    results.append(result)
        
        # 3. تجميع جميع النتائج
        final_result = self.result_processor.aggregate_results(results)
        
        # 4. تنسيق الاستجابة النهائية
        response = self.result_processor.format_response(final_result, mod_request)
        
        # 5. حفظ في cache
        if context.use_cache:
            self._cache_result(mod_request, response)
        
        return response
    
    # ================== LEGACY COMPATIBILITY ==================
    
    async def check_content_legacy(
        self,
        content: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        age: int = 10,
        language: str = "en",
        context=None,
    ) -> Dict[str, Any]:
        """🔄 دعم الواجهة القديمة"""
        request = ModerationRequest(
            content=content,
            user_id=user_id,
            session_id=session_id,
            age=age,
            language=language,
            context=context
        )
        
        return await self.check_content(request)
    
    # ================== HELPER METHODS ==================
    
    def _should_use_ai_check(
        self, 
        request: ModerationRequest, 
        local_result, 
        context: ModerationContext
    ) -> bool:
        """🤖 هل نحتاج فحص AI؟"""
        return ConditionalDecomposer.should_use_ai_check(
            len(request.content),
            local_result.is_safe,
            context.enable_openai and self.api_clients.openai_client is not None
        )
    
    def _cache_result(self, request: ModerationRequest, response: Dict[str, Any]) -> None:
        """💾 حفظ في cache"""
        try:
            self.cache_manager.set(
                request.content, 
                request.age, 
                request.language, 
                response
            )
        except Exception as e:
            self.logger.error(f"Cache error: {e}")
    
    # ================== MANAGEMENT METHODS ==================
    
    async def update_whitelist(self, words: list, action: str = "add") -> bool:
        """📝 تحديث whitelist"""
        return await self.local_checkers.update_whitelist(words, action)
    
    async def update_blacklist(self, words: list, action: str = "add") -> bool:
        """📝 تحديث blacklist"""
        return await self.local_checkers.update_blacklist(words, action)
    
    def get_service_status(self) -> Dict[str, Any]:
        """📊 حالة الخدمة"""
        return {
            "api_clients": self.api_clients.get_client_status(),
            "local_checkers": self.local_checkers.get_status(),
            "cache": self.cache_manager.get_stats(),
            "service_ready": True,
        }
    
    def clear_cache(self) -> None:
        """🗑️ مسح cache"""
        self.cache_manager.clear()


# ================== FACTORY FUNCTIONS ==================

def create_moderation_service(config=None) -> ModerationServiceRefactored:
    """🏭 Factory function لإنشاء الخدمة المحسنة"""
    return ModerationServiceRefactored(config)


def create_moderation_request(
    content: str,
    user_id: Optional[str] = None,
    age: int = 10,
    language: str = "en"
) -> ModerationRequest:
    """📦 Helper function لإنشاء Parameter Object"""
    return ModerationRequest(
        content=content,
        user_id=user_id,
        age=age,
        language=language
    )
