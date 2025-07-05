import uuid
from datetime import datetime
from typing import List, Optional


class ChildResolver:
    """Resolvers for Child operations"""

    def __init__(self, child_repository, auth_service):
        self.child_repository = child_repository
        self.auth_service = auth_service

    async def get_child(self, id: str, info) -> Optional["Child"]:
        """Get child by ID with authorization"""
        # Check authorization
        user = await self.auth_service.get_current_user(info.context)
        if not user:
            raise Exception("Unauthorized")

        # Get child
        child = await self.child_repository.get(id)
        if not child or child.parent_id != user.id:
            return None

        return child

    async def get_children(self, parent_id: str, info) -> List["Child"]:
        """Get all children for parent"""
        user = await self.auth_service.get_current_user(info.context)
        if not user or user.id != parent_id:
            raise Exception("Unauthorized")

        return await self.child_repository.get_by_parent(parent_id)

    async def create_child(
            self,
            name: str,
            age: int,
            language: str,
            info) -> "Child":
        """Create new child profile"""
        user = await self.auth_service.get_current_user(info.context)
        if not user:
            raise Exception("Unauthorized")

        child_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "age": age,
            "language": language,
            "parent_id": user.id,
            "created_at": datetime.now(),
        }

        return await self.child_repository.create(child_data)


class ConversationResolver:
    """Resolvers for Conversation operations"""

    def __init__(self, conversation_service, auth_service):
        self.conversation_service = conversation_service
        self.auth_service = auth_service

    async def start_conversation(self, child_id: str, info) -> "Conversation":
        """Start new conversation"""
        user = await self.auth_service.get_current_user(info.context)
        if not user:
            raise Exception("Unauthorized")

        return await self.conversation_service.start_conversation(
            child_id=child_id, parent_id=user.id
        )

    async def send_message(
            self,
            conversation_id: str,
            content: str,
            info) -> "Message":
        """Send message in conversation"""
        user = await self.auth_service.get_current_user(info.context)
        if not user:
            raise Exception("Unauthorized")

        return await self.conversation_service.send_message(
            conversation_id=conversation_id, content=content, sender_id=user.id
        )
