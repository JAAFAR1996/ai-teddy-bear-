#!/usr/bin/env python3
"""
🏗️ Parentdashboard Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

# Original imports
import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from typing import List, Dict, Optional, Any, Tuple

    def _calculate_topic_frequency(self, logs: List[ConversationLogEntry]) -> Dict[str, int]:
        """Calculate topic frequency from logs"""
        topic_freq = defaultdict(int)
        for log in logs:
            for topic in log.topics:
                topic_freq[topic] += 1
        return dict(topic_freq)


    def _calculate_sentiment_breakdown(self, logs: List[ConversationLogEntry]) -> Dict[str, float]:
        """Calculate average sentiment breakdown"""
        if not logs:
            return {'positive': 0, 'neutral': 0, 'negative': 0}

        sentiment_totals = defaultdict(float)
        for log in logs:
            for sentiment, score in log.sentiment_scores.items():
                sentiment_totals[sentiment] += score

        count = len(logs)
        return {k: v/count for k, v in sentiment_totals.items()}


    def _calculate_peak_hours(self, logs: List[ConversationLogEntry]) -> List[int]:
        """Calculate peak usage hours"""
        hour_counts = defaultdict(int)
        for log in logs:
            hour = log.started_at.hour
            hour_counts[hour] += 1

        # Get top 3 hours
        sorted_hours = sorted(hour_counts.items(),
                              key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:3]]