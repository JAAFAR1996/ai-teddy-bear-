"""
🛡️ Fallback Response Service - Enterprise 2025 Implementation
Smart fallback responses for error handling and system resilience
"""

import logging
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.application.services.ai.models.ai_response_models import AIResponseModel
from src.core.domain.entities.child import Child

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
        self.usage_stats = {"rate_limit": 0, "timeout": 0, "api_error": 0, "generic_error": 0, "total_fallbacks": 0}

        logger.info("✅ Fallback Response Service initialized")

    def _load_fallback_responses(self) -> Dict[str, Dict[str, List[str]]]:
        """Load comprehensive fallback response templates"""
        return {
            "rate_limit": {
                "story": [
                    "يا {name}، أنا مشغول قليلاً الآن! سأحكي لك قصة جميلة بعد لحظة! 📚✨",
                    "دعني أجمع أفكاري يا {name} وسأعود بقصة رائعة! 🌟📖",
                    "صبراً يا {name}، أحضر قصة مميزة لك! 🧸💭",
                ],
                "play": [
                    "يا {name}، دعني أرتاح لثانية وسنلعب لعبة رائعة! 🎮🧸",
                    "تعال نلعب بعد قليل يا {name}! سأحضر لعبة جديدة! 🎯⭐",
                    "استعد للعب يا {name}، أحضر شيئاً ممتعاً! 🎪🎈",
                ],
                "question": [
                    "سؤال ممتاز يا {name}! دعني أفكر وسأجيبك بعد لحظة! 🤔💭",
                    "أحب فضولك يا {name}! سأبحث عن إجابة رائعة! 🔍✨",
                    "سؤالك يحتاج تفكير يا {name}، انتظرني قليلاً! 🧠💫",
                ],
                "general": [
                    "صبراً يا {name}، سأعود إليك بعد لحظة! 🧸💫",
                    "أحتاج دقيقة واحدة يا {name}! 🕐🌟",
                    "دعني أجمع أفكاري وسأكون معك! 💭🤗",
                ],
            },
            "timeout": {
                "encouraging": [
                    "يا {name}، استغرق الأمر وقتاً أطول مما توقعت! حاول مرة أخرى! 🔄🧸",
                    "أعتذر للتأخير يا {name}! دعنا نحاول مرة أخرى! 🔁💪",
                    "الصبر مفتاح الفرج يا {name}! هيا نعيد المحاولة! ⏰✨",
                ],
                "playful": [
                    "يبدو أنني أبطأ من السلحفاة اليوم يا {name}! 🐢😅",
                    "عذراً يا {name}، كنت أحلم بالعسل! دعنا نعيد المحاولة! 🍯😴",
                    "أظن أنني احتجت إلى قيلولة يا {name}! الآن أنا مستعد! 😴➡️😊",
                ],
            },
            "api_error": {
                "story_context": [
                    "يا {name}، دعني أحكي لك قصة بسيطة... كان يا ما كان، طفل رائع اسمه {name}! 📖✨",
                    "هل تريد قصة يا {name}؟ أعرف قصة عن دب صغير شجاع مثلك! 🐻🌟",
                    "تعال أحكي لك يا {name} عن مغامرة جميلة حدثت في الغابة! 🌳🗺️",
                ],
                "play_context": [
                    "يا {name}، تعال نلعب لعبة الكلمات! قل لي اسم حيوان! 🐾🎮",
                    "هيا نلعب يا {name}! ما رأيك في لعبة التخمين؟ 🔮🎯",
                    "تعال نبدع معاً يا {name}! فكر في شيء تحبه وأخبرني! 💭🌈",
                ],
                "educational": [
                    "يا {name}، هل تعرف أن الأفيال تستطيع السباحة؟ 🐘💧",
                    "معلومة مثيرة يا {name}: النجوم تغني أغاني جميلة في السماء! ⭐🎵",
                    "هل تعلم يا {name} أن الفراشات تتذوق بأقدامها؟ 🦋👣",
                ],
                "general": [
                    "يا {name}، هذا مثير للاهتمام! حدثني أكثر عما تفكر فيه! 🤔💭",
                    "أحب الحديث معك يا {name}! ما الشيء الجميل الذي حدث معك اليوم؟ 🌟🗣️",
                    "يا {name}، أنت رائع! أخبرني عن شيء تحبه! ❤️🎈",
                ],
            },
            "generic_error": {
                "positive": [
                    "يا {name}، أحب الحديث معك! أخبرني، ما الشيء المفضل لديك اليوم؟ 🌟🧸",
                    "أنت مميز يا {name}! دعنا نتحدث عن شيء يجعلك سعيداً! 🌈😊",
                    "يا {name}، أنا هنا دائماً من أجلك! ما الذي تريد أن نفعله معاً؟ 🤗💫",
                ],
                "curious": [
                    "يا {name}، عقلك مليء بالأفكار الرائعة! شاركني واحدة منها! 🧠✨",
                    "فضولك رائع يا {name}! ما الذي تود أن تعرفه اليوم؟ 🔍🌟",
                    "أحب أسئلتك يا {name}! هل لديك سؤال جديد لي؟ ❓🎯",
                ],
            },
            "wake_word": {
                "enthusiastic": [
                    "نعم {name}؟ أنا هنا! كيف يمكنني مساعدتك؟ 🧸✨",
                    "مرحباً {name}! أسعد بسماع صوتك! بماذا تفكر؟ 🌟😊",
                    "أهلاً وسهلاً {name}! أنا مستعد للحديث! ما الذي تريد أن نفعله؟ 🎉🧸",
                ],
                "warm": [
                    "أهلاً بك يا {name}! كيف حالك اليوم؟ 🤗🌅",
                    "يا {name} الغالي! أتمنى أن يكون يومك رائعاً! 💖🌸",
                    "مرحباً بصديقي {name}! ما الجديد معك؟ 👋😄",
                ],
            },
        }

    async def create_rate_limit_fallback(self, message: str, child: Child, session_id: str) -> AIResponseModel:
        """🚦 Create smart rate limit fallback response"""
        self.usage_stats["rate_limit"] += 1
        self.usage_stats["total_fallbacks"] += 1

        # Detect context from message
        context = self._detect_message_context(message.lower())

        # Get appropriate response
        responses = self.fallback_responses["rate_limit"].get(context, self.fallback_responses["rate_limit"]["general"])

        response_text = random.choice(responses).format(name=child.name)

        # Add encouragement for patience
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
            error="rate_limit",
        )

    async def create_timeout_fallback(self, message: str, child: Child, session_id: str) -> AIResponseModel:
        """⏰ Create smart timeout fallback response"""
        self.usage_stats["timeout"] += 1
        self.usage_stats["total_fallbacks"] += 1

        # Choose response style based on child's age
        if child.age <= 5:
            response_style = "playful"
        else:
            response_style = "encouraging"

        responses = self.fallback_responses["timeout"].get(
            response_style, self.fallback_responses["timeout"]["encouraging"]
        )

        response_text = random.choice(responses).format(name=child.name)

        return AIResponseModel(
            text=response_text,
            emotion="patient",
            category="system_message",
            learning_points=["patience", "persistence", "trying_again"],
            session_id=session_id,
            confidence=0.7,
            processing_time_ms=8,
            error="timeout",
        )

    async def create_api_error_fallback(
        self, message: str, child: Child, session_id: str, error_details: str
    ) -> AIResponseModel:
        """🔧 Create smart API error fallback response"""
        self.usage_stats["api_error"] += 1
        self.usage_stats["total_fallbacks"] += 1

        # Detect context and provide appropriate fallback
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
            error=f"api_error: {error_details[:50]}...",
        )

    async def create_generic_fallback(
        self, message: str, child: Child, session_id: str, error_details: str
    ) -> AIResponseModel:
        """🛠️ Create generic fallback response"""
        self.usage_stats["generic_error"] += 1
        self.usage_stats["total_fallbacks"] += 1

        # Choose response style based on message characteristics
        if any(word in message.lower() for word in ["كيف", "لماذا", "ماذا", "why", "how", "what"]):
            response_style = "curious"
        else:
            response_style = "positive"

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
            error=f"generic_error: {error_details[:50]}...",
        )

    async def create_wake_word_response(self, child: Child, session_id: str) -> AIResponseModel:
        """👋 Create wake word response with variety"""
        # Choose response style based on time or randomness
        style = random.choice(["enthusiastic", "warm"])

        responses = self.fallback_responses["wake_word"][style]
        response_text = random.choice(responses).format(name=child.name)

        return AIResponseModel(
            text=response_text,
            emotion="happy",
            category="greeting",
            learning_points=["social_interaction", "communication", "greeting"],
            session_id=session_id,
            confidence=1.0,
            processing_time_ms=3,
        )

    def _detect_message_context(self, message_lower: str) -> str:
        """🔍 Detect message context for appropriate fallback"""
        context_patterns = {
            "story": ["قصة", "story", "حكاية", "احكي", "حدثني", "قصص"],
            "play": ["لعب", "play", "game", "نلعب", "العب", "لعبة"],
            "question": ["?", "؟", "كيف", "لماذا", "متى", "أين", "ماذا", "مين", "why", "how", "what"],
            "music": ["غناء", "sing", "أغنية", "موسيقى", "غني"],
            "learning": ["تعلم", "learn", "درس", "أتعلم", "علمني"],
        }

        for context, keywords in context_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return context

        return "general"

    def _get_context_keywords(self, context: str) -> List[str]:
        """📝 Get keywords for specific context"""
        context_map = {
            "story": ["قصة", "story", "حكاية", "احكي", "حدثني"],
            "play": ["لعب", "play", "game", "نلعب", "العب"],
            "question": ["?", "؟", "كيف", "لماذا", "متى", "أين", "ماذا"],
        }
        return context_map.get(context, [])

    async def create_contextual_educational_response(
        self, child: Child, session_id: str, topic: Optional[str] = None
    ) -> AIResponseModel:
        """📚 Create educational fallback response"""
        educational_facts = {
            "animals": [
                f"يا {child.name}، هل تعرف أن الدلافين تنادي بعضها بأسماء خاصة؟ 🐬✨",
                f"معلومة رائعة يا {child.name}: النحل يرقص ليخبر أصدقاءه عن مكان الزهور! 🐝💃",
                f"يا {child.name}، الفيلة تستطيع أن تسمع بأقدامها من بعيد! 🐘👂",
            ],
            "space": [
                f"يا {child.name}، هل تعلم أن النجوم تغني أغاني جميلة في الفضاء؟ ⭐🎵",
                f"معلومة مذهلة يا {child.name}: هناك مليارات النجوم في السماء! 🌟✨",
                f"يا {child.name}، القمر يؤثر على المحيطات ويصنع المد والجزر! 🌙🌊",
            ],
            "nature": [
                f"يا {child.name}، الأشجار تتحدث مع بعضها عبر جذورها! 🌳💬",
                f"هل تعلم يا {child.name} أن قوس القزح يحتوي على سبعةألوان رائعة؟ 🌈🎨",
                f"معلومة جميلة يا {child.name}: الفراشات تتذوق بأقدامها! 🦋👣",
            ],
        }

        if not topic:
            topic = random.choice(list(educational_facts.keys()))

        facts = educational_facts.get(topic, educational_facts["animals"])
        response_text = random.choice(facts)

        return AIResponseModel(
            text=response_text,
            emotion="educational",
            category="learning",
            learning_points=["knowledge", "curiosity", "science"],
            session_id=session_id,
            confidence=0.9,
            processing_time_ms=12,
        )

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
                "generic_error_percentage": (self.usage_stats["generic_error"] / total * 100) if total > 0 else 0,
            },
        }

    def reset_statistics(self) -> None:
        """🔄 Reset usage statistics"""
        self.usage_stats = {"rate_limit": 0, "timeout": 0, "api_error": 0, "generic_error": 0, "total_fallbacks": 0}
        logger.info("Fallback usage statistics reset")
