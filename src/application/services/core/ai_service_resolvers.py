from typing import List, Optional
from datetime import datetime, timedelta

try:
    import strawberry
except ImportError:
    class strawberry:
        def enum(x): return x
        type = lambda *args, **kwargs: (lambda x: x)
        federation = type("federation", (), {
                          "type": type, "field": lambda **kwargs: None})()
        field = lambda *args, **kwargs: None
        ID = type("ID", (), {})

from .service_resolvers import Child, Conversation, EmotionType, LearningStyle, PersonalityTrait, AIProfile, EmotionSnapshot, LearningProgress, ConversationAnalysis


@strawberry.federation.type(extend=True)
class Child:
    id: strawberry.ID = strawberry.federation.field(external=True)

    @strawberry.field
    async def ai_profile(self) -> "AIProfile":
        return AIProfile(
            personality_traits=[
                PersonalityTrait(name="Curiosity", score=0.85, confidence=0.92,
                                 description="Highly curious and eager to learn"),
                PersonalityTrait(name="Creativity", score=0.78, confidence=0.88,
                                 description="Shows strong creative thinking")
            ],
            learning_style=LearningStyle.VISUAL,
            created_at=datetime.now() - timedelta(days=30),
            last_updated=datetime.now()
        )

    @strawberry.field
    async def emotion_history(self) -> List["EmotionSnapshot"]:
        return [
            EmotionSnapshot(timestamp=datetime.now() - timedelta(minutes=30), emotion=EmotionType.HAPPY,
                            intensity=0.8, context="Playing learning game", valence=0.7, arousal=0.6),
            EmotionSnapshot(timestamp=datetime.now() - timedelta(hours=2), emotion=EmotionType.EXCITED,
                            intensity=0.9, context="Story time", valence=0.8, arousal=0.9)
        ]

    @strawberry.field
    async def learning_progress(self) -> "LearningProgress":
        return LearningProgress(current_level=12, total_xp=2450, achievements_count=15)


@strawberry.federation.type(extend=True)
class Conversation:
    id: strawberry.ID = strawberry.federation.field(external=True)
    child_id: strawberry.ID = strawberry.federation.field(external=True)

    @strawberry.field
    async def ai_analysis(self) -> "ConversationAnalysis":
        return ConversationAnalysis(sentiment=0.75, engagement=0.88, comprehension=0.82)


class AIServiceResolvers:
    @staticmethod
    async def get_ai_profile(child_id: strawberry.ID) -> Optional["AIProfile"]:
        return AIProfile(
            personality_traits=[PersonalityTrait(
                name="Empathy", score=0.72, confidence=0.85, description="Shows good emotional understanding")],
            learning_style=LearningStyle.AUDITORY,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
