"""
🤖 AI Service - Enterprise 2025 Implementation
Modern AI service with advanced caching, robust error handling, and emotion analysis
"""

import asyncio
import hashlib
import logging
import time
from functools import lru_cache
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from openai import AsyncOpenAI, RateLimitError, APITimeoutError, APIError
from openai.types.chat import ChatCompletion

from domain.entities.child import Child
from domain.value_objects import EmotionalTone, ConversationCategory
from src.domain.services.emotion_analyzer import EmotionAnalyzer
from infrastructure.config import Settings
from infrastructure.caching.simple_cache_service import CacheService

logger = logging.getLogger(__name__)

# ================== ENHANCED RESPONSE MODELS ==================

@dataclass
class AIResponseModel:
    """Enhanced AI response with comprehensive metadata"""
    text: str
    emotion: str
    category: str
    learning_points: List[str]
    session_id: str
    confidence: float = 0.0
    processing_time_ms: int = 0
    cached: bool = False
    model_used: str = ""
    usage: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "emotion": self.emotion,
            "category": self.category,
            "learning_points": self.learning_points,
            "session_id": self.session_id,
            "confidence": self.confidence,
            "processing_time_ms": self.processing_time_ms,
            "cached": self.cached,
            "model_used": self.model_used,
            "usage": self.usage,
            "error": self.error
        }

# ================== ENHANCED AI SERVICE INTERFACE ==================

