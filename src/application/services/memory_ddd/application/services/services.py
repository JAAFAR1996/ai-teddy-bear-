#!/usr/bin/env python3
"""
🏗️ Memory Domain - DDD Implementation
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
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

    def _calculate_importance(
        self,
        user_message: str,
        ai_response: str,
        metadata: Dict[str, Any]

def calculate_memory_similarity(memory1: Memory, memory2: Memory) -> float:
    """Calculate similarity between two memories"""
    if memory1.embedding is None or memory2.embedding is None:
        # Fallback to text similarity
        common_topics = set(memory1.topics) & set(memory2.topics)
        return len(common_topics) / max(len(memory1.topics), len(memory2.topics), 1)

    # Cosine similarity
    dot_product = np.dot(memory1.embedding, memory2.embedding)
    norm1 = np.linalg.norm(memory1.embedding)
    norm2 = np.linalg.norm(memory2.embedding)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)



def generate_memory_graph(memories: List[Memory], threshold: float = 0.5) -> Dict[str, List[str]]:
    """Generate a graph of related memories"""
    graph = defaultdict(list)

    for i, memory1 in enumerate(memories):
        for j, memory2 in enumerate(memories[i+1:], i+1):
            similarity = calculate_memory_similarity(memory1, memory2)

            if similarity > threshold:
                graph[memory1.id].append(memory2.id)
                graph[memory2.id].append(memory1.id)

    return dict(graph)