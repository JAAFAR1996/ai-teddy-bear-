"""
Child Interaction Domain Service

Domain service for child interaction and time management business logic.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import logging

from src.core.domain.entities.child import Child


class ChildInteractionDomainService:
    """Domain service for child interaction business logic"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_interaction_time(self, child: Child, additional_time: int) -> bool:
        """
        Validate if additional interaction time is allowed
        
        Args:
            child: Child entity
            additional_time: Additional time in seconds
            
        Returns:
            True if interaction time is allowed
        """
        if additional_time <= 0:
            return False
        
        total_time_after = child.total_interaction_time + additional_time
        return total_time_after <= child.max_daily_interaction_time
    
    def calculate_remaining_interaction_time(self, child: Child) -> int:
        """
        Calculate remaining daily interaction time
        
        Args:
            child: Child entity
            
        Returns:
            Remaining time in seconds
        """
        remaining = child.max_daily_interaction_time - child.total_interaction_time
        return max(0, remaining)
    
    def is_over_time_limit(self, child: Child) -> bool:
        """
        Check if child has exceeded daily time limit
        
        Args:
            child: Child entity
            
        Returns:
            True if over limit
        """
        return child.total_interaction_time >= child.max_daily_interaction_time
    
    def calculate_optimal_session_duration(self, child: Child) -> int:
        """
        Calculate optimal session duration based on child's profile
        
        Args:
            child: Child entity
            
        Returns:
            Optimal session duration in seconds
        """
        # Base duration by age
        if child.age <= 5:
            base_duration = 900  # 15 minutes
        elif child.age <= 10:
            base_duration = 1800  # 30 minutes
        else:
            base_duration = 2700  # 45 minutes
        
        # Adjust for remaining time
        remaining_time = self.calculate_remaining_interaction_time(child)
        
        # Don't exceed remaining time
        optimal_duration = min(base_duration, remaining_time)
        
        # Minimum session of 5 minutes
        return max(300, optimal_duration)
    
    def should_send_time_warning(self, child: Child, warning_threshold: float = 0.8) -> bool:
        """
        Check if time warning should be sent
        
        Args:
            child: Child entity
            warning_threshold: Threshold as percentage of daily limit
            
        Returns:
            True if warning should be sent
        """
        usage_percentage = child.total_interaction_time / child.max_daily_interaction_time
        return usage_percentage >= warning_threshold
    
    def get_interaction_patterns(self, child: Child) -> dict:
        """
        Analyze interaction patterns for a child
        
        Args:
            child: Child entity
            
        Returns:
            Dictionary with pattern analysis
        """
        patterns = {
            'is_consistent': False,
            'preferred_session_length': 0,
            'usage_efficiency': 0.0,
            'engagement_trend': 'stable'
        }
        
        # Calculate usage efficiency
        if child.max_daily_interaction_time > 0:
            patterns['usage_efficiency'] = child.total_interaction_time / child.max_daily_interaction_time
        
        # Determine consistency based on last interaction
        if child.last_interaction:
            days_since_last = (datetime.now() - child.last_interaction).days
            patterns['is_consistent'] = days_since_last <= 2
        
        return patterns 