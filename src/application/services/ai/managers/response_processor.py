import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from src.application.services.ai.models.ai_response_models import AIResponseModel
from src.application.services.ai.managers.cache_manager import CacheManager
from openai.types.chat import ChatCompletion

import logging

logger = logging.getLogger(__name__)


@dataclass
class ResponseModelData:
    """Data class for creating AIResponseModel."""
    response: Any
    message: str
    emotion_task: asyncio.Task
    category_task: asyncio.Task
    session_id: str
    device_id: str
    cache_key: str
    start_time: datetime
    conversation_history: List[Dict]
    max_history_length: int


class ResponseProcessor:
    """Processes the OpenAI response and creates the final AIResponseModel."""

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager

    async def create_response_model(self, model_data: ResponseModelData) -> AIResponseModel:
        """Create the final AI response model with all metadata"""
        response_text = model_data.response.choices[0].message.content.strip()

        emotion, category = await asyncio.gather(model_data.emotion_task, model_data.category_task)
        learning_points = await self._extract_learning_points(model_data.message, response_text)

        processing_time = int(
            (datetime.utcnow() - model_data.start_time).total_seconds() * 1000)

        ai_response = AIResponseModel(
            text=response_text,
            emotion=emotion,
            category=category,
            learning_points=learning_points,
            session_id=model_data.session_id,
            confidence=0.95,
            processing_time_ms=processing_time,
            cached=False,
            model_used=model_data.response.model,
            usage=model_data.response.usage.model_dump() if model_data.response.usage else {},
        )

        self._update_conversation_history(
            conversation_history=model_data.conversation_history,
            max_history_length=model_data.max_history_length,
            message=model_data.message,
            response=response_text,
            emotion=emotion,
        )

        await self.cache_manager.store_response(model_data.cache_key, ai_response)

        logger.info(
            f"✅ AI response generated in {processing_time}ms (model: {model_data.response.model})"
        )
        return ai_response

    async def _extract_learning_points(self, message: str, response: str) -> List[str]:
        """Enhanced learning points extraction"""
        points = []
        combined_text = f"{message} {response}".lower()
        learning_patterns = {
            "emotional_intelligence": ["مشاعر", "حزين", "سعيد", "خائف"],
            "language_development": ["كلمة", "جملة", "قراءة", "كتابة"],
            "mathematical_thinking": ["رقم", "عدد", "حساب", "جمع"],
            "scientific_curiosity": ["لماذا", "كيف", "تجربة", "اكتشاف"],
            "social_skills": ["صديق", "شكراً", "من فضلك", "آسف"],
            "creative_expression": ["رسم", "قصة", "إبداع", "خيال"],
            "cultural_awareness": ["تقاليد", "عادات", "ثقافة"],
            "problem_solving": ["حل", "مشكلة", "فكر", "طريقة"],
        }
        for skill, keywords in learning_patterns.items():
            if any(keyword in combined_text for keyword in keywords):
                points.append(skill)
        return points if points else ["general_communication"]

    def _update_conversation_history(
        self,
        conversation_history: List[Dict],
        max_history_length: int,
        message: str,
        response: str,
        emotion: str,
    ):
        """Enhanced conversation history with emotion tracking"""
        conversation_history.append(
            {"role": "user", "content": message, "emotion": emotion,
                "timestamp": datetime.utcnow().isoformat()}
        )
        conversation_history.append(
            {"role": "assistant", "content": response,
                "timestamp": datetime.utcnow().isoformat()}
        )
        if len(conversation_history) > max_history_length * 2:
            del conversation_history[: -max_history_length * 2]
