"""
Enhanced Memory Service Coordinator - Uses refactored components
This replaces the original God Class with a clean coordinator
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..application.services.memory.memory_storage_service import MemoryStorageService

# Import refactored components
from ..domain.memory.models import (
    ChildMemoryProfile,
    Memory,
    MemoryImportance,
    MemoryType,
)
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

    def _memory_matches_query(self, memory: Memory, query: str) -> bool:
        """Check if a memory matches the search query"""
        return query.lower() in memory.content.lower()

    def _filter_memories_by_query(
        self, memories: List[Memory], query: str
    ) -> List[Memory]:
        """Filter memories that match the query and update access count"""
        relevant_memories = []

        for memory in memories:
            if self._memory_matches_query(memory, query):
                memory.access()  # Update access count
                relevant_memories.append(memory)

        return relevant_memories

    def _apply_memory_limit(
            self,
            memories: List[Memory],
            limit: int) -> List[Memory]:
        """Apply limit to the number of memories returned"""
        return memories[:limit]

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
            working_memories = self.storage_service.get_working_memory(
                child_id)

            # Filter memories by query
            relevant_memories = self._filter_memories_by_query(
                working_memories, query)

            # If we need more memories, search vector store
            if len(relevant_memories) < limit:
                # In a full implementation, we'd use sentence transformer here
                # For now, return what we have
                pass

            # Apply limit and return
            return self._apply_memory_limit(relevant_memories, limit)

        except Exception as e:
            self.logger.error(f"Failed to recall memories: {e}")
            return []

    def _extract_topics_from_memories(
            self, memories: List[Memory]) -> List[str]:
        """Extract unique topics from a list of memories"""
        all_topics = []
        for memory in memories:
            all_topics.extend(memory.topics)
        return list(set(all_topics))[:5]  # Return top 5 unique topics

    def _extract_emotions_from_memories(
            self, memories: List[Memory]) -> List[str]:
        """Extract recent emotions from a list of memories"""
        all_emotions = []
        for memory in memories:
            all_emotions.extend(memory.emotions)
        return list(set(all_emotions))[-3:]  # Return last 3 unique emotions

    def _has_memories_for_summary(
        self, short_term: List[Memory], working_mem: List[Memory]
    ) -> bool:
        """Check if there are enough memories to generate a summary"""
        return bool(short_term or working_mem)

    def _create_conversation_summary(
            self, has_memories: bool) -> Optional[str]:
        """Create a conversation summary if memories exist"""
        if has_memories:
            return "Recent conversation context available"
        return None

    async def get_conversation_context(
        self, child_id: str, include_summary: bool = True
    ) -> Dict[str, Any]:
        """Get conversation context from memory"""
        try:
            # Get recent memories from storage service
            short_term = self.storage_service.get_short_term_buffer(child_id)
            working_mem = self.storage_service.get_working_memory(child_id)

            # Combine all memories for processing
            all_memories = short_term + working_mem

            # Extract topics and emotions using helper methods
            recent_topics = self._extract_topics_from_memories(all_memories)
            emotional_state = self._extract_emotions_from_memories(
                all_memories)

            # Check if we have memories for summary
            has_memories = self._has_memories_for_summary(
                short_term, working_mem)

            # Build context
            context = {
                "recent_topics": recent_topics,
                "emotional_state": emotional_state,
                "memory_count": len(all_memories),
                "summary": None,
            }

            # Add summary if requested and available
            if include_summary:
                context["summary"] = self._create_conversation_summary(
                    has_memories)

            return context

        except Exception as e:
            self.logger.error(f"Failed to get conversation context: {e}")
            return {}

    async def get_child_profile(
            self, child_id: str) -> Optional[ChildMemoryProfile]:
        """Get child memory profile"""
        return await self.repository.get_child_profile(child_id)

    def _create_new_child_profile(
        self, child_id: str, interaction_data: Dict[str, Any]
    ) -> ChildMemoryProfile:
        """Create a new child profile with default values"""
        return ChildMemoryProfile(
            child_id=child_id,
            name=interaction_data.get("name", "Unknown"),
            age=interaction_data.get("age", 8),
            total_interactions=0,
            first_interaction=datetime.now(),
            last_interaction=datetime.now(),
        )

    def _update_topic_preferences(
        self, profile: ChildMemoryProfile, interaction_data: Dict[str, Any]
    ):
        """Update topic preferences in the profile"""
        topics = interaction_data.get("topics", [])
        for topic in topics:
            profile.update_topic_preference(topic, 1.0)

    async def update_child_profile(
        self, child_id: str, interaction_data: Dict[str, Any]
    ):
        """Update child profile with new interaction data"""
        try:
            profile = await self.get_child_profile(child_id)

            # Create new profile if it doesn't exist
            if not profile:
                profile = self._create_new_child_profile(
                    child_id, interaction_data)

            # Update interaction count
            profile.add_interaction()

            # Update topic preferences if provided
            self._update_topic_preferences(profile, interaction_data)

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

    topic_sim = len(shared_topics) / \
        max(len(memory1.topics) + len(memory2.topics), 1)
    emotion_sim = len(shared_emotions) / max(
        len(memory1.emotions) + len(memory2.emotions), 1
    )

    return (topic_sim + emotion_sim) / 2


def _is_memory_pair_similar(
        memory1: Memory,
        memory2: Memory,
        threshold: float) -> bool:
    """Check if two memories are similar enough to be related"""
    similarity = calculate_memory_similarity(memory1, memory2)
    return similarity >= threshold


def _find_related_memories(
    target_memory: Memory, all_memories: List[Memory], threshold: float
) -> List[str]:
    """Find all memories related to a target memory"""
    related_ids = []

    for candidate_memory in all_memories:
        if target_memory.id == candidate_memory.id:
            continue

        if _is_memory_pair_similar(target_memory, candidate_memory, threshold):
            related_ids.append(candidate_memory.id)

    return related_ids


def generate_memory_graph(
    memories: List[Memory], threshold: float = 0.5
) -> Dict[str, List[str]]:
    """Generate a graph of related memories"""
    # Early return for empty input
    if not memories:
        return {}

    # Early return for single memory
    if len(memories) == 1:
        return {memories[0].id: []}

    graph = {}

    for memory in memories:
        related_ids = _find_related_memories(memory, memories, threshold)
        graph[memory.id] = related_ids

    return graph
