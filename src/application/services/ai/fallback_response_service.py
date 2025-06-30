"""
🛡️ Fallback Response Service - Enterprise 2025 Implementation
Smart fallback responses for error handling and system resilience
"""

import random
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.application.services.ai.models.ai_response_models import AIResponseModel
from src.domain.entities.child import Child

logger = logging.getLogger(__name__)

class FallbackResponseService:
    """
    🛡️ Advanced fallback response service with:
    - Context-aware error responses
    - Smart recovery strategies
    - Cultural sensitivity
    - Learning opportunity creation
    """
    
    def __init__(self):
        self.fallback_responses = self._load_fallback_responses()
        self.usage_stats = {
            "rate_limit": 0,
            "timeout": 0,
            "api_error": 0,
            "generic_error": 0,
            "total_fallbacks": 0
        }
        
        logger.info("✅ Fallback Response Service initialized")
    
    def _load_fallback_responses(self) -> Dict[str, Dict[str, List[str]]]:
        """Load comprehensive fallback response templates"""
        return {
            "rate_limit": {
                "story": [
                    "يا {name}، أنا مشغول قليلاً الآن! سأحكي لك قصة جميلة بعد لحظة! 📚✨",
                    "دعني أجمع أفكاري يا {name} وسأعود بقصة رائعة! 🌟📖"
                ],
                "play": [
                    "يا {name}، دعني أرتاح لثانية وسنلعب لعبة رائعة! 🎮🧸",
                    "تعال نلعب بعد قليل يا {name}! سأحضر لعبة جديدة! 🎯⭐"
                ],
                "question": [
                    "سؤال ممتاز يا {name}! دعني أفكر وسأجيبك بعد لحظة! 🤔💭",
                    "أحب فضولك يا {name}! سأبحث عن إجابة رائعة! 🔍✨"
                ],
                "general": [
                    "صبراً يا {name}، سأعود إليك بعد لحظة! 🧸💫",
                    "أحتاج دقيقة واحدة يا {name}! 🕐🌟"
                ]
            },
            "timeout": {
                "encouraging": [
                    "يا {name}، استغرق الأمر وقتاً أطول مما توقعت! حاول مرة أخرى! 🔄🧸",
                    "أعتذر للتأخير يا {name}! دعنا نحاول مرة أخرى! 🔁💪"
                ],
                "playful": [
                    "يبدو أنني أبطأ من السلحفاة اليوم يا {name}! 🐢😅",
                    "عذراً يا {name}، كنت أحلم بالعسل! دعنا نعيد المحاولة! 🍯😴"
                ]
            },
            "api_error": {
                "story_context": [
                    "يا {name}، دعني أحكي لك قصة بسيطة... كان يا ما كان، طفل رائع اسمه {name}! 📖✨",
                    "هل تريد قصة يا {name}؟ أعرف قصة عن دب صغير شجاع مثلك! 🐻🌟"
                ],
                "play_context": [
                    "يا {name}، تعال نلعب لعبة الكلمات! قل لي اسم حيوان! 🐾🎮",
                    "هيا نلعب يا {name}! ما رأيك في لعبة التخمين؟ 🔮🎯"
                ],
                "educational": [
                    "يا {name}، هل تعرف أن الأفيال تستطيع السباحة؟ 🐘💧",
                    "معلومة مثيرة يا {name}: النجوم تغني أغاني جميلة في السماء! ⭐🎵"
                ],
                "general": [
                    "يا {name}، هذا مثير للاهتمام! حدثني أكثر عما تفكر فيه! 🤔💭",
                    "أحب الحديث معك يا {name}! ما الشيء الجميل الذي حدث معك اليوم؟ 🌟🗣️"
                ]
            },
            "generic_error": {
                "positive": [
                    "يا {name}، أحب الحديث معك! أخبرني، ما الشيء المفضل لديك اليوم؟ 🌟🧸",
                    "أنت مميز يا {name}! دعنا نتحدث عن شيء يجعلك سعيداً! 🌈😊"
                ],
                "curious": [
                    "يا {name}، عقلك مليء بالأفكار الرائعة! شاركني واحدة منها! 🧠✨",
                    "فضولك رائع يا {name}! ما الذي تود أن تعرفه اليوم؟ 🔍🌟"
                ]
            }
        }
    
    async def create_rate_limit_fallback(
        self,
        message: str,
        child: Child,
        session_id: str
    ) -> AIResponseModel:
        """🚦 Create smart rate limit fallback response"""
        self.usage_stats["rate_limit"] += 1
        self.usage_stats["total_fallbacks"] += 1
        
        context = self._detect_message_context(message.lower())
        responses = self.fallback_responses["rate_limit"].get(context, 
                    self.fallback_responses["rate_limit"]["general"])
        
        response_text = random.choice(responses).format(name=child.name)
        
        learning_points = ["patience", "understanding", "resilience"]
        if context == "question":
            learning_points.append("curiosity")
        elif context == "story":
            learning_points.append("imagination")
        elif context == "play":
            learning_points.append("creativity")
        
        return AIResponseModel(
            text=response_text,
            emotion="encouraging",
            category="system_message",
            learning_points=learning_points,
            session_id=session_id,
            confidence=0.8,
            processing_time_ms=5,
            error="rate_limit"
        )
    
    async def create_timeout_fallback(
        self,
        message: str,
        child: Child,
        session_id: str
    ) -> AIResponseModel:
        """⏰ Create smart timeout fallback response"""
        self.usage_stats["timeout"] += 1
        self.usage_stats["total_fallbacks"] += 1
        
        response_style = "playful" if child.age <= 5 else "encouraging"
        responses = self.fallback_responses["timeout"].get(response_style,
                    self.fallback_responses["timeout"]["encouraging"])
        
        response_text = random.choice(responses).format(name=child.name)
        
        return AIResponseModel(
            text=response_text,
            emotion="patient",
            category="system_message",
            learning_points=["patience", "persistence", "trying_again"],
            session_id=session_id,
            confidence=0.7,
            processing_time_ms=8,
            error="timeout"
        )
    
    async def create_api_error_fallback(
        self,
        message: str,
        child: Child,
        session_id: str,
        error_details: str
    ) -> AIResponseModel:
        """🔧 Create smart API error fallback response"""
        self.usage_stats["api_error"] += 1
        self.usage_stats["total_fallbacks"] += 1
        
        context = self._detect_message_context(message.lower())
        
        if context == "story":
            response_category = "story_context"
            emotion = "storytelling"
            learning_points = ["imagination", "creativity", "storytelling"]
        elif context == "play":
            response_category = "play_context"
            emotion = "playful"
            learning_points = ["creativity", "play", "interaction"]
        elif context == "question":
            response_category = "educational"
            emotion = "educational"
            learning_points = ["learning", "curiosity", "knowledge"]
        else:
            response_category = "general"
            emotion = "friendly"
            learning_points = ["communication", "friendship"]
        
        responses = self.fallback_responses["api_error"][response_category]
        response_text = random.choice(responses).format(name=child.name)
        
        return AIResponseModel(
            text=response_text,
            emotion=emotion,
            category="fallback",
            learning_points=learning_points,
            session_id=session_id,
            confidence=0.75,
            processing_time_ms=10,
            error=f"api_error: {error_details[:50]}..."
        )
    
    async def create_generic_fallback(
        self,
        message: str,
        child: Child,
        session_id: str,
        error_details: str
    ) -> AIResponseModel:
        """🛠️ Create generic fallback response"""
        self.usage_stats["generic_error"] += 1
        self.usage_stats["total_fallbacks"] += 1
        
        question_words = ["كيف", "لماذا", "ماذا", "why", "how", "what"]
        response_style = "curious" if any(word in message.lower() for word in question_words) else "positive"
        
        responses = self.fallback_responses["generic_error"][response_style]
        response_text = random.choice(responses).format(name=child.name)
        
        return AIResponseModel(
            text=response_text,
            emotion="supportive",
            category="conversation",
            learning_points=["social_interaction", "communication"],
            session_id=session_id,
            confidence=0.6,
            processing_time_ms=5,
            error=f"generic_error: {error_details[:50]}..."
        )
    
    def _detect_message_context(self, message_lower: str) -> str:
        """🔍 Detect message context for appropriate fallback"""
        context_patterns = {
            "story": ["قصة", "story", "حكاية", "احكي", "حدثني"],
            "play": ["لعب", "play", "game", "نلعب", "العب"],
            "question": ["?", "؟", "كيف", "لماذا", "متى", "أين", "ماذا"],
            "music": ["غناء", "sing", "أغنية", "موسيقى"],
            "learning": ["تعلم", "learn", "درس", "علمني"]
        }
        
        for context, keywords in context_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return context
        
        return "general"
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """📊 Get fallback usage statistics"""
        total = self.usage_stats["total_fallbacks"]
        
        return {
            "total_fallbacks_used": total,
            "rate_limit_fallbacks": self.usage_stats["rate_limit"],
            "timeout_fallbacks": self.usage_stats["timeout"],
            "api_error_fallbacks": self.usage_stats["api_error"],
            "generic_error_fallbacks": self.usage_stats["generic_error"],
            "fallback_distribution": {
                "rate_limit_percentage": (self.usage_stats["rate_limit"] / total * 100) if total > 0 else 0,
                "timeout_percentage": (self.usage_stats["timeout"] / total * 100) if total > 0 else 0,
                "api_error_percentage": (self.usage_stats["api_error"] / total * 100) if total > 0 else 0,
                "generic_error_percentage": (self.usage_stats["generic_error"] / total * 100) if total > 0 else 0
            }
        } 