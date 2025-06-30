#!/usr/bin/env python3
"""
🏗️ Ai Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

# Original imports
import asyncio
import hashlib
import logging
import time
from functools import lru_cache

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "emotion": self.emotion,
            "category": self.category,
            "learning_points": self.learning_points,
            "session_id": self.session_id,
            "confidence": self.confidence,
            "processing_time_ms": self.processing_time_ms,
            "cached": self.cached,
            "model_used": self.model_used,
            "usage": self.usage,
            "error": self.error
        }

# ================== ENHANCED AI SERVICE INTERFACE ==================


    def _create_wake_word_response(self, child: Child, session_id: str) -> AIResponseModel:
        """Enhanced wake word response with variety"""
        
        responses = [
            f"نعم {child.name}؟ أنا هنا! كيف يمكنني مساعدتك؟ 🧸✨",
            f"مرحباً {child.name}! أسعد بسماع صوتك! بماذا تفكر؟ 🌟😊",
            f"أهلاً وسهلاً {child.name}! أنا مستعد للحديث! ما الذي تريد أن نفعله؟ 🎉🧸"
        ]
        
        return AIResponseModel(
            text=random.choice(responses),
            emotion="happy",
            category="greeting",
            learning_points=["social_interaction", "communication"],
            session_id=session_id,
            confidence=1.0,
            processing_time_ms=8
        )
    

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        avg_processing_time = (
            self.total_processing_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "rate_limit_hits": self.rate_limit_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "average_processing_time_ms": avg_processing_time,
            "cache_size": len(self.memory_cache),
            "active_conversations": len(self.conversation_history)
        }

# ================== ENHANCED FACTORY ==================