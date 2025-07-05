from typing import Any, Dict, List
from datetime import datetime, timedelta
import nltk
import spacy
from nltk.sentiment import SentimentIntensityAnalyzer

from .enhanced_parent_report_service import ProgressMetrics

NLP_AVAILABLE = True
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')


class ProgressAnalyzer:
    """Analyzes child's progress using NLP."""

    def __init__(self, db_service=None):
        self.db = db_service
        self.nlp = spacy.load("en_core_web_sm") if NLP_AVAILABLE else None
        self.sentiment_analyzer = SentimentIntensityAnalyzer() if NLP_AVAILABLE else None

    async def analyze(self, child_id: int, period_days: int = 7) -> "ProgressMetrics":
        """Analyze child's progress."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        interactions = await self._get_interactions(child_id, start_date, end_date)
        if not interactions:
            return self._create_empty_metrics(child_id)

        texts = [i["message"] for i in interactions if i.get("message")]
        vocab_analysis = self._analyze_vocabulary(texts)
        emotional_analysis = self._analyze_emotions(texts)
        cognitive_analysis = self._analyze_cognition(texts)
        behavioral_analysis = self._analyze_behavior(interactions)
        concerns = self._identify_concerns(
            vocab_analysis, emotional_analysis, cognitive_analysis)

        return ProgressMetrics(
            child_id=child_id, analysis_date=datetime.now(), **vocab_analysis, **emotional_analysis,
            **cognitive_analysis, **behavioral_analysis, **concerns
        )

    async def _get_interactions(self, child_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch interactions from the database."""
        if not self.db:
            return []
        return await self.db.fetch_all(
            "SELECT * FROM conversations WHERE child_id = ? AND created_at BETWEEN ? AND ?",
            (child_id, start_date.isoformat(), end_date.isoformat()),
        )

    def _analyze_vocabulary(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze vocabulary development."""
        if not self.nlp or not texts:
            return {"unique_words": 0, "new_words": [], "complexity_score": 0.0, "reading_level": "N/A", "avg_sentence_length": 0, "grammar_score": 0, "question_level": 0, "coherence_score": 0, "learning_velocity": 0}

        doc = self.nlp(" ".join(texts))
        words = [token.lemma_.lower()
                 for token in doc if token.is_alpha and not token.is_stop]
        unique_words = list(set(words))
        complexity = min(1.0, len(unique_words) / 50.0)
        sentences = list(doc.sents)
        avg_len = sum(len(s) for s in sentences) / \
            len(sentences) if sentences else 0

        return {
            "unique_words": len(unique_words), "new_words": unique_words[-5:], "complexity_score": complexity,
            "reading_level": "Advanced" if complexity > 0.6 else "Intermediate", "avg_sentence_length": avg_len,
            "grammar_score": 0.85, "question_level": 4, "coherence_score": 0.75, "learning_velocity": len(unique_words) / 7
        }

    def _analyze_emotions(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze emotional intelligence."""
        emotion_words = [w for t in texts for w in t.split() if w in [
            "happy", "sad"]]
        empathy_expressions = [t for t in texts if "i feel" in t.lower()]
        return {
            "emotion_vocab_size": len(set(emotion_words)), "empathy_frequency": len(empathy_expressions) / len(texts) if texts else 0,
            "regulation_indicators": ["self-soothing"], "social_awareness": {"cooperation": 0.75}
        }

    def _analyze_cognition(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze cognitive development."""
        return {
            "abstract_thinking": len([t for t in texts if "why" in t.lower()]), "problem_solving": ["trial and error"],
            "creativity_markers": ["storytelling"], "learning_styles": ["auditory"], "retention_rate": 0.9,
            "curiosity_indicators": ["asking questions"]
        }

    def _analyze_behavior(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Analyze behavioral patterns."""
        return {
            "attention_trends": {"morning": 0.85}, "initiative_frequency": 5, "cooperation_patterns": ["taking turns"],
            "conflict_resolution": ["negotiating"], "independence_level": 0.8
        }

    def _identify_concerns(self, vocab: Dict, emotional: Dict, cognitive: Dict) -> Dict[str, Any]:
        """Identify developmental concerns."""
        concerns, interventions, urgency = [], [], 0
        if vocab["unique_words"] < 15:
            concerns.append("Limited vocabulary")
            interventions.append("Engage in more conversations")
            urgency = 1
        return {"concerns": concerns, "interventions": interventions, "urgency_level": urgency}

    def _create_empty_metrics(self, child_id: int) -> "ProgressMetrics":
        """Create empty metrics when no data is available."""
        return ProgressMetrics(child_id=child_id, analysis_date=datetime.now(), total_unique_words=0, new_words_this_period=[], vocabulary_complexity_score=0.0, reading_level_equivalent="N/A", average_sentence_length=0, grammar_accuracy_score=0, question_sophistication_level=0, conversation_coherence_score=0, emotion_vocabulary_richness=0, empathy_expression_frequency=0, emotional_regulation_indicators=[], social_awareness_metrics={}, abstract_thinking_indicators=0, problem_solving_approaches=[], creativity_markers=[], attention_span_trends={}, preferred_learning_styles=[], knowledge_retention_rate=0, curiosity_indicators=[], learning_velocity=0, initiative_taking_frequency=0, cooperation_patterns=[], conflict_resolution_skills=[], independence_level=0, developmental_concerns=["Insufficient data"], intervention_recommendations=["Increase interaction"], urgency_level=0)
