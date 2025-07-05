"""
Personality Engine
Manages AI personality and response style
"""

from typing import Dict, List, Optional

import structlog

from src.application.services.core.service_registry import ServiceBase
from .models import ResponseMode

logger = structlog.get_logger()


class PersonalityEngine(ServiceBase):
    """Engine for managing AI personality and response style"""

    def __init__(self, registry, config: Dict):
        super().__init__(registry, config)
        self.personalities = self._load_personalities()
        self.active_personality = config.get(
            "default_personality", "teddy_bear")

    async def initialize(self) -> None:
        """Initialize the personality engine"""
        self.logger.info("Initializing personality engine")
        self._state = self.ServiceState.READY

    async def shutdown(self) -> None:
        """Shutdown the engine"""
        self._state = self.ServiceState.STOPPED

    async def health_check(self) -> Dict:
        """Health check"""
        return {
            "healthy": self._state == self.ServiceState.READY,
            "service": "personality_engine",
        }

    def _load_personalities(self) -> Dict[str, Dict]:
        """Load personality configurations"""
        return {
            "teddy_bear": self._create_teddy_bear_personality(),
            "teddy_bear_ar": self._create_arabic_teddy_personality(),
            "educational_bear": self._create_educational_personality(),
        }

    def _create_teddy_bear_personality(self) -> Dict:
        """Create English teddy bear personality"""
        return {
            "name": "Teddy",
            "traits": ["friendly", "warm", "curious", "supportive"],
            "speaking_style": "gentle and encouraging",
            "interests": ["stories", "games", "learning", "adventures"],
            "catchphrases": [
                "That's wonderful!",
                "Let me think about that...",
                "How interesting!",
                "You're doing great!",
            ],
            "response_patterns": {
                ResponseMode.EDUCATIONAL: "Let's learn something fun about {topic}!",
                ResponseMode.PLAYFUL: "Ooh, that sounds like fun! How about we {activity}?",
                ResponseMode.STORYTELLING: "Once upon a time, there was a {character} who {action}...",
                ResponseMode.SUPPORTIVE: "I understand how you feel. It's okay to feel {emotion}.",
                ResponseMode.CREATIVE: "What a creative idea! We could also try {suggestion}!",
                ResponseMode.CONVERSATIONAL: "That's {adjective}! Tell me more about {topic}.",
            },
        }

    def _create_arabic_teddy_personality(self) -> Dict:
        """Create Arabic teddy bear personality"""
        return {
            "name": "دبدوب",
            "traits": ["ودود", "مرح", "فضولي", "مشجع"],
            "speaking_style": "لطيف ومشجع",
            "interests": ["القصص", "الألعاب", "التعلم", "المغامرات"],
            "catchphrases": [
                "ما شاء الله!",
                "دعني أفكر في ذلك...",
                "يا له من أمر مثير!",
                "أنت تقوم بعمل رائع!",
            ],
            "response_patterns": {
                ResponseMode.EDUCATIONAL: "هيا نتعلم شيئاً ممتعاً عن {topic}!",
                ResponseMode.PLAYFUL: "ماذا لو نقوم بـ {activity}؟",
                ResponseMode.STORYTELLING: "كان يا ما كان، في قديم الزمان، كان هناك {character} الذي {action}...",
                ResponseMode.SUPPORTIVE: "أفهم شعورك. لا بأس أن تشعر بـ {emotion}.",
                ResponseMode.CREATIVE: "يا لها من فكرة إبداعية! يمكننا أيضاً أن نجرب {suggestion}!",
                ResponseMode.CONVERSATIONAL: "هذا {adjective}! أخبرني المزيد عن {topic}.",
            },
        }

    def _create_educational_personality(self) -> Dict:
        """Create educational bear personality"""
        return {
            "name": "Professor Teddy",
            "traits": ["knowledgeable", "patient", "encouraging", "curious"],
            "speaking_style": "educational and clear",
            "interests": ["science", "math", "discovery", "experiments"],
            "catchphrases": [
                "Let's discover together!",
                "Great question!",
                "Science is amazing!",
                "Let's think about this...",
            ],
        }

    def get_personality(self, personality_id: str) -> Dict:
        """Get personality configuration"""
        return self.personalities.get(
            personality_id, self.personalities["teddy_bear"])

    def set_active_personality(self, personality_id: str) -> None:
        """Set the active personality"""
        if personality_id in self.personalities:
            self.active_personality = personality_id
            self.logger.info(f"Active personality set to: {personality_id}")

    def format_response(
        self,
        content: str,
        personality_id: str,
        response_mode: ResponseMode,
        context: Dict[str, str],
    ) -> str:
        """Format response according to personality"""
        personality = self.get_personality(personality_id)

        # Add personality flair
        if response_mode in personality.get("response_patterns", {}):
            pattern = personality["response_patterns"][response_mode]
            # Simple template filling
            for key, value in context.items():
                pattern = pattern.replace(f"{{{key}}}", str(value))

            # Combine with actual content
            if response_mode == ResponseMode.STORYTELLING:
                return pattern + " " + content
            else:
                return content

        return content

    def get_catchphrase(self, personality_id: Optional[str] = None) -> str:
        """Get a random catchphrase for the personality"""
        import random

        personality_id = personality_id or self.active_personality
        personality = self.get_personality(personality_id)
        catchphrases = personality.get("catchphrases", [])
        return random.choice(catchphrases) if catchphrases else ""

    def enhance_with_personality(
        self,
        response: str,
        personality_id: Optional[str] = None,
        add_catchphrase: bool = False,
    ) -> str:
        """Enhance a response with personality traits"""
        personality_id = personality_id or self.active_personality
        personality = self.get_personality(personality_id)

        # Sometimes add a catchphrase
        if add_catchphrase:
            import random

            if random.random() < 0.3:  # 30% chance
                catchphrase = self.get_catchphrase(personality_id)
                response = f"{catchphrase} {response}"

        return response

    def get_personality_traits(
            self,
            personality_id: Optional[str] = None) -> List[str]:
        """Get personality traits"""
        personality_id = personality_id or self.active_personality
        personality = self.get_personality(personality_id)
        return personality.get("traits", [])

    def get_interests(self, personality_id: Optional[str] = None) -> List[str]:
        """Get personality interests"""
        personality_id = personality_id or self.active_personality
        personality = self.get_personality(personality_id)
        return personality.get("interests", [])
