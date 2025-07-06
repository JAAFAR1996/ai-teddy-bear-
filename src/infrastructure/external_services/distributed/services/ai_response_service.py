"""
Distributed AI response service deployment.
"""

import logging
import time
from typing import Any, Dict

try:
    from ray import serve
    from openai import AsyncOpenAI
    AI_SERVICES_AVAILABLE = True
except ImportError:
    AI_SERVICES_AVAILABLE = False
    serve = None

from ..mocks import MockAIServices
from ..models import ChildContext

logger = logging.getLogger(__name__)

if AI_SERVICES_AVAILABLE:
    @serve.deployment(
        name="ai-response-service",
        num_replicas=2,
        ray_actor_options={"num_cpus": 1, "memory": 2000 * 1024 * 1024},  # 2GB
    )
    class AIResponseService:
        """Distributed AI response generation service."""

        def __init__(self):
            self.openai_client = None
            self.service_stats = {"requests": 0, "total_time": 0.0}
            self._initialize_models()

        def _initialize_models(self) -> Any:
            """Initialize AI response models."""
            try:
                self.openai_client = AsyncOpenAI()
                logger.info("✅ AI response service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize AI response models: {e}")

        async def generate_response(
            self, text: str, child_context: ChildContext, emotion: str = "neutral"
        ) -> Dict[str, Any]:
            """Generate AI response based on input and context."""
            start_time = time.time()
            self.service_stats["requests"] += 1

            try:
                if self.openai_client:
                    # Real AI response generation
                    result = await self._generate_with_openai(
                        text, child_context, emotion
                    )
                else:
                    # Mock AI response
                    result = await MockAIServices.generate_ai_response(
                        text, child_context
                    )

                processing_time = (time.time() - start_time) * 1000
                result["processing_time_ms"] = processing_time
                self.service_stats["total_time"] += processing_time

                return result

            except Exception as e:
                logger.error(f"❌ AI response generation failed: {e}")
                return await MockAIServices.generate_ai_response(text, child_context)

        async def _generate_with_openai(
            self, text: str, child_context: ChildContext, emotion: str
        ) -> Dict[str, Any]:
            """Generate response using OpenAI."""
            try:
                # Create contextual prompt
                prompt = self._create_contextual_prompt(
                    text, child_context, emotion)

                # Generate response
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": prompt["system"]},
                        {"role": "user", "content": prompt["user"]},
                    ],
                    max_tokens=150,
                    temperature=0.7,
                )

                response_text = response.choices[0].message.content

                return {
                    "response_text": response_text,
                    "emotion": emotion,
                    "confidence": 0.9,
                    "personalized": True,
                }

            except Exception as e:
                logger.error(f"❌ OpenAI response error: {e}")
                return await MockAIServices.generate_ai_response(text, child_context)

        def _create_contextual_prompt(
            self, text: str, child_context: ChildContext, emotion: str
        ) -> Dict[str, str]:
            """Create contextual prompt for AI generation."""
            age_appropriate = "very simple" if child_context.age < 6 else "simple"

            system_prompt = f"""
            You are Teddy, a friendly AI teddy bear talking to {child_context.name},
            a {child_context.age}-year-old child. Respond in {child_context.language}
            with {age_appropriate} language. The child seems {emotion}.
            Be caring, educational, and age-appropriate.
            """

            user_prompt = f"Child said: '{text}'"

            return {"system": system_prompt.strip(), "user": user_prompt}
else:
    AIResponseService = MockAIServices
