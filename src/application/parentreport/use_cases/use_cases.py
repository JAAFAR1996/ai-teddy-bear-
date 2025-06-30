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

    def _analyze_vocabulary_nlp(self, interactions: List[InteractionAnalysis]) -> Dict[str, Any]:
        """NLP analysis of vocabulary development"""
        # Extract text from interactions
        texts = []
        for interaction in interactions:
            # Extract text from topics_discussed and behavioral_indicators
            text_content = ' '.join(interaction.topics_discussed + interaction.behavioral_indicators)
            if text_content.strip():
                texts.append(text_content)
        
        if not texts:
            return {
                'unique_words': 0,
                'new_words': [],
                'complexity': 0.0,
                'avg_word_length': 0.0
            }
        
        all_text = ' '.join(texts).lower()
        
        # Simple NLP processing
        words = [w for w in all_text.split() if len(w) > 2 and w.isalpha()]
        unique_words = list(set(words))
        
        # Calculate complexity
        avg_word_length = sum(len(w) for w in unique_words) / len(unique_words) if unique_words else 0
        complexity = min(1.0, avg_word_length / 8.0)
        
        return {
            'unique_words': len(unique_words),
            'new_words': unique_words[-5:] if len(unique_words) > 5 else unique_words,
            'complexity': complexity,
            'avg_word_length': avg_word_length
        }
    