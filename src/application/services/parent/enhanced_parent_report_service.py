"""
🧠 Enhanced Parent Report Service - Task 7
تحليل تقدم الطفل باستخدام NLP متقدم وLLM مع Chain-of-Thought prompting
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from .progress_analyzer import ProgressAnalyzer
from .llm_recommender import LLMRecommender
from .enhanced_parent_report_service import ProgressMetrics, LLMRecommendation

# NLP Libraries
try:
    from collections import Counter

    import nltk
    import spacy
    from nltk.sentiment import SentimentIntensityAnalyzer

    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logger.warning(
        "⚠️ NLP libraries not available. Install with: pip install spacy nltk"
    )

# LLM Integration
try:
    import openai
    from anthropic import Anthropic

    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning(
        "⚠️ LLM libraries not available. Install with: pip install openai anthropic"
    )


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


@dataclass
class LLMRecommendation:
    """LLM-generated recommendation with reasoning"""

    category: str  # "emotional", "cognitive", "social", "learning"
    recommendation: str
    reasoning: str
    expected_impact: str
    implementation_steps: List[str]
    success_metrics: List[str]
    priority_level: int  # 1-5


class EnhancedParentReportService:
    """
    Orchestrates the generation of enhanced parent reports by delegating to specialized services.
    """

    def __init__(self, database_service=None, config=None):
        self.db = database_service
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.progress_analyzer = ProgressAnalyzer(database_service)
        self.llm_recommender = LLMRecommender(config)

    async def generate_and_store_report(
        self, child_id: int, period_days: int = 7
    ) -> Dict[str, Any]:
        """Generate and store a comprehensive report for a child."""
        metrics = await self.progress_analyzer.analyze(child_id, period_days)
        child_info = await self._get_child_info(child_id)
        recommendations = await self.llm_recommender.generate_recommendations(metrics, child_info)
        report_id = await self.store_analysis_results(metrics, recommendations)
        return {
            "report_id": report_id,
            "metrics": asdict(metrics),
            "recommendations": [asdict(rec) for rec in recommendations],
            "generated_at": datetime.now().isoformat(),
        }

    async def store_analysis_results(
        self, metrics: "ProgressMetrics", recommendations: List["LLMRecommendation"]
    ) -> str:
        """Store analysis results in the database."""
        if not self.db:
            raise Exception("Database service is not available.")
        report_data = {
            "child_id": metrics.child_id,
            "generated_at": metrics.analysis_date.isoformat(),
            "metrics": asdict(metrics),
            "recommendations": [asdict(rec) for rec in recommendations],
            "analysis_version": "2.0_task7_refactored",
        }
        try:
            report_id = await self.db.execute(
                "INSERT INTO parent_reports (child_id, generated_at, metrics, recommendations, analysis_version) VALUES (?, ?, ?, ?, ?)",
                (
                    metrics.child_id,
                    report_data["generated_at"],
                    json.dumps(report_data["metrics"]),
                    json.dumps(report_data["recommendations"]),
                    report_data["analysis_version"],
                ),
            )
            self.logger.info(f"✅ Analysis results stored with ID: {report_id}")
            return str(report_id)
        except Exception as e:
            self.logger.error(f"Failed to store analysis results: {e}")
            raise

    async def _get_child_info(self, child_id: int) -> Dict[str, Any]:
        """Fetch child information from the database."""
        if not self.db:
            return {"name": "Unknown", "age": 5}
        try:
            child = await self.db.fetch_one("SELECT * FROM children WHERE id = ?", (child_id,))
            return dict(child) if child else {"name": "Unknown", "age": 5}
        except Exception as e:
            self.logger.error(f"Failed to fetch child info: {e}")
            return {"name": "Unknown", "age": 5}
