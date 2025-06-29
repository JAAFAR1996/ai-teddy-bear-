# conversation_repository.py - Enhanced repository for conversation management

from typing import List, Optional, Dict, Any, Tuple, AsyncIterator
from datetime import datetime, timedelta, date
from abc import abstractmethod
import json
import csv
import io
from collections import defaultdict, Counter
from enum import Enum

from src.domain.repositories.base import (
    BaseRepository, QueryOptions, SearchCriteria, 
    SortOrder, BulkOperationResult
)
from src.domain.entities.conversation import (
    Conversation, Message, MessageRole, InteractionType,
    EmotionalState, ConversationMetrics, ConversationSummary,
    ContentType
)


class TimeRange(Enum):
    """Predefined time ranges for queries"""
    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    CUSTOM = "custom"


class ConversationRepository(BaseRepository[Conversation, str]):
    """
    Enhanced repository for managing conversation records with advanced analytics
    """
    
    def __init__(self):
        super().__init__(Conversation)
    
    # Basic Retrieval Methods
    
    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """
        Get conversation by session ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            Conversation or None
        """
        pass
    
    @abstractmethod
    async def get_conversations_by_child(
        self, 
        child_id: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Conversation]:
        """
        Retrieve conversations for a specific child
        
        Args:
            child_id: Child's unique identifier
            start_date: Start of date range
            end_date: End of date range
            limit: Maximum number of conversations
        
        Returns:
            List of matching conversations
        """
        pass
    
    @abstractmethod
    async def get_conversations_by_parent(
        self,
        parent_id: str,
        include_all_children: bool = True
    ) -> List[Conversation]:
        """
        Get all conversations for children of a parent
        
        Args:
            parent_id: Parent's ID
            include_all_children: Include all children's conversations
            
        Returns:
            List of conversations
        """
        pass
    
    # Time-based Queries
    
    async def get_conversations_by_time_range(
        self,
        time_range: TimeRange,
        child_id: Optional[str] = None,
        custom_start: Optional[datetime] = None,
        custom_end: Optional[datetime] = None
    ) -> List[Conversation]:
        """
        Get conversations by predefined time range
        
        Args:
            time_range: Time range enum
            child_id: Optional child filter
            custom_start: For CUSTOM range
            custom_end: For CUSTOM range
            
        Returns:
            List of conversations
        """
        start_date, end_date = self._calculate_time_range(
            time_range, custom_start, custom_end
        )
        
        criteria = []
        criteria.append(SearchCriteria('start_time', 'gte', start_date))
        criteria.append(SearchCriteria('start_time', 'lte', end_date))
        
        if child_id:
            criteria.append(SearchCriteria('child_id', 'eq', child_id))
            
        return await self.search(criteria)
    
    async def get_today_interactions(
        self, 
        child_id: str
    ) -> List[Conversation]:
        """Get today's conversations for a child"""
        return await self.get_conversations_by_time_range(
            TimeRange.TODAY,
            child_id=child_id
        )
    
    async def get_active_conversations(
        self,
        inactive_threshold_minutes: int = 30
    ) -> List[Conversation]:
        """
        Get currently active conversations
        
        Args:
            inactive_threshold_minutes: Minutes before considering inactive
            
        Returns:
            List of active conversations
        """
        threshold = datetime.now() - timedelta(minutes=inactive_threshold_minutes)
        
        criteria = [
            SearchCriteria('end_time', 'eq', None),  # Not ended
            SearchCriteria('start_time', 'gte', threshold)
        ]
        
        return await self.search(criteria)
    
    # Topic and Content Queries
    
    @abstractmethod
    async def get_conversations_by_topics(
        self, 
        topics: List[str], 
        match_all: bool = False,
        child_id: Optional[str] = None
    ) -> List[Conversation]:
        """
        Retrieve conversations by topics
        
        Args:
            topics: List of topics to match
            match_all: Require all topics to be present
            child_id: Optional child ID filter
        
        Returns:
            List of matching conversations
        """
        pass
    
    async def search_conversation_content(
        self,
        query: str,
        child_id: Optional[str] = None,
        search_in: List[MessageRole] = None
    ) -> List[Tuple[Conversation, List[Message]]]:
        """
        Full-text search in conversation messages
        
        Args:
            query: Search query
            child_id: Optional child filter
            search_in: Roles to search in
            
        Returns:
            List of (conversation, matching_messages) tuples
        """
        if search_in is None:
            search_in = [MessageRole.USER, MessageRole.ASSISTANT]
            
        results = []
        
        # Get all conversations
        if child_id:
            conversations = await self.get_conversations_by_child(child_id)
        else:
            conversations = await self.list()
            
        # Search in messages
        for conv in conversations:
            matching_messages = []
            
            for msg in conv.messages:
                if msg.role in search_in and query.lower() in msg.content.lower():
                    matching_messages.append(msg)
                    
            if matching_messages:
                results.append((conv, matching_messages))
                
        return results
    
    async def get_conversations_by_interaction_type(
        self,
        interaction_type: InteractionType,
        child_id: Optional[str] = None
    ) -> List[Conversation]:
        """Get conversations by interaction type"""
        criteria = [
            SearchCriteria('interaction_type', 'eq', interaction_type.value)
        ]
        
        if child_id:
            criteria.append(SearchCriteria('child_id', 'eq', child_id))
            
        return await self.search(criteria)
    
    # Emotional Analysis Queries
    
    @abstractmethod
    async def get_conversations_by_emotional_tone(
        self, 
        emotion: str, 
        threshold: float = 0.5,
        child_id: Optional[str] = None
    ) -> List[Conversation]:
        """
        Retrieve conversations by emotional tone
        
        Args:
            emotion: Emotional tone to filter
            threshold: Minimum emotion intensity
            child_id: Optional child ID filter
        
        Returns:
            List of matching conversations
        """
        pass
    
    async def get_emotional_patterns(
        self,
        child_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze emotional patterns over time
        
        Args:
            child_id: Child's ID
            days: Number of days to analyze
            
        Returns:
            Emotional pattern analysis
        """
        start_date = datetime.now() - timedelta(days=days)
        conversations = await self.get_conversations_by_child(
            child_id, start_date=start_date
        )
        
        # Analyze emotions by day
        daily_emotions = defaultdict(lambda: defaultdict(float))
        emotion_transitions = defaultdict(int)
        
        for conv in conversations:
            conv_date = conv.start_time.date()
            
            # Track emotions throughout conversation
            prev_emotion = None
            for state in conv.emotional_states:
                daily_emotions[conv_date][state.primary_emotion] += state.confidence
                
                # Track transitions
                if prev_emotion:
                    transition = f"{prev_emotion}->{state.primary_emotion}"
                    emotion_transitions[transition] += 1
                prev_emotion = state.primary_emotion
        
        # Calculate averages
        emotion_summary = {}
        for emotion in ['happy', 'sad', 'neutral', 'excited', 'frustrated']:
            total_days = sum(
                1 for day_emotions in daily_emotions.values()
                if emotion in day_emotions
            )
            if total_days > 0:
                total_score = sum(
                    day_emotions.get(emotion, 0)
                    for day_emotions in daily_emotions.values()
                )
                emotion_summary[emotion] = total_score / total_days
        
        return {
            'daily_emotions': dict(daily_emotions),
            'emotion_summary': emotion_summary,
            'emotion_transitions': dict(emotion_transitions),
            'most_common_emotion': max(
                emotion_summary.items(), 
                key=lambda x: x[1]
            )[0] if emotion_summary else None
        }
    
    # Quality and Safety Queries
    
    async def get_low_quality_conversations(
        self,
        quality_threshold: float = 0.5,
        limit: Optional[int] = None
    ) -> List[Conversation]:
        """Get conversations with low quality scores"""
        criteria = [
            SearchCriteria('quality_score', 'lt', quality_threshold)
        ]
        
        options = QueryOptions(
            limit=limit,
            sort_by='quality_score',
            sort_order=SortOrder.ASC
        )
        
        return await self.search(criteria, options)
    
    async def get_flagged_conversations(
        self,
        child_id: Optional[str] = None,
        severity_threshold: Optional[str] = None
    ) -> List[Conversation]:
        """Get conversations with moderation flags"""
        criteria = [
            SearchCriteria('safety_score', 'lt', 1.0)
        ]
        
        if child_id:
            criteria.append(SearchCriteria('child_id', 'eq', child_id))
            
        conversations = await self.search(criteria)
        
        # Filter by severity if specified
        if severity_threshold:
            filtered = []
            for conv in conversations:
                # Check if any message has high severity flag
                has_severity = any(
                    severity_threshold in msg.metadata.moderation_flags
                    for msg in conv.messages
                    if msg.metadata.moderation_flags
                )
                if has_severity:
                    filtered.append(conv)
            return filtered
            
        return conversations
    
    # Analytics and Statistics
    
    async def get_conversation_analytics(
        self, 
        child_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = 'day'  # day, week, month
    ) -> Dict[str, Any]:
        """
        Generate comprehensive conversation analytics
        
        Args:
            child_id: Optional child ID filter
            start_date: Start of analysis period
            end_date: End of analysis period
            group_by: Grouping period
            
        Returns:
            Detailed analytics dictionary
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
            
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
        
        # Calculate metrics
        total_duration = sum(
            conv.duration.total_seconds() 
            for conv in conversations 
            if conv.duration
        )
        
        # Group by period
        grouped_data = self._group_conversations_by_period(
            conversations, group_by
        )
        
        # Topic analysis
        all_topics = []
        for conv in conversations:
            all_topics.extend(conv.topics)
        topic_counts = dict(self._count_occurrences(all_topics))
        
        # Interaction type distribution
        type_distribution = defaultdict(int)
        for conv in conversations:
            type_distribution[conv.interaction_type.value] += 1
            
        # Quality metrics
        quality_scores = [
            conv.quality_score 
            for conv in conversations 
            if conv.quality_score is not None
        ]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Engagement metrics
        engagement_scores = [
            conv.metrics.engagement_score 
            for conv in conversations
        ]
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_conversations': len(conversations),
                'total_duration_hours': total_duration / 3600,
                'average_duration_minutes': (total_duration / len(conversations) / 60) if conversations else 0,
                'total_messages': sum(conv.metrics.total_messages for conv in conversations),
                'average_messages_per_conversation': sum(conv.metrics.total_messages for conv in conversations) / len(conversations) if conversations else 0
            },
            'grouped_data': grouped_data,
            'topics': {
                'distribution': topic_counts,
                'total_unique': len(set(all_topics)),
                'most_discussed': max(topic_counts.items(), key=lambda x: x[1])[0] if topic_counts else None
            },
            'interaction_types': dict(type_distribution),
            'quality_metrics': {
                'average_quality_score': avg_quality,
                'average_engagement_score': avg_engagement,
                'low_quality_count': sum(1 for conv in conversations if conv.quality_score < 0.5),
                'high_quality_count': sum(1 for conv in conversations if conv.quality_score >= 0.8)
            },
            'safety': {
                'flagged_conversations': sum(1 for conv in conversations if conv.safety_score < 1.0),
                'total_moderation_flags': sum(
                    conv.metrics.moderation_flags 
                    for conv in conversations
                )
            }
        }
    
    async def get_learning_analytics(
        self,
        child_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze learning progress from conversations
        
        Args:
            child_id: Child's ID
            days: Days to analyze
            
        Returns:
            Learning analytics
        """
        start_date = datetime.now() - timedelta(days=days)
        conversations = await self.get_conversations_by_child(
            child_id, start_date=start_date
        )
        
        # Filter educational conversations
        educational_convs = [
            conv for conv in conversations
            if conv.interaction_type == InteractionType.LEARNING
            or conv.educational_score > 0.5
        ]
        
        # Extract concepts learned
        concepts_discussed = []
        questions_asked = 0
        
        for conv in educational_convs:
            # Extract educational topics
            edu_topics = [
                topic for topic in conv.topics
                if topic in ['education', 'science', 'math', 'history', 'language']
            ]
            concepts_discussed.extend(edu_topics)
            
            # Count questions
            questions_asked += conv.metrics.questions_asked
        
        return {
            'total_educational_conversations': len(educational_convs),
            'total_learning_time_hours': sum(
                conv.duration.total_seconds() / 3600
                for conv in educational_convs
                if conv.duration
            ),
            'concepts_discussed': dict(self._count_occurrences(concepts_discussed)),
            'total_questions_asked': questions_asked,
            'average_questions_per_session': questions_asked / len(educational_convs) if educational_convs else 0,
            'learning_engagement_trend': self._calculate_trend(
                educational_convs, 'metrics.engagement_score'
            )
        }
    
    # Aggregation Methods
    
    async def aggregate_by_child(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate conversation data by child
        
        Returns:
            Dictionary of child_id -> aggregated stats
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
            
        conversations = await self.get_conversations_by_time_range(
            TimeRange.CUSTOM,
            custom_start=start_date,
            custom_end=end_date
        )
        
        child_stats = defaultdict(lambda: {
            'total_conversations': 0,
            'total_duration_seconds': 0,
            'total_messages': 0,
            'topics': [],
            'average_quality': 0,
            'quality_scores': []
        })
        
        for conv in conversations:
            stats = child_stats[conv.child_id]
            stats['total_conversations'] += 1
            stats['total_duration_seconds'] += conv.duration.total_seconds() if conv.duration else 0
            stats['total_messages'] += conv.metrics.total_messages
            stats['topics'].extend(conv.topics)
            if conv.quality_score is not None:
                stats['quality_scores'].append(conv.quality_score)
        
        # Calculate averages
        for child_id, stats in child_stats.items():
            if stats['quality_scores']:
                stats['average_quality'] = sum(stats['quality_scores']) / len(stats['quality_scores'])
            del stats['quality_scores']  # Remove temporary list
            
            # Get unique topics
            stats['unique_topics'] = list(set(stats['topics']))
            stats['topics'] = dict(self._count_occurrences(stats['topics']))
            
        return dict(child_stats)
    
    # Export and Import Methods
    
    async def export_conversations(
        self, 
        child_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = 'json',
        include_transcripts: bool = True
    ) -> bytes:
        """
        Export conversations to specified format
        
        Args:
            child_id: Optional child ID filter
            start_date: Start of export period
            end_date: End of export period
            format: Export format (json, csv, txt)
            include_transcripts: Include full transcripts
        
        Returns:
            Exported data as bytes
        """
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
                'start_time': conv.start_time.isoformat(),
                'end_time': conv.end_time.isoformat() if conv.end_time else None,
                'duration_seconds': conv.duration.total_seconds() if conv.duration else 0,
                'topics': conv.topics,
                'quality_score': conv.quality_score,
                'safety_score': conv.safety_score,
                'message_count': conv.metrics.total_messages
            }
            
            if include_transcripts:
                conv_data['transcript'] = conv.get_transcript()
                
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
                'start_time': conv.start_time.isoformat(),
                'end_time': conv.end_time.isoformat() if conv.end_time else '',
                'duration_minutes': round(conv.duration.total_seconds() / 60, 2) if conv.duration else 0,
                'message_count': conv.metrics.total_messages,
                'topics': ', '.join(conv.topics),
                'quality_score': round(conv.quality_score, 2) if conv.quality_score else '',
                'safety_score': round(conv.safety_score, 2),
                'engagement_score': round(conv.metrics.engagement_score, 2)
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
            lines.append(f"Date: {conv.start_time.strftime('%Y-%m-%d %H:%M')}")
            lines.append(f"Duration: {conv.duration.total_seconds() / 60:.1f} minutes" if conv.duration else "Duration: N/A")
            lines.append(f"Topics: {', '.join(conv.topics)}")
            lines.append(f"Quality Score: {conv.quality_score:.2f}" if conv.quality_score else "Quality Score: N/A")
            
            if include_transcripts:
                lines.append("\nTranscript:")
                lines.append(conv.get_transcript())
                
            lines.append("")
            
        return '\n'.join(lines).encode('utf-8')
    
    # Maintenance Methods
    
    async def delete_old_conversations(
        self, 
        retention_days: int = 90,
        exclude_flagged: bool = True
    ) -> int:
        """
        Delete old conversations
        
        Args:
            retention_days: Days to retain
            exclude_flagged: Don't delete flagged conversations
            
        Returns:
            Number deleted
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        criteria = [
            SearchCriteria('end_time', 'lt', cutoff_date)
        ]
        
        if exclude_flagged:
            criteria.append(SearchCriteria('safety_score', 'eq', 1.0))
            
        old_conversations = await self.search(criteria)
        
        result = await self.bulk_delete([conv.id for conv in old_conversations])
        
        return result.success_count
    
    async def archive_conversations(
        self,
        days_old: int = 30,
        archive_path: str = "archives/"
    ) -> int:
        """
        Archive old conversations to storage
        
        Args:
            days_old: Age threshold for archiving
            archive_path: Path to archive storage
            
        Returns:
            Number archived
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        criteria = [
            SearchCriteria('end_time', 'lt', cutoff_date),
            SearchCriteria('parent_visible', 'eq', True)  # Only archive visible
        ]
        
        to_archive = await self.search(criteria)
        
        # Export each month to separate file
        by_month = defaultdict(list)
        for conv in to_archive:
            month_key = conv.start_time.strftime('%Y-%m')
            by_month[month_key].append(conv)
            
        archived_count = 0
        for month, conversations in by_month.items():
            # Export to file
            archive_data = self._export_json(conversations, include_transcripts=True)
            archive_file = f"{archive_path}conversations_{month}.json"
            
            # Save file (implementation specific)
            # await save_to_storage(archive_file, archive_data)
            
            # Delete from active storage
            result = await self.bulk_delete([c.id for c in conversations])
            archived_count += result.success_count
            
        return archived_count
    
    # Summary Generation
    
    async def generate_daily_summary(
        self,
        date: date,
        child_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate daily conversation summary
        
        Args:
            date: Date to summarize
            child_id: Optional child filter
            
        Returns:
            Daily summary
        """
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        if child_id:
            conversations = await self.get_conversations_by_child(
                child_id, start, end
            )
        else:
            conversations = await self.get_conversations_by_time_range(
                TimeRange.CUSTOM,
                custom_start=start,
                custom_end=end
            )
            
        if not conversations:
            return {'date': date.isoformat(), 'no_activity': True}
            
        # Aggregate metrics
        total_time = sum(
            c.duration.total_seconds() for c in conversations if c.duration
        )
        
        all_topics = []
        all_emotions = []
        
        for conv in conversations:
            all_topics.extend(conv.topics)
            all_emotions.extend([
                state.primary_emotion 
                for state in conv.emotional_states
            ])
            
        return {
            'date': date.isoformat(),
            'summary': {
                'total_conversations': len(conversations),
                'total_time_minutes': round(total_time / 60, 1),
                'unique_children': len(set(c.child_id for c in conversations)),
                'topics_discussed': dict(self._count_occurrences(all_topics)[:5]),
                'dominant_emotions': dict(self._count_occurrences(all_emotions)[:3]),
                'average_quality': sum(c.quality_score for c in conversations if c.quality_score) / len(conversations),
                'educational_conversations': sum(
                    1 for c in conversations 
                    if c.interaction_type == InteractionType.LEARNING
                ),
                'flagged_conversations': sum(
                    1 for c in conversations 
                    if c.safety_score < 1.0
                )
            },
            'highlights': self._extract_highlights(conversations)
        }
    
    # Helper Methods
    
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
    
    def _group_conversations_by_period(
        self,
        conversations: List[Conversation],
        group_by: str
    ) -> Dict[str, Dict[str, Any]]:
        """Group conversations by time period"""
        grouped = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0,
            'total_messages': 0,
            'topics': []
        })
        
        for conv in conversations:
            if group_by == 'day':
                key = conv.start_time.strftime('%Y-%m-%d')
            elif group_by == 'week':
                # Get Monday of the week
                monday = conv.start_time - timedelta(days=conv.start_time.weekday())
                key = monday.strftime('%Y-W%U')
            elif group_by == 'month':
                key = conv.start_time.strftime('%Y-%m')
            else:
                raise ValueError(f"Unsupported group_by value: {group_by}")
                
            group_data = grouped[key]
            group_data['count'] += 1
            group_data['total_duration'] += conv.duration.total_seconds() if conv.duration else 0
            group_data['total_messages'] += conv.metrics.total_messages
            group_data['topics'].extend(conv.topics)
            
        # Process grouped data
        for key, data in grouped.items():
            data['average_duration'] = data['total_duration'] / data['count'] if data['count'] > 0 else 0
            data['unique_topics'] = list(set(data['topics']))
            data['topic_distribution'] = dict(self._count_occurrences(data['topics']))
            del data['topics']  # Remove raw topics list
            
        return dict(grouped)
    
    def _count_occurrences(self, items: List[str]) -> List[Tuple[str, int]]:
        """Count occurrences and return sorted list"""
        counter = Counter(items)
        return counter.most_common()
    
    def _calculate_trend(self, conversations: List[Conversation], metric_path: str) -> Dict[str, Any]:
        """Calculate trend for a specific metric"""
        if not conversations:
            return {'trend': 'no_data', 'direction': None, 'change_rate': 0}
            
        # Sort conversations by time
        sorted_convs = sorted(conversations, key=lambda x: x.start_time)
        
        # Extract metric values
        values = []
        for conv in sorted_convs:
            # Navigate nested attribute path
            value = conv
            for attr in metric_path.split('.'):
                value = getattr(value, attr, 0)
            values.append(float(value))
            
        if len(values) < 2:
            return {'trend': 'insufficient_data', 'direction': None, 'change_rate': 0}
            
        # Calculate simple trend
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        change_rate = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        
        if abs(change_rate) < 5:  # Less than 5% change
            direction = 'stable'
        elif change_rate > 0:
            direction = 'improving'
        else:
            direction = 'declining'
            
        return {
            'trend': direction,
            'direction': direction,
            'change_rate': round(change_rate, 2),
            'first_period_avg': round(first_avg, 2),
            'second_period_avg': round(second_avg, 2)
        }
    
    def _extract_highlights(self, conversations: List[Conversation]) -> List[Dict[str, Any]]:
        """Extract conversation highlights"""
        highlights = []
        
        # Find high-quality conversations
        high_quality = [c for c in conversations if c.quality_score and c.quality_score > 0.8]
        if high_quality:
            best_conv = max(high_quality, key=lambda x: x.quality_score)
            highlights.append({
                'type': 'high_quality',
                'title': 'Best Conversation',
                'conversation_id': best_conv.id,
                'score': best_conv.quality_score,
                'summary': f"High-quality conversation covering {', '.join(best_conv.topics[:3])}"
            })
        
        # Find educational breakthroughs
        educational_convs = [
            c for c in conversations 
            if c.interaction_type == InteractionType.LEARNING and c.metrics.engagement_score > 0.7
        ]
        if educational_convs:
            highlights.append({
                'type': 'learning',
                'title': 'Learning Moment',
                'conversation_id': educational_convs[0].id,
                'topics': educational_convs[0].topics[:3],
                'engagement': educational_convs[0].metrics.engagement_score
            })
        
        # Find emotional support moments
        emotional_convs = [
            c for c in conversations
            if any(state.primary_emotion in ['sad', 'frustrated', 'anxious'] 
                  for state in c.emotional_states)
        ]
        if emotional_convs:
            highlights.append({
                'type': 'emotional_support',
                'title': 'Emotional Support Provided',
                'conversation_id': emotional_convs[0].id,
                'emotions_addressed': list(set([
                    state.primary_emotion for state in emotional_convs[0].emotional_states
                    if state.primary_emotion in ['sad', 'frustrated', 'anxious']
                ]))
            })
        
        return highlights
    
    # Advanced Analytics Methods
    
    async def get_conversation_patterns(
        self,
        child_id: str,
        pattern_type: str = 'time_of_day',
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze conversation patterns
        
        Args:
            child_id: Child's ID
            pattern_type: Type of pattern to analyze ('time_of_day', 'day_of_week', 'duration')
            days: Number of days to analyze
            
        Returns:
            Pattern analysis results
        """
        start_date = datetime.now() - timedelta(days=days)
        conversations = await self.get_conversations_by_child(
            child_id, start_date=start_date
        )
        
        if pattern_type == 'time_of_day':
            return self._analyze_time_patterns(conversations)
        elif pattern_type == 'day_of_week':
            return self._analyze_day_patterns(conversations)
        elif pattern_type == 'duration':
            return self._analyze_duration_patterns(conversations)
        else:
            raise ValueError(f"Unsupported pattern type: {pattern_type}")
    
    def _analyze_time_patterns(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Analyze conversation patterns by time of day"""
        time_buckets = defaultdict(list)
        
        for conv in conversations:
            hour = conv.start_time.hour
            if 6 <= hour < 12:
                bucket = 'morning'
            elif 12 <= hour < 17:
                bucket = 'afternoon'
            elif 17 <= hour < 21:
                bucket = 'evening'
            else:
                bucket = 'night'
                
            time_buckets[bucket].append(conv)
        
        results = {}
        for bucket, convs in time_buckets.items():
            if convs:
                avg_duration = sum(c.duration.total_seconds() for c in convs if c.duration) / len(convs)
                avg_engagement = sum(c.metrics.engagement_score for c in convs) / len(convs)
                
                results[bucket] = {
                    'count': len(convs),
                    'average_duration_minutes': round(avg_duration / 60, 1),
                    'average_engagement': round(avg_engagement, 2),
                    'most_common_topics': dict(self._count_occurrences([
                        topic for conv in convs for topic in conv.topics
                    ])[:3])
                }
        
        return {
            'pattern_type': 'time_of_day',
            'analysis_period_days': 30,
            'patterns': results,
            'peak_time': max(results.items(), key=lambda x: x[1]['count'])[0] if results else None
        }
    
    def _analyze_day_patterns(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Analyze conversation patterns by day of week"""
        day_buckets = defaultdict(list)
        
        for conv in conversations:
            day_name = conv.start_time.strftime('%A')
            day_buckets[day_name].append(conv)
        
        results = {}
        for day, convs in day_buckets.items():
            if convs:
                avg_duration = sum(c.duration.total_seconds() for c in convs if c.duration) / len(convs)
                avg_quality = sum(c.quality_score for c in convs if c.quality_score) / len([c for c in convs if c.quality_score])
                
                results[day] = {
                    'count': len(convs),
                    'average_duration_minutes': round(avg_duration / 60, 1),
                    'average_quality': round(avg_quality, 2) if avg_quality else 0,
                    'total_conversations': len(convs)
                }
        
        return {
            'pattern_type': 'day_of_week',
            'patterns': results,
            'most_active_day': max(results.items(), key=lambda x: x[1]['count'])[0] if results else None
        }
    
    def _analyze_duration_patterns(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Analyze conversation duration patterns"""
        durations = [c.duration.total_seconds() / 60 for c in conversations if c.duration]
        
        if not durations:
            return {'pattern_type': 'duration', 'no_data': True}
        
        # Categorize by duration
        short = [d for d in durations if d < 5]      # < 5 minutes
        medium = [d for d in durations if 5 <= d < 15]  # 5-15 minutes
        long = [d for d in durations if d >= 15]     # 15+ minutes
        
        return {
            'pattern_type': 'duration',
            'statistics': {
                'average_minutes': round(sum(durations) / len(durations), 1),
                'median_minutes': round(sorted(durations)[len(durations)//2], 1),
                'shortest_minutes': round(min(durations), 1),
                'longest_minutes': round(max(durations), 1)
            },
            'distribution': {
                'short_conversations': len(short),
                'medium_conversations': len(medium),
                'long_conversations': len(long)
            },
            'percentages': {
                'short_percent': round(len(short) / len(durations) * 100, 1),
                'medium_percent': round(len(medium) / len(durations) * 100, 1),
                'long_percent': round(len(long) / len(durations) * 100, 1)
            }
        }
    
    # Batch Processing Methods
    
    async def batch_update_quality_scores(
        self,
        conversation_ids: List[str],
        quality_calculator_func
    ) -> BulkOperationResult:
        """
        Update quality scores for multiple conversations
        
        Args:
            conversation_ids: List of conversation IDs
            quality_calculator_func: Function to calculate quality score
            
        Returns:
            Bulk operation result
        """
        success_count = 0
        failed_ids = []
        
        for conv_id in conversation_ids:
            try:
                conversation = await self.get_by_id(conv_id)
                if conversation:
                    new_score = await quality_calculator_func(conversation)
                    conversation.quality_score = new_score
                    await self.update(conversation)
                    success_count += 1
                else:
                    failed_ids.append(conv_id)
            except Exception as e:
                failed_ids.append(conv_id)
                
        return BulkOperationResult(
            success_count=success_count,
            failed_count=len(failed_ids),
            failed_ids=failed_ids
        )
    
    async def batch_analyze_emotions(
        self,
        conversation_ids: List[str],
        emotion_analyzer_func
    ) -> Dict[str, List[EmotionalState]]:
        """
        Analyze emotions for multiple conversations
        
        Args:
            conversation_ids: List of conversation IDs
            emotion_analyzer_func: Function to analyze emotions
            
        Returns:
            Dictionary mapping conversation_id to emotional states
        """
        results = {}
        
        for conv_id in conversation_ids:
            try:
                conversation = await self.get_by_id(conv_id)
                if conversation:
                    emotional_states = await emotion_analyzer_func(conversation)
                    results[conv_id] = emotional_states
            except Exception as e:
                results[conv_id] = []
                
        return results
    
    # Report Generation Methods
    
    async def generate_comprehensive_report(
        self,
        child_id: str,
        report_type: str = 'monthly',
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive child development report
        
        Args:
            child_id: Child's ID
            report_type: Type of report (weekly, monthly, quarterly)
            include_recommendations: Include AI-generated recommendations
            
        Returns:
            Comprehensive report data
        """
        # Determine time range
        if report_type == 'weekly':
            days = 7
        elif report_type == 'monthly':
            days = 30
        elif report_type == 'quarterly':
            days = 90
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        # Gather all analytics
        conversation_analytics = await self.get_conversation_analytics(child_id, group_by='day')
        learning_analytics = await self.get_learning_analytics(child_id, days)
        emotional_patterns = await self.get_emotional_patterns(child_id, days)
        time_patterns = await self.get_conversation_patterns(child_id, 'time_of_day', days)
        
        # Generate executive summary
        total_conversations = conversation_analytics['summary']['total_conversations']
        avg_engagement = conversation_analytics['quality_metrics']['average_engagement_score']
        
        executive_summary = {
            'period': f"Last {days} days",
            'total_interactions': total_conversations,
            'average_daily_interactions': round(total_conversations / days, 1),
            'overall_engagement': round(avg_engagement, 2),
            'primary_emotions': list(emotional_patterns['emotion_summary'].keys())[:3],
            'learning_progress': 'positive' if learning_analytics['total_educational_conversations'] > 0 else 'limited'
        }
        
        report = {
            'report_metadata': {
                'child_id': child_id,
                'report_type': report_type,
                'generation_date': datetime.now().isoformat(),
                'analysis_period_days': days
            },
            'executive_summary': executive_summary,
            'conversation_analytics': conversation_analytics,
            'learning_analytics': learning_analytics,
            'emotional_patterns': emotional_patterns,
            'behavioral_patterns': time_patterns
        }
        
        if include_recommendations:
            report['recommendations'] = await self._generate_recommendations(
                child_id, conversation_analytics, learning_analytics, emotional_patterns
            )
        
        return report
    
    async def _generate_recommendations(
        self,
        child_id: str,
        conversation_analytics: Dict[str, Any],
        learning_analytics: Dict[str, Any],
        emotional_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        # Engagement recommendations
        avg_engagement = conversation_analytics['quality_metrics']['average_engagement_score']
        if avg_engagement < 0.6:
            recommendations.append({
                'category': 'engagement',
                'priority': 'high',
                'title': 'Boost Interaction Engagement',
                'description': 'Consider introducing more interactive games or story-telling sessions',
                'specific_actions': [
                    'Try asking more open-ended questions',
                    'Introduce creative activities like drawing or music',
                    'Use the child\'s favorite topics more frequently'
                ]
            })
        
        # Learning recommendations
        if learning_analytics['total_educational_conversations'] < 3:
            recommendations.append({
                'category': 'learning',
                'priority': 'medium',
                'title': 'Increase Educational Content',
                'description': 'More learning opportunities could benefit development',
                'specific_actions': [
                    'Schedule regular educational conversations',
                    'Explore STEM topics through fun experiments',
                    'Practice reading comprehension with interactive stories'
                ]
            })
        
        # Emotional wellness recommendations
        dominant_emotion = emotional_patterns.get('most_common_emotion')
        if dominant_emotion in ['sad', 'frustrated', 'anxious']:
            recommendations.append({
                'category': 'emotional_wellness',
                'priority': 'high',
                'title': 'Emotional Support Focus',
                'description': f'Child frequently experiences {dominant_emotion} emotions',
                'specific_actions': [
                    'Provide more comforting and validating responses',
                    'Introduce relaxation and mindfulness activities',
                    'Consider discussing feelings more openly'
                ]
            })
        
        return recommendations