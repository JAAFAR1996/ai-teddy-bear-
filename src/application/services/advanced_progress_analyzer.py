# Transformers imports patched for development
"""
🧠 Advanced Progress Analyzer Service - Task 7
Orchestrator for child progress analysis.
"""

import asyncio
import json
import logging
import re
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Domain objects
from .progress_analyzer.domain.metrics import ProgressMetrics
from .progress_analyzer.domain.recommendations import LLMRecommendation

# Child analysis services
from .progress_analyzer.services.behavioral_analyzer import BehavioralAnalyzer
from .progress_analyzer.services.cognitive_analyzer import CognitiveAnalyzer
from .progress_analyzer.services.emotional_analyzer import EmotionalAnalyzer
from .progress_analyzer.services.social_analyzer import SocialAnalyzer
from .progress_analyzer.services.vocabulary_analyzer import VocabularyAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependency Availability Flags
NLP_AVAILABLE = False
TRANSFORMERS_AVAILABLE = False
LLM_AVAILABLE = False

try:
    import spacy
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLP_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ NLP libraries (spacy, nltk) not available.")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Transformers library not available.")

try:
    import openai
    from anthropic import Anthropic
    LLM_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ LLM libraries (openai, anthropic) not available.")


class AdvancedProgressAnalyzer:
    """
    Orchestrates the analysis of a child's progress by coordinating
    various specialized analysis services.
    """

    def __init__(self, database_service=None, config=None):
        self.db = database_service
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        self._init_nlp_models()
        self._init_llm_clients()
        self._load_analysis_templates()

        # Initialize specialized analyzers
        self.vocabulary_analyzer = VocabularyAnalyzer(
            getattr(self, 'nlp_en', None))
        self.emotional_analyzer = EmotionalAnalyzer()
        self.cognitive_analyzer = CognitiveAnalyzer()
        self.social_analyzer = SocialAnalyzer()
        self.behavioral_analyzer = BehavioralAnalyzer()

    def _init_nlp_models(self):
        """Initializes NLP models required by the analysis services."""
        if not NLP_AVAILABLE:
            return
        try:
            self.nlp_en = spacy.load("en_core_web_sm")
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            if TRANSFORMERS_AVAILABLE:
                self.emotion_classifier = pipeline(
                    "text-classification", model="j-hartmann/emotion-english-distilroberta-base")
                self.topic_classifier = pipeline(
                    "zero-shot-classification", model="facebook/bart-large-mnli")
            self.logger.info("✅ NLP models initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize NLP models: {e}")
            self.nlp_en = None

    def _init_llm_clients(self):
        """Initializes LLM clients for generating recommendations."""
        if not LLM_AVAILABLE:
            return
        try:
            if openai_key := self.config.get("openai_api_key"):
                self.openai_client = openai.OpenAI(api_key=openai_key)
            if anthropic_key := self.config.get("anthropic_api_key"):
                self.anthropic_client = Anthropic(api_key=anthropic_key)
            self.logger.info("✅ LLM clients initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM clients: {e}")

    def _load_analysis_templates(self):
        """Loads Chain-of-Thought prompting templates."""
        # This could be moved to a separate template management service
        self.cot_templates = {
            "recommendation_generation": """
                Generate a personalized recommendation for a child.
                Context: Child={child_name}, Age={age}, Category={category}.
                Thinking Step-by-Step:
                1. Current Situation: {current_situation}
                2. Target Goal: {target_goal}
                3. Strategy: {strategy}
                4. Implementation Plan: {implementation_plan}
                5. Success Criteria: {success_criteria}
                Final Recommendation (JSON format):
            """
        }

    async def analyze_progress(self, child_id: int, period_days: int = 7) -> str:
        """
        Analyzes a child's progress over a given period.
        This is the main orchestration method.
        """
        self.logger.info(
            f"Starting progress analysis for child_id: {child_id} over {period_days} days.")
        child_info = await self._fetch_child_data(child_id)
        interactions = await self._fetch_interaction_data(child_id, period_days)

        if not interactions:
            self.logger.warning(
                f"No interactions for child {child_id}. Cannot analyze.")
            metrics = await self._create_empty_metrics(child_id)
        else:
            conversation_texts = self._extract_conversation_texts(interactions)
            analysis_results = await self._run_analyses_in_parallel(conversation_texts, interactions)
            metrics = self._aggregate_analysis_results(
                child_id, analysis_results)

        report_id = await self._generate_and_store_report(metrics, child_info)
        return report_id

    async def _run_analyses_in_parallel(
        self, conversation_texts: List[str], interactions: List[Dict]
    ) -> Dict[str, Any]:
        """Runs all NLP analyses in parallel for efficiency."""
        tasks = [
            self.vocabulary_analyzer.analyze(conversation_texts),
            self.emotional_analyzer.analyze(conversation_texts),
            self.cognitive_analyzer.analyze(conversation_texts),
            self.social_analyzer.analyze(conversation_texts),
            self.behavioral_analyzer.analyze(interactions),
        ]
        results = await asyncio.gather(*tasks)
        return {
            "vocabulary": results[0],
            "emotional": results[1],
            "cognitive": results[2],
            "social": results[3],
            "behavioral": results[4],
        }

    def _aggregate_analysis_results(
        self, child_id: int, analyses: Dict[str, Any]
    ) -> ProgressMetrics:
        """Aggregates results from all analyses into a ProgressMetrics object."""
        # Placeholder for developmental concern logic
        concerns = {"concerns": [], "interventions": [], "urgency_level": 0}

        return ProgressMetrics(
            child_id=child_id,
            analysis_date=datetime.now(),
            **analyses["vocabulary"],
            **analyses["emotional"],
            **analyses["cognitive"],
            **analyses["social"],
            **analyses["behavioral"],
            developmental_concerns=concerns["concerns"],
            intervention_recommendations=concerns["interventions"],
            urgency_level=concerns["urgency_level"],
        )

    async def _generate_and_store_report(
        self, metrics: ProgressMetrics, child_info: Dict[str, Any]
    ) -> str:
        """Generates recommendations and stores the final report."""
        recommendations = await self.generate_llm_recommendations(metrics, child_info)
        report_id = await self.store_analysis_results(metrics, recommendations)
        self.logger.info(
            f"✅ Analysis complete for child {metrics.child_id}. Report ID: {report_id}")
        return report_id

    # Data Fetching Methods (Could be moved to a dedicated data service)
    async def _fetch_child_data(self, child_id: int) -> Dict[str, Any]:
        self.logger.info(f"Fetching data for child_id: {child_id}")
        return {"id": child_id, "name": "Test Child", "age": 5}

    async def _fetch_interaction_data(self, child_id: int, period_days: int) -> List[Dict]:
        self.logger.info(
            f"Fetching interactions for the last {period_days} days.")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        return await self._get_interactions_with_text(child_id, start_date, end_date)

    async def _get_interactions_with_text(
        self, child_id: int, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        if not self.db:
            return []
        try:
            # Example query, replace with actual DB call
            rows = await self.db.fetch_all("SELECT * FROM conversations WHERE child_id = ? AND created_at BETWEEN ? AND ?", (child_id, start_date, end_date))
            return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to fetch interactions: {e}")
            return []

    # LLM Recommendation Generation (Could be moved to a dedicated service)
    async def generate_llm_recommendations(
        self, metrics: ProgressMetrics, child_info: Dict[str, Any]
    ) -> List[LLMRecommendation]:
        if not hasattr(self, "openai_client"):
            return []

        # Simplified generation logic
        prompt = self.cot_templates["recommendation_generation"].format(
            child_name=child_info["name"], age=child_info["age"], category="overall", current_situation="...", target_goal="...", strategy="...", implementation_plan="...", success_criteria="...")

        try:
            response_str = await self._call_openai_with_cot(prompt)
            return [self._parse_llm_recommendation("overall", response_str)]
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return []

    async def _call_openai_with_cot(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            model="gpt-4-turbo-preview",
            messages=[{"role": "system", "content": "You are a child development expert."}, {
                "role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    def _parse_llm_recommendation(self, category: str, response: str) -> LLMRecommendation:
        try:
            data = json.loads(response)
            return LLMRecommendation(**data)
        except (json.JSONDecodeError, TypeError):
            return LLMRecommendation(category=category, recommendation="Could not parse recommendation.", reasoning="", expected_impact="", implementation_steps=[], success_metrics=[], priority_level=3)

    # Storage Method (Could be moved to a dedicated service)
    async def store_analysis_results(
        self, metrics: ProgressMetrics, recommendations: List[LLMRecommendation]
    ) -> str:
        if not self.db:
            raise Exception("Database service not available")

        report_data = {
            "child_id": metrics.child_id,
            "generated_at": metrics.analysis_date.isoformat(),
            "metrics": asdict(metrics),
            "recommendations": [asdict(rec) for rec in recommendations],
        }

        try:
            # Example query, replace with actual DB call
            report_id = await self.db.execute("INSERT INTO parent_reports (child_id, generated_at, report_data) VALUES (?, ?, ?)", (metrics.child_id, report_data["generated_at"], json.dumps(report_data)))
            self.logger.info(f"✅ Analysis results stored with ID: {report_id}")
            return str(report_id)
        except Exception as e:
            self.logger.error(f"Failed to store analysis results: {e}")
            raise

    # Utility and Placeholder Methods
    def _extract_conversation_texts(self, interactions: List[Dict]) -> List[str]:
        return [i["text"] for i in interactions if "text" in i and i["text"]]

    async def _create_empty_metrics(self, child_id: int) -> ProgressMetrics:
        """Creates empty metrics for cases with no interaction data."""
        empty_vocab = VocabularyAnalyzer(None)._empty_vocabulary_analysis()
        empty_emotion = EmotionalAnalyzer()._empty_emotional_analysis()
        empty_cognitive = CognitiveAnalyzer()._empty_cognitive_analysis()
        empty_social = SocialAnalyzer().analyze([])
        empty_behavioral = BehavioralAnalyzer().analyze([])

        return ProgressMetrics(
            child_id=child_id,
            analysis_date=datetime.now(),
            **empty_vocab,
            **empty_emotion,
            **empty_cognitive,
            **await empty_social,
            **await empty_behavioral,
            developmental_concerns=["No data available for analysis."],
            intervention_recommendations=["Encourage more interaction."],
            urgency_level=0,
        )
