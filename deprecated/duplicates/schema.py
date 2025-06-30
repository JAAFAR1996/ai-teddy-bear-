import strawberry
from typing import List, Optional
from datetime import datetime
import uuid

@strawberry.type
class Child:
    id: str
    name: str
    age: int
    language: str
    created_at: datetime

@strawberry.type
class Message:
    id: str
    role: str
    content: str
    timestamp: datetime
    emotion: Optional[str] = None

@strawberry.type
class Conversation:
    id: str
    child_id: str
    messages: List[Message]
    started_at: datetime

@strawberry.type
class Query:
    @strawberry.field
    async def child(self, id: str) -> Optional[Child]:
        """Get child by ID"""
        # Mock implementation
        return Child(
            id=id,
            name="Test Child",
            age=6,
            language="ar",
            created_at=datetime.now()
        )
    
    @strawberry.field
    async def children(self, parent_id: str) -> List[Child]:
        """Get all children for parent"""
        # Mock implementation
        return [
            Child(
                id=str(uuid.uuid4()),
                name="Ahmed",
                age=7,
                language="ar",
                created_at=datetime.now()
            ),
            Child(
                id=str(uuid.uuid4()),
                name="Fatima",
                age=5,
                language="ar",
                created_at=datetime.now()
            )
        ]
    
    @strawberry.field
    async def conversation(self, id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        return Conversation(
            id=id,
            child_id="child-123",
            messages=[
                Message(
                    id=str(uuid.uuid4()),
                    role="child",
                    content="مرحبا",
                    timestamp=datetime.now(),
                    emotion="happy"
                ),
                Message(
                    id=str(uuid.uuid4()),
                    role="assistant",
                    content="مرحبا بك يا صديقي!",
                    timestamp=datetime.now(),
                    emotion="friendly"
                )
            ],
            started_at=datetime.now()
        )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_child(
        self,
        name: str,
        age: int,
        language: str = "ar"
    ) -> Child:
        """Create new child profile"""
        return Child(
            id=str(uuid.uuid4()),
            name=name,
            age=age,
            language=language,
            created_at=datetime.now()
        )
    
    @strawberry.mutation
    async def start_conversation(
        self,
        child_id: str
    ) -> Conversation:
        """Start new conversation"""
        return Conversation(
            id=str(uuid.uuid4()),
            child_id=child_id,
            messages=[],
            started_at=datetime.now()
        )
    
    @strawberry.mutation
    async def send_message(
        self,
        conversation_id: str,
        content: str
    ) -> Message:
        """Send message in conversation"""
        return Message(
            id=str(uuid.uuid4()),
            role="child",
            content=content,
            timestamp=datetime.now(),
            emotion="neutral"
        )

schema = strawberry.Schema(query=Query, mutation=Mutation)