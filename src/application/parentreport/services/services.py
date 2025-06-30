#!/usr/bin/env python3
"""
🏗️ Parentreport Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

# Original imports
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
import pandas as pd

    def _calculate_longest_conversation(self, interactions: List[InteractionAnalysis]) -> int:
        """Calculate longest conversation in minutes"""
        if not interactions:
            return 0
        return max(interaction.duration for interaction in interactions) // 60
    

    def _calculate_emotion_stability(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate emotional stability (0-1, higher = more stable)"""
        if len(interactions) < 2:
            return 1.0
        
        # Calculate variance in emotion scores
        emotions = [interaction.primary_emotion for interaction in interactions]
        emotion_changes = sum(1 for i in range(1, len(emotions)) 
                            if emotions[i] != emotions[i-1])
        
        # Stability = 1 - (changes / possible_changes)
        max_changes = len(emotions) - 1
        if max_changes == 0:
            return 1.0
        
        stability = 1 - (emotion_changes / max_changes)
        return max(0.0, min(1.0, stability))
    

    def _calculate_attention_span(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate average attention span in minutes"""
        if not interactions:
            return 0.0
        
        total_duration = sum(interaction.duration for interaction in interactions)
        return (total_duration / len(interactions)) / 60  # Convert to minutes
    