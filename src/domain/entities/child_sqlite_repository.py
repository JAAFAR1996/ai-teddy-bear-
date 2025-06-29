import os
import sqlite3
import json
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from src.infrastructure.persistence.base_sqlite_repository import BaseSQLiteRepository
from src.domain.entities.child import Child
from src.domain.repositories.child_repository import ChildRepository
from src.domain.repositories.base import SearchCriteria, QueryOptions, SortOrder


class ChildSQLiteRepository(BaseSQLiteRepository[Child, int], ChildRepository):

    """
    SQLite implementation of Child Repository
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
        Initialize Child SQLite Repository
        
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
            table_name='children', 
            entity_class=Child
        )
        
    async def initialize(self):
        # لا تفعل شيئاً هنا
        pass
    
    def _get_table_schema(self) -> str:
        """
        Get the CREATE TABLE SQL statement for children table
        
        Returns:
            str: SQL CREATE TABLE statement
        """
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
    
    def _serialize_child_for_db(self, child: Child) -> Dict[str, Any]:
        """
        Serialize child entity for database storage
        
        Args:
            child: Child entity
            
        Returns:
            Dictionary for database storage
        """
        data = child.dict() if hasattr(child, 'dict') else child.__dict__.copy()
        
        # Generate ID if not present
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
    async def add(self, child: Child) -> Child:
        """
        Add a new child (alias for create)
        
        Args:
            child: Child entity to add
            
        Returns:
            Added child with assigned ID
        """
        return await self.create(child)

    async def aggregate(
        self, 
        field: str, 
        operation: str, 
        criteria: Optional[List[SearchCriteria]] = None
    ) -> Any:
        """
        Perform aggregation operations on child data
        
        Args:
            field: Field to aggregate (age, total_interaction_time, etc.)
            operation: Operation type ('count', 'avg', 'sum', 'min', 'max')
            criteria: Optional search criteria to filter data
            
        Returns:
            Aggregation result
        """
        try:
            with self.transaction() as cursor:
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
                        sql += " WHERE " + " AND ".join(conditions) + " AND is_active = 1"
                    else:
                        sql += " WHERE is_active = 1"
                else:
                    sql += " WHERE is_active = 1"
                
                cursor.execute(sql, params)
                result = cursor.fetchone()
                
                return result[0] if result and result[0] is not None else 0
                
        except sqlite3.Error as e:
            self.logger.error(f"Error in aggregation operation: {e}")
            raise

    async def find_by_learning_level(self, level: str) -> List[Child]:
        """
        Find children by educational learning level
        
        Args:
            level: Educational level ('beginner', 'intermediate', 'advanced', etc.)
            
        Returns:
            List of children matching the learning level
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE educational_level = ? AND is_active = 1"
            cursor.execute(sql, (level,))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children by learning level: {e}")
            raise

    async def find_by_parent(self, parent_id: str) -> List[Child]:
        """
        Find all children belonging to a specific parent
        
        Args:
            parent_id: Parent's unique identifier
            
        Returns:
            List of children belonging to the parent
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE parent_id = ? AND is_active = 1 ORDER BY created_at DESC"
            cursor.execute(sql, (parent_id,))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children by parent: {e}")
            raise

    async def get(self, child_id: str) -> Optional[Child]:
        """
        Get child by ID (alias for get_by_id)
        
        Args:
            child_id: Child's unique identifier
            
        Returns:
            Child entity or None if not found
        """
        return await self.get_by_id(child_id)

    async def get_inactive_children(self, days_inactive: int = 30) -> List[Child]:
        """
        Get children who have been inactive for specified number of days
        
        Args:
            days_inactive: Number of days of inactivity
            
        Returns:
            List of inactive children
        """
        cutoff_date = datetime.now() - timedelta(days=days_inactive)
        
        try:
            cursor = self._connection.cursor()
            sql = f"""
                SELECT * FROM {self.table_name} 
                WHERE (last_interaction IS NULL OR last_interaction < ?) 
                AND is_active = 1
                ORDER BY last_interaction ASC
            """
            cursor.execute(sql, (cutoff_date.isoformat(),))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding inactive children: {e}")
            raise
    
    async def get_children_by_family(self, family_code: str) -> List[Child]:
        """
        Get all children belonging to the same family
        
        Args:
            family_code: Family code for grouping siblings
            
        Returns:
            List of children in the same family
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE family_code = ? AND is_active = 1 ORDER BY age ASC"
            cursor.execute(sql, (family_code,))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children by family: {e}")
            raise
    
    async def find_by_communication_style(self, style: str) -> List[Child]:
        """
        Find children by their preferred communication style
        
        Args:
            style: Communication style ('formal', 'casual', 'playful', etc.)
            
        Returns:
            List of children with matching communication style
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE communication_style = ? AND is_active = 1"
            cursor.execute(sql, (style,))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children by communication style: {e}")
            raise
    
    async def get_children_needing_attention(self) -> List[Child]:
        """
        Get children who may need special attention based on various factors
        
        Returns:
            List of children who may need attention
        """
        try:
            cursor = self._connection.cursor()
            # Children who haven't interacted in 3+ days OR have special needs
            cutoff_date = (datetime.now() - timedelta(days=3)).isoformat()
            
            sql = f"""
                SELECT * FROM {self.table_name} 
                WHERE is_active = 1 AND (
                    last_interaction < ? OR 
                    last_interaction IS NULL OR
                    special_needs != '[]' OR
                    medical_notes IS NOT NULL
                )
                ORDER BY last_interaction ASC
            """
            cursor.execute(sql, (cutoff_date,))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children needing attention: {e}")
            raise
    
    async def update_interaction_analytics(self, child_id: str, additional_time: int, topics: List[str]) -> bool:
        """
        Update child's interaction analytics after a session
        
        Args:
            child_id: Child's unique identifier
            additional_time: Additional interaction time in seconds
            topics: List of topics discussed in the session
            
        Returns:
            True if updated successfully
        """
        try:
            with self.transaction() as cursor:
                # Update interaction time and last interaction
                current_time = datetime.now().isoformat()
                
                # Get current data
                cursor.execute(f"SELECT total_interaction_time, allowed_topics FROM {self.table_name} WHERE id = ?", (child_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                
                current_time_total = row[0] or 0
                current_topics = json.loads(row[1]) if row[1] else []
                
                # Add new topics if not already present
                for topic in topics:
                    if topic not in current_topics:
                        current_topics.append(topic)
                
                # Update database
                sql = f"""
                    UPDATE {self.table_name} 
                    SET total_interaction_time = ?, 
                        last_interaction = ?, 
                        allowed_topics = ?,
                        updated_at = ?
                    WHERE id = ?
                """
                
                cursor.execute(sql, (
                    current_time_total + additional_time,
                    current_time,
                    json.dumps(current_topics),
                    current_time,
                    child_id
                ))
                
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            self.logger.error(f"Error updating interaction analytics: {e}")
            raise
    
    async def get_engagement_insights(self, child_id: str) -> Dict[str, Any]:
        """
        Get comprehensive engagement insights for a child
        
        Args:
            child_id: Child's unique identifier
            
        Returns:
            Dictionary with engagement insights and recommendations
        """
        try:
            child = await self.get_by_id(child_id)
            if not child:
                return {}
            
            # Calculate engagement metrics
            total_days_since_creation = (datetime.now() - child.created_at).days
            days_since_last_interaction = 0
            if child.last_interaction:
                days_since_last_interaction = (datetime.now() - child.last_interaction).days
            
            # Engagement level calculation
            engagement_level = "high"
            if days_since_last_interaction > 7:
                engagement_level = "low"
            elif days_since_last_interaction > 3:
                engagement_level = "medium"
            
            # Time usage analysis
            daily_avg_time = child.total_interaction_time / max(total_days_since_creation, 1)
            time_utilization = (child.total_interaction_time / child.max_daily_interaction_time) * 100
            
            # Generate recommendations
            recommendations = []
            if days_since_last_interaction > 3:
                recommendations.append("Consider sending a gentle reminder to engage with the AI assistant")
            
            if time_utilization < 30:
                recommendations.append("Child may benefit from shorter, more frequent interactions")
            elif time_utilization > 90:
                recommendations.append("Consider increasing daily interaction time limit")
            
            if len(child.interests) < 3:
                recommendations.append("Add more interests to personalize conversations")
            
            return {
                "child_id": child_id,
                "engagement_level": engagement_level,
                "days_since_last_interaction": days_since_last_interaction,
                "total_interaction_time": child.total_interaction_time,
                "daily_average_time": daily_avg_time,
                "time_utilization_percentage": time_utilization,
                "interaction_streak": max(0, 7 - days_since_last_interaction),
                "recommendations": recommendations,
                "last_analysis": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating engagement insights: {e}")
            return {}
    
    async def bulk_update_settings(self, updates: List[Dict[str, Any]]) -> BulkOperationResult:
        """
        Bulk update child settings
        
        Args:
            updates: List of update dictionaries with 'child_id' and settings to update
            
        Returns:
            Bulk operation result
        """
        success_count = 0
        failed_count = 0
        failed_ids = []
        
        try:
            with self.transaction() as cursor:
                for update_data in updates:
                    try:
                        child_id = update_data.get('child_id')
                        if not child_id:
                            failed_count += 1
                            failed_ids.append('unknown')
                            continue
                        
                        # Build update SQL dynamically
                        update_fields = []
                        update_values = []
                        
                        for key, value in update_data.items():
                            if key != 'child_id' and hasattr(self, f'_{key}'):
                                update_fields.append(f"{key} = ?")
                                # Serialize JSON fields
                                if key in ['interests', 'personality_traits', 'allowed_topics', 'restricted_topics']:
                                    update_values.append(json.dumps(value) if value else None)
                                else:
                                    update_values.append(value)
                        
                        if update_fields:
                            update_fields.append("updated_at = ?")
                            update_values.append(datetime.now().isoformat())
                            update_values.append(child_id)
                            
                            sql = f"UPDATE {self.table_name} SET {', '.join(update_fields)} WHERE id = ?"
                            cursor.execute(sql, update_values)
                            
                            if cursor.rowcount > 0:
                                success_count += 1
                            else:
                                failed_count += 1
                                failed_ids.append(child_id)
                        else:
                            failed_count += 1
                            failed_ids.append(child_id)
                            
                    except Exception as e:
                        failed_count += 1
                        child_id = update_data.get('child_id', 'unknown')
                        failed_ids.append(child_id)
                        self.logger.warning(f"Failed to update child {child_id}: {e}")
                
        except sqlite3.Error as e:
            self.logger.error(f"Error in bulk update: {e}")
            raise
        
        from src.domain.repositories.base import BulkOperationResult
        return BulkOperationResult(
            success_count=success_count,
            failed_count=failed_count,
            failed_ids=failed_ids
        )
    
    async def search_by_multiple_criteria(
        self, 
        name_query: Optional[str] = None,
        age_range: Optional[Tuple[int, int]] = None,
        languages: Optional[List[str]] = None,
        interests: Optional[List[str]] = None,
        has_special_needs: Optional[bool] = None
    ) -> List[Child]:
        """
        Advanced search with multiple criteria
        
        Args:
            name_query: Search in child names (partial match)
            age_range: Tuple of (min_age, max_age)
            languages: List of preferred languages
            interests: List of interests to match
            has_special_needs: Filter by presence of special needs
            
        Returns:
            List of children matching the criteria
        """
        try:
            cursor = self._connection.cursor()
            
            # Build dynamic query
            conditions = ["is_active = 1"]
            params = []
            
            if name_query:
                conditions.append("name LIKE ?")
                params.append(f"%{name_query}%")
            
            if age_range:
                min_age, max_age = age_range
                conditions.append("age BETWEEN ? AND ?")
                params.extend([min_age, max_age])
            
            if languages:
                language_conditions = []
                for lang in languages:
                    language_conditions.append("language_preference = ?")
                    params.append(lang)
                if language_conditions:
                    conditions.append(f"({' OR '.join(language_conditions)})")
            
            if has_special_needs is not None:
                if has_special_needs:
                    conditions.append("special_needs != '[]' AND special_needs IS NOT NULL")
                else:
                    conditions.append("(special_needs = '[]' OR special_needs IS NULL)")
            
            # Handle interests search
            if interests:
                interest_conditions = []
                for interest in interests:
                    interest_conditions.append("JSON_EXTRACT(interests, '$') LIKE ?")
                    params.append(f'%"{interest}"%')
                if interest_conditions:
                    conditions.append(f"({' OR '.join(interest_conditions)})")
            
            sql = f"SELECT * FROM {self.table_name} WHERE {' AND '.join(conditions)} ORDER BY name"
            cursor.execute(sql, params)
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error in advanced search: {e}")
            raise

    def _deserialize_child_from_db(self, data: Dict[str, Any]) -> Child:
        """
        Deserialize child data from database
        
        Args:
            data: Database row data
            
        Returns:
            Child entity
        """
        # Parse JSON fields
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
    
    async def create(self, child: Child) -> Child:
        """
        Create a new child profile
        
        Args:
            child: Child entity to create
            
        Returns:
            Created child with assigned ID
        """
        try:
            with self.transaction() as cursor:
                data = self._serialize_child_for_db(child)
                
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
                
                cursor.execute(sql, list(data.values()))
                
                # Assign ID if not already present
                if not child.id:
                    child.id = data['id']
                
                return child
                
        except sqlite3.Error as e:
            self.logger.error(f"Error creating child: {e}")
            raise
    
    async def get_by_id(self, child_id: str) -> Optional[Child]:
        """
        Retrieve child by ID
        
        Args:
            child_id: Child's unique identifier
            
        Returns:
            Child entity or None
        """
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
        """
        Update existing child profile
        
        Args:
            child: Child entity to update
            
        Returns:
            Updated child
        """
        try:
            with self.transaction() as cursor:
                data = self._serialize_child_for_db(child)
                
                if 'id' not in data or not data['id']:
                    raise ValueError("Child must have an ID for update")
                
                # Prepare update SQL
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
        """
        Soft delete child (mark as inactive)
        
        Args:
            child_id: Child's unique identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            with self.transaction() as cursor:
                sql = f"UPDATE {self.table_name} SET is_active = 0, updated_at = ? WHERE id = ?"
                cursor.execute(sql, (datetime.now().isoformat(), child_id))
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting child {child_id}: {e}")
            raise
    
    async def list(self, options: Optional[QueryOptions] = None) -> List[Child]:
        """
        List active children with optional filtering and sorting
        
        Args:
            options: Query options
            
        Returns:
            List of children
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE is_active = 1"
            params = []
            
            # Apply additional filters
            if options and hasattr(options, 'filters') and options.filters:
                filter_conditions = []
                for key, value in options.filters.items():
                    filter_conditions.append(f"{key} = ?")
                    params.append(self._serialize_for_db(value))
                
                if filter_conditions:
                    sql += " AND " + " AND ".join(filter_conditions)
            
            # Apply sorting
            if options and hasattr(options, 'sort_by') and options.sort_by:
                order = "DESC" if hasattr(options, 'sort_order') and options.sort_order == SortOrder.DESC else "ASC"
                sql += f" ORDER BY {options.sort_by} {order}"
            
            # Apply pagination
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
    
    # Child-specific repository methods
    
    async def find_by_name(self, name: str) -> Optional[Child]:
        """
        Find a child by their name
        
        Args:
            name: Child's name
        
        Returns:
            Matching child profile or None
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE name = ? AND is_active = 1"
            cursor.execute(sql, (name,))
            
            row = cursor.fetchone()
            if row:
                return self._deserialize_child_from_db(dict(row))
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding child by name: {e}")
            raise
    
    async def find_by_age_range(self, min_age: int, max_age: int) -> List[Child]:
        """
        Find children within a specific age range
        
        Args:
            min_age: Minimum age (inclusive)
            max_age: Maximum age (inclusive)
        
        Returns:
            List of children in the specified age range
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE age BETWEEN ? AND ? AND is_active = 1"
            cursor.execute(sql, (min_age, max_age))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children by age range: {e}")
            raise
    
    async def find_by_interests(self, interests: List[str], match_all: bool = False) -> List[Child]:
        """
        Find children with matching interests
        
        Args:
            interests: List of interests to match
            match_all: Whether to match all interests or any
        
        Returns:
            List of children with matching interests
        """
        try:
            cursor = self._connection.cursor()
            
            if match_all:
                # Use JSON functions for exact matching
                conditions = []
                params = []
                for interest in interests:
                    conditions.append("JSON_EXTRACT(interests, '$') LIKE ?")
                    params.append(f'%"{interest}"%')
                
                sql = f"SELECT * FROM {self.table_name} WHERE {' AND '.join(conditions)} AND is_active = 1"
            else:
                # Match any interest
                conditions = []
                params = []
                for interest in interests:
                    conditions.append("JSON_EXTRACT(interests, '$') LIKE ?")
                    params.append(f'%"{interest}"%')
                
                sql = f"SELECT * FROM {self.table_name} WHERE ({' OR '.join(conditions)}) AND is_active = 1"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children by interests: {e}")
            raise
    
    async def find_by_language(self, language: str) -> List[Child]:
        """
        Find children by language preference
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
        
        Returns:
            List of children with matching language preference
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE language_preference = ? AND is_active = 1"
            cursor.execute(sql, (language,))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children by language: {e}")
            raise
    
    async def get_children_with_recent_interactions(self, days: int = 7) -> List[Child]:
        """
        Get children who have had interactions within the last N days
        
        Args:
            days: Number of days to look back
        
        Returns:
            Children with recent interactions
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE last_interaction >= ? AND is_active = 1"
            cursor.execute(sql, (cutoff_date.isoformat(),))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children with recent interactions: {e}")
            raise
    
    async def get_children_by_max_interaction_time(self, max_time: int) -> List[Child]:
        """
        Get children with maximum daily interaction time less than or equal to specified time
        
        Args:
            max_time: Maximum daily interaction time in seconds
        
        Returns:
            Children matching the interaction time criteria
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE max_daily_interaction_time <= ? AND is_active = 1"
            cursor.execute(sql, (max_time,))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children by max interaction time: {e}")
            raise
    
    async def get_children_by_age_group(self, age_group: str) -> List[Child]:
        """
        Get children by predefined age groups
        
        Args:
            age_group: Age group ('preschool', 'elementary', 'middle', 'high')
        
        Returns:
            Children in the specified age group
        """
        age_ranges = {
            'preschool': (3, 5),
            'elementary': (6, 11),
            'middle': (12, 14),
            'high': (15, 18)
        }
        
        if age_group not in age_ranges:
            raise ValueError(f"Invalid age group: {age_group}")
        
        min_age, max_age = age_ranges[age_group]
        return await self.find_by_age_range(min_age, max_age)
    
    async def update_last_interaction(self, child_id: str) -> bool:
        """
        Update last interaction timestamp for a child
        
        Args:
            child_id: Child's unique identifier
        
        Returns:
            True if updated successfully
        """
        try:
            with self.transaction() as cursor:
                sql = f"UPDATE {self.table_name} SET last_interaction = ?, updated_at = ? WHERE id = ? AND is_active = 1"
                now = datetime.now().isoformat()
                cursor.execute(sql, (now, now, child_id))
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            self.logger.error(f"Error updating last interaction: {e}")
            raise
    
    async def update_interaction_time(self, child_id: str, additional_time: int) -> bool:
        """
        Add to total interaction time for a child
        
        Args:
            child_id: Child's unique identifier
            additional_time: Additional interaction time in seconds
        
        Returns:
            True if updated successfully
        """
        try:
            with self.transaction() as cursor:
                sql = f"""
                    UPDATE {self.table_name} 
                    SET total_interaction_time = total_interaction_time + ?, 
                        last_interaction = ?,
                        updated_at = ? 
                    WHERE id = ? AND is_active = 1
                """
                now = datetime.now().isoformat()
                cursor.execute(sql, (additional_time, now, now, child_id))
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            self.logger.error(f"Error updating interaction time: {e}")
            raise
    
    async def reset_daily_interaction_time(self) -> int:
        """
        Reset daily interaction tracking for all children
        
        Returns:
            Number of children updated
        """
        try:
            with self.transaction() as cursor:
                # Reset daily interaction tracking fields
                sql = f"""
                    UPDATE {self.table_name} 
                    SET total_interaction_time = 0,
                        updated_at = ?
                    WHERE is_active = 1
                """
                cursor.execute(sql, (datetime.now().isoformat(),))
                return cursor.rowcount
                
        except sqlite3.Error as e:
            self.logger.error(f"Error resetting daily interaction time: {e}")
            raise
    
    async def get_children_over_time_limit(self) -> List[Child]:
        """
        Get children who have exceeded their daily interaction time limit
        
        Returns:
            List of children over their time limit
        """
        try:
            cursor = self._connection.cursor()
            sql = f"""
                SELECT * FROM {self.table_name} 
                WHERE total_interaction_time >= max_daily_interaction_time 
                AND is_active = 1
            """
            cursor.execute(sql)
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error finding children over time limit: {e}")
            raise
    
    async def search_children(self, query: str) -> List[Child]:
        """
        Search children by name, interests, or other text fields
        
        Args:
            query: Search query
        
        Returns:
            List of matching children
        """
        try:
            cursor = self._connection.cursor()
            sql = f"""
                SELECT * FROM {self.table_name} 
                WHERE (
                    name LIKE ? OR 
                    interests LIKE ? OR 
                    cultural_background LIKE ? OR
                    educational_level LIKE ?
                ) AND is_active = 1
            """
            search_term = f"%{query}%"
            cursor.execute(sql, (search_term, search_term, search_term, search_term))
            
            rows = cursor.fetchall()
            return [self._deserialize_child_from_db(dict(row)) for row in rows]
            
        except sqlite3.Error as e:
            self.logger.error(f"Error searching children: {e}")
            raise
    
    async def get_children_statistics(self) -> Dict[str, Any]:
        """
        Get statistical information about children in the database
        
        Returns:
            Dictionary with various statistics
        """
        try:
            cursor = self._connection.cursor()
            
            # Total count
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name} WHERE is_active = 1")
            total_count = cursor.fetchone()[0]
            
            # Age distribution
            cursor.execute(f"""
                SELECT 
                    MIN(age) as min_age,
                    MAX(age) as max_age,
                    AVG(age) as avg_age
                FROM {self.table_name} 
                WHERE is_active = 1
            """)
            age_stats = cursor.fetchone()
            
            # Language distribution
            cursor.execute(f"""
                SELECT language_preference, COUNT(*) as count
                FROM {self.table_name} 
                WHERE is_active = 1
                GROUP BY language_preference
            """)
            language_distribution = dict(cursor.fetchall())
            
            # Recent activity
            cutoff_date = datetime.now() - timedelta(days=7)
            cursor.execute(f"""
                SELECT COUNT(*) FROM {self.table_name} 
                WHERE last_interaction >= ? AND is_active = 1
            """, (cutoff_date.isoformat(),))
            recent_activity_count = cursor.fetchone()[0]
            
            return {
                'total_children': total_count,
                'age_statistics': {
                    'min_age': age_stats[0] if age_stats[0] else 0,
                    'max_age': age_stats[1] if age_stats[1] else 0,
                    'average_age': round(age_stats[2], 1) if age_stats[2] else 0
                },
                'language_distribution': language_distribution,
                'recent_activity': {
                    'children_active_last_7_days': recent_activity_count,
                    'activity_percentage': round((recent_activity_count / total_count * 100), 1) if total_count > 0 else 0
                }
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error getting children statistics: {e}")
            raise
    
    async def backup_child_data(self, child_id: str) -> Dict[str, Any]:
        """
        Create a backup of all child data
        
        Args:
            child_id: Child's unique identifier
        
        Returns:
            Complete child data backup
        """
        child = await self.get_by_id(child_id)
        if not child:
            raise ValueError(f"Child with ID {child_id} not found")
        
        return {
            'child_profile': child.dict() if hasattr(child, 'dict') else child.__dict__,
            'backup_timestamp': datetime.now().isoformat(),
            'backup_version': '1.0'
        }
    
    async def restore_child_data(self, backup_data: Dict[str, Any]) -> Child:
        """
        Restore child data from backup
        
        Args:
            backup_data: Backup data dictionary
        
        Returns:
            Restored child entity
        """
        child_data = backup_data['child_profile']
        child = Child(**child_data)
        
        # Update or create the child
        existing_child = await self.get_by_id(child.id)
        if existing_child:
            return await self.update(child)
        else:
            return await self.create(child)