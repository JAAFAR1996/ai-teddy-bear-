#!/usr/bin/env python3
"""
🚀 Optimized GraphQL Schema with DataLoader Pattern
Lead Architect: جعفر أديب (Jaafar Adeeb)
High-performance GraphQL with advanced caching and pagination
"""

import strawberry
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog

logger = structlog.get_logger()


# ================== GraphQL Types ==================

@strawberry.type
class Child:
    """Child entity with optimized field resolution"""
    id: strawberry.ID
    name: str
    age: int
    language: str
    parent_id: strawberry.ID
    created_at: datetime
    updated_at: Optional[datetime] = None
    profile_picture: Optional[str] = None
    is_active: bool = True
    
    @strawberry.field
    async def conversations(
        self,
        info,
        first: Optional[int] = 20,
        after: Optional[str] = None
    ) -> "ConversationConnection":
        """Get conversations for child with pagination"""
        paginator = info.context["paginators"]["conversation"]
        
        connection = await paginator.paginate(
            first=first,
            after=after,
            filters={"child_id": self.id}
        )
        
        return ConversationConnection.from_connection(connection)
    
    @strawberry.field
    async def conversation_count(self, info) -> int:
        """Get total conversation count for child"""
        # Use DataLoader to batch conversation counts
        conversation_count_loader = info.context["dataloaders"]["conversation_count"]
        return await conversation_count_loader.load(self.id)


@strawberry.type
class Message:
    """Message entity"""
    id: strawberry.ID
    conversation_id: strawberry.ID
    role: str
    content: str
    timestamp: datetime
    emotion: Optional[str] = None
    
    @strawberry.field
    async def conversation(self, info) -> Optional["Conversation"]:
        """Get conversation for message"""
        conversation_loader = info.context["dataloaders"]["conversation"]
        return await conversation_loader.load(self.conversation_id)


@strawberry.type
class Conversation:
    """Conversation entity with optimized loading"""
    id: strawberry.ID
    child_id: strawberry.ID
    title: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    message_count: int = 0
    topics: List[str] = strawberry.field(default_factory=list)
    is_active: bool = True
    
    @strawberry.field
    async def child(self, info) -> Optional[Child]:
        """Get child for conversation using DataLoader"""
        child_loader = info.context["dataloaders"]["child"]
        return await child_loader.load(self.child_id)
    
    @strawberry.field
    async def messages(
        self,
        info,
        first: Optional[int] = 50,
        after: Optional[str] = None
    ) -> "MessageConnection":
        """Get messages with pagination"""
        # Use optimized message loading
        message_paginator = info.context["paginators"]["message"]
        
        connection = await message_paginator.paginate(
            first=first,
            after=after,
            filters={"conversation_id": self.id}
        )
        
        return MessageConnection.from_connection(connection)


# ================== Connection Types ==================

@strawberry.type
class PageInfo:
    """GraphQL Relay PageInfo"""
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None
    total_count: Optional[int] = None


@strawberry.type
class ChildEdge:
    """Child connection edge"""
    node: Child
    cursor: str


@strawberry.type
class ChildConnection:
    """Child connection with pagination"""
    edges: List[ChildEdge]
    page_info: PageInfo
    total_count: Optional[int] = None
    
    @classmethod
    def from_connection(cls, connection):
        """Create from pagination connection"""
        edges = [
            ChildEdge(node=Child(**edge.node), cursor=edge.cursor)
            for edge in connection.edges
        ]
        
        return cls(
            edges=edges,
            page_info=PageInfo(
                has_next_page=connection.page_info.has_next_page,
                has_previous_page=connection.page_info.has_previous_page,
                start_cursor=connection.page_info.start_cursor,
                end_cursor=connection.page_info.end_cursor,
                total_count=connection.page_info.total_count
            ),
            total_count=connection.total_count
        )


@strawberry.type
class ConversationEdge:
    """Conversation connection edge"""
    node: Conversation
    cursor: str


@strawberry.type
class ConversationConnection:
    """Conversation connection with pagination"""
    edges: List[ConversationEdge]
    page_info: PageInfo
    total_count: Optional[int] = None
    
    @classmethod
    def from_connection(cls, connection):
        """Create from pagination connection"""
        edges = [
            ConversationEdge(node=Conversation(**edge.node), cursor=edge.cursor)
            for edge in connection.edges
        ]
        
        return cls(
            edges=edges,
            page_info=PageInfo(
                has_next_page=connection.page_info.has_next_page,
                has_previous_page=connection.page_info.has_previous_page,
                start_cursor=connection.page_info.start_cursor,
                end_cursor=connection.page_info.end_cursor,
                total_count=connection.page_info.total_count
            ),
            total_count=connection.total_count
        )


@strawberry.type
class MessageEdge:
    """Message connection edge"""
    node: Message
    cursor: str


