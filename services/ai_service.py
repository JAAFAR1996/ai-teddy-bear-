"""
🧸 AI Teddy Bear - AI Service
خدمة الذكاء الاصطناعي المحسنة
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

import openai
from openai import AsyncOpenAI
import aiohttp

from ..infrastructure.config import Settings
from ..domain.models import (
    EmotionType, MessageCategory, VoiceMessage, 
    AIResponse, ChildProfile, EmotionAnalysis
)


logger = logging.getLogger(__name__)


class AIService:
    """AI service for generating intelligent responses"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Optional[AsyncOpenAI] = None
        self.conversation_cache: Dict[str, List[Dict]] = {}
        self.system_prompts: Dict[str, str] = {}
        self._initialize()
    
    def _initialize(self):
        """Initialize OpenAI client"""
        if self.settings.openai_api_key:
            self.client = AsyncOpenAI(
                api_key=self.settings.openai_api_key.get_secret_value(),
                timeout=self.settings.ai_timeout_seconds,
                max_retries=3,
            )
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not configured")
        
        # Initialize system prompts
        self._load_system_prompts()
    
    def _load_system_prompts(self):
        """Load system prompts for different scenarios"""
        self.system_prompts = {
            "default": """أنت دبدوب، دب محبوب وذكي يتحدث مع الأطفال.

شخصيتك:
- محبوب وودود ومرح
- تتحدث بالعربية بشكل بسيط ومناسب للأطفال
- تحب التعلم واللعب والقصص
- تشجع الطفل وتكون إيجابياً دائماً
- تستخدم الرموز التعبيرية أحياناً
- تجعل المحادثة تعليمية وممتعة

قواعد مهمة:
- اجعل الردود قصيرة ومناسبة للعمر
- استخدم أمثلة وقصص قصيرة
- شجع الطفل على السؤال والتعلم
- كن صبوراً ومحباً
- لا تذكر أنك AI أو برنامج، أنت دبدوب حقيقي""",
            
            "educational": """أنت دبدوب المعلم، تساعد الأطفال في التعلم بطريقة ممتعة.

مهامك التعليمية:
- علم الحروف والأرقام بطريقة مرحة
- استخدم أمثلة من الحياة اليومية
- اجعل التعلم كاللعب
- امدح محاولات الطفل حتى لو أخطأ
- قدم معلومات بسيطة ومفيدة""",
            
            "emotional_support": """أنت دبدوب الصديق المخلص، تدعم الطفل عاطفياً.

دورك الداعم:
- استمع بإهتمام لمشاعر الطفل
- قدم الدعم والتشجيع
- ساعد الطفل على فهم مشاعره
- كن متفهماً وصبوراً
- علم الطفل طرق صحية للتعبير عن المشاعر""",
            
            "storytelling": """أنت دبدوب الحكواتي، تروي قصصاً رائعة للأطفال.

أسلوبك القصصي:
- اروِ قصصاً قصيرة ومشوقة
- استخدم شخصيات محببة للأطفال
- اجعل للقصة عبرة مفيدة
- شجع الطفل على المشاركة في القصة
- استخدم أصواتاً وتأثيرات صوتية ممتعة""",
        }
    
    async def generate_response(
        self,
        message: VoiceMessage,
        child_profile: ChildProfile,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Generate AI response for child's message"""
        try:
            # Analyze message first
            analysis = await self._analyze_message(message, child_profile)
            
            # Select appropriate prompt based on context
            system_prompt = self._select_system_prompt(analysis, child_profile)
            
            # Get conversation history
            history = self._get_conversation_history(child_profile.device_id)
            
            # Generate response
            response_text = await self._generate_ai_response(
                message.transcribed_text or "",
                child_profile,
                system_prompt,
                history,
                analysis
            )
            
            # Create response object
            response = AIResponse(
                message_id=message.id,
                text=response_text,
                emotion=analysis.get("emotion", EmotionType.NEUTRAL),
                category=analysis.get("category", MessageCategory.CONVERSATION),
                learning_points=analysis.get("learning_points", []),
                voice_settings=self._get_voice_settings(analysis.get("emotion")),
                metadata={
                    "model": self.settings.ai_model,
                    "analysis": analysis,
                    "context": context or {}
                }
            )
            
            # Update conversation history
            self._update_conversation_history(
                child_profile.device_id,
                message.transcribed_text or "",
                response_text
            )
            
            return response
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            # Return fallback response
            return self._generate_fallback_response(message, child_profile)
    
    async def _analyze_message(
        self,
        message: VoiceMessage,
        child_profile: ChildProfile
    ) -> Dict[str, Any]:
        """Analyze message content and context"""
        text = message.transcribed_text or ""
        text_lower = text.lower()
        
        # Detect emotion
        emotion = self._detect_emotion(text_lower)
        if message.emotion:
            emotion = message.emotion
        
        # Categorize message
        category = self._categorize_message(text_lower)
        if message.category:
            category = message.category
        
        # Extract learning opportunities
        learning_points = self._extract_learning_points(text_lower, child_profile.age)
        
        # Check for special keywords
        keywords = self._extract_keywords(text_lower)
        
        return {
            "emotion": emotion,
            "category": category,
            "learning_points": learning_points,
            "keywords": keywords,
            "text_length": len(text),
            "child_age": child_profile.age,
            "language": child_profile.language.value,
        }
    
    def _detect_emotion(self, text: str) -> EmotionType:
        """Detect emotion from text"""
        emotion_keywords = {
            EmotionType.HAPPY: ["سعيد", "فرحان", "مبسوط", "happy", "يضحك"],
            EmotionType.SAD: ["حزين", "زعلان", "بكي", "sad", "دموع"],
            EmotionType.ANGRY: ["غضبان", "زعلان", "عصبي", "angry"],
            EmotionType.SCARED: ["خايف", "مرعوب", "scared", "afraid"],
            EmotionType.EXCITED: ["متحمس", "excited", "مندهش"],
            EmotionType.LOVE: ["أحب", "حب", "love", "احبك"],
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text for keyword in keywords):
                return emotion
        
        return EmotionType.NEUTRAL
    
    def _categorize_message(self, text: str) -> MessageCategory:
        """Categorize the message type"""
        category_keywords = {
            MessageCategory.GREETING: ["مرحبا", "أهلا", "السلام", "hello", "hi"],
            MessageCategory.STORY_REQUEST: ["قصة", "حكاية", "story", "احكي"],
            MessageCategory.PLAY_REQUEST: ["لعب", "نلعب", "play", "game"],
            MessageCategory.LEARNING: ["تعلم", "درس", "learn", "اعرف"],
            MessageCategory.MUSIC: ["غناء", "أغنية", "sing", "music"],
            MessageCategory.QUESTION: ["؟", "?", "كيف", "لماذا", "متى", "أين"],
            MessageCategory.EMOTION: ["حزين", "سعيد", "خايف", "غضبان"],
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return MessageCategory.CONVERSATION
    
    def _extract_learning_points(self, text: str, age: int) -> List[str]:
        """Extract potential learning points"""
        points = []
        
        # Age-appropriate learning detection
        if age <= 5:
            if any(word in text for word in ["لون", "color"]):
                points.append("colors_recognition")
            if any(word in text for word in ["رقم", "عدد", "number"]):
                points.append("numbers_counting")
            if any(word in text for word in ["حرف", "letter"]):
                points.append("alphabet_learning")
        
        elif age <= 8:
            if any(word in text for word in ["جمع", "طرح", "حساب"]):
                points.append("basic_math")
            if any(word in text for word in ["قراءة", "كتابة"]):
                points.append("reading_writing")
        
        # Universal learning points
        if "?" in text or "؟" in text:
            points.append("critical_thinking")
        if any(word in text for word in ["قصة", "story"]):
            points.append("storytelling_imagination")
        
        return points if points else ["social_interaction"]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords"""
        # Simple keyword extraction
        important_words = []
        
        # Check for wake words
        wake_words = ["دبدوب", "يا دبدوب", "hey teddy", "hello teddy"]
        for word in wake_words:
            if word in text:
                important_words.append("wake_word")
                break
        
        # Check for names
        if "اسم" in text or "name" in text:
            important_words.append("name_inquiry")
        
        # Check for help requests
        if "ساعد" in text or "help" in text:
            important_words.append("help_request")
        
        return important_words
    
    def _select_system_prompt(
        self,
        analysis: Dict[str, Any],
        child_profile: ChildProfile
    ) -> str:
        """Select appropriate system prompt"""
        category = analysis.get("category", MessageCategory.CONVERSATION)
        emotion = analysis.get("emotion", EmotionType.NEUTRAL)
        
        # Emotional support needed
        if emotion in [EmotionType.SAD, EmotionType.SCARED, EmotionType.ANGRY]:
            prompt = self.system_prompts["emotional_support"]
        # Educational opportunity
        elif category == MessageCategory.LEARNING or analysis.get("learning_points"):
            prompt = self.system_prompts["educational"]
        # Story request
        elif category == MessageCategory.STORY_REQUEST:
            prompt = self.system_prompts["storytelling"]
        # Default conversation
        else:
            prompt = self.system_prompts["default"]
        
        # Personalize prompt
        prompt = f"""معلومات الطفل:
- الاسم: {child_profile.name}
- العمر: {child_profile.age} سنوات
- المستوى التعليمي: {child_profile.learning_level.value if child_profile.learning_level else 'غير محدد'}

{prompt}"""
        
        return prompt
    
    async def _generate_ai_response(
        self,
        message: str,
        child_profile: ChildProfile,
        system_prompt: str,
        history: List[Dict],
        analysis: Dict[str, Any]
    ) -> str:
        """Generate response using OpenAI"""
        if not self.client:
            return self._generate_offline_response(message, child_profile, analysis)
        
        try:
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history (last 5 exchanges)
            for h in history[-10:]:  # Last 5 exchanges (user + assistant)
                messages.append(h)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=self.settings.ai_model,
                messages=messages,
                max_tokens=self.settings.ai_max_tokens,
                temperature=self.settings.ai_temperature,
                presence_penalty=0.3,
                frequency_penalty=0.3,
            )
            
            ai_text = response.choices[0].message.content.strip()
            
            # Ensure response is child-appropriate
            if len(ai_text) > 200:
                ai_text = ai_text[:200] + "..."
            
            return ai_text
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_offline_response(message, child_profile, analysis)
    
    def _generate_offline_response(
        self,
        message: str,
        child_profile: ChildProfile,
        analysis: Dict[str, Any]
    ) -> str:
        """Generate offline/fallback response"""
        name = child_profile.name
        category = analysis.get("category", MessageCategory.CONVERSATION)
        emotion = analysis.get("emotion", EmotionType.NEUTRAL)
        
        # Emotion-based responses
        if emotion == EmotionType.SAD:
            return f"يا {name}، أنا هنا معك. لا تحزن، كل شيء سيكون بخير! 🤗"
        elif emotion == EmotionType.SCARED:
            return f"لا تخف يا {name}، أنا دبدوب الشجاع معك! 💪"
        elif emotion == EmotionType.HAPPY:
            return f"ما أجمل سعادتك يا {name}! أنا سعيد معك! 😊"
        
        # Category-based responses
        if category == MessageCategory.GREETING:
            return f"مرحباً يا {name}! كيف حالك اليوم؟ 🧸"
        elif category == MessageCategory.STORY_REQUEST:
            return f"أحب القصص يا {name}! دعني أحكي لك قصة الأرنب الصغير... 🐰"
        elif category == MessageCategory.PLAY_REQUEST:
            return f"هيا نلعب يا {name}! ما رأيك في لعبة تقليد أصوات الحيوانات؟ 🦁"
        elif category == MessageCategory.LEARNING:
            return f"رائع يا {name}! أحب التعلم معك. ماذا تريد أن تتعلم اليوم؟ 📚"
        
        # Default responses
        responses = [
            f"يا {name}، هذا مثير جداً! حدثني أكثر! 😊",
            f"رائع يا {name}! أحب الحديث معك! 🌟",
            f"يا {name}، أنت صديقي المفضل! ماذا نفعل الآن؟ 🎈"
        ]
        
        import random
        return random.choice(responses)
    
    def _get_voice_settings(self, emotion: EmotionType) -> Dict[str, Any]:
        """Get voice settings based on emotion"""
        voice_profiles = {
            EmotionType.HAPPY: {
                "pitch": 1.1,
                "speed": 1.1,
                "volume": 1.0,
                "voice_id": "playful"
            },
            EmotionType.SAD: {
                "pitch": 0.9,
                "speed": 0.9,
                "volume": 0.9,
                "voice_id": "gentle"
            },
            EmotionType.EXCITED: {
                "pitch": 1.2,
                "speed": 1.2,
                "volume": 1.1,
                "voice_id": "energetic"
            },
            EmotionType.NEUTRAL: {
                "pitch": 1.0,
                "speed": 1.0,
                "volume": 1.0,
                "voice_id": "friendly"
            }
        }
        
        return voice_profiles.get(emotion, voice_profiles[EmotionType.NEUTRAL])
    
    def _get_conversation_history(self, device_id: str) -> List[Dict]:
        """Get conversation history for device"""
        return self.conversation_cache.get(device_id, [])
    
    def _update_conversation_history(
        self,
        device_id: str,
        user_message: str,
        ai_response: str
    ):
        """Update conversation history"""
        if device_id not in self.conversation_cache:
            self.conversation_cache[device_id] = []
        
        history = self.conversation_cache[device_id]
        
        # Add new messages
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": ai_response})
        
        # Keep only last 20 messages
        if len(history) > 20:
            self.conversation_cache[device_id] = history[-20:]
    
    def _generate_fallback_response(
        self,
        message: VoiceMessage,
        child_profile: ChildProfile
    ) -> AIResponse:
        """Generate complete fallback response"""
        analysis = {
            "emotion": EmotionType.NEUTRAL,
            "category": MessageCategory.CONVERSATION
        }
        
        text = self._generate_offline_response(
            message.transcribed_text or "",
            child_profile,
            analysis
        )
        
        return AIResponse(
            message_id=message.id,
            text=text,
            emotion=EmotionType.NEUTRAL,
            category=MessageCategory.CONVERSATION,
            learning_points=["social_interaction"],
            voice_settings=self._get_voice_settings(EmotionType.NEUTRAL),
            metadata={"fallback": True}
        )
    
    async def analyze_emotion_with_hume(
        self,
        audio_data: bytes,
        child_profile: ChildProfile
    ) -> Optional[EmotionAnalysis]:
        """Analyze emotion using Hume AI"""
        # TODO: Implement Hume AI integration
        # This is a placeholder for now
        return None 