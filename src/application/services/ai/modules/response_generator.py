#!/usr/bin/env python3
"""
Response Generator Module - Extracted from main_service.py
Handles response generation for AI Teddy Bear interactions
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
import structlog

from .emotion_analyzer import EmotionResult
from .session_manager import SessionContext


class ActivityType(Enum):
    """Types of activities the teddy can engage in"""

    CONVERSATION = "conversation"
    STORY = "story"
    GAME = "game"
    LEARNING = "learning"
    COMFORT = "comfort"
    SLEEP_ROUTINE = "sleep_routine"


@dataclass
class ResponseContext:
    """Context for generating responses"""

    text: str
    emotion: str
    activity_type: ActivityType
    metadata: Dict = field(default_factory=dict)
    processing_time: int = 0


class ResponseGenerator:
    """Generates contextual responses for AI Teddy Bear"""

    def __init__(self, ai_service=None, story_generator=None, game_engine=None):
        self.logger = structlog.get_logger()
        self.ai_service = ai_service
        self.story_generator = story_generator
        self.game_engine = game_engine

    async def generate_contextual_response(
        self,
        text: str,
        emotion: EmotionResult,
        session: SessionContext
    ) -> ResponseContext:
        """Generate response based on context and emotion"""

        # Determine activity type
        activity_type = await self.determine_activity_type(text, emotion, session)

        # Update session activity
        session.current_activity = activity_type

        # Generate appropriate response
        start_time = datetime.utcnow()

        response_text = await self.generate_response_for_activity(
            text, emotion, activity_type, session
        )

        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000)

        return ResponseContext(
            text=response_text,
            emotion=self.map_emotion_to_voice(emotion),
            activity_type=activity_type,
            processing_time=processing_time,
        )

    async def determine_activity_type(
        self, text: str, emotion: EmotionResult, session: SessionContext
    ) -> ActivityType:
        """Determine the type of activity based on input and context"""

        text_lower = text.lower()

        # Check for explicit activity requests first
        explicit_activity = self._check_explicit_activity_requests(text_lower)
        if explicit_activity:
            return explicit_activity

        # Check emotion and session context
        return self._determine_activity_from_emotion_and_session(emotion, session)

    def _check_explicit_activity_requests(self, text_lower: str) -> Optional[ActivityType]:
        """Check for explicit activity requests in text"""
        activity_keywords = {
            ActivityType.STORY: ["story", "tell me a story", "tale"],
            ActivityType.GAME: ["game", "play", "let's play"],
            ActivityType.LEARNING: ["learn", "teach", "what is", "how does"],
            ActivityType.SLEEP_ROUTINE: ["sleep", "tired", "bedtime", "night"]
        }

        for activity_type, keywords in activity_keywords.items():
            if any(word in text_lower for word in keywords):
                return activity_type

        return None

    def _determine_activity_from_emotion_and_session(
        self, emotion: EmotionResult, session: SessionContext
    ) -> ActivityType:
        """Determine activity based on emotion and session context"""
        # Check emotional state for comfort needs
        if emotion.primary_emotion in ["sad", "scared", "upset"]:
            return ActivityType.COMFORT

        # Continue previous activity if applicable
        if session.current_activity and session.interaction_count < 3:
            return session.current_activity

        # Default to conversation
        return ActivityType.CONVERSATION

    async def generate_response_for_activity(
        self,
        text: str,
        emotion: EmotionResult,
        activity_type: ActivityType,
        session: SessionContext,
    ) -> str:
        """Generate response based on activity type"""

        context = {
            "child_age": session.metadata.get("age", 5),
            "language": session.language_preference,
            "previous_interactions": len(session.interactions),
            "emotion": emotion.to_dict(),
        }

        if activity_type == ActivityType.STORY:
            return await self._handle_story_request(text, emotion, session)

        elif activity_type == ActivityType.GAME:
            return await self._handle_game_interaction(text, session)

        elif activity_type == ActivityType.LEARNING:
            return await self._handle_learning_interaction(text, context)

        elif activity_type == ActivityType.COMFORT:
            return await self._generate_comfort_response(text, emotion, context)

        elif activity_type == ActivityType.SLEEP_ROUTINE:
            return await self._handle_sleep_routine(text, session)

        else:  # CONVERSATION
            return await self._handle_conversation(text, context)

    async def generate_welcome_message(self, child_id: str, preferences: Dict) -> str:
        """Generate personalized welcome message"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                "generate welcome message",
                context={
                    "mode": "welcome",
                    "child_age": preferences.get("age", 5),
                    "language": preferences.get("language", "en"),
                    "interests": preferences.get("interests", []),
                },
            )

        # Fallback messages
        messages = {
            "en": "Hello! I'm so happy to talk with you today! What would you like to do?",
            "es": "¡Hola! ¡Estoy muy feliz de hablar contigo hoy! ¿Qué te gustaría hacer?",
            "fr": "Bonjour! Je suis très heureux de parler avec toi aujourd'hui! Que voudrais-tu faire?",
            "ar": "مرحبا! أنا سعيد جداً للتحدث معك اليوم! ماذا تريد أن تفعل؟",
        }

        language = preferences.get("language", "en")
        return messages.get(language, messages["en"])

    async def generate_goodbye_message(
        self, session: SessionContext, summary: Dict
    ) -> str:
        """Generate personalized goodbye message"""

        emotion_summary = summary.get("emotion_summary", {})
        dominant_emotion = emotion_summary.get("dominant", "neutral")

        if self.ai_service:
            return await self.ai_service.generate_response(
                "generate goodbye message",
                context={
                    "mode": "goodbye",
                    "dominant_emotion": dominant_emotion,
                    "duration_minutes": summary["duration_minutes"],
                    "language": session.language_preference,
                    "activities": [i.get("activity_type") for i in session.interactions[-5:]],
                },
            )

        # Fallback messages based on emotion
        if dominant_emotion in ["happy", "excited"]:
            return "That was so much fun! I can't wait to play with you again soon! Sweet dreams!"
        elif dominant_emotion in ["sad", "upset"]:
            return "I hope you feel better soon. Remember, I'm always here when you need a friend! Take care!"
        else:
            return "It was wonderful spending time with you today! Come back and play with me anytime!"

    def get_fallback_response(self, session: SessionContext) -> str:
        """Get appropriate fallback response"""

        responses = [
            "I'm sorry, I didn't quite understand that. Can you tell me again?",
            "Hmm, that's interesting! Can you help me understand what you mean?",
            "Oh, I think I missed that. Could you say it another way?",
            "Let me think about that... Can you tell me more?",
        ]

        # Use interaction count to vary responses
        index = session.interaction_count % len(responses)
        return responses[index]

    # Private helper methods for different activity types

    async def _handle_story_request(
        self, text: str, emotion: EmotionResult, session: SessionContext
    ) -> str:
        """Handle story generation requests"""

        if self.story_generator:
            return await self.story_generator.generate_story(
                prompt=text,
                emotion=emotion.primary_emotion,
                age=session.metadata.get("age", 5)
            )

        # Simple fallback story
        return ("Once upon a time, there was a magical teddy bear who loved to make "
                "children smile. This teddy bear had a special power - it could understand "
                "exactly how children felt and always knew the right thing to say...")

    async def _handle_game_interaction(self, text: str, session: SessionContext) -> str:
        """Handle game interactions"""

        if self.game_engine:
            return await self.game_engine.process_game_input(text, session.session_id)

        # Simple guessing game fallback
        return ("Let's play a guessing game! I'm thinking of an animal that's "
                "big and gray with a long trunk. Can you guess what it is?")

    async def _handle_learning_interaction(self, text: str, context: Dict) -> str:
        """Handle educational content requests"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                text,
                context={**context, "mode": "educational", "child_safe": True}
            )

        return "That's a great question! Learning new things is so much fun. Let me explain..."

    async def _generate_comfort_response(
        self, text: str, emotion: EmotionResult, context: Dict
    ) -> str:
        """Generate comforting response for upset children"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                text,
                context={
                    **context,
                    "mode": "comfort",
                    "emotion": emotion.primary_emotion,
                    "child_safe": True
                }
            )

        # Empathetic fallback responses
        if emotion.primary_emotion == "sad":
            return ("I understand you're feeling sad. It's okay to feel that way sometimes. "
                    "Would you like to talk about it, or shall we do something fun together?")
        elif emotion.primary_emotion == "scared":
            return ("It's okay to feel scared sometimes. I'm here with you, and you're safe. "
                    "Would you like me to tell you a happy story or sing a song?")
        else:
            return "I'm here for you. Everything will be okay. What would make you feel better?"

    async def _handle_sleep_routine(self, text: str, session: SessionContext) -> str:
        """Handle bedtime routine interactions"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                text,
                context={
                    "mode": "bedtime",
                    "child_age": session.metadata.get("age", 5),
                    "soothing": True
                }
            )

        return ("It's time to rest now. Close your eyes and imagine floating on a "
                "soft, fluffy cloud. The stars are twinkling gently above you...")

    async def _handle_conversation(self, text: str, context: Dict) -> str:
        """Handle general conversation"""

        if self.ai_service:
            return await self.ai_service.generate_response(
                text,
                context={**context, "mode": "conversation", "child_safe": True}
            )

        return "That sounds interesting! Tell me more about that."

    def map_emotion_to_voice(self, emotion: EmotionResult) -> str:
        """Map emotion to appropriate voice style"""

        emotion_voice_map = {
            "happy": "cheerful",
            "sad": "sympathetic",
            "scared": "comforting",
            "angry": "calm",
            "excited": "enthusiastic",
            "neutral": "friendly"
        }

        return emotion_voice_map.get(emotion.primary_emotion, "warm")
