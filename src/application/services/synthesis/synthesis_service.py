#!/usr/bin/env python3
"""
🔊 Modern Synthesis Service - Refactored for High Cohesion
خدمة تركيب الصوت الحديثة - مُعاد هيكلتها باستخدام نمط Facade
"""

import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional

from src.domain.value_objects import EmotionalTone

from .models import (
    SynthesisConfig,
    SynthesisServiceCredentials,
    SynthesisContext,
    VoiceProvider
)
from .audio_buffer import StreamingAudioBuffer
from .character_manager import VoiceCharacterManager
from .audio_processor import AudioProcessor
from .performance_monitor import PerformanceMonitor
from .providers import (
    ElevenLabsProvider,
    OpenAIProvider,
    AzureProvider,
    FallbackProvider
)

logger = logging.getLogger(__name__)


class ModernSynthesisService:
    """
    🔊 Modern Synthesis Service - Facade Pattern
    
    تم تطبيق EXTRACT CLASS refactoring لتحسين التماسك:
    - StreamingAudioBuffer: إدارة مخزن الصوت
    - VoiceCharacterManager: إدارة شخصيات الصوت
    - AudioProcessor: معالجة الصوت
    - PerformanceMonitor: مراقبة الأداء
    - Providers: موفري خدمات التركيب المختلفة
    """

    def __init__(self, config: Optional[SynthesisConfig] = None):
        """تهيئة الخدمة مع جميع المكونات المنفصلة"""
        self.config = config or SynthesisConfig()
        
        # تهيئة المكونات المتخصصة (High Cohesion)
        self.audio_buffer = StreamingAudioBuffer(self.config)
        self.character_manager = VoiceCharacterManager(self.config)
        self.audio_processor = AudioProcessor(self.config)
        self.performance_monitor = PerformanceMonitor()
        
        # تهيئة موفري الخدمات
        self.providers = {
            VoiceProvider.ELEVENLABS: ElevenLabsProvider(),
            VoiceProvider.OPENAI: OpenAIProvider(),
            VoiceProvider.AZURE: AzureProvider(),
            VoiceProvider.SYSTEM: FallbackProvider()
        }
        
        logger.info("✅ Modern Synthesis Service initialized")

    async def initialize(
        self,
        credentials: Optional[SynthesisServiceCredentials] = None
    ) -> None:
        """تهيئة جميع موفري الخدمات والمكونات"""
        try:
            if credentials is None:
                credentials = SynthesisServiceCredentials()

            # تهيئة موفري الخدمات
            await self._initialize_providers(credentials)
            
            # تحميل شخصيات الصوت الافتراضية
            await self.character_manager.load_default_characters()
            
            # تسجيل الموفرين المتاحين
            available_providers = [
                provider.value for provider in credentials.get_available_providers()
            ]
            logger.info(f"🚀 Synthesis service initialized with providers: {available_providers}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize synthesis service: {e}")
            raise

    async def _initialize_providers(self, credentials: SynthesisServiceCredentials) -> None:
        """تهيئة جميع موفري الخدمات"""
        credentials_dict = {
            "elevenlabs_api_key": credentials.elevenlabs_api_key,
            "openai_api_key": credentials.openai_api_key,
            "azure_speech_key": credentials.azure_speech_key,
            "azure_speech_region": credentials.azure_speech_region
        }
        
        # تهيئة كل موفر خدمة
        for provider_type, provider in self.providers.items():
            try:
                success = await provider.initialize(credentials_dict)
                if success:
                    logger.info(f"✅ {provider.get_provider_name()} provider initialized")
                else:
                    logger.warning(f"⚠️ {provider.get_provider_name()} provider not available")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {provider.get_provider_name()}: {e}")

    # === Main Synthesis Methods ===

    async def synthesize_stream(
        self,
        text: str,
        emotion: EmotionalTone = EmotionalTone.FRIENDLY,
        character_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """🌊 تركيب الصوت مع البث المباشر"""
        start_time = time.time()
        
        try:
            # إعداد سياق التركيب
            context = await self._prepare_synthesis_context(text, emotion, character_id, language)
            
            # تنفيذ التركيب المتدفق
            async for chunk in self._execute_streaming_synthesis(context):
                yield chunk
            
            # تحديث الإحصائيات
            self._update_performance_stats(context, start_time, success=True)
            
        except Exception as e:
            logger.error(f"❌ Stream synthesis failed: {e}")
            self._update_performance_stats(None, start_time, success=False)
            
            # استخدام التركيب الاحتياطي
            async for chunk in self._fallback_stream_synthesis(text):
                yield chunk

    async def synthesize_audio(
        self,
        text: str,
        emotion: EmotionalTone = EmotionalTone.FRIENDLY,
        character_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> Optional[bytes]:
        """🎯 تركيب الصوت الكامل"""
        start_time = time.time()
        
        try:
            # إعداد سياق التركيب
            context = await self._prepare_synthesis_context(text, emotion, character_id, language)
            
            # تنفيذ التركيب
            audio_data = await self._execute_audio_synthesis(context)
            
            # معالجة الصوت
            if audio_data:
                audio_data = await self.audio_processor.apply_voice_adjustments(
                    audio_data, context.character
                )
            
            # تحديث الإحصائيات
            self._update_performance_stats(context, start_time, success=True)
            
            logger.debug(f"🎯 Synthesized in {time.time() - start_time:.2f}s: '{text[:50]}...'")
            return audio_data
            
        except Exception as e:
            logger.error(f"❌ Audio synthesis failed: {e}")
            self._update_performance_stats(None, start_time, success=False)
            return await self._fallback_audio_synthesis(text)

    # === Internal Synthesis Methods ===

    async def _prepare_synthesis_context(
        self,
        text: str,
        emotion: EmotionalTone,
        character_id: Optional[str],
        language: Optional[str]
    ) -> SynthesisContext:
        """إعداد سياق التركيب"""
        character = await self.character_manager.select_character(character_id, language)
        voice_settings = character.emotional_settings.get(
            emotion, 
            character.emotional_settings[EmotionalTone.FRIENDLY]
        )
        
        return SynthesisContext(
            text=text,
            emotion=emotion,
            character=character,
            voice_settings=voice_settings
        )

    async def _execute_streaming_synthesis(self, context: SynthesisContext) -> AsyncIterator[bytes]:
        """تنفيذ التركيب المتدفق"""
        provider = self.providers.get(context.character.provider)
        if provider and provider.is_available():
            async for chunk in provider.synthesize_stream(context):
                yield chunk
        else:
            # استخدام موفر احتياطي
            fallback_provider = self.providers[VoiceProvider.SYSTEM]
            async for chunk in fallback_provider.synthesize_stream(context):
                yield chunk

    async def _execute_audio_synthesis(self, context: SynthesisContext) -> Optional[bytes]:
        """تنفيذ تركيب الصوت"""
        provider = self.providers.get(context.character.provider)
        if provider and provider.is_available():
            return await provider.synthesize_audio(context)
        else:
            # استخدام موفر احتياطي
            fallback_provider = self.providers[VoiceProvider.SYSTEM]
            return await fallback_provider.synthesize_audio(context)

    async def _fallback_stream_synthesis(self, text: str) -> AsyncIterator[bytes]:
        """التركيب الاحتياطي المتدفق"""
        fallback_provider = self.providers[VoiceProvider.SYSTEM]
        
        # إنشاء سياق احتياطي بسيط
        character = await self.character_manager.select_character(None, None)
        context = SynthesisContext(
            text=text,
            emotion=EmotionalTone.FRIENDLY,
            character=character,
            voice_settings=character.emotional_settings[EmotionalTone.FRIENDLY]
        )
        
        async for chunk in fallback_provider.synthesize_stream(context):
            yield chunk

    async def _fallback_audio_synthesis(self, text: str) -> Optional[bytes]:
        """التركيب الاحتياطي للصوت"""
        try:
            fallback_provider = self.providers[VoiceProvider.SYSTEM]
            
            # إنشاء سياق احتياطي بسيط
            character = await self.character_manager.select_character(None, None)
            context = SynthesisContext(
                text=text,
                emotion=EmotionalTone.FRIENDLY,
                character=character,
                voice_settings=character.emotional_settings[EmotionalTone.FRIENDLY]
            )
            
            return await fallback_provider.synthesize_audio(context)
            
        except Exception as e:
            logger.error(f"❌ Fallback synthesis also failed: {e}")
            return None

    # === Character and Configuration Management ===

    def set_character(self, character_id: str) -> bool:
        """تعيين شخصية الصوت الحالية"""
        return self.character_manager.set_current_character(character_id)

    def get_available_characters(self) -> List[Dict[str, Any]]:
        """الحصول على قائمة شخصيات الصوت المتاحة"""
        return self.character_manager.get_available_characters()

    # === Performance and Health Monitoring ===

    def get_performance_metrics(self) -> Dict[str, Any]:
        """الحصول على مقاييس الأداء"""
        return self.performance_monitor.get_performance_metrics()

    async def health_check(self) -> Dict[str, Any]:
        """فحص صحة الخدمة"""
        try:
            # فحص جميع موفري الخدمات
            provider_health = {}
            for provider_type, provider in self.providers.items():
                provider_health[provider_type.value] = await provider.health_check()
            
            # فحص المكونات الأخرى
            character_stats = self.character_manager.get_character_stats()
            
            return {
                "status": "healthy",
                "providers": provider_health,
                "characters": character_stats,
                "performance": self.performance_monitor.get_stats_summary(),
                "audio_buffer": await self.audio_buffer.get_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def _update_performance_stats(
        self, 
        context: Optional[SynthesisContext], 
        start_time: float, 
        success: bool
    ) -> None:
        """تحديث إحصائيات الأداء"""
        processing_time = time.time() - start_time
        provider = context.character.provider if context else VoiceProvider.SYSTEM
        
        self.performance_monitor.update_synthesis_stats(
            provider=provider,
            processing_time=processing_time,
            success=success
        ) 