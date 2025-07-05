from typing import List, Optional
from datetime import datetime
import uuid

try:
    import strawberry
    from strawberry.federation import Key
except ImportError:
    # Mocking for environments without strawberry
    class strawberry:
        ID = type("ID", (), {})
        def enum(x): return x
        type = lambda *args, **kwargs: (lambda x: x)
        federation = type("federation", (), {
                          "type": type, "field": lambda **kwargs: None})()
        field = lambda *args, **kwargs: None

from .service_resolvers import ContentFilterLevel, DifficultyLevel, SafetySettings, ChildPreferences, Conversation


@strawberry.federation.type(keys=["id"])
class Child:
    id: strawberry.ID
    name: str
    age: int
    language: str
    parent_id: strawberry.ID
    created_at: datetime
    updated_at: datetime
    profile_picture: Optional[str] = None
    is_active: bool = True

    @strawberry.field
    async def safety_settings(self) -> SafetySettings:
        return SafetySettings(max_daily_usage=120, content_filtering=ContentFilterLevel.MODERATE, is_active=True)

    @strawberry.field
    async def preferences(self) -> ChildPreferences:
        return ChildPreferences(
            favorite_topics=["animals", "space", "stories"],
            learning_goals=["reading", "math", "creativity"],
            difficulty_level=DifficultyLevel.BEGINNER
        )

    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        return Child(id=id, name=f"Child {id}", age=6, language="ar", parent_id="parent-123", created_at=datetime.now(), updated_at=datetime.now())


class ChildServiceResolvers:
    @staticmethod
    async def get_child(id: strawberry.ID) -> Optional[Child]:
        return Child(id=id, name="Ahmed", age=7, language="ar", parent_id="parent-123", created_at=datetime.now(), updated_at=datetime.now())

    @staticmethod
    async def get_children(parent_id: strawberry.ID) -> List[Child]:
        return [
            Child(id=str(uuid.uuid4()), name="Fatima", age=5, language="ar",
                  parent_id=parent_id, created_at=datetime.now(), updated_at=datetime.now()),
            Child(id=str(uuid.uuid4()), name="Omar", age=8, language="ar",
                  parent_id=parent_id, created_at=datetime.now(), updated_at=datetime.now()),
        ]
