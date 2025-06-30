#!/usr/bin/env python3
"""
🏗️ Enhancedchildinteraction Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

# Original imports
import asyncio
import time
from typing import Dict, Any, Optional, List, AsyncIterator
from dataclasses import dataclass, field
import structlog

    def get_session_summary(self, child_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على ملخص الجلسة"""
        
        if child_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[child_id]
        
        return {
            'child_info': {
                'id': session.child_id,
                'name': session.child_name,
                'age': session.child_age
            },
            'session_stats': {
                'duration_minutes': (time.time() - session.session_start) / 60,
                'interaction_count': session.interaction_count,
                'average_processing_time': (
                    session.total_processing_time / max(1, session.interaction_count)
                ),
                'topics_discussed': session.topics_discussed,
                'educational_progress': session.educational_progress
            },
            'mood_analysis': {
                'mood_history': session.mood_history,
                'current_mood': session.mood_history[-1] if session.mood_history else 'unknown',
                'mood_stability': self._calculate_mood_stability(session.mood_history)
            },
            'safety_summary': {
                'total_violations': len(session.safety_violations),
                'violation_types': list(set(v['type'] for v in session.safety_violations)),
                'last_violation': session.safety_violations[-1] if session.safety_violations else None
            }
        }
    

    def _calculate_mood_stability(self, mood_history: List[str]) -> float:
        """حساب استقرار المزاج"""
        
        if len(mood_history) < 2:
            return 1.0
        
        changes = 0
        for i in range(1, len(mood_history)):
            if mood_history[i] != mood_history[i-1]:
                changes += 1
        
        stability = 1.0 - (changes / (len(mood_history) - 1))
        return stability
    