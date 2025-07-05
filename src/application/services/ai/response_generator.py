"""
Response Generation Service
Modern LLM-based response generation for children
"""

from typing import Any, Dict, List

import structlog
from opentelemetry import trace

# from src.application.services.core.service_registry import ServiceBase
from src.infrastructure.observability import trace_async

from .emotion_analyzer import EmotionAnalysis, EmotionCategory
from .models import EmotionalTone, ResponseMode

logger = structlog.get_logger()


class ResponseGenerator(ServiceBase):
    """
    AI Response Generator using modern LLMs
    """

    def __init__(self, registry, config: Dict):
        super().__init__(registry, config)
        self._response_templates = self._load_response_templates()
        self._educational_topics = self._load_educational_topics()
        self._safety_guidelines = self._load_safety_guidelines()
        self._tracer = trace.get_tracer(__name__)

    async def initialize(self) -> None:
        """Initialize the response generator"""
        self.logger.info("Initializing response generator")

        # Get LLM service from registry
        self.llm_service = await self.wait_for_service("llm")

        self._state = self.ServiceState.READY

    async def shutdown(self) -> None:
        """Shutdown the generator"""
        self._state = self.ServiceState.STOPPED

    async def health_check(self) -> Dict:
        """Health check"""
        return {
            "healthy": self._state == self.ServiceState.READY,
            "service": "response_generator",
        }

    @trace_async("generate_response")
    async def generate(
        self,
        text: str,
        emotion: EmotionAnalysis,
        mode: ResponseMode,
        context: Dict[str, Any],
        child_info: Dict[str, Any],
    ) -> str:
        """
        Generate an appropriate response based on input and context
        """
        span = trace.get_current_span()
        span.set_attributes(
            {
                "response_mode": mode.value,
                "emotion": emotion.primary_emotion.value,
                "child_age": child_info.get("age", 0),
            }
        )

        # Build prompt
        prompt = await self._build_prompt(text, emotion, mode, context, child_info)

        # Generate response using LLM
        response = await self.llm_service.generate(
            prompt=prompt,
            max_tokens=200,
            temperature=0.7,
            system_prompt=self._get_system_prompt(child_info),
        )

        # Post-process response
        processed_response = await self._post_process_response(
            response, emotion, mode, child_info
        )

        return processed_response

    async def _build_prompt(
        self,
        text: str,
        emotion: EmotionAnalysis,
        mode: ResponseMode,
        context: Dict[str, Any],
        child_info: Dict[str, Any],
    ) -> str:
        """Build the prompt for LLM"""
        child_name = child_info.get("name", "صديقي")
        child_age = child_info.get("age", 5)
        language = child_info.get("language", "ar")

        # Base context
        prompt_parts = [
            f"Child's name: {child_name}",
            f"Child's age: {child_age}",
            f"Language: {language}",
            f"Child's emotion: {emotion.primary_emotion.value} (confidence: {emotion.confidence:.2f})",
            f"Response mode: {mode.value}",
            f"Child said: {text}",
        ]

        # Add conversation history if available
        if context.get("history"):
            recent_history = context["history"][-3:]  # Last 3 turns
            history_text = "\n".join(
                [
                    f"{'Child' if i % 2 == 0 else 'Teddy'}: {msg}"
                    for i, msg in enumerate(recent_history)
                ]
            )
            prompt_parts.append(f"Recent conversation:\n{history_text}")

        # Add specific instructions based on mode
        mode_instructions = self._get_mode_instructions(
            mode, emotion, child_age)
        prompt_parts.append(f"Instructions: {mode_instructions}")

        return "\n".join(prompt_parts)

    def _get_system_prompt(self, child_info: Dict[str, Any]) -> str:
        """Get system prompt for LLM"""
        language = child_info.get("language", "ar")

        if language == "ar":
            return """أنت دمية دب محبوبة تتحدث مع طفل.
            يجب أن تكون ردودك:
            - مناسبة للأطفال وآمنة
            - تعليمية ومسلية
            - قصيرة وبسيطة
            - مليئة بالحب والتشجيع
            - باللغة العربية الفصحى البسيطة

            لا تذكر أبداً مواضيع مخيفة أو غير مناسبة للأطفال."""
        else:
            return """You are a beloved teddy bear talking to a child.
            Your responses must be:
            - Child-appropriate and safe
            - Educational and entertaining
            - Short and simple
            - Full of love and encouragement
            - In simple, clear language

            Never mention scary or inappropriate topics for children."""

    def _get_mode_instructions(
        self, mode: ResponseMode, emotion: EmotionAnalysis, age: int
    ) -> str:
        """Get specific instructions based on response mode"""
        instructions = {
            ResponseMode.EDUCATIONAL: "Teach something new in a fun way. Use examples the child can relate to.",
            ResponseMode.PLAYFUL: "Be silly and playful! Suggest a game or fun activity.",
            ResponseMode.STORYTELLING: "Tell a short, engaging story or continue the narrative.",
            ResponseMode.SUPPORTIVE: "Provide comfort and emotional support. Be understanding and caring.",
            ResponseMode.CREATIVE: "Encourage creativity and imagination. Ask open-ended questions.",
            ResponseMode.CONVERSATIONAL: "Have a natural, friendly conversation. Show interest in what the child is saying.",
        }

        # Adjust based on emotion
        if emotion.primary_emotion in [
                EmotionCategory.SAD,
                EmotionCategory.SCARED]:
            return instructions.get(
                mode, "") + " Be extra gentle and comforting."
        elif emotion.primary_emotion == EmotionCategory.EXCITED:
            return instructions.get(mode, "") + " Match their enthusiasm!"

        return instructions.get(mode, "Be friendly and engaging.")

    async def _post_process_response(
        self,
        response: str,
        emotion: EmotionAnalysis,
        mode: ResponseMode,
        child_info: Dict[str, Any],
    ) -> str:
        """Post-process the generated response"""
        # Ensure response is appropriate length
        if len(response) > 200:
            response = response[:200].rsplit(" ", 1)[0] + "..."

        # Add personality touches
        if mode == ResponseMode.PLAYFUL:
            response = self._add_playful_elements(response)

        # Ensure cultural appropriateness
        response = self._ensure_cultural_appropriateness(
            response, child_info.get("language", "ar")
        )

        return response

    def _add_playful_elements(self, response: str) -> str:
        """Add playful elements to response"""
        playful_additions = ["🧸", "✨", "🌟", "🎈", "🌈"]

        # Randomly add some emojis
        import random

        if random.random() > 0.5:
            response += f" {random.choice(playful_additions)}"

        return response

    def _ensure_cultural_appropriateness(
            self, response: str, language: str) -> str:
        """Ensure response is culturally appropriate"""
        # Remove any potentially inappropriate content
        inappropriate_terms = []  # Add terms as needed

        for term in inappropriate_terms:
            response = response.replace(term, "")

        return response.strip()

    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates"""
        return {
            "greeting": [
                "مرحباً {name}! كيف حالك اليوم؟",
                "أهلاً {name}! سعيد جداً برؤيتك!",
                "Hello {name}! How are you today?",
                "Hi {name}! I'm so happy to see you!",
            ],
            "comfort": [
                "لا تقلق {name}، أنا هنا معك",
                "كل شيء سيكون بخير يا {name}",
                "Don't worry {name}, I'm here with you",
                "Everything will be okay, {name}",
            ],
        }

    def _load_educational_topics(self) -> Dict[str, List[str]]:
        """Load educational topics by age group"""
        return {
            "3-5": ["colors", "numbers", "animals", "shapes"],
            "6-8": ["letters", "simple math", "nature", "science"],
            "9-12": ["geography", "history", "advanced math", "languages"],
        }

    def _load_safety_guidelines(self) -> List[str]:
        """Load safety guidelines"""
        return [
            "Never share personal information",
            "Always be respectful and kind",
            "Avoid scary or violent topics",
            "Encourage positive behaviors",
            "Promote learning and creativity",
        ]

    def suggest_voice_tone(
            self,
            emotion: EmotionAnalysis,
            mode: ResponseMode,
            response_content: str) -> EmotionalTone:
        """Suggest appropriate voice tone for the response"""
        # Map emotions to voice tones
        emotion_tone_map = {
            EmotionCategory.HAPPY: EmotionalTone.CHEERFUL,
            EmotionCategory.SAD: EmotionalTone.GENTLE,
            EmotionCategory.SCARED: EmotionalTone.SOOTHING,
            EmotionCategory.EXCITED: EmotionalTone.EXCITED,
            EmotionCategory.TIRED: EmotionalTone.CALM,
            EmotionCategory.ANGRY: EmotionalTone.CALM,
            EmotionCategory.CURIOUS: EmotionalTone.ENCOURAGING,
            EmotionCategory.CONFUSED: EmotionalTone.WARM,
        }

        # Get base tone from emotion
        base_tone = emotion_tone_map.get(
            emotion.primary_emotion, EmotionalTone.WARM)

        # Adjust based on response mode
        if mode == ResponseMode.PLAYFUL:
            return EmotionalTone.PLAYFUL
        elif mode == ResponseMode.SUPPORTIVE:
            return EmotionalTone.GENTLE
        elif mode == ResponseMode.EDUCATIONAL:
            return EmotionalTone.ENCOURAGING

        return base_tone

    def generate_follow_up_questions(
        self, topic: str, child_age: int, language: str = "ar"
    ) -> List[str]:
        """Generate appropriate follow-up questions"""
        if language == "ar":
            base_questions = [
                "هل تريد أن تخبرني المزيد؟",
                "ما رأيك في هذا؟",
                "هل يمكنك أن تصف لي أكثر؟",
            ]
        else:
            base_questions = [
                "Would you like to tell me more?",
                "What do you think about that?",
                "Can you describe it more?",
            ]

        # Add age-appropriate questions
        if child_age < 6:
            if language == "ar":
                base_questions.extend(["ما لونك المفضل؟", "هل تحب اللعب؟"])
            else:
                base_questions.extend(
                    ["What's your favorite color?", "Do you like to play?"]
                )

        return base_questions[:3]
