#!/usr/bin/env python3
"""
🏗️ Enhancedchildinteraction Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

# Original imports
import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

import structlog

    def __init__(
        self,
        audio_processor: EnhancedAudioProcessor,
        ai_orchestrator: AdvancedAIOrchestrator,
        content_filter: AdvancedContentFilter

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
    

    def get_service_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الخدمة الشاملة"""
        
        # إحصائيات من المكونات الفرعية
        audio_stats = self.audio_processor.get_performance_stats()
        ai_stats = asyncio.create_task(self.ai_orchestrator.get_performance_report())
        filter_stats = self.content_filter.get_filter_statistics()
        
        return {
            'service_stats': self.service_stats,
            'component_stats': {
                'audio_processor': audio_stats,
                'content_filter': filter_stats,
                'active_sessions': len(self.active_sessions)
            },
            'performance_metrics': {
                'success_rate': (
                    self.service_stats['successful_interactions'] / 
                    max(1, self.service_stats['total_interactions'])
                ) * 100,
                'safety_rate': (
                    (self.service_stats['total_interactions'] - self.service_stats['safety_violations']) /
                    max(1, self.service_stats['total_interactions'])
                ) * 100,
                'educational_rate': (
                    self.service_stats['educational_interactions'] /
                    max(1, self.service_stats['total_interactions'])
                ) * 100
            }
        }
    