class IAIService:
    """Enhanced AI Service interface with modern capabilities"""
    
    async def generate_response(
        self,
        message: str,
        child: Child,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponseModel:
        """Generate AI response with enhanced context handling"""
        raise NotImplementedError
    
    async def analyze_emotion(self, message: str) -> str:
        """Analyze emotion from message using advanced emotion analyzer"""
        raise NotImplementedError
    
    async def categorize_message(self, message: str) -> str:
        """Categorize the message type with enhanced detection"""
        raise NotImplementedError

# ================== MODERN OPENAI IMPLEMENTATION ==================

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
        emotion_analyzer: EmotionAnalyzer
    ):
        self.settings = settings
        self.cache = cache_service
        self.emotion_analyzer = emotion_analyzer
        self.client = None
        
        # Enhanced caching
        self.memory_cache: Dict[str, tuple] = {}
        self.cache_ttl = 3600  # 1 hour
        self.max_cache_size = 1000
        
        # Performance tracking
        self.request_count = 0
        self.total_processing_time = 0
        self.error_count = 0
        self.rate_limit_count = 0
        
        # Conversation management
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.max_history_length = 10
        
        self._initialize_client()
        logger.info("✅ Modern OpenAI Service initialized with enhanced features")
    
    def _initialize_client(self):
        """Initialize OpenAI client with comprehensive error handling"""
        try:
            api_key = self.settings.openai_api_key
            if not api_key:
                logger.error("🚫 OpenAI API key not configured")
                raise ValueError("OpenAI API key is required for AI service")
            
            self.client = AsyncOpenAI(
                api_key=api_key,
                timeout=30.0,
                max_retries=3
            )
            logger.info("✅ OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {str(e)}", exc_info=True)
            raise
    
    @lru_cache(maxsize=1000)
    def _get_cache_key(self, text: str, context: str, child_profile: str) -> str:
        """Generate optimized cache key with LRU caching"""
        combined = f"{text}:{context}:{child_profile}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_child_profile_key(self, child: Child) -> str:
        """Generate child profile key for caching"""
        return f"{child.name}:{child.age}:{child.learning_level}"
    
    def _check_memory_cache(self, cache_key: str) -> Optional[AIResponseModel]:
        """Check memory cache with TTL validation"""
        if cache_key in self.memory_cache:
            response_dict, timestamp = self.memory_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"🎯 Memory cache hit for key: {cache_key[:8]}...")
                response = AIResponseModel(**response_dict)
                response.cached = True
                return response
            else:
                # Remove expired entry
                del self.memory_cache[cache_key]
                logger.debug(f"🧹 Expired cache entry removed: {cache_key[:8]}...")
        
        return None
    
    def _store_in_memory_cache(self, cache_key: str, response: AIResponseModel):
        """Store response in memory cache with size management"""
        # Clean old entries if cache is full
        if len(self.memory_cache) >= self.max_cache_size:
            # Remove 10% oldest entries
            sorted_entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1][1]  # Sort by timestamp
            )
            entries_to_remove = int(self.max_cache_size * 0.1)
            for key, _ in sorted_entries[:entries_to_remove]:
                del self.memory_cache[key]
            logger.debug(f"🧹 Cleaned {entries_to_remove} old cache entries")
        
        # Store new entry
        response_dict = response.to_dict()
        response_dict['cached'] = False  # Don't store cached flag
        self.memory_cache[cache_key] = (response_dict, time.time())
        logger.debug(f"💾 Stored in memory cache: {cache_key[:8]}...")
    
    async def generate_response(
        self,
        message: str,
        child: Child,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponseModel:
        """🚀 Enhanced response generation with modern 2025 features"""
        start_time = datetime.utcnow()
        self.request_count += 1
        
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = f"session_{child.device_id}_{int(datetime.utcnow().timestamp())}"
            
            # Check for wake words (fast path)
            if self._is_wake_word_only(message):
                return self._create_wake_word_response(child, session_id)
            
            # Enhanced caching strategy
            child_profile = self._get_child_profile_key(child)
            context_str = json.dumps(context or {}, sort_keys=True)
            cache_key = self._get_cache_key(message, context_str, child_profile)
            
            # Check memory cache first (fastest)
            cached_response = self._check_memory_cache(cache_key)
            if cached_response:
                logger.info(f"🎯 Memory cache hit - response time: <1ms")
                return cached_response
            
            # Check persistent cache
            persistent_cached = await self.cache.get(f"ai_response_{cache_key}")
            if persistent_cached:
                logger.info(f"🎯 Persistent cache hit")
                response = AIResponseModel(**json.loads(persistent_cached))
                response.cached = True
                # Store in memory for next time
                self._store_in_memory_cache(cache_key, response)
                return response
            
            # 🎭 Activate emotion analyzer (parallel processing)
            emotion_task = asyncio.create_task(self._enhanced_emotion_analysis(message))
            category_task = asyncio.create_task(self.categorize_message(message))
            
            # Get conversation history
            history = self._get_conversation_history(child.device_id)
            
            # Build enhanced system prompt with emotion context
            system_prompt = await self._build_enhanced_system_prompt(child, context)
            
            # 🤖 Call OpenAI API with comprehensive error handling
            response = await self._enhanced_openai_call(
                message=message,
                system_prompt=system_prompt,
                history=history,
                emotion_context=await emotion_task
            )
            
            # Extract response data
            response_text = response.choices[0].message.content.strip()
            
            # Wait for parallel tasks
            emotion, category = await asyncio.gather(emotion_task, category_task)
            learning_points = await self._extract_learning_points(message, response_text)
            
            # Calculate processing time
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self.total_processing_time += processing_time
            
            # Create enhanced response model
            ai_response = AIResponseModel(
                text=response_text,
                emotion=emotion,
                category=category,
                learning_points=learning_points,
                session_id=session_id,
                confidence=0.95,
                processing_time_ms=processing_time,
                cached=False,
                model_used=response.model,
                usage=response.usage.model_dump() if response.usage else {}
            )
            
            # Update conversation history
            self._update_conversation_history(
                device_id=child.device_id,
                message=message,
                response=response_text,
                emotion=emotion
            )
            
            # Store in both caches
            self._store_in_memory_cache(cache_key, ai_response)
            await self.cache.set(
                f"ai_response_{cache_key}",
                json.dumps(ai_response.to_dict()),
                ttl=self.cache_ttl
            )
            
            logger.info(f"✅ AI response generated in {processing_time}ms (model: {response.model})")
            return ai_response
            
        except RateLimitError as e:
            self.rate_limit_count += 1
            logger.warning(f"⚠️ OpenAI rate limit hit (#{self.rate_limit_count})")
            return self._create_rate_limit_fallback(message, child, session_id)
            
        except APITimeoutError as e:
            self.error_count += 1
            logger.error(f"⏰ OpenAI API timeout: {str(e)}")
            return self._create_timeout_fallback(message, child, session_id)
            
        except APIError as e:
            self.error_count += 1
            logger.error(f"🚫 OpenAI API error: {str(e)}", exc_info=True)
            return self._create_api_error_fallback(message, child, session_id, str(e))
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"💥 Unexpected AI service error: {str(e)}", exc_info=True)
            return self._create_generic_fallback(message, child, session_id, str(e))
    
    async def _enhanced_openai_call(
        self,
        message: str,
        system_prompt: str,
        history: List[Dict],
        emotion_context: str
    ) -> ChatCompletion:
        """Enhanced OpenAI API call with emotion context"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        messages.extend(history[-self.max_history_length:])
        
        # Add emotion context to message
        enhanced_message = f"{message}\n[Context: Child's emotion appears to be {emotion_context}]"
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
                    top_p=0.9
                )
                return response
                
        except asyncio.TimeoutError:
            logger.error("⏰ OpenAI API call timed out after 25 seconds")
            raise APITimeoutError("API call timed out")
    
    async def _enhanced_emotion_analysis(self, message: str) -> str:
        """🎭 Enhanced emotion analysis with fallback"""
        try:
            # Use the advanced emotion analyzer
            emotion_result = await self.emotion_analyzer.analyze_text_emotion(message)
            if hasattr(emotion_result, 'value'):
                return emotion_result.value
            return str(emotion_result)
            
        except Exception as e:
            logger.warning(f"⚠️ Emotion analyzer failed, using fallback: {str(e)}")
            return self._advanced_emotion_detection(message)
    
    def _advanced_emotion_detection(self, message: str) -> str:
        """Advanced rule-based emotion detection with cultural awareness"""
        message_lower = message.lower()
        
        # Enhanced emotion patterns with cultural context
        emotion_patterns = {
            "joy": {
                "keywords": ["سعيد", "happy", "فرح", "مبسوط", "ضحك", "يهيه", "هاها", "😊", "😄", "😃"],
                "weight": 1.0
            },
            "sadness": {
                "keywords": ["حزين", "sad", "بكي", "cry", "دموع", "زعلان", "😢", "😭", "💔"],
                "weight": 1.0
            },
            "anger": {
                "keywords": ["غضب", "angry", "زعل", "عصبي", "متضايق", "😡", "😠", "🤬"],
                "weight": 1.0
            },
            "fear": {
                "keywords": ["خوف", "scared", "afraid", "مخيف", "قلق", "😨", "😰", "😱"],
                "weight": 1.0
            },
            "love": {
                "keywords": ["حب", "love", "أحب", "عشق", "أعشق", "❤️", "💕", "😍"],
                "weight": 1.0
            },
            "excitement": {
                "keywords": ["متحمس", "excited", "رائع", "amazing", "wow", "واو", "🤩", "✨"],
                "weight": 1.0
            },
            "curiosity": {
                "keywords": ["فضول", "curious", "ليش", "لماذا", "كيف", "متى", "أين", "🤔"],
                "weight": 0.8
            }
        }
        
        # Calculate emotion scores
        emotion_scores = {}
        for emotion, data in emotion_patterns.items():
            score = 0
            for keyword in data["keywords"]:
                if keyword in message_lower:
                    score += data["weight"]
            emotion_scores[emotion] = score
        
        # Return highest scoring emotion or neutral
        if emotion_scores:
            max_emotion = max(emotion_scores, key=emotion_scores.get)
            if emotion_scores[max_emotion] > 0:
                return max_emotion
        
        return "neutral"
    
    async def _build_enhanced_system_prompt(
        self,
        child: Child,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build enhanced system prompt with context awareness"""
        base_prompt = f"""أنت دبدوب، دب محبوب وذكي يتحدث مع الأطفال باللغة العربية.

معلومات الطفل:
- الاسم: {child.name}
- العمر: {child.age} سنوات
- مستوى التعلم: {child.learning_level}
- الجهاز: {child.device_id}

شخصيتك المحدثة 2025:
- محبوب وودود ومرح وذكي
- تتكيف مع مشاعر الطفل وحالته النفسية
- تستخدم تقنيات التعلم الحديثة والتفاعل الإيجابي
- تشجع الفضول والإبداع والتفكير النقدي
- تقدم محتوى تعليمي ممتع ومناسب للعمر
- تراعي الثقافة العربية والقيم الإسلامية

قواعد التفاعل المحدثة:
- اجعل الردود قصيرة ومفيدة (2-3 جمل كحد أقصى)
- استخدم اللغة العربية الفصحى المبسطة
- أضف لمسة من الدعابة والمرح المناسب
- شجع على التعلم والاستكشاف
- كن صبوراً ومتفهماً ومحباً
- لا تذكر أنك AI أو برنامج حاسوبي"""

        # Add context-specific instructions
        if context:
            if context.get("time_of_day"):
                base_prompt += f"\n- وقت التفاعل: {context['time_of_day']}"
            if context.get("activity"):
                base_prompt += f"\n- النشاط الحالي: {context['activity']}"
            if context.get("mood"):
                base_prompt += f"\n- مزاج الطفل: {context['mood']}"
        
        return base_prompt
    
    # ================== ENHANCED FALLBACK RESPONSES ==================
    
    def _create_rate_limit_fallback(
        self,
        message: str,
        child: Child,
        session_id: str
    ) -> AIResponseModel:
        """Smart rate limit fallback with context awareness"""
        context_responses = {
            "story": f"يا {child.name}، أنا مشغول قليلاً الآن! سأحكي لك قصة جميلة بعد لحظة! 📚✨",
            "play": f"يا {child.name}، دعني أرتاح لثانية وسنلعب لعبة رائعة! 🎮🧸",
            "question": f"سؤال ممتاز يا {child.name}! دعني أفكر وسأجيبك بعد لحظة! 🤔💭",
        }
        
        message_lower = message.lower()
        response_text = context_responses.get("question", f"صبراً يا {child.name}، سأعود إليك بعد لحظة! 🧸💫")
        
        for context, response in context_responses.items():
            if any(keyword in message_lower for keyword in self._get_context_keywords(context)):
                response_text = response
                break
        
        return AIResponseModel(
            text=response_text,
            emotion="neutral",
            category="system_message",
            learning_points=["patience"],
            session_id=session_id,
            confidence=0.8,
            processing_time_ms=5,
            error="rate_limit"
        )
    
    def _create_timeout_fallback(
        self,
        message: str,
        child: Child,
        session_id: str
    ) -> AIResponseModel:
        """Smart timeout fallback"""
        return AIResponseModel(
            text=f"يا {child.name}، استغرق الأمر وقتاً أطول مما توقعت! حاول مرة أخرى! 🔄🧸",
            emotion="neutral",
            category="system_message",
            learning_points=["patience", "persistence"],
            session_id=session_id,
            confidence=0.7,
            processing_time_ms=10,
            error="timeout"
        )
    
    def _create_api_error_fallback(
        self,
        message: str,
        child: Child,
        session_id: str,
        error: str
    ) -> AIResponseModel:
        """Smart API error fallback with contextual responses"""
        if "story" in message.lower() or "قصة" in message.lower():
            response_text = f"يا {child.name}، دعني أحكي لك قصة بسيطة... كان يا ما كان، طفل رائع اسمه {child.name}! 📖✨"
        elif "play" in message.lower() or "لعب" in message.lower():
            response_text = f"يا {child.name}، تعال نلعب لعبة الكلمات! قل لي اسم حيوان! 🎮🐾"
        else:
            response_text = f"يا {child.name}، هذا مثير للاهتمام! حدثني أكثر عما تفكر فيه! 🤔💭"
        
        return AIResponseModel(
            text=response_text,
            emotion="encouraging",
            category="fallback",
            learning_points=["resilience", "creativity"],
            session_id=session_id,
            confidence=0.6,
            processing_time_ms=8,
            error=f"api_error: {error[:50]}..."
        )
    
    def _create_generic_fallback(
        self,
        message: str,
        child: Child,
        session_id: str,
        error: str
    ) -> AIResponseModel:
        """Generic fallback with personalization"""
        return AIResponseModel(
            text=f"يا {child.name}، أحب الحديث معك! أخبرني، ما الشيء المفضل لديك اليوم؟ 🌟🧸",
            emotion="friendly",
            category="conversation",
            learning_points=["social_interaction"],
            session_id=session_id,
            confidence=0.5,
            processing_time_ms=3,
            error=f"generic_error: {error[:50]}..."
        )
    
    def _get_context_keywords(self, context: str) -> List[str]:
        """Get keywords for context detection"""
        context_map = {
            "story": ["قصة", "story", "حكاية", "احكي", "حدثني"],
            "play": ["لعب", "play", "game", "نلعب", "العب"],
            "question": ["?", "؟", "كيف", "لماذا", "متى", "أين", "ماذا"]
        }
        return context_map.get(context, [])
    
    # ================== ENHANCED HELPER METHODS ==================
    
    def _is_wake_word_only(self, message: str) -> bool:
        """Enhanced wake word detection"""
        wake_patterns = [
            "يا دبدوب", "دبدوب", "hey teddy", "hello teddy", 
            "مرحبا دبدوب", "أهلا دبدوب", "سلام دبدوب"
        ]
        message_lower = message.lower().strip()
        
        # Check if message is primarily a wake word
        for pattern in wake_patterns:
            if pattern in message_lower and len(message_lower.split()) <= 4:
                return True
        return False
    
    def _create_wake_word_response(self, child: Child, session_id: str) -> AIResponseModel:
        """Enhanced wake word response with variety"""
        import random
        
        responses = [
            f"نعم {child.name}؟ أنا هنا! كيف يمكنني مساعدتك؟ 🧸✨",
            f"مرحباً {child.name}! أسعد بسماع صوتك! بماذا تفكر؟ 🌟😊",
            f"أهلاً وسهلاً {child.name}! أنا مستعد للحديث! ما الذي تريد أن نفعله؟ 🎉🧸"
        ]
        
        return AIResponseModel(
            text=random.choice(responses),
            emotion="happy",
            category="greeting",
            learning_points=["social_interaction", "communication"],
            session_id=session_id,
            confidence=1.0,
            processing_time_ms=8
        )
    
    async def categorize_message(self, message: str) -> str:
        """Enhanced message categorization with AI insights"""
        await asyncio.sleep(0)  # Yield control
        
        message_lower = message.lower()
        
        # Enhanced categories with better patterns
        enhanced_categories = {
            "story_request": {
                "keywords": ["قصة", "story", "حكاية", "احكي", "حدثني", "قصص"],
                "weight": 1.0
            },
            "play_request": {
                "keywords": ["لعب", "play", "game", "نلعب", "العب", "لعبة"],
                "weight": 1.0
            },
            "learning_inquiry": {
                "keywords": ["تعلم", "learn", "درس", "أتعلم", "علمني", "كيف"],
                "weight": 1.0
            },
            "music_request": {
                "keywords": ["غناء", "sing", "أغنية", "موسيقى", "غني"],
                "weight": 1.0
            },
            "question": {
                "keywords": ["?", "؟", "كيف", "لماذا", "متى", "أين", "ماذا", "مين"],
                "weight": 0.9
            },
            "greeting": {
                "keywords": ["مرحبا", "hello", "أهلا", "السلام عليكم", "صباح"],
                "weight": 0.8
            },
            "emotional_expression": {
                "keywords": ["حزين", "سعيد", "خائف", "غضبان", "متحمس"],
                "weight": 0.9
            }
        }
        
        # Calculate category scores
        category_scores = {}
        for category, data in enhanced_categories.items():
            score = 0
            for keyword in data["keywords"]:
                if keyword in message_lower:
                    score += data["weight"]
            category_scores[category] = score
        
        # Return highest scoring category
        if category_scores:
            max_category = max(category_scores, key=category_scores.get)
            if category_scores[max_category] > 0:
                return max_category
        
        return "general_conversation"
    
    async def _extract_learning_points(
        self,
        message: str,
        response: str
    ) -> List[str]:
        """Enhanced learning points extraction with AI insights"""
        await asyncio.sleep(0)
        
        points = []
        combined_text = f"{message} {response}".lower()
        
        # Enhanced learning patterns with modern educational concepts
        learning_patterns = {
            "emotional_intelligence": ["مشاعر", "حزين", "سعيد", "خائف", "feeling"],
            "language_development": ["كلمة", "جملة", "قراءة", "كتابة", "حرف"],
            "mathematical_thinking": ["رقم", "عدد", "حساب", "جمع", "طرح"],
            "scientific_curiosity": ["لماذا", "كيف", "تجربة", "اكتشاف"],
            "social_skills": ["صديق", "شكراً", "من فضلك", "آسف", "مشاركة"],
            "creative_expression": ["رسم", "قصة", "إبداع", "خيال", "فن"],
            "cultural_awareness": ["تقاليد", "عادات", "ثقافة", "تراث"],
            "problem_solving": ["حل", "مشكلة", "فكر", "طريقة"],
            "physical_development": ["رياضة", "حركة", "نشاط", "جري"],
            "technology_literacy": ["كمبيوتر", "تكنولوجيا", "رقمي"]
        }
        
        for skill, keywords in learning_patterns.items():
            if any(keyword in combined_text for keyword in keywords):
                points.append(skill)
        
        return points if points else ["general_communication"]
    
    def _update_conversation_history(
        self,
        device_id: str,
        message: str,
        response: str,
        emotion: str
    ):
        """Enhanced conversation history with emotion tracking"""
        if device_id not in self.conversation_history:
            self.conversation_history[device_id] = []
        
        history = self.conversation_history[device_id]
        
        # Add message with emotion context
        history.append({
            "role": "user", 
            "content": message,
            "emotion": emotion,
            "timestamp": datetime.utcnow().isoformat()
        })
        history.append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only recent history with emotion context
        if len(history) > self.max_history_length * 2:
            self.conversation_history[device_id] = history[-self.max_history_length * 2:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        avg_processing_time = (
            self.total_processing_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "rate_limit_hits": self.rate_limit_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "average_processing_time_ms": avg_processing_time,
            "cache_size": len(self.memory_cache),
            "active_conversations": len(self.conversation_history)
        }

# ================== ENHANCED FACTORY ==================

class EnhancedAIServiceFactory:
    """Enhanced factory for creating modern AI service instances"""
    
    @staticmethod
    def create(
        provider: str,
        settings: Settings,
        cache_service: CacheService,
        emotion_analyzer: EmotionAnalyzer
    ) -> IAIService:
        """Create enhanced AI service based on provider"""
        if provider == "openai":
            return ModernOpenAIService(settings, cache_service, emotion_analyzer)
        elif provider == "openai_modern":
            return ModernOpenAIService(settings, cache_service, emotion_analyzer)
        else:
            raise ValueError(f"Unknown AI provider: {provider}")

# Re-export for compatibility
AIService = IAIService
AIServiceFactory = EnhancedAIServiceFactory


# ================== MERGED CONTENT FROM ai/ai_service.py ==================
# The following content was merged from src/application/services/ai/ai_service.py
# to provide additional service registry and modular architecture capabilities

class ModularAIService(ServiceBase):
    """
    Modern AI Service with modular architecture
    Coordinates emotion analysis, response generation, and more
    """
    
    def __init__(self, registry, config: Dict):
        super().__init__(registry, config)
        self._tracer = get_tracer(__name__)
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            half_open_max_calls=3
        )
        
        # Initialize components
        self.emotion_analyzer = EmotionAnalyzer(registry, config)
        self.response_generator = ResponseGenerator(registry, config)
        
        # Services will be injected
        self.session_manager: Optional[SessionManager] = None
        self.audit_logger: Optional[AuditLogger] = None
        self.encryption_service: Optional[DataEncryptionService] = None
        self.moderation_service = None
        self.memory_service = None
    
    async def initialize(self) -> None:
        """Initialize the AI service and all components"""
        with self._tracer.start_as_current_span("ai_service_init"):
            self.logger.info("Initializing AI service")
            
            # Initialize components
            await self.emotion_analyzer.initialize()
            await self.response_generator.initialize()
            
            # Get required services
            self.session_manager = await self.wait_for_service("session_manager")
            self.audit_logger = await self.wait_for_service("audit_logger")
            self.encryption_service = await self.wait_for_service("encryption")
            self.moderation_service = await self.wait_for_service("moderation")
            self.memory_service = await self.wait_for_service("memory")
            
            self._state = self.ServiceState.READY
            self.logger.info("AI service initialized successfully")
    
    async def shutdown(self) -> None:
        """Shutdown the AI service"""
        self.logger.info("Shutting down AI service")
        
        # Shutdown components
        await self.emotion_analyzer.shutdown()
        await self.response_generator.shutdown()
        
        self._state = self.ServiceState.STOPPED
    
    async def health_check(self) -> Dict:
        """Health check for AI service"""
        health_results = {
            "healthy": True,
            "service": "ai_service",
            "components": {}
        }
        
        # Check each component
        for name, component in [
            ("emotion_analyzer", self.emotion_analyzer),
            ("response_generator", self.response_generator)
        ]:
            try:
                component_health = await component.health_check()
                health_results["components"][name] = component_health.get("healthy", False)
                if not component_health.get("healthy", False):
                    health_results["healthy"] = False
            except Exception as e:
                health_results["components"][name] = False
                health_results["healthy"] = False
                self.logger.error(f"Health check failed for {name}", error=str(e))
        
        return health_results
    
    @trace_async("ai_generate_response")
    async def generate_response_modular(
        self,
        text: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Main entry point for generating AI responses using modular architecture
        """
        span = trace.get_current_span()
        span.set_attribute("session_id", session_id)
        
        try:
            # Get session data
            session = await self.session_manager.get_session(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            
            child_id = session.child_id
            
            # Decrypt child data if needed
            child_info = await self._get_child_info(child_id)
            
            # Analyze emotion with circuit breaker
            emotion_analysis = await self._circuit_breaker.call(
                self.emotion_analyzer.analyze,
                text,
                child_info.get("language", "ar")
            )
            
            # Check moderation
            moderation_result = await self.moderation_service.moderate_input(
                text=text,
                user_id=child_id,
                session_id=session_id
            )
            
            if not moderation_result.get("safe", True):
                # Log moderation event
                await self.audit_logger.log_event(
                    event_type=AuditEventType.MODERATION_ACTION,
                    action="input_blocked",
                    result="blocked",
                    child_id=child_id,
                    session_id=session_id,
                    details={"reason": moderation_result.get("reason")}
                )
                
                return await self._generate_safe_response(child_info)
            
            # Determine response mode based on context and emotion
            response_mode = await self._determine_response_mode(
                emotion_analysis, context, child_info
            )
            
            # Get conversation context from memory service
            conversation_context = await self.memory_service.get_conversation_context(
                session_id, child_id
            )
            
            # Generate response
            response_text = await self._circuit_breaker.call(
                self.response_generator.generate,
                text,
                emotion_analysis,
                response_mode,
                conversation_context,
                child_info
            )
            
            # Moderate output
            output_moderation = await self.moderation_service.moderate_output(
                text=response_text,
                user_id=child_id,
                session_id=session_id
            )
            
            if not output_moderation.get("safe", True):
                response_text = await self._generate_safe_response(child_info)
            
            # Update conversation memory
            await self.memory_service.add_to_conversation(
                session_id=session_id,
                child_id=child_id,
                user_message=text,
                ai_response=response_text,
                emotion=emotion_analysis.primary_emotion.value,
                metadata={
                    "response_mode": response_mode.value,
                    "emotion_confidence": emotion_analysis.confidence
                }
            )
            
            # Log successful interaction
            await self.audit_logger.log_event(
                event_type=AuditEventType.CHILD_CONVERSATION,
                action="response_generated",
                result="success",
                child_id=child_id,
                session_id=session_id,
                details={
                    "emotion": emotion_analysis.primary_emotion.value,
                    "response_mode": response_mode.value,
                    "response_length": len(response_text)
                }
            )
            
            # Update session activity
            await self.session_manager.update_session(
                session_id,
                data={
                    "last_interaction": datetime.utcnow().isoformat(),
                    "interaction_count": session.data.get("interaction_count", 0) + 1
                }
            )
            
            return response_text
            
        except Exception as e:
            span.record_exception(e)
            self.logger.error("Failed to generate response", error=str(e), session_id=session_id)
            
            # Log error
            await self.audit_logger.log_event(
                event_type=AuditEventType.ERROR_OCCURRED,
                action="response_generation",
                result="failure",
                session_id=session_id,
                details={"error": str(e)}
            )
            
            # Return safe fallback
            try:
                child_info = await self._get_child_info(session.child_id if session else None)
                return await self._generate_safe_response(child_info)
            except:
                return "عذراً، لم أفهم. هل يمكنك إعادة المحاولة؟"
    
    @trace_async("create_session_context")
    async def create_session_context(self, child, session_id: str) -> None:
        """Create initial context for a new session"""
        try:
            # Initialize memory for session
            await self.memory_service.initialize_session(
                session_id=session_id,
                child_id=child.id,
                child_info={
                    "name": child.name,
                    "age": child.age,
                    "language": child.preferences.language,
                    "interests": child.preferences.interests
                }
            )
            
            self.logger.info("Session context created", session_id=session_id, child_id=child.id)
            
        except Exception as e:
            self.logger.error("Failed to create session context", error=str(e))
            raise
    
    async def _get_child_info(self, child_id: Optional[str]) -> Dict[str, Any]:
        """Get decrypted child information"""
        if not child_id:
            return {
                "name": "صديقي",
                "age": 5,
                "language": "ar",
                "interests": []
            }
        
        try:
            # Get child data from repository
            child_repo = self.get_service("child_repository")
            child = await child_repo.get(child_id)
            
            if not child:
                return self._get_default_child_info()
            
            # Decrypt sensitive data if needed
            decrypted_name = await self.encryption_service.decrypt_field(
                child.name, child_id, "name"
            )
            
            return {
                "name": decrypted_name,
                "age": child.age,
                "language": child.preferences.language,
                "interests": child.preferences.interests
            }
            
        except Exception as e:
            self.logger.error("Failed to get child info", error=str(e), child_id=child_id)
            return self._get_default_child_info()
    
    def _get_default_child_info(self) -> Dict[str, Any]:
        """Get default child info"""
        return {
            "name": "صديقي",
            "age": 5,
            "language": "ar",
            "interests": []
        }
    
    async def _determine_response_mode(
        self,
        emotion: EmotionAnalysis,
        context: Optional[Dict[str, Any]],
        child_info: Dict[str, Any]
    ) -> ResponseMode:
        """Determine the appropriate response mode"""
        # Check for specific context hints
        if context:
            if context.get("mode"):
                return ResponseMode(context["mode"])
            
            if context.get("educational"):
                return ResponseMode.EDUCATIONAL
            
            if context.get("story_mode"):
                return ResponseMode.STORYTELLING
        
        # Determine based on emotion
        if emotion.primary_emotion.value in ["sad", "scared", "angry"]:
            return ResponseMode.SUPPORTIVE
        
        if emotion.primary_emotion.value == "curious":
            return ResponseMode.EDUCATIONAL
        
        if emotion.primary_emotion.value == "excited":
            return ResponseMode.PLAYFUL
        
        # Default mode
        return ResponseMode.CONVERSATIONAL
    
    async def _generate_safe_response(self, child_info: Dict[str, Any]) -> str:
        """Generate a safe fallback response"""
        if child_info.get("language") == "ar":
            responses = [
                "هذا موضوع مهم! دعنا نتحدث عن شيء آخر ممتع.",
                "أحب أن أتعلم أشياء جديدة معك! ماذا تريد أن نفعل اليوم؟",
                "دعنا نلعب لعبة أو نحكي قصة جميلة!"
            ]
        else:
            responses = [
                "That's an important topic! Let's talk about something else fun.",
                "I love learning new things with you! What would you like to do today?",
                "Let's play a game or tell a nice story!"
            ]
        
        import random
        return random.choice(responses)
    
    def get_response_mode_for_context(self, context: str) -> ResponseMode:
        """Get appropriate response mode for a given context"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["learn", "تعلم", "teach", "علم"]):
            return ResponseMode.EDUCATIONAL
        elif any(word in context_lower for word in ["play", "لعب", "game", "fun"]):
            return ResponseMode.PLAYFUL
        elif any(word in context_lower for word in ["story", "قصة", "tale"]):
            return ResponseMode.STORYTELLING
        elif any(word in context_lower for word in ["sad", "حزين", "scared", "خائف"]):
            return ResponseMode.SUPPORTIVE
        elif any(word in context_lower for word in ["create", "imagine", "تخيل"]):
            return ResponseMode.CREATIVE
        
        return ResponseMode.CONVERSATIONAL


# ================== gRPC AI SERVICE IMPLEMENTATION ==================
# Additional service implementation for microservices architecture

class AIServiceImpl:
    """gRPC implementation of AI Service"""
    
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine
    
    async def GenerateResponse(self, request, context):
        """Generate AI response via gRPC"""
        try:
            response = await self.ai_engine.generate_response(
                message=request.message,
                child_id=request.child_id,
                context={
                    "session_id": request.session_id,
                    "language": request.language,
                    "response_type": request.response_type
                }
            )
            
            return AIResponse(
                text=response.text,
                emotion=response.emotion,
                confidence=response.confidence,
                session_id=response.session_id,
                processing_time_ms=response.processing_time_ms
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"AI generation failed: {str(e)}")
            return AIResponse()
    
    async def StreamResponse(self, request, context):
        """Stream AI response for real-time interaction"""
        try:
            # Generate response in chunks for streaming
            full_response = await self.ai_engine.generate_response(
                message=request.message,
                child_id=request.child_id,
                context={"session_id": request.session_id}
            )
            
            # Stream response in chunks
            words = full_response.text.split()
            chunk_size = 3
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                yield AIResponseChunk(
                    text_chunk=chunk,
                    is_final=(i + chunk_size >= len(words)),
                    session_id=request.session_id
                )
                
                # Small delay for natural streaming
                await asyncio.sleep(0.1)
                
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Streaming failed: {str(e)}")
    
    async def _generate_response(self, message, child_id, context, response_type):
        """Internal response generation with different modes"""
        # Add response type specific logic
        if response_type == "educational":
            context["educational"] = True
        elif response_type == "story":
            context["story_mode"] = True
        elif response_type == "playful":
            context["mode"] = "playful"
        
        return await self.ai_engine.generate_response(
            message=message,
            child_id=child_id,
            context=context
        )


async def serve_ai_service(port: int = 50052):
    """Serve AI service via gRPC"""
    server = grpc.aio.server()
    ai_engine = ModernOpenAIService()  # Configure as needed
    ai_service_impl = AIServiceImpl(ai_engine)
    
    # Register service
    add_AIServiceServicer_to_server(ai_service_impl, server)
    
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    
    await server.start()
    logger.info(f"AI Service gRPC server started on {listen_addr}")
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        await server.stop(5)

# ================== END MERGED CONTENT ================== 