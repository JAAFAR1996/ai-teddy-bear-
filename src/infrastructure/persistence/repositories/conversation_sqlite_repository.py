import os
import sqlite3
import json
import uuid
import csv
import io
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter

from src.infrastructure.persistence.base_sqlite_repository import BaseSQLiteRepository
from src.domain.entities.conversation import (
    Conversation, Message, MessageRole, InteractionType,
    EmotionalState, ConversationMetrics, ConversationSummary,
    ContentType
)
from src.domain.repositories.conversation_repository import (
    ConversationRepository, TimeRange
)
from src.domain.repositories.base import SearchCriteria, QueryOptions, SortOrder, BulkOperationResult


class ConversationSQLiteRepository(BaseSQLiteRepository[Conversation, str], ConversationRepository):
    """
    Enhanced SQLite implementation of Conversation Repository
    """
    def __init__(
        self, session_factory,
        db_path: str = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            '..', 
            '..', 
            'data', 
            'teddyai.db'
        )
    ):
        """
        Initialize Conversation SQLite Repository
        
        Args:
            db_path (str): Path to SQLite database
        """
        self.session_factory = session_factory
        # Ensure data directory exists
        data_dir = os.path.dirname(db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            
        # Create connection
        connection = sqlite3.connect(db_path, check_same_thread=False)
        
        super().__init__(
            connection=connection,
            table_name='conversations', 
            entity_class=Conversation
        )
        
        # Create related tables
        self._create_messages_table()
        self._create_emotional_states_table()

    async def add(self, conversation: Conversation) -> Conversation:
        """
        Add a new conversation (alias for create)
        
        Args:
            conversation: Conversation entity to add
            
        Returns:
            Added conversation with assigned ID
        """
        return await self.create(conversation)

    async def aggregate(
        self,
        field: str,
        operation: str,
        criteria: Optional[List[SearchCriteria]] = None
    ) -> Any:
        """
        Perform aggregation operations on conversation data
        
        Args:
            field: Field to aggregate (duration, total_messages, etc.)
            operation: Operation type ('count', 'avg', 'sum', 'min', 'max')
            criteria: Optional search criteria to filter data
            
        Returns:
            Aggregation result
        """
        try:
            cursor = self._connection.cursor()
            
            # Handle special aggregations
            if operation.lower() == 'count':
                sql = f"SELECT COUNT(*) FROM {self.table_name}"
            else:
                sql = f"SELECT {operation.upper()}({field}) FROM {self.table_name}"
            
            params = []
            
            # Apply criteria filters
            if criteria:
                conditions = []
                for criterion in criteria:
                    condition, param = self._build_search_condition(criterion)
                    conditions.append(condition)
                    if param is not None:
                        params.append(param)
                
                if conditions:
                    sql += " WHERE " + " AND ".join(conditions) + " AND archived = 0"
                else:
                    sql += " WHERE archived = 0"
            else:
                sql += " WHERE archived = 0"
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            
            return result[0] if result and result[0] is not None else 0
            
        except sqlite3.Error as e:
            self.logger.error(f"Error in conversation aggregation: {e}")
            raise

    async def get(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get conversation by ID (alias for get_by_id)
        
        Args:
            conversation_id: Conversation's unique identifier
            
        Returns:
            Conversation entity or None if not found
        """
        return await self.get_by_id(conversation_id)
    async def initialize(self):
        # لا تفعل شيئاً هنا حالياً
        pass
    
    def _get_table_schema(self) -> str:
        """
        Get the CREATE TABLE SQL statement for conversations table
        
        Returns:
            str: SQL CREATE TABLE statement
        """
        return '''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                child_id TEXT NOT NULL,
                parent_id TEXT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                duration INTEGER DEFAULT 0,
                interaction_type TEXT DEFAULT 'general',
                topics TEXT,
                primary_language TEXT DEFAULT 'en',
                quality_score REAL,
                safety_score REAL DEFAULT 1.0,
                educational_score REAL DEFAULT 0.0,
                engagement_score REAL DEFAULT 0.0,
                llm_provider TEXT,
                model_version TEXT,
                context_summary TEXT,
                metadata TEXT,
                total_messages INTEGER DEFAULT 0,
                child_messages INTEGER DEFAULT 0,
                assistant_messages INTEGER DEFAULT 0,
                questions_asked INTEGER DEFAULT 0,
                moderation_flags INTEGER DEFAULT 0,
                parent_visible BOOLEAN DEFAULT 1,
                archived BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(child_id) REFERENCES children(id)
            )
        '''
    
    def _create_messages_table(self):
        """Create messages table for storing individual messages"""
        schema = '''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'text',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sequence_number INTEGER,
                metadata TEXT,
                moderation_flags TEXT,
                embedding_vector BLOB,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        '''
        self._connection.execute(schema)
        self._connection.execute("CREATE INDEX IF NOT EXISTS idx_conversation_id ON messages (conversation_id)")
        self._connection.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON messages (timestamp)")
        self._connection.execute("CREATE INDEX IF NOT EXISTS idx_role ON messages (role)")
        self._connection.commit()
        try:
            self._connection.execute(schema)
            self._connection.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error creating messages table: {e}")
    
    def _create_emotional_states_table(self):
        """Create emotional states table"""
        schema = '''
            CREATE TABLE IF NOT EXISTS emotional_states (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                primary_emotion TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                secondary_emotions TEXT,
                arousal_level REAL DEFAULT 0.0,
                valence_level REAL DEFAULT 0.0,
                emotional_context TEXT,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        '''
        try:
            self._connection.execute(schema)
            self._connection.execute("CREATE INDEX IF NOT EXISTS idx_conversation_id_emotion ON emotional_states (conversation_id)")
            self._connection.execute("CREATE INDEX IF NOT EXISTS idx_primary_emotion ON emotional_states (primary_emotion)")
            self._connection.commit()    
        except sqlite3.Error as e:
            self.logger.error(f"Error creating emotional_states table: {e}")
    
    def _serialize_conversation_for_db(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Serialize conversation entity for database storage
        """
        data = conversation.dict() if hasattr(conversation, 'dict') else conversation.__dict__.copy()
        
        # Generate ID if not present
        if not data.get('id'):
            data['id'] = str(uuid.uuid4())
        
        # Serialize complex fields to JSON
        json_fields = ['topics', 'metadata']
        for field in json_fields:
            if field in data and data[field] is not None:
                data[field] = json.dumps(data[field])
        
        # Handle datetime fields
        datetime_fields = ['start_time', 'end_time', 'created_at', 'updated_at']
        for field in datetime_fields:
            if field in data and data[field] and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
        
        # Handle duration (timedelta to seconds)
        if 'duration' in data and data['duration']:
            if hasattr(data['duration'], 'total_seconds'):
                data['duration'] = int(data['duration'].total_seconds())
        
        # Extract metrics for direct storage
        if hasattr(conversation, 'metrics') and conversation.metrics:
            metrics = conversation.metrics
            data.update({
                'total_messages': metrics.total_messages,
                'child_messages': metrics.child_messages,
                'assistant_messages': metrics.assistant_messages,
                'questions_asked': metrics.questions_asked,
                'moderation_flags': metrics.moderation_flags,
                'engagement_score': metrics.engagement_score
            })
        
        # Set updated timestamp
        data['updated_at'] = datetime.now().isoformat()
        
        return data
    
    def _deserialize_conversation_from_db(self, data: Dict[str, Any]) -> Conversation:
        """
        Deserialize conversation data from database
        """
        # Parse JSON fields
        json_fields = ['topics', 'metadata']
        for field in json_fields:
            if field in data and data[field]:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = [] if field == 'topics' else {}
            else:
                data[field] = [] if field == 'topics' else {}
        
        # Parse datetime fields
        datetime_fields = ['start_time', 'end_time', 'created_at', 'updated_at']
        for field in datetime_fields:
            if field in data and data[field]:
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except (ValueError, TypeError):
                    data[field] = None
        
        # Convert duration from seconds to timedelta
        if 'duration' in data and data['duration']:
            try:
                data['duration'] = timedelta(seconds=int(data['duration']))
            except (ValueError, TypeError):
                data['duration'] = None
        
        # Convert interaction type
        if 'interaction_type' in data and data['interaction_type']:
            try:
                data['interaction_type'] = InteractionType(data['interaction_type'])
            except ValueError:
                data['interaction_type'] = InteractionType.GENERAL
        
        # Convert boolean fields
        bool_fields = ['parent_visible', 'archived']
        for field in bool_fields:
            if field in data:
                data[field] = bool(data[field])
        
        # Load related data
        if 'id' in data:
            data['messages'] = self._load_messages(data['id'])
            data['emotional_states'] = self._load_emotional_states(data['id'])
            data['metrics'] = self._create_metrics_from_data(data)
        
        return Conversation(**data)
    
    def _load_messages(self, conversation_id: str) -> List[Message]:
        """Load messages for a conversation"""
        try:
            cursor = self._connection.cursor()
            sql = """
                SELECT * FROM messages 
                WHERE conversation_id = ? 
                ORDER BY sequence_number, timestamp
            """
            cursor.execute(sql, (conversation_id,))
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                row_dict = dict(row)
                
                # Parse metadata and moderation_flags
                if row_dict.get('metadata'):
                    try:
                        row_dict['metadata'] = json.loads(row_dict['metadata'])
                    except json.JSONDecodeError:
                        row_dict['metadata'] = {}
                
                if row_dict.get('moderation_flags'):
                    try:
                        row_dict['moderation_flags'] = json.loads(row_dict['moderation_flags'])
                    except json.JSONDecodeError:
                        row_dict['moderation_flags'] = []
                
                # Parse timestamp
                if row_dict.get('timestamp'):
                    try:
                        row_dict['timestamp'] = datetime.fromisoformat(row_dict['timestamp'])
                    except ValueError:
                        row_dict['timestamp'] = datetime.now()
                
                # Convert role to enum
                if row_dict.get('role'):
                    try:
                        row_dict['role'] = MessageRole(row_dict['role'])
                    except ValueError:
                        row_dict['role'] = MessageRole.USER
                
                # Convert content type to enum
                if row_dict.get('content_type'):
                    try:
                        row_dict['content_type'] = ContentType(row_dict['content_type'])
                    except ValueError:
                        row_dict['content_type'] = ContentType.TEXT
                
                messages.append(Message(**row_dict))
            
            return messages
            
        except sqlite3.Error as e:
            self.logger.error(f"Error loading messages: {e}")
            return []
    
    def _load_emotional_states(self, conversation_id: str) -> List[EmotionalState]:
        """Load emotional states for a conversation"""
        try:
            cursor = self._connection.cursor()
            sql = """
                SELECT * FROM emotional_states 
                WHERE conversation_id = ? 
                ORDER BY timestamp
            """
            cursor.execute(sql, (conversation_id,))
            rows = cursor.fetchall()
            
            emotional_states = []
            for row in rows:
                row_dict = dict(row)
                
                # Parse secondary emotions
                if row_dict.get('secondary_emotions'):
                    try:
                        row_dict['secondary_emotions'] = json.loads(row_dict['secondary_emotions'])
                    except json.JSONDecodeError:
                        row_dict['secondary_emotions'] = []
                
                # Parse timestamp
                if row_dict.get('timestamp'):
                    try:
                        row_dict['timestamp'] = datetime.fromisoformat(row_dict['timestamp'])
                    except ValueError:
                        row_dict['timestamp'] = datetime.now()
                
                emotional_states.append(EmotionalState(**row_dict))
            
            return emotional_states
            
        except sqlite3.Error as e:
            self.logger.error(f"Error loading emotional states: {e}")
            return []
    
    def _create_metrics_from_data(self, data: Dict[str, Any]) -> ConversationMetrics:
        """Create ConversationMetrics from database data"""
        return ConversationMetrics(
            total_messages=data.get('total_messages', 0),
            child_messages=data.get('child_messages', 0),
            assistant_messages=data.get('assistant_messages', 0),
            questions_asked=data.get('questions_asked', 0),
            moderation_flags=data.get('moderation_flags', 0),
            engagement_score=data.get('engagement_score', 0.0),
            response_time_avg=0.0,  # Could be calculated from messages
            conversation_turns=data.get('total_messages', 0) // 2
        )
    
    def _save_messages(self, conversation_id: str, messages: List[Message]):
        """Save messages to the messages table"""
        try:
            with self.transaction() as cursor:
                # Delete existing messages
                cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
                
                # Insert new messages
                for i, message in enumerate(messages):
                    message_data = {
                        'id': message.id or str(uuid.uuid4()),
                        'conversation_id': conversation_id,
                        'role': message.role.value,
                        'content': message.content,
                        'content_type': message.content_type.value if message.content_type else ContentType.TEXT.value,
                        'timestamp': message.timestamp.isoformat() if message.timestamp else datetime.now().isoformat(),
                        'sequence_number': i,
                        'metadata': json.dumps(message.metadata) if message.metadata else None,
                        'moderation_flags': json.dumps(message.moderation_flags) if message.moderation_flags else None
                    }
                    
                    columns = ', '.join(message_data.keys())
                    placeholders = ', '.join(['?' for _ in message_data])
                    sql = f"INSERT INTO messages ({columns}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, list(message_data.values()))
                    
        except sqlite3.Error as e:
            self.logger.error(f"Error saving messages: {e}")
            raise
    
    def _save_emotional_states(self, conversation_id: str, emotional_states: List[EmotionalState]):
        """Save emotional states to the emotional_states table"""
        try:
            with self.transaction() as cursor:
                # Delete existing emotional states
                cursor.execute("DELETE FROM emotional_states WHERE conversation_id = ?", (conversation_id,))
                
                # Insert new emotional states
                for state in emotional_states:
                    state_data = {
                        'id': state.id or str(uuid.uuid4()),
                        'conversation_id': conversation_id,
                        'timestamp': state.timestamp.isoformat() if state.timestamp else datetime.now().isoformat(),
                        'primary_emotion': state.primary_emotion,
                        'confidence': state.confidence,
                        'secondary_emotions': json.dumps(state.secondary_emotions) if state.secondary_emotions else None,
                        'arousal_level': state.arousal_level,
                        'valence_level': state.valence_level,
                        'emotional_context': state.emotional_context
                    }
                    
                    columns = ', '.join(state_data.keys())
                    placeholders = ', '.join(['?' for _ in state_data])
                    sql = f"INSERT INTO emotional_states ({columns}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, list(state_data.values()))
                    
        except sqlite3.Error as e:
            self.logger.error(f"Error saving emotional states: {e}")
            raise
    
    # Implement ConversationRepository interface methods
    
    async def create(self, conversation: Conversation) -> Conversation:
        """Create a new conversation"""
        try:
            with self.transaction() as cursor:
                data = self._serialize_conversation_for_db(conversation)
                
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
                
                cursor.execute(sql, list(data.values()))
                
                # Assign ID if not already present
                if not conversation.id:
                    conversation.id = data['id']
                
                # Save related data
                if conversation.messages:
                    self._save_messages(conversation.id, conversation.messages)
                
                if conversation.emotional_states:
                    self._save_emotional_states(conversation.id, conversation.emotional_states)
                
                return conversation
                
        except sqlite3.Error as e:
            self.logger.error(f"Error creating conversation: {e}")
            raise
    
    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve conversation by ID"""
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE id = ? AND archived = 0"
            cursor.execute(sql, (conversation_id,))
            
            row = cursor.fetchone()
            if row:
                return self._deserialize_conversation_from_db(dict(row))
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversation {conversation_id}: {e}")
            raise
    
    async def get_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID"""
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE session_id = ? AND archived = 0"
            cursor.execute(sql, (session_id,))
            
            row = cursor.fetchone()
            if row:
                return self._deserialize_conversation_from_db(dict(row))
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversation by session {session_id}: {e}")
            raise
    
    async def update(self, conversation: Conversation) -> Conversation:
        """Update existing conversation"""
        try:
            with self.transaction() as cursor:
                data = self._serialize_conversation_for_db(conversation)
                
                if 'id' not in data or not data['id']:
                    raise ValueError("Conversation must have an ID for update")
                
                # Prepare update SQL
                update_fields = [f"{k} = ?" for k in data.keys() if k != 'id']
                update_values = [v for k, v in data.items() if k != 'id']
                update_values.append(data['id'])
                
                sql = f"UPDATE {self.table_name} SET {', '.join(update_fields)} WHERE id = ?"
                
                cursor.execute(sql, update_values)
                
                if cursor.rowcount == 0:
                    raise ValueError(f"No conversation found with ID {data['id']}")
                
                # Update related data
                if conversation.messages:
                    self._save_messages(conversation.id, conversation.messages)
                
                if conversation.emotional_states:
                    self._save_emotional_states(conversation.id, conversation.emotional_states)
                
                return conversation
                
        except sqlite3.Error as e:
            self.logger.error(f"Error updating conversation: {e}")
            raise
    
    async def delete(self, conversation_id: str) -> bool:
        """Soft delete conversation (mark as archived)"""
        try:
            with self.transaction() as cursor:
                sql = f"UPDATE {self.table_name} SET archived = 1, updated_at = ? WHERE id = ?"
                cursor.execute(sql, (datetime.now().isoformat(), conversation_id))
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting conversation {conversation_id}: {e}")
            raise
    
    async def get_conversations_by_child(
        self, 
        child_id: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Conversation]:
        """Retrieve conversations for a specific child"""
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE child_id = ? AND archived = 0"
            params = [child_id]
            
            if start_date:
                sql += " AND start_time >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                sql += " AND start_time <= ?"
                params.append(end_date.isoformat())
            
            sql += " ORDER BY start_time DESC"
            
            if limit:
                sql += f" LIMIT {limit}"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [self._deserialize_conversation_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversations for child {child_id}: {e}")
            raise
    
    async def get_conversations_by_parent(
        self,
        parent_id: str,
        include_all_children: bool = True
    ) -> List[Conversation]:
        """Get all conversations for children of a parent"""
        try:
            cursor = self._connection.cursor()
            
            if include_all_children:
                # Get all conversations for children under this parent
                sql = f"""
                    SELECT c.* FROM {self.table_name} c
                    JOIN children ch ON c.child_id = ch.id
                    WHERE ch.parent_id = ? AND c.archived = 0
                    ORDER BY c.start_time DESC
                """
                cursor.execute(sql, (parent_id,))
            else:
                # Get conversations where parent is directly associated
                sql = f"SELECT * FROM {self.table_name} WHERE parent_id = ? AND archived = 0 ORDER BY start_time DESC"
                cursor.execute(sql, (parent_id,))
            
            rows = cursor.fetchall()
            return [self._deserialize_conversation_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversations for parent {parent_id}: {e}")
            raise
    
    async def get_conversations_by_topics(
        self, 
        topics: List[str], 
        match_all: bool = False,
        child_id: Optional[str] = None
    ) -> List[Conversation]:
        """Retrieve conversations by topics"""
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE archived = 0"
            params = []
            
            if match_all:
                # All topics must be present
                for topic in topics:
                    sql += " AND JSON_EXTRACT(topics, '$') LIKE ?"
                    params.append(f'%"{topic}"%')
            else:
                # Any topic matches
                topic_conditions = []
                for topic in topics:
                    topic_conditions.append("JSON_EXTRACT(topics, '$') LIKE ?")
                    params.append(f'%"{topic}"%')
                
                if topic_conditions:
                    sql += f" AND ({' OR '.join(topic_conditions)})"
            
            if child_id:
                sql += " AND child_id = ?"
                params.append(child_id)
            
            sql += " ORDER BY start_time DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [self._deserialize_conversation_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversations by topics: {e}")
            raise
    
    async def get_conversations_by_emotional_tone(
        self, 
        emotion: str, 
        threshold: float = 0.5,
        child_id: Optional[str] = None
    ) -> List[Conversation]:
        """Retrieve conversations by emotional tone"""
        try:
            cursor = self._connection.cursor()
            sql = f"""
                SELECT DISTINCT c.* FROM {self.table_name} c
                JOIN emotional_states es ON c.id = es.conversation_id
                WHERE es.primary_emotion = ? AND es.confidence >= ? AND c.archived = 0
            """
            params = [emotion, threshold]
            
            if child_id:
                sql += " AND c.child_id = ?"
                params.append(child_id)
            
            sql += " ORDER BY c.start_time DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [self._deserialize_conversation_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversations by emotional tone: {e}")
            raise
    
    # Helper methods for analytics (implementation from the enhanced repository)
    
    def _calculate_time_range(
        self,
        time_range: TimeRange,
        custom_start: Optional[datetime] = None,
        custom_end: Optional[datetime] = None
    ) -> Tuple[datetime, datetime]:
        """Calculate start and end dates for time range"""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if time_range == TimeRange.TODAY:
            return today, now
        elif time_range == TimeRange.YESTERDAY:
            yesterday = today - timedelta(days=1)
            return yesterday, today
        elif time_range == TimeRange.THIS_WEEK:
            week_start = today - timedelta(days=today.weekday())
            return week_start, now
        elif time_range == TimeRange.LAST_WEEK:
            week_start = today - timedelta(days=today.weekday() + 7)
            week_end = week_start + timedelta(days=7)
            return week_start, week_end
        elif time_range == TimeRange.THIS_MONTH:
            month_start = today.replace(day=1)
            return month_start, now
        elif time_range == TimeRange.LAST_MONTH:
            last_month_end = today.replace(day=1) - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return last_month_start, last_month_end
        elif time_range == TimeRange.LAST_30_DAYS:
            return now - timedelta(days=30), now
        elif time_range == TimeRange.LAST_90_DAYS:
            return now - timedelta(days=90), now
        elif time_range == TimeRange.CUSTOM:
            if not custom_start or not custom_end:
                raise ValueError("Custom time range requires start and end dates")
            return custom_start, custom_end
        else:
            raise ValueError(f"Unknown time range: {time_range}")
    
    def _count_occurrences(self, items: List[str]) -> List[Tuple[str, int]]:
        """Count occurrences and return sorted list"""
        counter = Counter(items)
        return counter.most_common()
    
    # Export functionality with enhanced features
    
    async def export_conversations(
        self, 
        child_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = 'json',
        include_transcripts: bool = True
    ) -> bytes:
        """Export conversations to specified format"""
        # Get conversations
        if child_id:
            conversations = await self.get_conversations_by_child(
                child_id, start_date, end_date
            )
        else:
            conversations = await self.get_conversations_by_time_range(
                TimeRange.CUSTOM,
                custom_start=start_date,
                custom_end=end_date
            )
        
        if format == 'json':
            return self._export_json(conversations, include_transcripts)
        elif format == 'csv':
            return self._export_csv(conversations)
        elif format == 'txt':
            return self._export_text(conversations, include_transcripts)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(
        self, 
        conversations: List[Conversation],
        include_transcripts: bool
    ) -> bytes:
        """Export as JSON"""
        data = []
        
        for conv in conversations:
            conv_data = {
                'id': conv.id,
                'child_id': conv.child_id,
                'start_time': conv.start_time.isoformat() if conv.start_time else None,
                'end_time': conv.end_time.isoformat() if conv.end_time else None,
                'duration_seconds': conv.duration.total_seconds() if conv.duration else 0,
                'topics': conv.topics,
                'quality_score': conv.quality_score,
                'safety_score': conv.safety_score,
                'message_count': len(conv.messages) if conv.messages else 0
            }
            
            if include_transcripts:
                conv_data['messages'] = [
                    {
                        'role': msg.role.value,
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
                    }
                    for msg in conv.messages
                ] if conv.messages else []
                
            data.append(conv_data)
            
        return json.dumps(data, indent=2).encode('utf-8')
    
    def _export_csv(self, conversations: List[Conversation]) -> bytes:
        """Export as CSV"""
        output = io.StringIO()
        
        fieldnames = [
            'id', 'child_id', 'start_time', 'end_time', 
            'duration_minutes', 'message_count', 'topics',
            'quality_score', 'safety_score', 'engagement_score'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for conv in conversations:
            writer.writerow({
                'id': conv.id,
                'child_id': conv.child_id,
                'start_time': conv.start_time.isoformat() if conv.start_time else '',
                'end_time': conv.end_time.isoformat() if conv.end_time else '',
                'duration_minutes': round(conv.duration.total_seconds() / 60, 2) if conv.duration else 0,
                'message_count': len(conv.messages) if conv.messages else 0,
                'topics': ', '.join(conv.topics) if conv.topics else '',
                'quality_score': round(conv.quality_score, 2) if conv.quality_score else '',
                'safety_score': round(conv.safety_score, 2) if conv.safety_score else '',
                'engagement_score': round(conv.metrics.engagement_score, 2) if conv.metrics else ''
            })
            
        return output.getvalue().encode('utf-8')
    
    def _export_text(
        self,
        conversations: List[Conversation],
        include_transcripts: bool
    ) -> bytes:
        """Export as human-readable text"""
        lines = []
        
        for conv in conversations:
            lines.append(f"{'=' * 50}")
            lines.append(f"Conversation ID: {conv.id}")
            lines.append(f"Child ID: {conv.child_id}")
            lines.append(f"Date: {conv.start_time.strftime('%Y-%m-%d %H:%M') if conv.start_time else 'N/A'}")
            lines.append(f"Duration: {conv.duration.total_seconds() / 60:.1f} minutes" if conv.duration else "Duration: N/A")
            lines.append(f"Topics: {', '.join(conv.topics) if conv.topics else 'None'}")
            lines.append(f"Quality Score: {conv.quality_score:.2f}" if conv.quality_score else "Quality Score: N/A")
            
            if include_transcripts and conv.messages:
                lines.append("\nTranscript:")
                for msg in conv.messages:
                    timestamp = msg.timestamp.strftime('%H:%M:%S') if msg.timestamp else 'N/A'
                    lines.append(f"[{timestamp}] {msg.role.value.upper()}: {msg.content}")
                
            lines.append("")
            
        return '\n'.join(lines).encode('utf-8')
    
    # Additional analytics methods
    
    async def get_conversation_analytics(
        self, 
        child_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = 'day'
    ) -> Dict[str, Any]:
        """Generate comprehensive conversation analytics"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        try:
            cursor = self._connection.cursor()
            
            # Base query
            sql = f"""
                SELECT 
                    COUNT(*) as total_conversations,
                    SUM(duration) as total_duration_seconds,
                    AVG(duration) as avg_duration_seconds,
                    SUM(total_messages) as total_messages,
                    AVG(total_messages) as avg_messages_per_conversation,
                    AVG(quality_score) as avg_quality_score,
                    AVG(safety_score) as avg_safety_score,
                    AVG(engagement_score) as avg_engagement_score,
                    COUNT(CASE WHEN safety_score < 1.0 THEN 1 END) as flagged_conversations
                FROM {self.table_name}
                WHERE start_time BETWEEN ? AND ? AND archived = 0
            """
            params = [start_date.isoformat(), end_date.isoformat()]
            
            if child_id:
                sql += " AND child_id = ?"
                params.append(child_id)
            
            cursor.execute(sql, params)
            result = cursor.fetchone()
            
            # Get topics distribution
            topic_sql = f"""
                SELECT topics FROM {self.table_name}
                WHERE start_time BETWEEN ? AND ? AND archived = 0 AND topics IS NOT NULL
            """
            topic_params = [start_date.isoformat(), end_date.isoformat()]
            
            if child_id:
                topic_sql += " AND child_id = ?"
                topic_params.append(child_id)
            
            cursor.execute(topic_sql, topic_params)
            topic_rows = cursor.fetchall()
            
            # Process topics
            all_topics = []
            for row in topic_rows:
                if row[0]:
                    try:
                        topics = json.loads(row[0])
                        all_topics.extend(topics)
                    except json.JSONDecodeError:
                        pass
            
            topic_counts = dict(self._count_occurrences(all_topics)[:10])
            
            # Get interaction type distribution
            interaction_sql = f"""
                SELECT interaction_type, COUNT(*) as count
                FROM {self.table_name}
                WHERE start_time BETWEEN ? AND ? AND archived = 0
                GROUP BY interaction_type
            """
            interaction_params = [start_date.isoformat(), end_date.isoformat()]
            
            if child_id:
                interaction_sql += " AND child_id = ?"
                interaction_params.append(child_id)
            
            cursor.execute(interaction_sql, interaction_params)
            interaction_distribution = dict(cursor.fetchall())
            
            return {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {
                    'total_conversations': result[0] or 0,
                    'total_duration_hours': (result[1] or 0) / 3600,
                    'average_duration_minutes': ((result[2] or 0) / 60) if result[2] else 0,
                    'total_messages': result[3] or 0,
                    'average_messages_per_conversation': result[4] or 0
                },
                'topics': {
                    'distribution': topic_counts,
                    'total_unique': len(set(all_topics)),
                    'most_discussed': max(topic_counts.items(), key=lambda x: x[1])[0] if topic_counts else None
                },
                'interaction_types': interaction_distribution,
                'quality_metrics': {
                    'average_quality_score': result[5] or 0,
                    'average_engagement_score': result[7] or 0,
                    'average_safety_score': result[6] or 1.0
                },
                'safety': {
                    'flagged_conversations': result[8] or 0,
                    'safety_percentage': ((result[0] - (result[8] or 0)) / result[0] * 100) if result[0] else 100
                }
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error generating conversation analytics: {e}")
            raise
    
    async def get_conversations_by_time_range(
        self,
        time_range: TimeRange,
        child_id: Optional[str] = None,
        custom_start: Optional[datetime] = None,
        custom_end: Optional[datetime] = None
    ) -> List[Conversation]:
        """Get conversations by predefined time range"""
        start_date, end_date = self._calculate_time_range(
            time_range, custom_start, custom_end
        )
        
        return await self.get_conversations_by_child(
            child_id, start_date, end_date
        ) if child_id else await self._get_conversations_in_range(start_date, end_date)
    
    async def _get_conversations_in_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Conversation]:
        """Get all conversations in date range"""
        try:
            cursor = self._connection.cursor()
            sql = f"""
                SELECT * FROM {self.table_name}
                WHERE start_time BETWEEN ? AND ? AND archived = 0
                ORDER BY start_time DESC
            """
            cursor.execute(sql, (start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            return [self._deserialize_conversation_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversations in range: {e}")
            raise
    
    async def get_today_interactions(self, child_id: str) -> List[Conversation]:
        """Get today's conversations for a child"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return await self.get_conversations_by_child(child_id, start_date=today)
    
    async def get_active_conversations(
        self,
        inactive_threshold_minutes: int = 30
    ) -> List[Conversation]:
        """Get currently active conversations"""
        threshold = datetime.now() - timedelta(minutes=inactive_threshold_minutes)
        
        try:
            cursor = self._connection.cursor()
            sql = f"""
                SELECT * FROM {self.table_name}
                WHERE end_time IS NULL AND start_time >= ? AND archived = 0
                ORDER BY start_time DESC
            """
            cursor.execute(sql, (threshold.isoformat(),))
            
            rows = cursor.fetchall()
            return [self._deserialize_conversation_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving active conversations: {e}")
            raise
    
    # Maintenance and cleanup methods
    
    async def delete_old_conversations(
        self, 
        retention_days: int = 90,
        exclude_flagged: bool = True
    ) -> int:
        """Delete old conversations"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            with self.transaction() as cursor:
                sql = f"DELETE FROM {self.table_name} WHERE start_time < ?"
                params = [cutoff_date.isoformat()]
                
                if exclude_flagged:
                    sql += " AND safety_score >= 1.0"
                
                cursor.execute(sql, params)
                
                return cursor.rowcount
                
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting old conversations: {e}")
            raise
    
    async def archive_conversations(
        self,
        days_old: int = 30,
        archive_path: str = "archives/"
    ) -> int:
        """Archive old conversations to storage"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        try:
            with self.transaction() as cursor:
                # Mark conversations as archived
                sql = f"""
                    UPDATE {self.table_name} 
                    SET archived = 1, updated_at = ?
                    WHERE start_time < ? AND archived = 0 AND parent_visible = 1
                """
                cursor.execute(sql, (datetime.now().isoformat(), cutoff_date.isoformat()))
                
                return cursor.rowcount
                
        except sqlite3.Error as e:
            self.logger.error(f"Error archiving conversations: {e}")
            raise
    
    # Search and filtering methods
    
    async def search_conversation_content(
        self,
        query: str,
        child_id: Optional[str] = None,
        search_in: List[MessageRole] = None
    ) -> List[Tuple[Conversation, List[Message]]]:
        """Full-text search in conversation messages"""
        if search_in is None:
            search_in = [MessageRole.USER, MessageRole.ASSISTANT]
        
        try:
            cursor = self._connection.cursor()
            
            # Build search query
            role_conditions = []
            for role in search_in:
                role_conditions.append("m.role = ?")
            
            sql = f"""
                SELECT DISTINCT c.*, m.id as message_id, m.content, m.role, m.timestamp as msg_timestamp
                FROM {self.table_name} c
                JOIN messages m ON c.id = m.conversation_id
                WHERE ({' OR '.join(role_conditions)}) 
                AND m.content LIKE ? 
                AND c.archived = 0
            """
            
            params = [role.value for role in search_in]
            params.append(f"%{query}%")
            
            if child_id:
                sql += " AND c.child_id = ?"
                params.append(child_id)
            
            sql += " ORDER BY c.start_time DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Group results by conversation
            conversation_messages = defaultdict(list)
            conversations = {}
            
            for row in rows:
                row_dict = dict(row)
                conv_id = row_dict['id']
                
                # Create conversation object if not exists
                if conv_id not in conversations:
                    conv_data = {k: v for k, v in row_dict.items() 
                               if k not in ['message_id', 'content', 'role', 'msg_timestamp']}
                    conversations[conv_id] = self._deserialize_conversation_from_db(conv_data)
                
                # Create message object
                message = Message(
                    id=row_dict['message_id'],
                    role=MessageRole(row_dict['role']),
                    content=row_dict['content'],
                    timestamp=datetime.fromisoformat(row_dict['msg_timestamp']) if row_dict['msg_timestamp'] else None
                )
                conversation_messages[conv_id].append(message)
            
            # Return list of (conversation, matching_messages) tuples
            results = []
            for conv_id, conv in conversations.items():
                results.append((conv, conversation_messages[conv_id]))
            
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"Error searching conversation content: {e}")
            raise
    
    async def get_conversation_statistics(self) -> Dict[str, Any]:
        """Get overall conversation statistics"""
        try:
            cursor = self._connection.cursor()
            
            # Basic counts
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name} WHERE archived = 0")
            total_conversations = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(DISTINCT child_id) FROM {self.table_name} WHERE archived = 0")
            unique_children = cursor.fetchone()[0]
            
            # Time statistics
            cursor.execute(f"""
                SELECT 
                    SUM(duration) as total_duration,
                    AVG(duration) as avg_duration,
                    MIN(start_time) as earliest_conversation,
                    MAX(start_time) as latest_conversation
                FROM {self.table_name} 
                WHERE archived = 0 AND duration IS NOT NULL
            """)
            time_stats = cursor.fetchone()
            
            # Quality statistics
            cursor.execute(f"""
                SELECT 
                    AVG(quality_score) as avg_quality,
                    AVG(safety_score) as avg_safety,
                    COUNT(CASE WHEN safety_score < 1.0 THEN 1 END) as flagged_count
                FROM {self.table_name} 
                WHERE archived = 0
            """)
            quality_stats = cursor.fetchone()
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(days=7)
            cursor.execute(f"""
                SELECT COUNT(*) FROM {self.table_name} 
                WHERE start_time >= ? AND archived = 0
            """, (recent_cutoff.isoformat(),))
            recent_conversations = cursor.fetchone()[0]
            
            return {
                'total_conversations': total_conversations,
                'unique_children': unique_children,
                'time_statistics': {
                    'total_duration_hours': (time_stats[0] or 0) / 3600,
                    'average_duration_minutes': ((time_stats[1] or 0) / 60),
                    'earliest_conversation': time_stats[2],
                    'latest_conversation': time_stats[3]
                },
                'quality_statistics': {
                    'average_quality_score': quality_stats[0] or 0,
                    'average_safety_score': quality_stats[1] or 1.0,
                    'flagged_conversations': quality_stats[2] or 0,
                    'safety_percentage': ((total_conversations - (quality_stats[2] or 0)) / total_conversations * 100) if total_conversations else 100
                },
                'recent_activity': {
                    'conversations_last_7_days': recent_conversations,
                    'activity_percentage': (recent_conversations / total_conversations * 100) if total_conversations else 0
                }
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error getting conversation statistics: {e}")
            raise
    
    # Daily summary and reporting
    
    async def generate_daily_summary(
        self,
        date: date,
        child_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate daily conversation summary"""
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        conversations = await self.get_conversations_by_child(
            child_id, start, end
        ) if child_id else await self._get_conversations_in_range(start, end)
        
        if not conversations:
            return {'date': date.isoformat(), 'no_activity': True}
        
        # Aggregate metrics
        total_time = sum(
            c.duration.total_seconds() for c in conversations if c.duration
        )
        
        all_topics = []
        all_emotions = []
        
        for conv in conversations:
            all_topics.extend(conv.topics if conv.topics else [])
            all_emotions.extend([
                state.primary_emotion 
                for state in conv.emotional_states
            ] if conv.emotional_states else [])
        
        return {
            'date': date.isoformat(),
            'summary': {
                'total_conversations': len(conversations),
                'total_time_minutes': round(total_time / 60, 1),
                'unique_children': len(set(c.child_id for c in conversations)),
                'topics_discussed': dict(self._count_occurrences(all_topics)[:5]),
                'dominant_emotions': dict(self._count_occurrences(all_emotions)[:3]),
                'average_quality': sum(c.quality_score for c in conversations if c.quality_score) / len([c for c in conversations if c.quality_score]) if any(c.quality_score for c in conversations) else 0,
                'educational_conversations': sum(
                    1 for c in conversations 
                    if c.interaction_type == InteractionType.LEARNING
                ),
                'flagged_conversations': sum(
                    1 for c in conversations 
                    if c.safety_score and c.safety_score < 1.0
                )
            }
        }
    
    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # Additional enterprise-level methods
    
    async def find_conversations_requiring_review(self) -> List[Conversation]:
        """
        Find conversations that may require manual review
        Based on safety scores, unusual patterns, or flagged content
        
        Returns:
            List of conversations requiring review
        """
        try:
            cursor = self._connection.cursor()
            
            # Conversations with low safety scores or high moderation flags
            sql = f"""
                SELECT * FROM {self.table_name} 
                WHERE (
                    safety_score < 0.8 OR 
                    moderation_flags > 2 OR
                    (total_messages > 50 AND duration_seconds < 300)
                ) AND archived = 0
                ORDER BY safety_score ASC, moderation_flags DESC
            """
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            return [self._deserialize_conversation_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding conversations requiring review: {e}")
            raise
    
    async def get_conversation_health_metrics(self, child_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive health metrics for a child's conversations
        
        Args:
            child_id: Child's unique identifier
            
        Returns:
            Dictionary with health metrics and insights
        """
        try:
            cursor = self._connection.cursor()
            
            # Get all conversations for the child
            cursor.execute(f"""
                SELECT * FROM {self.table_name} 
                WHERE child_id = ? AND archived = 0 
                ORDER BY start_time
            """, (child_id,))
            
            conversations = [self._deserialize_conversation_from_db(dict(row)) for row in cursor.fetchall()]
            
            if not conversations:
                return {"status": "no_data", "child_id": child_id}
            
            # Calculate health metrics
            total_conversations = len(conversations)
            recent_conversations = [
                c for c in conversations 
                if c.start_time and (datetime.now() - c.start_time).days <= 30
            ]
            
            # Safety analysis
            safety_scores = [c.safety_score for c in conversations if c.safety_score is not None]
            avg_safety = sum(safety_scores) / len(safety_scores) if safety_scores else 1.0
            low_safety_count = sum(1 for score in safety_scores if score < 0.8)
            
            # Engagement trends
            engagement_scores = [c.engagement_score for c in conversations if c.engagement_score is not None]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0
            
            # Communication patterns
            avg_messages_per_conversation = sum(c.total_messages for c in conversations) / total_conversations
            avg_duration_minutes = sum(c.duration_seconds or 0 for c in conversations) / total_conversations / 60
            
            # Emotional health analysis
            all_emotions = []
            for conv in conversations:
                if conv.emotional_states:
                    all_emotions.extend([state.primary_emotion for state in conv.emotional_states])
            
            emotion_distribution = Counter(all_emotions)
            positive_emotions = sum(
                count for emotion, count in emotion_distribution.items() 
                if emotion in ['happy', 'excited', 'confident', 'calm']
            )
            negative_emotions = sum(
                count for emotion, count in emotion_distribution.items() 
                if emotion in ['sad', 'angry', 'frustrated', 'anxious']
            )
            
            emotional_balance = (positive_emotions / (positive_emotions + negative_emotions)) if (positive_emotions + negative_emotions) > 0 else 0.5
            
            # Generate recommendations
            recommendations = []
            health_score = 100  # Start with perfect score
            
            if avg_safety < 0.9:
                recommendations.append("Monitor conversation content more closely")
                health_score -= 15
            
            if avg_engagement < 0.5:
                recommendations.append("Consider strategies to increase child engagement")
                health_score -= 10
            
            if emotional_balance < 0.3:
                recommendations.append("Child may need emotional support - consider involving a counselor")
                health_score -= 20
            
            if len(recent_conversations) < 3:
                recommendations.append("Encourage more regular interaction with AI assistant")
                health_score -= 10
            
            if avg_duration_minutes < 2:
                recommendations.append("Conversations are quite short - consider longer interaction sessions")
                health_score -= 5
            
            health_level = "excellent" if health_score >= 90 else "good" if health_score >= 70 else "needs_attention" if health_score >= 50 else "concerning"
            
            return {
                "status": "success",
                "child_id": child_id,
                "health_score": max(0, health_score),
                "health_level": health_level,
                "metrics": {
                    "total_conversations": total_conversations,
                    "recent_conversations_30_days": len(recent_conversations),
                    "average_safety_score": avg_safety,
                    "average_engagement_score": avg_engagement,
                    "emotional_balance_ratio": emotional_balance,
                    "average_messages_per_conversation": avg_messages_per_conversation,
                    "average_duration_minutes": avg_duration_minutes,
                    "low_safety_incidents": low_safety_count
                },
                "emotional_analysis": {
                    "dominant_emotions": dict(emotion_distribution.most_common(5)),
                    "positive_emotion_percentage": (positive_emotions / len(all_emotions) * 100) if all_emotions else 0,
                    "emotional_variety": len(emotion_distribution)
                },
                "recommendations": recommendations,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating health metrics: {e}")
            return {"status": "error", "message": str(e)}
    
    async def optimize_conversation_performance(self) -> Dict[str, Any]:
        """
        Analyze and suggest optimizations for conversation performance
        
        Returns:
            Dictionary with optimization suggestions
        """
        try:
            cursor = self._connection.cursor()
            
            # Analyze conversation patterns
            cursor.execute(f"""
                SELECT 
                    AVG(CASE WHEN end_time IS NOT NULL THEN 
                        (julianday(end_time) - julianday(start_time)) * 24 * 60 
                        ELSE NULL END) as avg_duration_minutes,
                    AVG(total_messages) as avg_messages,
                    COUNT(*) as total_conversations,
                    COUNT(CASE WHEN safety_score < 1.0 THEN 1 END) as flagged_conversations,
                    AVG(quality_score) as avg_quality
                FROM {self.table_name} 
                WHERE archived = 0 AND start_time >= datetime('now', '-30 days')
            """)
            
            stats = cursor.fetchone()
            
            optimizations = []
            performance_score = 100
            
            # Analyze performance bottlenecks
            if stats[0] and stats[0] > 15:  # Average duration > 15 minutes
                optimizations.append({
                    "area": "Duration Management",
                    "issue": "Conversations are running longer than optimal",
                    "suggestion": "Consider implementing time limits or conversation breaks",
                    "impact": "medium"
                })
                performance_score -= 10
            
            if stats[1] and stats[1] > 20:  # Too many messages per conversation
                optimizations.append({
                    "area": "Message Efficiency",
                    "issue": "High message count per conversation",
                    "suggestion": "Optimize AI responses to be more concise and effective",
                    "impact": "low"
                })
                performance_score -= 5
            
            if stats[3] and (stats[3] / stats[2]) > 0.05:  # More than 5% flagged
                optimizations.append({
                    "area": "Content Safety",
                    "issue": "High rate of flagged conversations",
                    "suggestion": "Review and improve content moderation rules",
                    "impact": "high"
                })
                performance_score -= 25
            
            if stats[4] and stats[4] < 0.7:  # Low quality score
                optimizations.append({
                    "area": "Conversation Quality",
                    "issue": "Below-average conversation quality scores",
                    "suggestion": "Review AI model performance and fine-tune responses",
                    "impact": "high"
                })
                performance_score -= 20
            
            # Database performance recommendations
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
            index_count = cursor.fetchone()[0]
            
            if index_count < 10:
                optimizations.append({
                    "area": "Database Performance",
                    "issue": "Insufficient database indexes",
                    "suggestion": "Add more indexes for frequently queried fields",
                    "impact": "medium"
                })
                performance_score -= 5
            
            return {
                "performance_score": max(0, performance_score),
                "performance_level": "excellent" if performance_score >= 90 else "good" if performance_score >= 70 else "needs_improvement",
                "statistics": {
                    "avg_duration_minutes": stats[0] or 0,
                    "avg_messages_per_conversation": stats[1] or 0,
                    "total_recent_conversations": stats[2] or 0,
                    "flagged_rate_percentage": ((stats[3] or 0) / (stats[2] or 1)) * 100,
                    "avg_quality_score": stats[4] or 0
                },
                "optimizations": optimizations,
                "recommendations": {
                    "immediate": [opt for opt in optimizations if opt["impact"] == "high"],
                    "planned": [opt for opt in optimizations if opt["impact"] == "medium"],
                    "optional": [opt for opt in optimizations if opt["impact"] == "low"]
                },
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in performance optimization analysis: {e}")
            return {"status": "error", "message": str(e)}