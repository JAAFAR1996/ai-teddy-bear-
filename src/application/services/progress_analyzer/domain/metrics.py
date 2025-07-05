from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class ProgressMetrics:
    """Advanced progress metrics using NLP analysis"""

    child_id: int
    analysis_date: datetime

    # Vocabulary Analysis
    total_unique_words: int
    new_words_this_period: List[str]
    vocabulary_complexity_score: float  # 0-1
    reading_level_equivalent: str

    # Language Development
    average_sentence_length: float
    grammar_accuracy_score: float
    question_sophistication_level: int  # 1-5
    conversation_coherence_score: float

    # Emotional Intelligence
    emotion_vocabulary_richness: int
    empathy_expression_frequency: float
    emotional_regulation_indicators: List[str]
    social_awareness_metrics: Dict[str, float]

    # Cognitive Development
    abstract_thinking_indicators: int
    problem_solving_approaches: List[str]
    creativity_markers: List[str]
    attention_span_trends: Dict[str, float]

    # Learning Patterns
    preferred_learning_styles: List[str]
    knowledge_retention_rate: float
    curiosity_indicators: List[str]
    learning_velocity: float  # words/concepts per day

    # Behavioral Insights
    initiative_taking_frequency: int
    cooperation_patterns: List[str]
    conflict_resolution_skills: List[str]
    independence_level: float

    # Red Flags & Concerns
    developmental_concerns: List[str]
    intervention_recommendations: List[str]
    urgency_level: int  # 0-3 (0=none, 3=urgent)