@strawberry.type
class MessageConnection:
    """Message connection with pagination"""
    edges: List[MessageEdge]
    page_info: PageInfo
    total_count: Optional[int] = None
    
    @classmethod
    def from_connection(cls, connection):
        """Create from pagination connection"""
        edges = [
            MessageEdge(node=Message(**edge.node), cursor=edge.cursor)
            for edge in connection.edges
        ]
        
        return cls(
            edges=edges,
            page_info=PageInfo(
                has_next_page=connection.page_info.has_next_page,
                has_previous_page=connection.page_info.has_previous_page,
                start_cursor=connection.page_info.start_cursor,
                end_cursor=connection.page_info.end_cursor,
                total_count=connection.page_info.total_count
            ),
            total_count=connection.total_count
        )


# ================== Query Root ==================

@strawberry.type
class Query:
    """Optimized GraphQL Query with DataLoader pattern"""
    
    @strawberry.field
    async def child(self, info, id: strawberry.ID) -> Optional[Child]:
        """Get child by ID using DataLoader"""
        child_loader = info.context["dataloaders"]["child"]
        child_data = await child_loader.load(id)
        
        if child_data:
            return Child(**child_data)
        return None
    
    @strawberry.field
    async def children(
        self,
        info,
        parent_id: strawberry.ID,
        first: Optional[int] = 20,
        after: Optional[str] = None
    ) -> ChildConnection:
        """Get children with pagination"""
        child_paginator = info.context["paginators"]["child"]
        
        connection = await child_paginator.paginate(
            first=first,
            after=after,
            filters={"parent_id": parent_id}
        )
        
        return ChildConnection.from_connection(connection)
    
    @strawberry.field
    async def conversation(self, info, id: strawberry.ID) -> Optional[Conversation]:
        """Get conversation by ID using DataLoader"""
        conversation_loader = info.context["dataloaders"]["conversation"]
        conversation_data = await conversation_loader.load(id)
        
        if conversation_data:
            return Conversation(**conversation_data)
        return None
    
    @strawberry.field
    async def conversation_history(
        self,
        info,
        child_id: strawberry.ID,
        first: Optional[int] = 50,
        after: Optional[str] = None
    ) -> ConversationConnection:
        """Get conversation history with cursor-based pagination"""
        conversation_paginator = info.context["paginators"]["conversation"]
        
        connection = await conversation_paginator.paginate(
            first=first,
            after=after,
            filters={"child_id": child_id},
            sort_field="started_at",
            sort_direction="DESC"
        )
        
        return ConversationConnection.from_connection(connection)
    
    @strawberry.field
    async def search_conversations(
        self,
        info,
        child_id: strawberry.ID,
        query: str,
        first: Optional[int] = 20,
        after: Optional[str] = None
    ) -> ConversationConnection:
        """Search conversations with full-text search"""
        conversation_paginator = info.context["paginators"]["conversation"]
        
        connection = await conversation_paginator.paginate(
            first=first,
            after=after,
            filters={
                "child_id": child_id,
                "search_query": query
            },
            sort_field="relevance_score",
            sort_direction="DESC"
        )
        
        return ConversationConnection.from_connection(connection)


# ================== Mutation Root ==================

@strawberry.type
class Mutation:
    """GraphQL mutations with optimized data loading"""
    
         @strawberry.mutation
     async def create_child(
         self,
         info,
         name: str,
         age: int,
         parent_id: strawberry.ID,
         language: str = "ar"
     ) -> Child:
        """Create new child profile"""
        child_repository = info.context["repositories"]["child"]
        
        child_data = await child_repository.create({
            "name": name,
            "age": age,
            "language": language,
            "parent_id": parent_id
        })
        
        # Clear cache for parent's children list
        child_loader = info.context["dataloaders"]["child"]
        child_loader.clear_all()
        
        return Child(**child_data)
    
    @strawberry.mutation
    async def start_conversation(
        self,
        info,
        child_id: strawberry.ID
    ) -> Conversation:
        """Start new conversation"""
        conversation_repository = info.context["repositories"]["conversation"]
        
        conversation_data = await conversation_repository.create({
            "child_id": child_id,
            "started_at": datetime.utcnow()
        })
        
        # Clear relevant caches
        conversation_loader = info.context["dataloaders"]["conversation"]
        conversation_loader.clear_all()
        
        return Conversation(**conversation_data)
    
    @strawberry.mutation
    async def send_message(
        self,
        info,
        conversation_id: strawberry.ID,
        content: str,
        role: str = "child"
    ) -> Message:
        """Send message in conversation"""
        message_repository = info.context["repositories"]["message"]
        
        message_data = await message_repository.create({
            "conversation_id": conversation_id,
            "content": content,
            "role": role,
            "timestamp": datetime.utcnow()
        })
        
        # Update conversation message count
        conversation_repository = info.context["repositories"]["conversation"]
        await conversation_repository.increment_message_count(conversation_id)
        
        # Clear caches
        message_loader = info.context["dataloaders"]["message"]
        conversation_loader = info.context["dataloaders"]["conversation"]
        message_loader.clear_all()
        conversation_loader.clear(conversation_id)
        
        return Message(**message_data)


# ================== Schema Creation ==================

def create_optimized_schema():
    """Create optimized GraphQL schema"""
    return strawberry.Schema(
        query=Query,
        mutation=Mutation,
        extensions=[
            # Add query complexity analyzer
            # Add performance monitoring
        ]
    ) 