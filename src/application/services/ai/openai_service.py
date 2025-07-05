"""
🤖 OpenAI Service - Enterprise 2025 Implementation
Modern OpenAI integration with advanced features and error handling
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError
from openai.types.chat import ChatCompletion
import secrets

from src.application.services.ai.analyzers.emotion_analyzer_service import (
    EmotionAnalyzerService,
)
from src.application.services.ai.fallback_response_service import (
    FallbackResponseService,
)
from src.application.services.ai.core import IAIService
from src.application.services.ai.managers.cache_manager import CacheManager
from src.application.services.ai.managers.error_handler import ErrorHandler
from src.application.services.ai.managers.prompt_builder import PromptBuilder
from src.application.services.ai.managers.response_processor import (
    ResponseProcessor,
    ResponseModelData,
)
from src.application.services.ai.models.ai_response_models import AIResponseModel
from src.core.domain.entities.child import Child
from src.infrastructure.caching.simple_cache_service import CacheService
from src.infrastructure.config import Settings

logger = logging.getLogger(__name__)


class ModernOpenAIService(IAIService):
    """
    🚀 Modern OpenAI implementation with 2025 enterprise features:
    - Advanced caching with LRU + TTL
    - Comprehensive error handling
    - Active emotion analysis
    - Performance monitoring
    - Circuit breaker pattern
    """

    def __init__(
        self,
        settings: Settings,
        cache_service: CacheService,
        emotion_analyzer: EmotionAnalyzerService,
        fallback_service: FallbackResponseService,
    ):
        self._initialize_services(
            settings, cache_service, emotion_analyzer, fallback_service
        )
        self._initialize_performance_tracking()
        self._initialize_client()
        logger.info(
            "✅ Modern OpenAI Service initialized with enhanced features")

    def _initialize_services(
        self, settings, cache_service, emotion_analyzer, fallback_service
    ):
        """Initializes service dependencies."""
        self.settings = settings
        self.emotion_analyzer = emotion_analyzer
        self.fallback_service = fallback_service
        self.cache_manager = CacheManager(cache_service)
        self.response_processor = ResponseProcessor(self.cache_manager)
        self.error_handler = ErrorHandler(fallback_service)
        self.prompt_builder = PromptBuilder()
        self.client = None
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.max_history_length = 10

    def _initialize_performance_tracking(self):
        """Initializes performance tracking metrics."""
        self.request_count = 0
        self.total_processing_time = 0

    def _initialize_client(self) -> None:
        """Initialize OpenAI client with comprehensive error handling"""
        try:
            api_key = self.settings.openai_api_key
            if not api_key:
                logger.error("🚫 OpenAI API key not configured")
                raise ValueError("OpenAI API key is required for AI service")

            self.client = AsyncOpenAI(
                api_key=api_key, timeout=30.0, max_retries=3)
            logger.info("✅ OpenAI client initialized successfully")

        except Exception as e:
            logger.error(
                f"❌ Failed to initialize OpenAI client: {str(e)}",
                exc_info=True)
            raise

    async def generate_response(
        self,
        message: str,
        child: Child,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AIResponseModel:
        """🚀 Enhanced response generation with modern 2025 features"""
        start_time = datetime.utcnow()
        self.request_count += 1

        try:
            # Prepare request context and check cache
            session_id, cache_key, cached_response = (
                await self._prepare_request_context(message, child, session_id, context)
            )

            if cached_response:
                return cached_response

            # Process with OpenAI and create response
            return await self._process_with_openai(
                message, child, session_id, context, cache_key, start_time
            )

        except (RateLimitError, APITimeoutError, APIError, Exception) as e:
            return await self.error_handler.handle_api_errors(e, message, child, session_id)

    async def _prepare_request_context(
        self,
        message: str,
        child: Child,
        session_id: Optional[str],
        context: Optional[Dict[str, Any]],
    ) -> tuple[str, str, Optional[AIResponseModel]]:
        """Prepare request context and check for cached responses"""
        # Generate session ID if not provided
        if not session_id:
            device_id = getattr(child, "device_id", "unknown")
            session_id = f"session_{device_id}_{int(datetime.utcnow().timestamp())}"

        # Check for wake words (fast path)
        if self._is_wake_word_only(message):
            wake_response = await self._create_wake_word_response(child, session_id)
            return session_id, "", wake_response

        # Enhanced caching strategy
        child_profile = self.cache_manager.get_child_profile_key(child)
        context_str = json.dumps(context or {}, sort_keys=True)
        cache_key = self.cache_manager.get_cache_key(
            message, context_str, child_profile)

        cached_response = await self.cache_manager.get_cached_response(cache_key)
        if cached_response:
            return session_id, cache_key, cached_response

        return session_id, cache_key, None

    async def _process_with_openai(
        self,
        message: str,
        child: Child,
        session_id: str,
        context: Optional[Dict[str, Any]],
        cache_key: str,
        start_time: datetime,
    ) -> AIResponseModel:
        """Process message with OpenAI API and create response"""
        # Start parallel tasks
        emotion_task = asyncio.create_task(
            self._enhanced_emotion_analysis(message))
        category_task = asyncio.create_task(self.categorize_message(message))

        # Get conversation history and build system prompt
        device_id = getattr(child, "device_id", "unknown")
        history = self._get_conversation_history(device_id)
        system_prompt = await self.prompt_builder.build_enhanced_system_prompt(
            child, context
        )

        # Call OpenAI API
        response = await self._enhanced_openai_call(
            message=message,
            system_prompt=system_prompt,
            history=history,
            emotion_context=await emotion_task,
        )

        model_data = ResponseModelData(
            response=response,
            message=message,
            emotion_task=emotion_task,
            category_task=category_task,
            session_id=session_id,
            device_id=device_id,
            cache_key=cache_key,
            start_time=start_time,
            conversation_history=history,
            max_history_length=self.max_history_length,
        )

        # Create and cache response
        return await self.response_processor.create_response_model(model_data)

    async def _enhanced_openai_call(
        self,
        message: str,
        system_prompt: str,
        history: List[Dict],
        emotion_context: str,
    ) -> ChatCompletion:
        """Enhanced OpenAI API call with emotion context"""
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        messages.extend(history[-self.max_history_length:])

        # Add emotion context to message
        enhanced_message = (
            f"{message}\n[Context: Child's emotion appears to be {emotion_context}]"
        )
        messages.append({"role": "user", "content": enhanced_message})

        try:
            async with asyncio.timeout(25):
                response = await self.client.chat.completions.create(
                    model=self.settings.openai_model or "gpt-4-turbo-preview",
                    messages=messages,
                    max_tokens=200,
                    temperature=0.7,  # Slightly more deterministic
                    presence_penalty=0.3,
                    frequency_penalty=0.3,
                    top_p=0.9,
                )
                return response

        except asyncio.TimeoutError:
            logger.error("⏰ OpenAI API call timed out after 25 seconds")
            raise APITimeoutError("API call timed out")

    async def _enhanced_emotion_analysis(self, message: str) -> str:
        """🎭 Enhanced emotion analysis with fallback"""
        try:
            emotion_result = await self.emotion_analyzer.analyze_text_emotion(message)
            return emotion_result.primary_emotion

        except Exception as e:
            logger.warning(
                f"⚠️ Emotion analyzer failed, using fallback: {str(e)}")
            return self._basic_emotion_detection(message)

    def _basic_emotion_detection(self, message: str) -> str:
        """Basic rule-based emotion detection"""
        message_lower = message.lower()
        emotion_map = {
            "joy": ["سعيد", "happy", "فرح", "مبسوط"],
            "sadness": ["حزين", "sad", "بكي", "زعلان"],
            "anger": ["غضب", "angry", "زعل", "عصبي"],
            "fear": ["خوف", "scared", "afraid", "خائف"],
            "love": ["حب", "love", "أحب"],
            "excitement": ["متحمس", "excited", "رائع", "واو"],
        }

        for emotion, keywords in emotion_map.items():
            if any(word in message_lower for word in keywords):
                return emotion

        return "neutral"

    async def analyze_emotion(self, message: str) -> str:
        """Analyze emotion from message"""
        return await self._enhanced_emotion_analysis(message)

    async def categorize_message(self, message: str) -> str:
        """Enhanced message categorization"""
        message_lower = message.lower()
        category_map = {
            "story_request": ["قصة", "story", "حكاية", "احكي"],
            "play_request": ["لعب", "play", "game", "نلعب"],
            "learning_inquiry": ["تعلم", "learn", "درس", "علمني"],
            "music_request": ["غناء", "sing", "أغنية", "غني"],
            "question": ["?", "؟", "كيف", "لماذا", "متى"],
            "greeting": ["مرحبا", "hello", "أهلا", "السلام"],
        }

        for category, keywords in category_map.items():
            if any(word in message_lower for word in keywords):
                return category

        return "general_conversation"

    def _is_wake_word_only(self, message: str) -> bool:
        """Enhanced wake word detection"""
        wake_patterns = [
            "يا دبدوب",
            "دبدوب",
            "hey teddy",
            "hello teddy",
            "مرحبا دبدوب",
            "أهلا دبدوب",
            "سلام دبدوب",
        ]
        message_lower = message.lower().strip()

        # Check if message is primarily a wake word
        for pattern in wake_patterns:
            if pattern in message_lower and len(message_lower.split()) <= 4:
                return True
        return False

    async def _create_wake_word_response(
        self, child: Child, session_id: str
    ) -> AIResponseModel:
        """Enhanced wake word response with variety"""
        responses = [
            f"نعم {child.name}؟ أنا هنا! كيف يمكنني مساعدتك؟ 🧸✨",
            f"مرحباً {child.name}! أسعد بسماع صوتك! بماذا تفكر؟ 🌟😊",
            f"أهلاً وسهلاً {child.name}! أنا مستعد للحديث! ما الذي تريد أن نفعله؟ 🎉🧸",
        ]

        return AIResponseModel(
            text=secrets.choice(responses),  # nosec
            emotion="happy",
            category="greeting",
            learning_points=["social_interaction", "communication"],
            session_id=session_id,
            confidence=1.0,
            processing_time_ms=8,
        )

    def _get_conversation_history(self, device_id: str) -> List[Dict]:
        """Get conversation history for device"""
        if device_id not in self.conversation_history:
            self.conversation_history[device_id] = []
        return self.conversation_history.get(device_id, [])

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        avg_processing_time = (
            self.total_processing_time / self.request_count
            if self.request_count > 0
            else 0
        )

        error_count = self.error_handler.error_count
        rate_limit_count = self.error_handler.rate_limit_count

        return {
            "total_requests": self.request_count,
            "total_errors": error_count,
            "rate_limit_hits": rate_limit_count,
            "error_rate": (
                error_count /
                self.request_count if self.request_count > 0 else 0),
            "average_processing_time_ms": avg_processing_time,
            "cache_size": len(
                self.cache_manager.memory_cache),
            "active_conversations": len(
                self.conversation_history),
        }
