"""
Enhanced Memory Service Coordinator - Uses refactored components
This replaces the original God Class with a clean coordinator
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..application.services.memory.memory_storage_service import \
    MemoryStorageService
# Import refactored components
from ..domain.memory.models import (ChildMemoryProfile, Memory, MemoryImportance, MemoryType)
from ..infrastructure.memory.memory_repository import MemoryRepository
from ..infrastructure.memory.vector_memory_store import VectorMemoryStore


class MemoryService:
    """
    Memory Service Coordinator - Clean replacement for the original God Class
    Uses dependency injection and Clean Architecture principles
    """

    def __init__(self, config=None, redis_client=None):
        """Initialize memory service coordinator"""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        # Storage paths
        self.data_path = Path(getattr(self.config, "data_path", "data"))
        self.data_path.mkdir(exist_ok=True)

        # Initialize components
        self.repository = MemoryRepository(self.data_path / "memories.db")
        self.vector_store = VectorMemoryStore()
        self.storage_service = MemoryStorageService(
            self.repository, self.vector_store, redis_client
        )

        self.logger.info("Memory service coordinator initialized")

    async def initialize(self):
        """Initialize async components"""
        await self.repository.initialize()
        await self.storage_service.initialize()

        # Load existing memories into vector store
        await self._load_recent_memories()

        self.logger.info("Memory service coordinator ready")

    async def _load_recent_memories(self):
        """Load recent memories into vector store"""
        try:
            recent_memories = await self.repository.get_recent_memories(days=30)
            for memory in recent_memories:
                if memory.embedding is not None:
                    self.vector_store.add_memory(memory)

            self.logger.info(f"Loaded {len(recent_memories)} recent memories")
        except Exception as e:
            self.logger.error(f"Failed to load memories: {e}")

    async def store_interaction(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        metadata: Dict[str, Any],
    ):
        """Store an interaction in memory (delegates to storage service)"""
        await self.storage_service.store_interaction(
            session_id, user_message, ai_response, metadata
        )

    async def recall_memories(
        self,
        child_id: str,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 5,
    ) -> List[Memory]:
        """Recall relevant memories for a child"""
        try:
            # Get from working memory first
            working_memories = self.storage_service.get_working_memory(child_id)

            # Filter by query
            relevant_memories = []
            for memory in working_memories:
                if query.lower() in memory.content.lower():
                    memory.access()  # Update access count
                    relevant_memories.append(memory)

            # If we need more, search vector store
            if len(relevant_memories) < limit:
                # In a full implementation, we'd use sentence transformer here
                # For now, return what we have
                pass

            return relevant_memories[:limit]

        except Exception as e:
            self.logger.error(f"Failed to recall memories: {e}")
            return []

    async def get_conversation_context(
        self, child_id: str, include_summary: bool = True
    ) -> Dict[str, Any]:
        """Get conversation context from memory"""
        try:
            # Get recent memories from storage service
            short_term = self.storage_service.get_short_term_buffer(child_id)
            working_mem = self.storage_service.get_working_memory(child_id)

            # Extract topics and emotions
            all_topics = []
            all_emotions = []

            for memory in short_term + working_mem:
                all_topics.extend(memory.topics)
                all_emotions.extend(memory.emotions)

            # Build context
            context = {
                "recent_topics": list(set(all_topics))[:5],
                "emotional_state": list(set(all_emotions))[-3:],
                "memory_count": len(short_term) + len(working_mem),
                "summary": None,
            }

            if include_summary and (short_term or working_mem):
                context["summary"] = "Recent conversation context available"

            return context

        except Exception as e:
            self.logger.error(f"Failed to get conversation context: {e}")
            return {}

    async def get_child_profile(self, child_id: str) -> Optional[ChildMemoryProfile]:
        """Get child memory profile"""
        return await self.repository.get_child_profile(child_id)

    async def update_child_profile(
        self, child_id: str, interaction_data: Dict[str, Any]
    ):
        """Update child profile with new interaction data"""
        try:
            profile = await self.get_child_profile(child_id)

            if not profile:
                # Create new profile
                profile = ChildMemoryProfile(
                    child_id=child_id,
                    name=interaction_data.get("name", "Unknown"),
                    age=interaction_data.get("age", 8),
                    total_interactions=0,
                    first_interaction=datetime.now(),
                    last_interaction=datetime.now(),
                )

            # Update profile
            profile.add_interaction()

            # Update preferences if provided
            if "topics" in interaction_data:
                for topic in interaction_data["topics"]:
                    profile.update_topic_preference(topic, 1.0)

            # Save updated profile
            await self.repository.save_child_profile(profile)

        except Exception as e:
            self.logger.error(f"Failed to update child profile: {e}")

    async def forget_memories(
        self,
        child_id: str,
        older_than_days: Optional[int] = None,
        importance_threshold: Optional[MemoryImportance] = None,
    ) -> int:
        """Forget old or unimportant memories (delegates to storage service)"""
        return await self.storage_service.forget_memories(
            child_id, older_than_days, importance_threshold
        )

    async def export_memories(
        self, child_id: str, format: str = "json"
    ) -> Optional[str]:
        """Export memories for a child"""
        try:
            memories = await self.repository.get_memories_by_child(child_id)

            if format == "json":
                import json

                export_data = {
                    "child_id": child_id,
                    "export_date": datetime.now().isoformat(),
                    "total_memories": len(memories),
                    "memories": [
                        {
                            "id": m.id,
                            "content": m.content,
                            "type": m.memory_type.value,
                            "importance": m.importance.value,
                            "timestamp": m.timestamp.isoformat(),
                            "topics": m.topics,
                            "emotions": m.emotions,
                        }
                        for m in memories
                    ],
                }
                return json.dumps(export_data, indent=2)

            return None

        except Exception as e:
            self.logger.error(f"Failed to export memories: {e}")
            return None

    async def close(self):
        """Close the memory service and cleanup"""
        await self.storage_service.close()
        await self.repository.close()
        self.logger.info("Memory service coordinator closed")


# Utility functions preserved from original
def calculate_memory_similarity(memory1: Memory, memory2: Memory) -> float:
    """Calculate similarity between two memories"""
    # Simple similarity based on shared topics and emotions
    shared_topics = set(memory1.topics) & set(memory2.topics)
    shared_emotions = set(memory1.emotions) & set(memory2.emotions)

    topic_sim = len(shared_topics) / max(len(memory1.topics) + len(memory2.topics), 1)
    emotion_sim = len(shared_emotions) / max(
        len(memory1.emotions) + len(memory2.emotions), 1
    )

    return (topic_sim + emotion_sim) / 2


def generate_memory_graph(
    memories: List[Memory], threshold: float = 0.5
) -> Dict[str, List[str]]:
    """Generate a graph of related memories"""
    graph = {}

    for i, memory1 in enumerate(memories):
        related = []
        for j, memory2 in enumerate(memories):
            if i != j:
                similarity = calculate_memory_similarity(memory1, memory2)
                if similarity >= threshold:
                    related.append(memory2.id)

        graph[memory1.id] = related

    return graph
