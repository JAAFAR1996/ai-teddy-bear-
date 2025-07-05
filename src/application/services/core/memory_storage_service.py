"""
Memory Storage Service - Handles memory persistence and organization
"""

import asyncio
import logging
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Optional

from ....domain.memory.models import Memory, MemoryImportance, MemoryType
from ....infrastructure.memory.memory_repository import MemoryRepository
from ....infrastructure.memory.vector_memory_store import VectorMemoryStore


class MemoryStorageService:
    """Service for storing and managing memories"""

    def __init__(
        self,
        repository: MemoryRepository,
        vector_store: VectorMemoryStore,
        redis_client=None,
    ):
        self.repository = repository
        self.vector_store = vector_store
        self.redis_client = redis_client
        self.logger = logging.getLogger(self.__class__.__name__)

        # Memory buffers
        self.short_term_buffer: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=50))
        self.working_memory: Dict[str, List[Memory]] = defaultdict(list)

        # Background consolidation
        self.consolidation_task = None

    async def initialize(self) -> None:
        """Initialize the storage service"""
        # Start consolidation task
        self.consolidation_task = asyncio.create_task(
            self._consolidation_loop())
        self.logger.info("Memory storage service initialized")

    async def store_interaction(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        metadata: Dict[str, any],
    ) -> None:
        """Store an interaction in memory"""
        try:
            child_id = metadata.get("child_id")
            if not child_id:
                return

            # Create memory content
            content = f"User: {user_message}\nAssistant: {ai_response}"

            # Determine importance
            importance = self._calculate_importance(
                user_message, ai_response, metadata)

            # Extract topics (simplified)
            topics = self._extract_topics(content)

            # Create memory
            memory = Memory(
                id=f"{session_id}_{datetime.now().timestamp()}",
                child_id=child_id,
                content=content,
                memory_type=MemoryType.EPISODIC,
                importance=importance,
                timestamp=datetime.now(),
                context=metadata,
                emotions=metadata.get("emotions", []),
                topics=topics,
            )

            # Store in different memory layers
            await self._store_short_term(memory)
            await self._update_working_memory(child_id, memory)

            # Store important memories long-term
            if importance.value >= MemoryImportance.MEDIUM.value:
                await self._store_long_term(memory)

        except Exception as e:
            self.logger.error(f"Failed to store interaction: {e}")

    async def _store_short_term(self, memory: Memory) -> None:
        """Store in short-term memory buffer"""
        self.short_term_buffer[memory.child_id].append(memory)

        # Cache in Redis for fast access
        if self.redis_client:
            import json

            key = f"stm:{memory.child_id}:{memory.id}"
            await self.redis_client.setex(
                key,
                3600,  # 1 hour TTL
                json.dumps(
                    {
                        "content": memory.content,
                        "topics": memory.topics,
                        "emotions": memory.emotions,
                    }
                ),
            )

    async def _update_working_memory(
            self, child_id: str, memory: Memory) -> None:
        """Update working memory with recent context"""
        working_mem = self.working_memory[child_id]

        # Keep last 10 memories in working memory
        working_mem.append(memory)
        if len(working_mem) > 10:
            working_mem.pop(0)

    async def _store_long_term(self, memory: Memory) -> None:
        """Store in long-term memory"""
        try:
            # Add to vector store if embedding exists
            if memory.embedding is not None:
                self.vector_store.add_memory(memory)

            # Store in database
            await self.repository.save_memory(memory)

        except Exception as e:
            self.logger.error(f"Failed to store long-term memory: {e}")

    async def _consolidation_loop(self) -> None:
        """Background task for memory consolidation"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._consolidate_memories()
            except Exception as e:
                self.logger.error(f"Memory consolidation error: {e}")

    async def _consolidate_memories(self) -> None:
        """Consolidate memories by finding patterns and relationships"""
        try:
            # Get recent memories for consolidation
            recent_memories = await self.repository.get_recent_memories(days=1)

            if len(recent_memories) < 10:
                return

            # Group by topics and find patterns
            topic_groups = defaultdict(list)
            for memory in recent_memories:
                for topic in memory.topics:
                    topic_groups[topic].append(memory)

            # Consolidate memories within topics
            for topic, memories in topic_groups.items():
                if len(memories) >= 3:
                    await self._consolidate_topic_memories(topic, memories)

        except Exception as e:
            self.logger.error(f"Memory consolidation failed: {e}")

    async def _consolidate_topic_memories(
        self, topic: str, memories: List[Memory]
    ) -> None:
        """Consolidate memories around a specific topic"""
        try:
            # Create a consolidated memory for this topic
            contents = [m.content for m in memories]
            combined_content = f"Topic: {topic}\nConsolidated memories: " + \
                "; ".join(contents[:3])

            consolidated_memory = Memory(
                id=f"consolidated_{topic}_{datetime.now().timestamp()}",
                child_id=memories[0].child_id,
                content=combined_content,
                memory_type=MemoryType.SEMANTIC,
                importance=MemoryImportance.MEDIUM,
                timestamp=datetime.now(),
                topics=[topic],
                related_memories=[m.id for m in memories],
            )

            await self._store_long_term(consolidated_memory)
            self.logger.info(
                f"Consolidated {len(memories)} memories for topic: {topic}"
            )

        except Exception as e:
            self.logger.error(f"Failed to consolidate topic memories: {e}")

    def _calculate_importance(
        self, user_message: str, ai_response: str, metadata: Dict[str, any]
    ) -> MemoryImportance:
        """Calculate importance of an interaction"""
        # Safety keywords = critical
        safety_keywords = ["help", "scared", "hurt", "emergency", "danger"]
        if any(keyword in user_message.lower() for keyword in safety_keywords):
            return MemoryImportance.CRITICAL

        # Learning keywords = high
        learning_keywords = ["learn", "teach", "how", "why", "what"]
        if any(keyword in user_message.lower()
               for keyword in learning_keywords):
            return MemoryImportance.HIGH

        # Emotional content = medium
        if metadata.get("emotions"):
            return MemoryImportance.MEDIUM

        # Regular conversation = low
        return MemoryImportance.LOW

    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content (simplified approach)"""
        # This is a simplified topic extraction
        # In production, you'd use NLP techniques
        common_topics = {
            "story": ["story", "tale", "once upon"],
            "math": ["number", "count", "add", "subtract"],
            "science": ["how", "why", "experiment"],
            "emotion": ["feel", "happy", "sad", "angry"],
            "family": ["mom", "dad", "brother", "sister"],
            "animals": ["dog", "cat", "bird", "animal"],
            "colors": ["red", "blue", "green", "yellow"],
            "toys": ["toy", "play", "game"],
        }

        topics = []
        content_lower = content.lower()

        for topic, keywords in common_topics.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def get_working_memory(self, child_id: str) -> List[Memory]:
        """Get working memory for a child"""
        return self.working_memory.get(child_id, [])

    def get_short_term_buffer(self, child_id: str) -> List[Memory]:
        """Get short-term memory buffer for a child"""
        return list(self.short_term_buffer.get(child_id, []))

    async def forget_memories(
        self,
        child_id: str,
        older_than_days: Optional[int] = None,
        importance_threshold: Optional[MemoryImportance] = None,
    ) -> int:
        """Forget old or unimportant memories"""
        try:
            # Get memories to potentially forget
            all_memories = await self.repository.get_memories_by_child(child_id)

            forgotten_count = 0
            for memory in all_memories:
                should_forget = False

                # Check age criteria
                if older_than_days:
                    age_days = (datetime.now() - memory.timestamp).days
                    if age_days > older_than_days:
                        should_forget = True

                # Check importance criteria
                if importance_threshold:
                    if memory.importance.value < importance_threshold.value:
                        should_forget = True

                # Don't forget critical memories or very recent ones
                recent_days = (datetime.now() - memory.timestamp).days
                if memory.importance == MemoryImportance.CRITICAL or recent_days < 1:
                    should_forget = False

                if should_forget:
                    await self.repository.delete_memory(memory.id)
                    forgotten_count += 1

            self.logger.info(
                f"Forgotten {forgotten_count} memories for child {child_id}"
            )
            return forgotten_count

        except Exception as e:
            self.logger.error(f"Failed to forget memories: {e}")
            return 0

    async def close(self) -> None:
        """Close the service and cleanup"""
        if self.consolidation_task:
            self.consolidation_task.cancel()
            try:
                await self.consolidation_task
            except asyncio.CancelledError:
                pass
