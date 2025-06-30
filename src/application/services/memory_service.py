# memory_service.py - Enhanced memory service with cognitive capabilities
import os
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import sqlite3
import aiosqlite
import redis.asyncio as aioredis
import numpy as np
from collections import defaultdict, deque
import pickle
from pathlib import Path

import openai
from sentence_transformers import SentenceTransformer
import faiss
from sklearn.cluster import DBSCAN
import torch
from transformers import pipeline

from src.infrastructure.config import Settings
from src.domain.entities.conversation import Conversation, Message
from src.domain.entities.child import Child


class MemoryType(Enum):
    """Types of memory storage"""
    SHORT_TERM = "short_term"      # Current session
    WORKING = "working"            # Active context (last few interactions)
    LONG_TERM = "long_term"        # Persistent memories
    EPISODIC = "episodic"          # Specific events/experiences
    SEMANTIC = "semantic"          # Facts and knowledge
    EMOTIONAL = "emotional"        # Emotional associations
    PROCEDURAL = "procedural"      # How to do things


class MemoryImportance(Enum):
    """Importance levels for memories"""
    CRITICAL = 5    # Never forget (safety, important facts)
    HIGH = 4        # Important memories (learning milestones)
    MEDIUM = 3      # Regular interactions
    LOW = 2         # Casual conversations
    TRIVIAL = 1     # Can be forgotten


@dataclass
class Memory:
    """Individual memory unit"""
    id: str
    child_id: str
    content: str
    memory_type: MemoryType
    importance: MemoryImportance
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    emotions: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    decay_rate: float = 0.1  # How fast the memory fades

    def access(self) -> Any:
        """Update access information"""
        self.access_count += 1
        self.last_accessed = datetime.now()

    def get_strength(self) -> float:
        """Calculate memory strength based on recency and access"""
        if not self.last_accessed:
            self.last_accessed = self.timestamp

        # Time decay
        days_old = (datetime.now() - self.timestamp).days
        time_factor = np.exp(-self.decay_rate * days_old)

        # Access reinforcement
        access_factor = min(1.0, self.access_count / 10)

        # Importance factor
        importance_factor = self.importance.value / 5

        return (time_factor * 0.4 + access_factor * 0.3 + importance_factor * 0.3)


@dataclass
class ConversationSummary:
    """Summary of a conversation session"""
    session_id: str
    child_id: str
    start_time: datetime
    end_time: datetime
    message_count: int
    topics_discussed: List[str]
    emotional_journey: List[Tuple[datetime, str]]  # (timestamp, emotion)
    key_learnings: List[str]
    memorable_moments: List[str]
    overall_sentiment: float
    engagement_level: float


@dataclass
class ChildMemoryProfile:
    """Complete memory profile for a child"""
    child_id: str
    name: str
    age: int
    total_interactions: int
    first_interaction: datetime
    last_interaction: datetime

    # Preferences learned over time
    favorite_topics: Dict[str, float] = field(default_factory=dict)
    favorite_activities: List[str] = field(default_factory=list)
    favorite_stories: List[str] = field(default_factory=list)

    # Learning progress
    concepts_learned: Dict[str, datetime] = field(default_factory=dict)
    skills_developed: Dict[str, float] = field(default_factory=dict)
    vocabulary_growth: List[Tuple[str, datetime]] = field(default_factory=list)

    # Emotional patterns
    emotional_triggers: Dict[str, List[str]] = field(default_factory=dict)
    comfort_strategies: List[str] = field(default_factory=list)

    # Behavioral patterns
    interaction_patterns: Dict[str, Any] = field(default_factory=dict)
    attention_span_minutes: float = 10.0
    preferred_interaction_style: str = "conversational"


class VectorMemoryStore:
    """Vector-based memory storage for semantic search"""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.memories: Dict[int, Memory] = {}
        self.current_idx = 0

    def add_memory(self, memory -> Any: Memory) -> Any:
        """Add memory with embedding to vector store"""
        if memory.embedding is not None:
            self.index.add(memory.embedding.reshape(1, -1))
            self.memories[self.current_idx] = memory
            self.current_idx += 1

    def search_similar(self, query_embedding: np.ndarray, k: int = 5) -> List[Memory]:
        """Search for similar memories"""
        if self.index.ntotal == 0:
            return []

        distances, indices = self.index.search(
            query_embedding.reshape(1, -1), min(k, self.index.ntotal))

        similar_memories = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx != -1:  # Valid index
                memory = self.memories[idx]
                similar_memories.append(memory)

        return similar_memories

    def cluster_memories(self, min_samples: int = 3) -> Dict[int, List[Memory]]:
        """Cluster memories by similarity"""
        if self.index.ntotal < min_samples:
            return {}

        # Get all embeddings
        embeddings = []
        memory_list = []

        for idx, memory in self.memories.items():
            if memory.embedding is not None:
                embeddings.append(memory.embedding)
                memory_list.append(memory)

        if not embeddings:
            return {}

        # Cluster using DBSCAN
        embeddings_array = np.array(embeddings)
        clustering = DBSCAN(eps=0.5, min_samples=min_samples).fit(
            embeddings_array)

        # Group memories by cluster
        clusters = defaultdict(list)
        for memory, label in zip(memory_list, clustering.labels_):
            clusters[label].append(memory)

        return dict(clusters)


