"""
Child SQLite Repository - Refactored

Clean Architecture implementation of Child Repository with separated concerns.
"""

import os
import sqlite3
import json
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from src.infrastructure.persistence.base_sqlite_repository import BaseSQLiteRepository
from src.core.domain.entities.child import Child
from src.infrastructure.persistence.child_repository import ChildRepository
from src.infrastructure.persistence.base import SearchCriteria, QueryOptions, SortOrder, BulkOperationResult


class ChildSQLiteRepositoryRefactored(BaseSQLiteRepository[Child, int], ChildRepository):
    """
    Refactored SQLite implementation of Child Repository
    Following Clean Architecture with separated concerns
    """
    
    def __init__(
        self, 
        session_factory,
        db_path: str = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'data', 'teddyai.db'
        )
    ):
        self.session_factory = session_factory
        
        # Ensure data directory exists
        data_dir = os.path.dirname(db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        
        # Create connection
        connection = sqlite3.connect(db_path, check_same_thread=False)
        
        super().__init__(
            connection=connection,
            table_name='children', 
            entity_class=Child
        )
    
    async def initialize(self):
        """Initialize repository (no-op for backwards compatibility)"""
        pass
    
    def _get_table_schema(self) -> str:
        """Get the CREATE TABLE SQL statement for children table"""
        return '''
            CREATE TABLE IF NOT EXISTS children (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                date_of_birth DATE,
                gender TEXT,
                interests TEXT,
                personality_traits TEXT,
                learning_preferences TEXT,
                communication_style TEXT,
                max_daily_interaction_time INTEGER DEFAULT 3600,
                allowed_topics TEXT,
                restricted_topics TEXT,
                language_preference TEXT DEFAULT 'en',
                cultural_background TEXT,
                parental_controls TEXT,
                emergency_contacts TEXT,
                medical_notes TEXT,
                educational_level TEXT,
                special_needs TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_interaction DATETIME,
                total_interaction_time INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                privacy_settings TEXT,
                custom_settings TEXT
            )
        '''
    
    # ======= CORE CRUD OPERATIONS =======
    
    async def create(self, child: Child) -> Child:
        """Create a new child profile"""
        try:
            with self.transaction() as cursor:
                data = self._serialize_child_for_db(child)
                
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
                
                cursor.execute(sql, list(data.values()))
                
                if not child.id:
                    child.id = data['id']
                
                return child
                
        except sqlite3.Error as e:
            self.logger.error(f"Error creating child: {e}")
            raise
    
    async def get_by_id(self, child_id: str) -> Optional[Child]:
        """Retrieve child by ID"""
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE id = ? AND is_active = 1"
            cursor.execute(sql, (child_id,))
            
            row = cursor.fetchone()
            if row:
                return self._deserialize_child_from_db(dict(row))
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving child {child_id}: {e}")
            raise
    
    async def update(self, child: Child) -> Child:
        """Update existing child profile"""
        try:
            with self.transaction() as cursor:
                data = self._serialize_child_for_db(child)
                
                if 'id' not in data or not data['id']:
                    raise ValueError("Child must have an ID for update")
                
                update_fields = [f"{k} = ?" for k in data.keys() if k != 'id']
                update_values = [v for k, v in data.items() if k != 'id']
                update_values.append(data['id'])
                
                sql = f"UPDATE {self.table_name} SET {', '.join(update_fields)} WHERE id = ?"
                
                cursor.execute(sql, update_values)
                
                if cursor.rowcount == 0:
                    raise ValueError(f"No child found with ID {data['id']}")
                
                return child
                
        except sqlite3.Error as e:
            self.logger.error(f"Error updating child: {e}")
            raise
    
    async def delete(self, child_id: str) -> bool:
        """Soft delete child (mark as inactive)"""
        try:
            with self.transaction() as cursor:
                sql = f"UPDATE {self.table_name} SET is_active = 0, updated_at = ? WHERE id = ?"
                cursor.execute(sql, (datetime.now().isoformat(), child_id))
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting child {child_id}: {e}")
            raise
    
    async def list(self, options: Optional[QueryOptions] = None) -> List[Child]:
        """List active children with optional filtering and sorting"""
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE is_active = 1"
            params = []
            
            if options and hasattr(options, 'sort_by') and options.sort_by:
                order = "DESC" if hasattr(options, 'sort_order') and options.sort_order == SortOrder.DESC else "ASC"
                sql += f" ORDER BY {options.sort_by} {order}"
            
            if options and hasattr(options, 'limit') and options.limit:
                sql += f" LIMIT {options.limit}"
                
            if options and hasattr(options, 'offset') and options.offset:
                sql += f" OFFSET {options.offset}"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error listing children: {e}")
            raise
    
    # ======= DELEGATION TO ORIGINAL METHODS =======
    
    async def find_by_name(self, name: str) -> Optional[Child]:
        """Delegate to original implementation"""
        return await super().find_by_name(name) if hasattr(super(), 'find_by_name') else None
    
    async def find_by_age_range(self, min_age: int, max_age: int) -> List[Child]:
        """Delegate to original implementation"""
        return await super().find_by_age_range(min_age, max_age) if hasattr(super(), 'find_by_age_range') else []
    
    # ======= HELPER METHODS =======
    
    def _serialize_child_for_db(self, child: Child) -> Dict[str, Any]:
        """Serialize child entity for database storage"""
        data = child.dict() if hasattr(child, 'dict') else child.__dict__.copy()
        
        if not data.get('id'):
            data['id'] = str(uuid.uuid4())
        
        # Serialize complex fields to JSON
        json_fields = [
            'interests', 'personality_traits', 'learning_preferences',
            'allowed_topics', 'restricted_topics', 'parental_controls',
            'emergency_contacts', 'privacy_settings', 'custom_settings'
        ]
        
        for field in json_fields:
            if field in data and data[field] is not None:
                data[field] = json.dumps(data[field])
        
        # Handle datetime fields
        if 'date_of_birth' in data and isinstance(data['date_of_birth'], datetime):
            data['date_of_birth'] = data['date_of_birth'].date().isoformat()
        
        # Set updated_at timestamp
        data['updated_at'] = datetime.now().isoformat()
        
        return data
    
    def _deserialize_child_from_db(self, data: Dict[str, Any]) -> Child:
        """Deserialize child data from database"""
        json_fields = [
            'interests', 'personality_traits', 'learning_preferences',
            'allowed_topics', 'restricted_topics', 'parental_controls',
            'emergency_contacts', 'privacy_settings', 'custom_settings'
        ]
        
        for field in json_fields:
            if field in data and data[field]:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = [] if field.endswith('s') else {}
            else:
                data[field] = [] if field.endswith('s') else {}
        
        # Parse datetime fields
        datetime_fields = ['created_at', 'updated_at', 'last_interaction']
        for field in datetime_fields:
            if field in data and data[field]:
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except (ValueError, TypeError):
                    data[field] = None
        
        # Parse date fields
        if 'date_of_birth' in data and data['date_of_birth']:
            try:
                data['date_of_birth'] = datetime.fromisoformat(data['date_of_birth']).date()
            except (ValueError, TypeError):
                data['date_of_birth'] = None
        
        # Convert boolean fields
        if 'is_active' in data:
            data['is_active'] = bool(data['is_active'])
        
        return Child(**data)
