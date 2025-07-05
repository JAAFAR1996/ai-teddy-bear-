import logging
from typing import Any, Dict, List

# Placeholder for NLP libraries, will need to be properly managed
try:
    import spacy
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False


class VocabularyAnalyzer:
    def __init__(self, nlp_en):
        self.logger = logging.getLogger(__name__)
        if NLP_AVAILABLE and nlp_en:
            self.nlp_en = nlp_en
        else:
            self.nlp_en = None
            self.logger.warning(
                "English NLP model not available for VocabularyAnalyzer.")

    def _calculate_vocabulary_complexity(self, doc) -> tuple[float, list[str]]:
        """Calculates vocabulary complexity from a spaCy doc."""
        words = [
            token.lemma_.lower()
            for token in doc
            if token.is_alpha and not token.is_stop
        ]
        unique_words = list(set(words))

        if not unique_words:
            return 0.0, []

        avg_word_length = sum(len(word)
                              for word in unique_words) / len(unique_words)
        rare_words_count = len([w for w in unique_words if len(w) > 6])
        abstract_concepts = len([token for token in doc if token.pos_ in [
                                "NOUN", "ADJ"] and len(token.lemma_) > 5])

        complexity_score = min(
            1.0, (avg_word_length / 8 + rare_words_count / 20 + abstract_concepts / 15) / 3)

        return complexity_score, unique_words

    def _analyze_sentence_structure(self, doc) -> float:
        """Analyzes sentence structure to find the average sentence length."""
        sentences = list(doc.sents)
        return sum(len(sent) for sent in sentences) / len(sentences) if sentences else 0.0

    def _detect_new_words(self, unique_words: list[str]) -> list[str]:
        """Detects new words from a list of unique words."""
        # This is a simplified implementation. In a real scenario, we would compare with historical data.
        return unique_words[-min(10, len(unique_words)):]

    def _estimate_reading_level(
        self, complexity_score: float, avg_sentence_length: float
    ) -> str:
        """Estimate reading level based on complexity"""
        if complexity_score < 0.3:
            return "مبتدئ"
        elif complexity_score < 0.6:
            return "متوسط"
        else:
            return "متقدم"

    def _estimate_grammar_accuracy(self, doc) -> float:
        # Placeholder
        return 0.95

    def _analyze_question_sophistication(self, texts: List[str]) -> int:
        # Placeholder
        return 3

    def _calculate_coherence_score(self, doc) -> float:
        # Placeholder
        return 0.8

    async def analyze(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze vocabulary development using NLP"""
        if not self.nlp_en or not texts:
            return self._empty_vocabulary_analysis()

        all_text = " ".join(texts)
        doc = self.nlp_en(all_text)

        complexity_score, unique_words = self._calculate_vocabulary_complexity(
            doc)
        avg_sentence_length = self._analyze_sentence_structure(doc)
        reading_level = self._estimate_reading_level(
            complexity_score, avg_sentence_length)
        new_words = self._detect_new_words(unique_words)

        return {
            "unique_words": len(unique_words),
            "new_words": new_words,
            "complexity_score": complexity_score,
            "reading_level": reading_level,
            "avg_sentence_length": avg_sentence_length,
            "grammar_score": self._estimate_grammar_accuracy(doc),
            "question_level": self._analyze_question_sophistication(texts),
            "coherence_score": self._calculate_coherence_score(doc),
            "learning_velocity": len(new_words) / 7,  # per day
        }

    def _empty_vocabulary_analysis(self) -> Dict[str, Any]:
        """Return empty vocabulary analysis"""
        return {
            "unique_words": 0,
            "new_words": [],
            "complexity_score": 0.0,
            "reading_level": "غير محدد",
            "avg_sentence_length": 0.0,
            "grammar_score": 0.0,
            "question_level": 1,
            "coherence_score": 0.0,
            "learning_velocity": 0.0,
        }