class MemoryService:
    """
    Enhanced memory service with cognitive capabilities
    """

    def __init__(self, config=None, redis_client=None, *args, **kwargs):
        """Initialize memory service"""
        if config is None:
            import json
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(
                base_dir, '..', '..', 'config', 'default_config.json')
            config_path = os.path.normpath(config_path)

            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.redis_client = redis_client
        # Storage paths
        self.data_path = Path(getattr(self.config, "data_path", "data"))
        self.data_path.mkdir(exist_ok=True)

        # SQLite for structured data
        self.db_path = self.data_path / 'memories.db'
        self.db_conn = None

        # Redis for fast access
        if hasattr(self.config, 'database'):
            self.redis_url = getattr(self.config.database, 'REDIS_URL', None)
        else:
            self.redis_url = getattr(self.config, 'REDIS_URL', None)

        # Vector store for semantic search
        self.vector_store = VectorMemoryStore()

        # Sentence transformer for embeddings
        try:
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Loaded sentence transformer model")
        except Exception as e:
            self.logger.warning(f"Failed to load sentence transformer: {e}")
            self.sentence_transformer = None

        # Summarization model
            try:
                # Get token from environment or config (prefer environment)
                hf_token = (
                    os.environ.get("HUGGINGFACE_TOKEN") or
                    os.environ.get("HUGGINGFACE_API_KEY") or
                    (getattr(getattr(self.config, "api_keys", None), "HUGGINGFACE_API_KEY", None) if self.config else None)
                )

                if hf_token:
                    self.summarizer = pipeline(
                        "summarization",
                        model="facebook/bart-large-cnn",
                        token=hf_token   # use use_auth_token for older versions
                    )
                else:
                    self.summarizer = pipeline(
                        "summarization",
                        model="facebook/bart-large-cnn"
                    )

                self.logger.info("Loaded summarizer model")
            except Exception as e:
                self.logger.warning(f"Failed to load summarizer: {e}")
                self.summarizer = None

        # Memory buffers
        self.short_term_buffer: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=50))
        self.working_memory: Dict[str, List[Memory]] = defaultdict(list)

        # Child profiles cache
        self.child_profiles: Dict[str, ChildMemoryProfile] = {}

        # Memory consolidation task
        self.consolidation_task = None

    async def initialize(self):
        """Initialize async components"""
        # Initialize database
        await self._init_database()

        # Initialize Redis
        if self.redis_url:
            try:
                self.redis_client = await aioredis.from_url(self.redis_url)
                await self.redis_client.ping()
                self.logger.info("Connected to Redis")
            except Exception as e:
                self.logger.warning(f"Redis connection failed: {e}")
                self.redis_client = None

        # Load existing memories
        await self._load_memories()

        # Start memory consolidation task
        self.consolidation_task = asyncio.create_task(
            self._consolidation_loop())

        self.logger.info("Memory service initialized")

    async def _init_database(self):
        """Initialize SQLite database"""
        self.db_conn = await aiosqlite.connect(str(self.db_path))

        # Create tables
        await self.db_conn.executescript("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            child_id TEXT NOT NULL,
            content TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            importance INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            context TEXT,
            embedding BLOB,
            emotions TEXT,
            topics TEXT,
            related_memories TEXT,
            access_count INTEGER DEFAULT 0,
            last_accessed DATETIME,
            decay_rate REAL DEFAULT 0.1
        );
        
        CREATE TABLE IF NOT EXISTS conversation_summaries (
            session_id TEXT PRIMARY KEY,
            child_id TEXT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            message_count INTEGER,
            topics_discussed TEXT,
            emotional_journey TEXT,
            key_learnings TEXT,
            memorable_moments TEXT,
            overall_sentiment REAL,
            engagement_level REAL
        );
        
        CREATE TABLE IF NOT EXISTS child_profiles (
            child_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            total_interactions INTEGER DEFAULT 0,
            first_interaction DATETIME,
            last_interaction DATETIME,
            favorite_topics TEXT,
            favorite_activities TEXT,
            favorite_stories TEXT,
            concepts_learned TEXT,
            skills_developed TEXT,
            vocabulary_growth TEXT,
            emotional_triggers TEXT,
            comfort_strategies TEXT,
            interaction_patterns TEXT,
            attention_span_minutes REAL DEFAULT 10.0,
            preferred_interaction_style TEXT DEFAULT 'conversational'
        );
        
        CREATE INDEX IF NOT EXISTS idx_memories_child_id ON memories(child_id);
        CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp);
        CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
        """)

        await self.db_conn.commit()

    async def _load_memories(self):
        """Load memories from database"""
        try:
            # Load recent memories into vector store
            cursor = await self.db_conn.execute("""
                SELECT * FROM memories 
                WHERE timestamp > datetime('now', '-30 days')
                ORDER BY importance DESC, timestamp DESC
                LIMIT 1000
            """)

            rows = await cursor.fetchall()

            for row in rows:
                memory = self._row_to_memory(row)
                if memory.embedding is not None:
                    self.vector_store.add_memory(memory)

            self.logger.info(f"Loaded {len(rows)} recent memories")

        except Exception as e:
            self.logger.error(f"Failed to load memories: {e}")

    async def _consolidation_loop(self):
        """Background task for memory consolidation"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._consolidate_memories()
            except Exception as e:
                self.logger.error(f"Memory consolidation error: {e}")

    async def store_interaction(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        metadata: Dict[str, Any]
    ):
        """Store an interaction in memory"""
        try:
            child_id = metadata.get('child_id')
            if not child_id:
                return

            # Create memory content
            content = f"User: {user_message}\nAssistant: {ai_response}"

            # Determine importance
            importance = self._calculate_importance(
                user_message, ai_response, metadata)

            # Extract topics
            topics = self._extract_topics(content)

            # Create embedding
            embedding = None
            if self.sentence_transformer:
                embedding = self.sentence_transformer.encode(content)

            # Create memory
            memory = Memory(
                id=f"{session_id}_{datetime.now().timestamp()}",
                child_id=child_id,
                content=content,
                memory_type=MemoryType.EPISODIC,
                importance=importance,
                timestamp=datetime.now(),
                context=metadata,
                embedding=embedding,
                emotions=metadata.get('emotions', []),
                topics=topics
            )

            # Store in different memory layers
            await self._store_short_term(memory)
            await self._update_working_memory(child_id, memory)

            # Store important memories long-term
            if importance.value >= MemoryImportance.MEDIUM.value:
                await self._store_long_term(memory)

        except Exception as e:
            self.logger.error(f"Failed to store interaction: {e}")

    async def _store_short_term(self, memory: Memory):
        """Store in short-term memory buffer"""
        self.short_term_buffer[memory.child_id].append(memory)

        # Cache in Redis for fast access
        if self.redis_client:
            key = f"stm:{memory.child_id}:{memory.id}"
            await self.redis_client.setex(
                key,
                3600,  # 1 hour TTL
                json.dumps({
                    'content': memory.content,
                    'topics': memory.topics,
                    'emotions': memory.emotions
                })
            )

    async def _update_working_memory(self, child_id: str, memory: Memory):
        """Update working memory with recent context"""
        working_mem = self.working_memory[child_id]

        # Keep last 10 memories in working memory
        working_mem.append(memory)
        if len(working_mem) > 10:
            working_mem.pop(0)

        # Find related memories
        if memory.embedding is not None:
            similar = self.vector_store.search_similar(memory.embedding, k=3)
            memory.related_memories = [
                m.id for m in similar if m.id != memory.id]

    async def _store_long_term(self, memory: Memory):
        """Store in long-term memory"""
        try:
            # Add to vector store
            if memory.embedding is not None:
                self.vector_store.add_memory(memory)

            # Store in database
            await self.db_conn.execute("""
                INSERT INTO memories 
                (id, child_id, content, memory_type, importance, timestamp, 
                 context, embedding, emotions, topics, related_memories, 
                 access_count, last_accessed, decay_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.child_id,
                memory.content,
                memory.memory_type.value,
                memory.importance.value,
                memory.timestamp,
                json.dumps(memory.context),
                pickle.dumps(
                    memory.embedding) if memory.embedding is not None else None,
                json.dumps(memory.emotions),
                json.dumps(memory.topics),
                json.dumps(memory.related_memories),
                memory.access_count,
                memory.last_accessed,
                memory.decay_rate
            ))

            await self.db_conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to store long-term memory: {e}")

    async def recall_memories(
        self,
        child_id: str,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 5
    ) -> List[Memory]:
        """Recall relevant memories"""
        memories = []

        try:
            # Search working memory first
            working_mem = self.working_memory.get(child_id, [])
            for memory in working_mem:
                if query.lower() in memory.content.lower():
                    memories.append(memory)

            # Semantic search if we have embeddings
            if self.sentence_transformer and query:
                query_embedding = self.sentence_transformer.encode(query)
                similar = self.vector_store.search_similar(
                    query_embedding, k=limit)

                # Filter by child and memory type
                for memory in similar:
                    if memory.child_id == child_id:
                        if not memory_types or memory.memory_type in memory_types:
                            memory.access()  # Update access count
                            memories.append(memory)

            # Remove duplicates and sort by relevance
            seen = set()
            unique_memories = []
            for memory in memories:
                if memory.id not in seen:
                    seen.add(memory.id)
                    unique_memories.append(memory)

            # Sort by strength
            unique_memories.sort(key=lambda m: m.get_strength(), reverse=True)

            return unique_memories[:limit]

        except Exception as e:
            self.logger.error(f"Failed to recall memories: {e}")
            return []

    async def get_conversation_context(
        self,
        child_id: str,
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """Get conversation context from memory"""
        context = {
            'recent_topics': [],
            'emotional_state': [],
            'learned_concepts': [],
            'preferences': {},
            'summary': None
        }

        try:
            # Get recent memories
            recent_memories = list(
                self.short_term_buffer.get(child_id, []))[-10:]

            # Extract topics
            all_topics = []
            all_emotions = []

            for memory in recent_memories:
                all_topics.extend(memory.topics)
                all_emotions.extend(memory.emotions)

            # Count frequencies
            topic_counts = defaultdict(int)
            for topic in all_topics:
                topic_counts[topic] += 1

            context['recent_topics'] = sorted(
                topic_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            # Recent emotions
            if all_emotions:
                context['emotional_state'] = all_emotions[-3:]

            # Get child profile
            profile = await self.get_child_profile(child_id)
            if profile:
                context['learned_concepts'] = list(
                    profile.concepts_learned.keys())[-5:]
                context['preferences'] = {
                    'favorite_topics': profile.favorite_topics,
                    'interaction_style': profile.preferred_interaction_style
                }

            # Generate summary if requested
            if include_summary and recent_memories:
                context['summary'] = await self._generate_context_summary(recent_memories)

            return context

        except Exception as e:
            self.logger.error(f"Failed to get conversation context: {e}")
            return context

    async def _generate_context_summary(self, memories: List[Memory]) -> str:
        """Generate summary of recent context"""
        if not memories:
            return ""

        # Combine memory contents
        combined_text = "\n".join([m.content for m in memories[-5:]])

        # Use summarizer if available
        if self.summarizer and len(combined_text) > 200:
            try:
                summary = self.summarizer(
                    combined_text,
                    max_length=100,
                    min_length=30,
                    do_sample=False
                )
                return summary[0]['summary_text']
            except IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)ndexError as e:
    logger.warning(f"Ignoring error: {e}")

        # Fallback to simple summary
        topics = set()
        for memory in memories:
            topics.update(memory.topics)

        return f"Recent conversation covered: {', '.join(list(topics)[:3])}"

    async def update_child_profile(
        self,
        child_id: str,
        interaction_data: Dict[str, Any]
    ):
        """Update child's memory profile"""
        try:
            profile = await self.get_child_profile(child_id)

            if not profile:
                # Create new profile
                profile = ChildMemoryProfile(
                    child_id=child_id,
                    name=interaction_data.get('name', 'Unknown'),
                    age=interaction_data.get('age', 5),
                    first_interaction=datetime.now(),
                    last_interaction=datetime.now(),
                    total_interactions=1
                )
            else:
                # Update existing profile
                profile.last_interaction = datetime.now()
                profile.total_interactions += 1

            # Update favorite topics
            topic = interaction_data.get('topic')
            if topic:
                profile.favorite_topics[topic] = profile.favorite_topics.get(
                    topic, 0) + 1

            # Update emotional patterns
            emotion = interaction_data.get('emotion')
            trigger = interaction_data.get('trigger')
            if emotion and trigger:
                if emotion not in profile.emotional_triggers:
                    profile.emotional_triggers[emotion] = []
                profile.emotional_triggers[emotion].append(trigger)

            # Update vocabulary
            new_words = interaction_data.get('new_vocabulary', [])
            for word in new_words:
                profile.vocabulary_growth.append((word, datetime.now()))

            # Update learned concepts
            concept = interaction_data.get('concept_learned')
            if concept:
                profile.concepts_learned[concept] = datetime.now()

            # Save profile
            await self._save_child_profile(profile)

            # Update cache
            self.child_profiles[child_id] = profile

        except Exception as e:
            self.logger.error(f"Failed to update child profile: {e}")

    async def get_child_profile(self, child_id: str) -> Optional[ChildMemoryProfile]:
        """Get child's memory profile"""
        # Check cache first
        if child_id in self.child_profiles:
            return self.child_profiles[child_id]

        try:
            cursor = await self.db_conn.execute(
                "SELECT * FROM child_profiles WHERE child_id = ?",
                (child_id,)
            )

            row = await cursor.fetchone()

            if row:
                profile = ChildMemoryProfile(
                    child_id=row[0],
                    name=row[1],
                    age=row[2],
                    total_interactions=row[3],
                    first_interaction=datetime.fromisoformat(
                        row[4]) if row[4] else None,
                    last_interaction=datetime.fromisoformat(
                        row[5]) if row[5] else None,
                    favorite_topics=json.loads(row[6]) if row[6] else {},
                    favorite_activities=json.loads(row[7]) if row[7] else [],
                    favorite_stories=json.loads(row[8]) if row[8] else [],
                    concepts_learned=self._parse_datetime_dict(
                        json.loads(row[9]) if row[9] else {}),
                    skills_developed=json.loads(row[10]) if row[10] else {},
                    vocabulary_growth=self._parse_vocabulary_list(
                        json.loads(row[11]) if row[11] else []),
                    emotional_triggers=json.loads(row[12]) if row[12] else {},
                    comfort_strategies=json.loads(row[13]) if row[13] else [],
                    interaction_patterns=json.loads(
                        row[14]) if row[14] else {},
                    attention_span_minutes=row[15],
                    preferred_interaction_style=row[16]
                )

                # Cache it
                self.child_profiles[child_id] = profile

                return profile

            return None

        except Exception as e:
            self.logger.error(f"Failed to get child profile: {e}")
            return None

    async def _save_child_profile(self, profile: ChildMemoryProfile):
        """Save child profile to database"""
        try:
            await self.db_conn.execute("""
                INSERT OR REPLACE INTO child_profiles 
                (child_id, name, age, total_interactions, first_interaction, 
                 last_interaction, favorite_topics, favorite_activities, 
                 favorite_stories, concepts_learned, skills_developed, 
                 vocabulary_growth, emotional_triggers, comfort_strategies, 
                 interaction_patterns, attention_span_minutes, preferred_interaction_style)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.child_id,
                profile.name,
                profile.age,
                profile.total_interactions,
                profile.first_interaction.isoformat() if profile.first_interaction else None,
                profile.last_interaction.isoformat() if profile.last_interaction else None,
                json.dumps(profile.favorite_topics),
                json.dumps(profile.favorite_activities),
                json.dumps(profile.favorite_stories),
                json.dumps(self._datetime_dict_to_str(
                    profile.concepts_learned)),
                json.dumps(profile.skills_developed),
                json.dumps(self._vocabulary_list_to_str(
                    profile.vocabulary_growth)),
                json.dumps(profile.emotional_triggers),
                json.dumps(profile.comfort_strategies),
                json.dumps(profile.interaction_patterns),
                profile.attention_span_minutes,
                profile.preferred_interaction_style
            ))

            await self.db_conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to save child profile: {e}")

    async def create_conversation_summary(
        self,
        session_id: str,
        child_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> ConversationSummary:
        """Create summary of a conversation session"""
        try:
            # Get all memories from session
            session_memories = [
                m for m in self.short_term_buffer.get(child_id, [])
                if session_id in m.id
            ]

            # Extract information
            topics = set()
            emotions = []
            key_moments = []

            for memory in session_memories:
                topics.update(memory.topics)
                emotions.extend([(memory.timestamp, e)
                                for e in memory.emotions])

                # Identify key moments (high importance memories)
                if memory.importance.value >= MemoryImportance.HIGH.value:
                    key_moments.append(memory.content[:100])

            # Calculate metrics
            sentiments = []
            for memory in session_memories:
                if 'sentiment' in memory.context:
                    sentiments.append(memory.context['sentiment'])

            overall_sentiment = np.mean(sentiments) if sentiments else 0.0

            # Estimate engagement
            message_rate = len(session_memories) / \
                max((end_time - start_time).seconds / 60, 1)
            # 5 messages per minute = full engagement
            engagement_level = min(1.0, message_rate / 5)

            # Extract learnings
            learnings = []
            for memory in session_memories:
                if memory.memory_type == MemoryType.SEMANTIC:
                    learnings.append(memory.content[:100])

            summary = ConversationSummary(
                session_id=session_id,
                child_id=child_id,
                start_time=start_time,
                end_time=end_time,
                message_count=len(session_memories),
                topics_discussed=list(topics),
                emotional_journey=emotions,
                key_learnings=learnings[:5],
                memorable_moments=key_moments[:5],
                overall_sentiment=overall_sentiment,
                engagement_level=engagement_level
            )

            # Save summary
            await self._save_conversation_summary(summary)

            return summary

        except Exception as e:
            self.logger.error(f"Failed to create conversation summary: {e}")
            return ConversationSummary(
                session_id=session_id,
                child_id=child_id,
                start_time=start_time,
                end_time=end_time,
                message_count=0,
                topics_discussed=[],
                emotional_journey=[],
                key_learnings=[],
                memorable_moments=[],
                overall_sentiment=0.0,
                engagement_level=0.0
            )

    async def _save_conversation_summary(self, summary: ConversationSummary):
        """Save conversation summary to database"""
        try:
            await self.db_conn.execute("""
                INSERT INTO conversation_summaries 
                (session_id, child_id, start_time, end_time, message_count, 
                 topics_discussed, emotional_journey, key_learnings, 
                 memorable_moments, overall_sentiment, engagement_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                summary.session_id,
                summary.child_id,
                summary.start_time.isoformat(),
                summary.end_time.isoformat(),
                summary.message_count,
                json.dumps(summary.topics_discussed),
                json.dumps([(t.isoformat(), e)
                           for t, e in summary.emotional_journey]),
                json.dumps(summary.key_learnings),
                json.dumps(summary.memorable_moments),
                summary.overall_sentiment,
                summary.engagement_level
            ))

            await self.db_conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to save conversation summary: {e}")

    async def get_learning_progress(
        self,
        child_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get child's learning progress"""
        try:
            profile = await self.get_child_profile(child_id)
            if not profile:
                return {}

            # Get recent concepts learned
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_concepts = {
                concept: date
                for concept, date in profile.concepts_learned.items()
                if date > cutoff_date
            }

            # Get vocabulary growth
            recent_vocabulary = [
                word for word, date in profile.vocabulary_growth
                if date > cutoff_date
            ]

            # Calculate learning velocity
            concepts_per_week = len(recent_concepts) * 7 / days
            words_per_week = len(recent_vocabulary) * 7 / days

            # Get skill improvements
            skill_progress = {}
            for skill, level in profile.skills_developed.items():
                # Estimate improvement (simplified)
                skill_progress[skill] = {
                    'current_level': level,
                    'improvement': 0.1 * profile.total_interactions / 100  # Rough estimate
                }

            return {
                'concepts_learned': recent_concepts,
                'vocabulary_growth': recent_vocabulary,
                'learning_velocity': {
                    'concepts_per_week': concepts_per_week,
                    'words_per_week': words_per_week
                },
                'skill_progress': skill_progress,
                'total_interactions': profile.total_interactions,
                'attention_span_minutes': profile.attention_span_minutes
            }

        except Exception as e:
            self.logger.error(f"Failed to get learning progress: {e}")
            return {}

    async def get_emotional_insights(
        self,
        child_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get emotional insights for a child"""
        try:
            # Get recent memories
            cutoff_date = datetime.now() - timedelta(days=days)

            cursor = await self.db_conn.execute("""
                SELECT emotions, timestamp, context 
                FROM memories 
                WHERE child_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """, (child_id, cutoff_date.isoformat()))

            rows = await cursor.fetchall()

            # Analyze emotional patterns
            emotion_timeline = []
            emotion_counts = defaultdict(int)
            emotion_triggers = defaultdict(list)

            for row in rows:
                emotions = json.loads(row[0]) if row[0] else []
                timestamp = datetime.fromisoformat(row[1])
                context = json.loads(row[2]) if row[2] else {}

                for emotion in emotions:
                    emotion_counts[emotion] += 1
                    emotion_timeline.append((timestamp, emotion))

                    # Track triggers
                    if 'topic' in context:
                        emotion_triggers[emotion].append(context['topic'])

            # Get profile for additional insights
            profile = await self.get_child_profile(child_id)

            # Calculate emotional stability
            stability_score = 1.0
            if emotion_timeline:
                # Check for rapid emotional changes
                rapid_changes = 0
                for i in range(1, len(emotion_timeline)):
                    time_diff = (
                        emotion_timeline[i][0] - emotion_timeline[i-1][0]).seconds
                    if time_diff < 300 and emotion_timeline[i][1] != emotion_timeline[i-1][1]:
                        rapid_changes += 1

                stability_score = max(
                    0.0, 1.0 - (rapid_changes / max(len(emotion_timeline), 1)))

            return {
                'emotion_distribution': dict(emotion_counts),
                'emotional_timeline': [
                    {'timestamp': t.isoformat(), 'emotion': e}
                    for t, e in emotion_timeline[-20:]  # Last 20 emotions
                ],
                'emotion_triggers': {
                    emotion: list(set(triggers))[:5]
                    for emotion, triggers in emotion_triggers.items()
                },
                'emotional_stability': stability_score,
                'comfort_strategies': profile.comfort_strategies if profile else [],
                'positive_emotion_ratio': (
                    emotion_counts.get('happy', 0) +
                    emotion_counts.get('excited', 0)
                ) / max(sum(emotion_counts.values()), 1)
            }

        except Exception as e:
            self.logger.error(f"Failed to get emotional insights: {e}")
            return {}

    async def _consolidate_memories(self):
        """Consolidate short-term memories into long-term"""
        try:
            for child_id, memories in self.short_term_buffer.items():
                if not memories:
                    continue

                # Group memories by topic
                topic_groups = defaultdict(list)
                for memory in memories:
                    for topic in memory.topics:
                        topic_groups[topic].append(memory)

                # Create consolidated memories for important topics
                for topic, topic_memories in topic_groups.items():
                    if len(topic_memories) >= 3:  # Repeated topic
                        # Create semantic memory
                        consolidated_content = self._consolidate_topic_memories(
                            topic, topic_memories
                        )

                        if consolidated_content:
                            semantic_memory = Memory(
                                id=f"semantic_{child_id}_{topic}_{datetime.now().timestamp()}",
                                child_id=child_id,
                                content=consolidated_content,
                                memory_type=MemoryType.SEMANTIC,
                                importance=MemoryImportance.HIGH,
                                timestamp=datetime.now(),
                                topics=[topic],
                                embedding=self.sentence_transformer.encode(
                                    consolidated_content)
                                if self.sentence_transformer else None
                            )

                            await self._store_long_term(semantic_memory)

                # Clear old memories from buffer
                cutoff_time = datetime.now() - timedelta(hours=2)
                self.short_term_buffer[child_id] = deque(
                    [m for m in memories if m.timestamp > cutoff_time],
                    maxlen=50
                )

        except Exception as e:
            self.logger.error(f"Memory consolidation failed: {e}")

    def _consolidate_topic_memories(
        self,
        topic: str,
        memories: List[Memory]
    ) -> Optional[str]:
        """Consolidate multiple memories about a topic"""
        if not memories:
            return None

        # Extract key information
        key_facts = []
        questions = []

        for memory in memories:
            content_lower = memory.content.lower()

            # Extract questions
            if '?' in content_lower:
                for line in memory.content.split('\n'):
                    if '?' in line:
                        questions.append(line.strip())

            # Extract statements about the topic
            for line in memory.content.split('\n'):
                if topic.lower() in line.lower() and '?' not in line:
                    key_facts.append(line.strip())

        # Build consolidated memory
        if key_facts or questions:
            consolidated = f"Knowledge about {topic}:\n"

            if key_facts:
                consolidated += "Facts learned:\n"
                for fact in list(set(key_facts))[:5]:
                    consolidated += f"- {fact}\n"

            if questions:
                consolidated += "\nQuestions explored:\n"
                for question in list(set(questions))[:3]:
                    consolidated += f"- {question}\n"

            return consolidated

        return None

    def _calculate_importance(
        self,
        user_message: str,
        ai_response: str,
        metadata: Dict[str, Any]
    ) -> MemoryImportance:
        """Calculate importance of a memory"""
        importance_score = 0

        # Learning moments
        learning_keywords = ['learned', 'understand',
                             'know', 'remember', 'تعلمت', 'أفهم']
        if any(keyword in user_message.lower() + ai_response.lower()
               for keyword in learning_keywords):
            importance_score += 2

        # Emotional moments
        if metadata.get('emotion') in ['sad', 'scared', 'very_happy']:
            importance_score += 2

        # First-time experiences
        if 'first time' in user_message.lower() or 'أول مرة' in user_message:
            importance_score += 3

        # Safety-related
        safety_keywords = ['danger', 'safe',
                           'careful', 'help', 'خطر', 'آمن', 'حذر']
        if any(keyword in user_message.lower() + ai_response.lower()
               for keyword in safety_keywords):
            importance_score += 4

        # Personal information
        if metadata.get('contains_personal_info'):
            importance_score += 3

        # Map score to importance level
        if importance_score >= 4:
            return MemoryImportance.CRITICAL
        elif importance_score >= 3:
            return MemoryImportance.HIGH
        elif importance_score >= 2:
            return MemoryImportance.MEDIUM
        elif importance_score >= 1:
            return MemoryImportance.LOW
        else:
            return MemoryImportance.TRIVIAL

    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content"""
        topics = []

        # Predefined topic keywords
        topic_map = {
            'animals': ['animal', 'dog', 'cat', 'bird', 'حيوان', 'كلب', 'قطة'],
            'learning': ['learn', 'study', 'know', 'تعلم', 'دراسة', 'معرفة'],
            'games': ['play', 'game', 'fun', 'لعب', 'لعبة', 'مرح'],
            'stories': ['story', 'tale', 'book', 'قصة', 'حكاية', 'كتاب'],
            'emotions': ['happy', 'sad', 'feel', 'سعيد', 'حزين', 'شعور'],
            'family': ['mom', 'dad', 'family', 'ماما', 'بابا', 'عائلة'],
            'science': ['science', 'why', 'how', 'علم', 'لماذا', 'كيف'],
            'numbers': ['number', 'count', 'math', 'رقم', 'عد', 'رياضيات']
        }

        content_lower = content.lower()

        for topic, keywords in topic_map.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics[:3]  # Limit to 3 topics

    def _row_to_memory(self, row: tuple) -> Memory:
        """Convert database row to Memory object"""
        return Memory(
            id=row[0],
            child_id=row[1],
            content=row[2],
            memory_type=MemoryType(row[3]),
            importance=MemoryImportance(row[4]),
            timestamp=datetime.fromisoformat(row[5]),
            context=json.loads(row[6]) if row[6] else {},
            embedding=pickle.loads(row[7]) if row[7] else None,
            emotions=json.loads(row[8]) if row[8] else [],
            topics=json.loads(row[9]) if row[9] else [],
            related_memories=json.loads(row[10]) if row[10] else [],
            access_count=row[11],
            last_accessed=datetime.fromisoformat(row[12]) if row[12] else None,
            decay_rate=row[13]
        )

    def _datetime_dict_to_str(self, dt_dict: Dict[str, datetime]) -> Dict[str, str]:
        """Convert datetime dict to string dict for JSON"""
        return {k: v.isoformat() for k, v in dt_dict.items()}

    def _parse_datetime_dict(self, str_dict: Dict[str, str]) -> Dict[str, datetime]:
        """Parse string dict to datetime dict"""
        return {k: datetime.fromisoformat(v) for k, v in str_dict.items()}

    def _vocabulary_list_to_str(self, vocab_list: List[Tuple[str, datetime]]) -> List[List[str]]:
        """Convert vocabulary list for JSON"""
        return [[word, dt.isoformat()] for word, dt in vocab_list]

    def _parse_vocabulary_list(self, str_list: List[List[str]]) -> List[Tuple[str, datetime]]:
        """Parse vocabulary list from JSON"""
        return [(word, datetime.fromisoformat(dt)) for word, dt in str_list]

    async def forget_memories(
        self,
        child_id: str,
        memory_type: Optional[MemoryType] = None,
        older_than_days: Optional[int] = None,
        importance_threshold: Optional[MemoryImportance] = None
    ):
        """Selectively forget memories based on criteria"""
        try:
            conditions = ["child_id = ?"]
            params = [child_id]

            if memory_type:
                conditions.append("memory_type = ?")
                params.append(memory_type.value)

            if older_than_days:
                cutoff_date = datetime.now() - timedelta(days=older_than_days)
                conditions.append("timestamp < ?")
                params.append(cutoff_date.isoformat())

            if importance_threshold:
                conditions.append("importance < ?")
                params.append(importance_threshold.value)

            # Delete from database
            await self.db_conn.execute(
                f"DELETE FROM memories WHERE {' AND '.join(conditions)}",
                params
            )

            await self.db_conn.commit()

            # Clear from buffers
            if child_id in self.short_term_buffer:
                self.short_term_buffer[child_id].clear()

            if child_id in self.working_memory:
                self.working_memory[child_id].clear()

            self.logger.info(
                f"Forgot memories for child {child_id} with specified criteria")

        except Exception as e:
            self.logger.error(f"Failed to forget memories: {e}")

    async def export_memories(
        self,
        child_id: str,
        format: str = 'json'
    ) -> Optional[str]:
        """Export child's memories"""
        try:
            # Get all memories
            cursor = await self.db_conn.execute(
                "SELECT * FROM memories WHERE child_id = ? ORDER BY timestamp DESC",
                (child_id,)
            )

            rows = await cursor.fetchall()
            memories = [self._row_to_memory(row) for row in rows]

            # Get profile
            profile = await self.get_child_profile(child_id)

            # Get summaries
            cursor = await self.db_conn.execute(
                "SELECT * FROM conversation_summaries WHERE child_id = ? ORDER BY start_time DESC",
                (child_id,)
            )

            summary_rows = await cursor.fetchall()

            export_data = {
                'export_date': datetime.now().isoformat(),
                'child_id': child_id,
                'profile': {
                    'name': profile.name if profile else 'Unknown',
                    'age': profile.age if profile else 0,
                    'total_interactions': profile.total_interactions if profile else 0,
                    'favorite_topics': profile.favorite_topics if profile else {},
                    'concepts_learned': list(profile.concepts_learned.keys()) if profile else [],
                    'vocabulary_size': len(profile.vocabulary_growth) if profile else 0
                },
                'memories': [
                    {
                        'id': m.id,
                        'content': m.content,
                        'type': m.memory_type.value,
                        'importance': m.importance.value,
                        'timestamp': m.timestamp.isoformat(),
                        'topics': m.topics,
                        'emotions': m.emotions
                    }
                    for m in memories[:100]  # Limit to recent 100
                ],
                'conversation_summaries': [
                    {
                        'session_id': row[0],
                        'start_time': row[2],
                        'end_time': row[3],
                        'message_count': row[4],
                        'topics': json.loads(row[5]) if row[5] else [],
                        'overall_sentiment': row[9],
                        'engagement_level': row[10]
                    }
                    for row in summary_rows[:20]  # Recent 20 summaries
                ]
            }

            if format == 'json':
                return json.dumps(export_data, indent=2)
            else:
                # Add other formats as needed
                return json.dumps(export_data)

        except Exception as e:
            self.logger.error(f"Failed to export memories: {e}")
            return None

    async def close(self):
        """Close all connections and clean up"""
        try:
            # Cancel consolidation task
            if self.consolidation_task:
                self.consolidation_task.cancel()

            # Close database
            if self.db_conn:
                await self.db_conn.close()

            # Close Redis
            if self.redis_client:
                await self.redis_client.close()

            self.logger.info("Memory service closed")

        except Exception as e:
            self.logger.error(f"Error closing memory service: {e}")


# Helper functions for memory analysis

def calculate_memory_similarity(memory1: Memory, memory2: Memory) -> float:
    """Calculate similarity between two memories"""
    if memory1.embedding is None or memory2.embedding is None:
        # Fallback to text similarity
        common_topics = set(memory1.topics) & set(memory2.topics)
        return len(common_topics) / max(len(memory1.topics), len(memory2.topics), 1)

    # Cosine similarity
    dot_product = np.dot(memory1.embedding, memory2.embedding)
    norm1 = np.linalg.norm(memory1.embedding)
    norm2 = np.linalg.norm(memory2.embedding)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def generate_memory_graph(memories: List[Memory], threshold: float = 0.5) -> Dict[str, List[str]]:
    """Generate a graph of related memories"""
    graph = defaultdict(list)

    for i, memory1 in enumerate(memories):
        for j, memory2 in enumerate(memories[i+1:], i+1):
            similarity = calculate_memory_similarity(memory1, memory2)

            if similarity > threshold:
                graph[memory1.id].append(memory2.id)
                graph[memory2.id].append(memory1.id)

    return dict(graph)