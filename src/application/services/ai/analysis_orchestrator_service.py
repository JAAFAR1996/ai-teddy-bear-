"""
Analysis Orchestrator Application Service
Coordinates complex analysis workflows across multiple domains
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from src.domain.reporting.models import (InteractionAnalysis, ProgressMetrics,
                                         UrgencyLevel)
from src.domain.reporting.services import (BehaviorAnalyzer,
                                           EmotionAnalyzerService,
                                           ProgressAnalyzer, SkillAnalyzer)


class AnalysisOrchestratorService:
    """Application service for orchestrating comprehensive analysis"""

    def __init__(self, database_service=None):
        self.db = database_service
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize domain services
        self.progress_analyzer = ProgressAnalyzer()
        self.emotion_analyzer = EmotionAnalyzerService()
        self.skill_analyzer = SkillAnalyzer()
        self.behavior_analyzer = BehaviorAnalyzer()

    async def analyze_progress(self, child_id: int) -> ProgressMetrics:
        """Comprehensive progress analysis with advanced metrics"""
        try:
            # Get recent interactions
            interactions = await self._get_recent_interactions(child_id)

            # Perform vocabulary analysis
            vocab_analysis = self._analyze_vocabulary_nlp(interactions)

            # Perform emotional analysis
            emotional_analysis = self._analyze_emotional_nlp(interactions)

            # Perform cognitive analysis
            cognitive_analysis = self._analyze_cognitive_nlp(interactions)

            # Identify concerns
            developmental_concerns = self._identify_concerns_task7(
                vocab_analysis, emotional_analysis
            )

            # Generate interventions
            intervention_recommendations = self._generate_interventions_task7(
                vocab_analysis, emotional_analysis
            )

            # Calculate urgency level
            urgency_level = self._calculate_urgency_task7(
                vocab_analysis, emotional_analysis
            )

            # Create comprehensive metrics
            metrics = ProgressMetrics(
                child_id=child_id,
                analysis_date=datetime.now(),
                total_unique_words=vocab_analysis.get("total_unique_words", 0),
                new_words_this_period=vocab_analysis.get("new_words", []),
                vocabulary_complexity_score=vocab_analysis.get("complexity_score", 0.5),
                emotional_intelligence_score=emotional_analysis.get(
                    "intelligence_score", 0.5
                ),
                cognitive_development_score=cognitive_analysis.get(
                    "development_score", 0.5
                ),
                developmental_concerns=developmental_concerns,
                intervention_recommendations=intervention_recommendations,
                urgency_level=urgency_level,
            )

            self.logger.info(f"Completed progress analysis for child {child_id}")
            return metrics

        except Exception as e:
            self.logger.error(f"Progress analysis failed for child {child_id}: {e}")
            raise

    def _analyze_vocabulary_nlp(
        self, interactions: List[InteractionAnalysis]
    ) -> Dict[str, Any]:
        """Advanced vocabulary analysis using NLP techniques"""
        try:
            if not interactions:
                return {
                    "total_unique_words": 0,
                    "new_words": [],
                    "complexity_score": 0.0,
                    "vocabulary_growth_rate": 0.0,
                }

            # Extract all topics and analyze vocabulary
            all_text = []
            for interaction in interactions:
                all_text.extend(interaction.topics_discussed)

            # Mock NLP analysis (in real implementation, use spaCy, NLTK, etc.)
            unique_words = set()
            for text in all_text:
                # Simple word extraction (mock)
                words = text.lower().split()
                unique_words.update(words)

            # Calculate complexity based on word length and diversity
            if unique_words:
                avg_word_length = sum(len(word) for word in unique_words) / len(
                    unique_words
                )
                complexity_score = min(avg_word_length / 8.0, 1.0)  # Normalize to 0-1
            else:
                complexity_score = 0.0

            # Estimate vocabulary growth
            vocab_growth_rate = len(unique_words) / max(len(interactions), 1)

            return {
                "total_unique_words": len(unique_words),
                "new_words": list(unique_words)[:10],  # Sample of new words
                "complexity_score": complexity_score,
                "vocabulary_growth_rate": vocab_growth_rate,
                "word_categories": self._categorize_words(unique_words),
                "advanced_vocabulary_usage": self._check_advanced_vocabulary(
                    unique_words
                ),
            }

        except Exception as e:
            self.logger.error(f"Vocabulary NLP analysis error: {e}")
            return {"total_unique_words": 0, "complexity_score": 0.0}

    def _analyze_emotional_nlp(
        self, interactions: List[InteractionAnalysis]
    ) -> Dict[str, Any]:
        """Advanced emotional analysis using NLP techniques"""
        try:
            if not interactions:
                return {
                    "intelligence_score": 0.0,
                    "emotion_regulation_score": 0.0,
                    "empathy_indicators": 0,
                }

            # Analyze emotional patterns
            emotion_distribution = self.emotion_analyzer.analyze_emotion_distribution(
                interactions
            )
            empathy_count = self.emotion_analyzer.count_empathy_indicators(interactions)

            # Calculate emotional intelligence score
            stability_factor = emotion_distribution.stability_score
            positive_emotion_ratio = sum(
                emotion_distribution.emotions.get(emotion, 0)
                for emotion in ["happy", "curious", "calm"]
            )

            intelligence_score = (
                stability_factor + positive_emotion_ratio + (empathy_count / 10)
            ) / 3
            intelligence_score = min(max(intelligence_score, 0.0), 1.0)

            # Analyze emotional regulation
            emotion_changes = 0
            for i in range(1, len(interactions)):
                if (
                    interactions[i].primary_emotion
                    != interactions[i - 1].primary_emotion
                ):
                    emotion_changes += 1

            regulation_score = 1.0 - (emotion_changes / max(len(interactions) - 1, 1))
            regulation_score = max(regulation_score, 0.0)

            return {
                "intelligence_score": intelligence_score,
                "emotion_regulation_score": regulation_score,
                "empathy_indicators": empathy_count,
                "dominant_emotions": emotion_distribution.emotions,
                "emotional_stability": emotion_distribution.stability_score,
                "social_emotional_markers": self._extract_social_emotional_markers(
                    interactions
                ),
            }

        except Exception as e:
            self.logger.error(f"Emotional NLP analysis error: {e}")
            return {"intelligence_score": 0.0}

    def _analyze_cognitive_nlp(
        self, interactions: List[InteractionAnalysis]
    ) -> Dict[str, Any]:
        """Advanced cognitive analysis using NLP techniques"""
        try:
            if not interactions:
                return {
                    "development_score": 0.0,
                    "reasoning_ability": 0.0,
                    "problem_solving_skills": 0.0,
                }

            # Analyze cognitive indicators
            skill_analysis = self.skill_analyzer.analyze_skills_practiced(interactions)
            behavioral_patterns = self.behavior_analyzer.analyze_behavioral_patterns(
                interactions
            )

            # Calculate cognitive development score
            skill_diversity = len(skill_analysis.skills_practiced)
            skill_mastery_avg = sum(skill_analysis.mastery_level.values()) / max(
                len(skill_analysis.mastery_level), 1
            )

            # Check for advanced cognitive skills
            advanced_skills = [
                "problem_solving",
                "critical_thinking",
                "creative_thinking",
            ]
            advanced_usage = sum(
                1
                for skill in advanced_skills
                if skill in skill_analysis.skills_practiced
            ) / len(advanced_skills)

            development_score = (
                skill_diversity / 10 + skill_mastery_avg + advanced_usage
            ) / 3
            development_score = min(max(development_score, 0.0), 1.0)

            # Analyze reasoning ability
            reasoning_indicators = sum(
                1
                for interaction in interactions
                if any(
                    skill in ["problem_solving", "logical_thinking"]
                    for skill in interaction.skills_used
                )
            )
            reasoning_ability = reasoning_indicators / max(len(interactions), 1)

            return {
                "development_score": development_score,
                "reasoning_ability": reasoning_ability,
                "problem_solving_skills": advanced_usage,
                "cognitive_flexibility": self._assess_cognitive_flexibility(
                    interactions
                ),
                "attention_regulation": behavioral_patterns.get(
                    "attention_consistency", "variable"
                ),
                "learning_progression": skill_analysis.get_total_practice_sessions(),
            }

        except Exception as e:
            self.logger.error(f"Cognitive NLP analysis error: {e}")
            return {"development_score": 0.0}

    def _identify_concerns_task7(
        self, vocab_analysis: Dict, emotional_analysis: Dict
    ) -> List[str]:
        """Identify developmental concerns based on comprehensive analysis"""
        try:
            concerns = []

            # Vocabulary concerns
            if vocab_analysis.get("complexity_score", 0) < 0.3:
                concerns.append("تأخر في تطوير المفردات المعقدة")

            if vocab_analysis.get("vocabulary_growth_rate", 0) < 2:
                concerns.append("بطء في اكتساب مفردات جديدة")

            # Emotional concerns
            if emotional_analysis.get("intelligence_score", 0) < 0.4:
                concerns.append("تحديات في الذكاء العاطفي")

            if emotional_analysis.get("emotion_regulation_score", 0) < 0.3:
                concerns.append("صعوبة في تنظيم المشاعر")

            # Social concerns
            if emotional_analysis.get("empathy_indicators", 0) < 2:
                concerns.append("انخفاض في مؤشرات التعاطف")

            return concerns

        except Exception as e:
            self.logger.error(f"Concerns identification error: {e}")
            return []

    def _generate_interventions_task7(
        self, vocab_analysis: Dict, emotional_analysis: Dict
    ) -> List[str]:
        """Generate targeted intervention recommendations"""
        try:
            interventions = []

            # Vocabulary interventions
            if vocab_analysis.get("complexity_score", 0) < 0.4:
                interventions.append("أنشطة تطوير المفردات المتقدمة")
                interventions.append("ألعاب الكلمات والمرادفات")

            # Emotional interventions
            if emotional_analysis.get("intelligence_score", 0) < 0.5:
                interventions.append("تمارين التعرف على المشاعر")
                interventions.append("أنشطة تطوير التعاطف")

            # Social interventions
            if emotional_analysis.get("empathy_indicators", 0) < 3:
                interventions.append("أنشطة التفاعل الاجتماعي الموجه")
                interventions.append("قصص تطوير التعاطف")

            return interventions

        except Exception as e:
            self.logger.error(f"Interventions generation error: {e}")
            return []

    def _calculate_urgency_task7(
        self, vocab_analysis: Dict, emotional_analysis: Dict
    ) -> UrgencyLevel:
        """Calculate urgency level for interventions"""
        try:
            urgency_score = 0

            # Check critical indicators
            if vocab_analysis.get("complexity_score", 0) < 0.2:
                urgency_score += 2

            if emotional_analysis.get("intelligence_score", 0) < 0.3:
                urgency_score += 2

            if emotional_analysis.get("emotion_regulation_score", 0) < 0.2:
                urgency_score += 3

            # Map score to urgency level
            if urgency_score >= 5:
                return UrgencyLevel.CRITICAL
            elif urgency_score >= 3:
                return UrgencyLevel.HIGH
            elif urgency_score >= 1:
                return UrgencyLevel.MEDIUM
            else:
                return UrgencyLevel.LOW

        except Exception as e:
            self.logger.error(f"Urgency calculation error: {e}")
            return UrgencyLevel.MEDIUM

    async def _get_recent_interactions(
        self, child_id: int
    ) -> List[InteractionAnalysis]:
        """Get recent interactions for analysis"""
        try:
            if self.db:
                return await self.db.get_recent_interactions(child_id, limit=20)

            # Mock data for testing
            return []

        except Exception as e:
            self.logger.error(f"Failed to get recent interactions for {child_id}: {e}")
            return []

    def _categorize_words(self, words: set) -> Dict[str, int]:
        """Categorize words by type (mock implementation)"""
        categories = {"nouns": 0, "verbs": 0, "adjectives": 0, "advanced": 0}

        # Mock categorization
        for word in words:
            if len(word) > 6:
                categories["advanced"] += 1
            elif word.endswith("ing"):
                categories["verbs"] += 1
            else:
                categories["nouns"] += 1

        return categories

    def _check_advanced_vocabulary(self, words: set) -> bool:
        """Check for advanced vocabulary usage"""
        advanced_words = {"complex", "understand", "because", "therefore", "however"}
        return len(advanced_words.intersection(words)) > 0

    def _extract_social_emotional_markers(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Extract social-emotional development markers"""
        markers = []

        for interaction in interactions:
            if "sharing" in interaction.behavioral_indicators:
                markers.append("sharing_behavior")
            if interaction.emotions.get("empathy", 0) > 0.5:
                markers.append("empathy_expression")

        return list(set(markers))

    def _assess_cognitive_flexibility(
        self, interactions: List[InteractionAnalysis]
    ) -> float:
        """Assess cognitive flexibility based on interaction patterns"""
        if not interactions:
            return 0.0

        topic_diversity = len(
            set().union(*[interaction.topics_discussed for interaction in interactions])
        )
        skill_diversity = len(
            set().union(*[interaction.skills_used for interaction in interactions])
        )

        flexibility_score = (topic_diversity + skill_diversity) / (
            len(interactions) * 2
        )
        return min(flexibility_score, 1.0)
