# ===================================================================
# 🧸 AI Teddy Bear - Feedback Collection System
# Enterprise ML Feedback Collection & Analysis
# ML Team Lead: Senior ML Engineer
# Date: January 2025
# ===================================================================

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List

import numpy as np

from .analysis_strategies import (
    EffectiveLearningStrategy,
    ExcellentSafetyStrategy,
    HighQualityStrategy,
    HighSatisfactionStrategy,
    LowQualityStrategy,
    LowSatisfactionStrategy,
    ParentExperienceStrategy,
    SafetyIssueStrategy,
)

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """أنواع التغذية الراجعة"""

    CHILD_INTERACTION = "child_interaction"
    PARENT_FEEDBACK = "parent_feedback"
    LEARNING_OUTCOME = "learning_outcome"
    SAFETY_INCIDENT = "safety_incident"
    ENGAGEMENT_METRIC = "engagement_metric"
    SATISFACTION_RATING = "satisfaction_rating"


@dataclass
class FeedbackData:
    """بيانات التغذية الراجعة"""

    feedback_id: str
    child_id: str
    feedback_type: FeedbackType
    timestamp: datetime
    content: Dict[str, Any]
    sentiment_score: float
    safety_score: float
    engagement_level: float
    learning_effectiveness: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractionFeedback:
    """تغذية راجعة من التفاعل"""

    conversation_id: str
    child_age: int
    interaction_duration: float
    response_quality: float
    child_satisfaction: float
    educational_value: float
    safety_compliance: bool
    topics_discussed: List[str]
    emotions_detected: List[str]


class FeedbackCollector:
    """جامع التغذية الراجعة الشامل"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feedback_buffer: List[FeedbackData] = []
        self.collection_stats = {
            "total_collected": 0,
            "by_type": {},
            "average_sentiment": 0.0,
            "safety_incidents": 0,
            "high_engagement_sessions": 0,
        }

        self._improvement_strategies = [
            LowQualityStrategy(),
            SafetyIssueStrategy(),
            LowSatisfactionStrategy(),
            ParentExperienceStrategy(),
        ]
        self._positive_trend_strategies = [
            HighQualityStrategy(),
            ExcellentSafetyStrategy(),
            HighSatisfactionStrategy(),
            EffectiveLearningStrategy(),
        ]

        logger.info("📊 Feedback Collector initialized")

    async def collect_daily_feedback(self) -> Dict[str, Any]:
        """جمع التغذية الراجعة اليومية من جميع المصادر"""

        logger.info("🔍 Starting daily feedback collection...")

        # جمع من مصادر متعددة بشكل متوازي
        collection_tasks = [
            self._collect_child_interactions(),
            self._collect_parent_feedback(),
            self._collect_learning_outcomes(),
            self._collect_safety_metrics(),
            self._collect_engagement_data(),
            self._collect_satisfaction_ratings(),
        ]

        results = await asyncio.gather(*collection_tasks, return_exceptions=True)

        # تجميع النتائج
        all_feedback = {
            "child_interactions": (
                results[0] if not isinstance(results[0], Exception) else []
            ),
            "parent_feedback": (
                results[1] if not isinstance(results[1], Exception) else []
            ),
            "learning_outcomes": (
                results[2] if not isinstance(results[2], Exception) else []
            ),
            "safety_metrics": (
                results[3] if not isinstance(results[3], Exception) else []
            ),
            "engagement_data": (
                results[4] if not isinstance(results[4], Exception) else []
            ),
            "satisfaction_ratings": (
                results[5] if not isinstance(results[5], Exception) else []
            ),
        }

        # تحليل وتصفية البيانات
        processed_feedback = await self._process_and_filter_feedback(all_feedback)

        # تحديث الإحصائيات
        await self._update_collection_stats(processed_feedback)

        logger.info(
            f"✅ Collected {len(processed_feedback.get('all_items', []))} feedback items"
        )

        return processed_feedback

    async def _collect_child_interactions(self) -> List[InteractionFeedback]:
        """جمع بيانات تفاعل الأطفال"""

        # محاكاة جمع بيانات التفاعل من قاعدة البيانات
        interactions = []

        # بيانات تفاعل محاكاة
        for i in range(50):  # 50 تفاعل يومي
            interaction = InteractionFeedback(
                conversation_id=f"conv_{datetime.now().strftime('%Y%m%d')}_{i:03d}",
                child_age=np.random.choice([3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
                interaction_duration=np.random.normal(
                    5.0, 2.0),  # 5 دقائق متوسط
                response_quality=np.random.beta(
                    8, 2),  # منحاز نحو الجودة العالية
                child_satisfaction=np.random.beta(7, 2),
                educational_value=np.random.beta(6, 3),
                safety_compliance=np.random.choice(
                    [True, False], p=[0.98, 0.02]),
                topics_discussed=np.random.choice(
                    [
                        ["animals", "nature"],
                        ["math", "counting"],
                        ["stories", "imagination"],
                        ["colors", "shapes"],
                        ["music", "songs"],
                        ["games", "puzzles"],
                    ]
                ),
                emotions_detected=np.random.choice(
                    [
                        ["happy", "excited"],
                        ["curious", "engaged"],
                        ["calm", "content"],
                        ["surprised", "delighted"],
                        ["focused", "attentive"],
                    ]
                ),
            )
            interactions.append(interaction)

        logger.info(f"📱 Collected {len(interactions)} child interactions")
        return interactions

    async def _collect_parent_feedback(self) -> List[Dict[str, Any]]:
        """جمع تغذية راجعة من الآباء"""

        parent_feedback = []

        # محاكاة تغذية راجعة من الآباء
        for i in range(15):  # 15 تقييم والدي يومي
            feedback = {
                "feedback_id": f"parent_{datetime.now().strftime('%Y%m%d')}_{i:03d}",
                "parent_id": f"parent_{i % 10}",
                "child_age": np.random.choice([3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
                "overall_satisfaction": np.random.beta(8, 2),
                "safety_confidence": np.random.beta(9, 1),
                "educational_value": np.random.beta(7, 2),
                "ease_of_use": np.random.beta(8, 2),
                "child_enjoyment": np.random.beta(8, 2),
                "would_recommend": np.random.choice([True, False], p=[0.9, 0.1]),
                "concerns": np.random.choice(
                    [
                        [],
                        ["screen_time"],
                        ["content_appropriateness"],
                        ["response_speed"],
                        ["variety_of_content"],
                    ],
                    p=[0.7, 0.1, 0.1, 0.05, 0.05],
                ),
                "suggestions": np.random.choice(
                    [
                        [],
                        ["more_educational_games"],
                        ["longer_conversations"],
                        ["more_personalization"],
                        ["better_voice_recognition"],
                    ],
                    p=[0.6, 0.15, 0.1, 0.1, 0.05],
                ),
                "timestamp": datetime.now() - timedelta(hours=np.random.randint(0, 24)),
            }
            parent_feedback.append(feedback)

        logger.info(
            f"👨‍👩‍👧‍👦 Collected {len(parent_feedback)} parent feedback items")
        return parent_feedback

    async def _collect_learning_outcomes(self) -> List[Dict[str, Any]]:
        """جمع نتائج التعلم"""

        learning_outcomes = []

        # محاكاة نتائج التعلم
        for i in range(30):  # 30 نتيجة تعلم يومية
            outcome = {
                "outcome_id": f"learning_{datetime.now().strftime('%Y%m%d')}_{i:03d}",
                "child_id": f"child_{i % 20}",
                "learning_objective": np.random.choice(
                    [
                        "number_recognition",
                        "letter_recognition",
                        "color_identification",
                        "shape_recognition",
                        "vocabulary_expansion",
                        "story_comprehension",
                        "emotional_recognition",
                        "social_skills",
                        "problem_solving",
                    ]
                ),
                "achievement_level": np.random.beta(6, 3),  # 0-1 scale
                "time_to_complete": np.random.normal(3.0, 1.0),  # minutes
                "attempts_needed": np.random.poisson(2) + 1,
                "engagement_during_learning": np.random.beta(7, 2),
                "retention_after_24h": np.random.beta(5, 3),
                "difficulty_level": np.random.choice(
                    ["easy", "medium", "hard"], p=[0.4, 0.4, 0.2]
                ),
                "learning_style_match": np.random.beta(6, 3),
                "timestamp": datetime.now() - timedelta(hours=np.random.randint(0, 24)),
            }
            learning_outcomes.append(outcome)

        logger.info(f"🎓 Collected {len(learning_outcomes)} learning outcomes")
        return learning_outcomes

    async def _collect_safety_metrics(self) -> List[Dict[str, Any]]:
        """جمع مقاييس الأمان"""

        safety_metrics = []

        # محاكاة مقاييس الأمان
        for i in range(100):  # 100 فحص أمان يومي
            metric = {
                "metric_id": f"safety_{datetime.now().strftime('%Y%m%d')}_{i:03d}",
                "interaction_id": f"interaction_{i}",
                "content_appropriateness": np.random.beta(20, 1),  # عالي جداً
                "language_safety": np.random.beta(20, 1),
                "emotional_safety": np.random.beta(15, 2),
                "privacy_compliance": np.random.choice([True, False], p=[0.999, 0.001]),
                "parental_control_respected": np.random.choice(
                    [True, False], p=[0.995, 0.005]
                ),
                "age_appropriateness": np.random.beta(18, 2),
                "harmful_content_detected": np.random.choice(
                    [False, True], p=[0.998, 0.002]
                ),
                "safety_flags": [] if np.random.random() > 0.02 else ["mild_language"],
                "auto_correction_applied": np.random.choice(
                    [False, True], p=[0.95, 0.05]
                ),
                "timestamp": datetime.now() - timedelta(hours=np.random.randint(0, 24)),
            }
            safety_metrics.append(metric)

        logger.info(f"🛡️ Collected {len(safety_metrics)} safety metrics")
        return safety_metrics

    async def _collect_engagement_data(self) -> List[Dict[str, Any]]:
        """جمع بيانات المشاركة"""

        engagement_data = []

        # محاكاة بيانات المشاركة
        for i in range(75):  # 75 جلسة مشاركة يومية
            engagement = {
                "engagement_id": f"engagement_{datetime.now().strftime('%Y%m%d')}_{i:03d}",
                "session_id": f"session_{i}",
                "child_age": np.random.choice([3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
                "session_duration": np.random.exponential(4.0),  # دقائق
                # تفاعلات في الجلسة
                "interaction_frequency": np.random.poisson(15),
                "attention_span": np.random.beta(5, 3),
                "response_enthusiasm": np.random.beta(6, 3),
                "question_asking_rate": np.random.poisson(3),
                "follow_up_engagement": np.random.beta(4, 4),
                "topic_switching_frequency": np.random.poisson(2),
                "emotional_engagement": np.random.beta(7, 2),
                "learning_momentum": np.random.beta(6, 3),
                "session_completion": np.random.choice([True, False], p=[0.85, 0.15]),
                "return_likelihood": np.random.beta(8, 2),
                "timestamp": datetime.now() - timedelta(hours=np.random.randint(0, 24)),
            }
            engagement_data.append(engagement)

        logger.info(f"🎯 Collected {len(engagement_data)} engagement metrics")
        return engagement_data

    async def _collect_satisfaction_ratings(self) -> List[Dict[str, Any]]:
        """جمع تقييمات الرضا"""

        satisfaction_ratings = []

        # محاكاة تقييمات الرضا
        for i in range(40):  # 40 تقييم رضا يومي
            rating = {
                "rating_id": f"satisfaction_{datetime.now().strftime('%Y%m%d')}_{i:03d}",
                "child_id": f"child_{i % 25}",
                "overall_satisfaction": np.random.beta(8, 2),
                "content_quality": np.random.beta(7, 2),
                "interaction_naturalness": np.random.beta(6, 3),
                "response_helpfulness": np.random.beta(7, 2),
                "entertainment_value": np.random.beta(8, 2),
                "educational_benefit": np.random.beta(6, 3),
                "ease_of_interaction": np.random.beta(8, 2),
                "voice_quality": np.random.beta(7, 2),
                "personalization_level": np.random.beta(5, 4),
                "safety_feeling": np.random.beta(9, 1),
                "would_use_again": np.random.choice([True, False], p=[0.9, 0.1]),
                "favorite_features": np.random.choice(
                    [["stories"], ["games"], ["learning"],
                        ["music"], ["conversations"]]
                ),
                "improvement_suggestions": np.random.choice(
                    [
                        [],
                        ["faster_responses"],
                        ["more_topics"],
                        ["better_understanding"],
                        ["more_games"],
                        ["longer_stories"],
                    ],
                    p=[0.6, 0.1, 0.1, 0.1, 0.05, 0.05],
                ),
                "timestamp": datetime.now() - timedelta(hours=np.random.randint(0, 24)),
            }
            satisfaction_ratings.append(rating)

        logger.info(
            f"⭐ Collected {len(satisfaction_ratings)} satisfaction ratings")
        return satisfaction_ratings

    def _process_individual_feedback(self, feedback_type: str, feedback_list: List[Any]) -> List[Dict[str, Any]]:
        """Processes a list of feedback items of a specific type."""
        processing_functions = {
            "child_interactions": self._process_child_interaction,
            "parent_feedback": self._process_parent_feedback,
            "learning_outcomes": self._process_learning_outcome,
        }

        func = processing_functions.get(feedback_type)
        if not func:
            return []

        return [func(item) for item in feedback_list if self._is_valid_feedback(feedback_type, item)]

    def _is_valid_feedback(self, feedback_type: str, item: Any) -> bool:
        if feedback_type == "child_interactions":
            return hasattr(item, "safety_compliance") and item.safety_compliance
        return True

    def _process_child_interaction(self, interaction: InteractionFeedback) -> Dict[str, Any]:
        return {
            "type": "child_interaction", "data": interaction,
            "quality_score": interaction.response_quality,
            "safety_score": 1.0 if interaction.safety_compliance else 0.0,
            "satisfaction": interaction.child_satisfaction,
        }

    def _process_parent_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "parent_feedback", "data": feedback,
            "quality_score": feedback["overall_satisfaction"],
            "safety_score": feedback["safety_confidence"],
            "satisfaction": feedback["overall_satisfaction"],
        }

    def _process_learning_outcome(self, outcome: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "learning_outcome", "data": outcome,
            "quality_score": outcome["achievement_level"],
            "safety_score": 1.0,
            "satisfaction": outcome["engagement_during_learning"],
        }

    def _calculate_learning_metrics(self, items: List[Dict[str, Any]], processed: Dict[str, Any]):
        """Calculates metrics related to learning outcomes."""
        learning_items = [
            item for item in items if item["type"] == "learning_outcome"]
        if learning_items:
            processed["learning_effectiveness"] = np.mean(
                [item["quality_score"] for item in learning_items])

    def _calculate_engagement_metrics(self, items: List[Dict[str, Any]], processed: Dict[str, Any]):
        """Calculates metrics related to child engagement."""
        engagement_items = [
            item for item in items if item["type"] == "child_interaction"]
        if engagement_items:
            processed["engagement_score"] = np.mean(
                [item["satisfaction"] for item in engagement_items])

    def _calculate_parent_satisfaction_metrics(self, items: List[Dict[str, Any]], processed: Dict[str, Any]):
        """Calculates metrics related to parent satisfaction."""
        parent_items = [
            item for item in items if item["type"] == "parent_feedback"]
        if parent_items:
            processed["parent_satisfaction"] = np.mean(
                [item["satisfaction"] for item in parent_items])

    async def _calculate_aggregate_metrics(self, all_items: List[Dict[str, Any]], processed: Dict[str, Any]):
        """Calculates and populates aggregate metrics from all processed feedback items."""
        if not all_items:
            return

        processed["total_items"] = len(all_items)
        processed["quality_score"] = np.mean(
            [item["quality_score"] for item in all_items])
        processed["safety_incidents"] = sum(
            1 for item in all_items if item["safety_score"] < 0.95)
        processed["high_satisfaction_rate"] = sum(
            1 for item in all_items if item["satisfaction"] > 0.8) / len(all_items)

        self._calculate_learning_metrics(all_items, processed)
        self._calculate_engagement_metrics(all_items, processed)
        self._calculate_parent_satisfaction_metrics(all_items, processed)

    async def _process_and_filter_feedback(
        self, raw_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """معالجة وتصفية التغذية الراجعة"""

        processed = {
            "collection_date": datetime.now(),
            "total_items": 0,
            "quality_score": 0.0,
            "safety_incidents": 0,
            "high_satisfaction_rate": 0.0,
            "learning_effectiveness": 0.0,
            "engagement_score": 0.0,
            "parent_satisfaction": 0.0,
            "areas_for_improvement": [],
            "positive_trends": [],
            "all_items": [],
        }

        feedback_map = {
            "child_interactions": raw_feedback.get("child_interactions", []),
            "parent_feedback": raw_feedback.get("parent_feedback", []),
            "learning_outcomes": raw_feedback.get("learning_outcomes", []),
        }

        all_items = []
        for feedback_type, feedback_list in feedback_map.items():
            all_items.extend(self._process_individual_feedback(
                feedback_type, feedback_list))

        await self._calculate_aggregate_metrics(all_items, processed)

        processed["areas_for_improvement"] = await self._identify_improvement_areas(
            all_items
        )
        processed["positive_trends"] = await self._identify_positive_trends(all_items)

        processed["all_items"] = all_items

        return processed

    async def _identify_improvement_areas(
        self, feedback_items: List[Dict]
    ) -> List[str]:
        """تحديد مجالات التحسين"""
        improvement_areas = []
        for strategy in self._improvement_strategies:
            result = strategy.analyze(feedback_items)
            if result:
                improvement_areas.append(result)
        return list(set(improvement_areas))

    async def _identify_positive_trends(
            self, feedback_items: List[Dict]) -> List[str]:
        """تحديد الاتجاهات الإيجابية"""
        positive_trends = []
        for strategy in self._positive_trend_strategies:
            result = strategy.analyze(feedback_items)
            if result:
                positive_trends.append(result)
        return list(set(positive_trends))

    async def _update_collection_stats(
        self, processed_feedback: Dict[str, Any]
    ) -> None:
        """تحديث إحصائيات الجمع"""

        self.collection_stats["total_collected"] += processed_feedback["total_items"]
        self.collection_stats["average_sentiment"] = processed_feedback["quality_score"]
        self.collection_stats["safety_incidents"] += processed_feedback[
            "safety_incidents"
        ]

        # تحديث الإحصائيات حسب النوع
        for item in processed_feedback["all_items"]:
            item_type = item["type"]
            if item_type not in self.collection_stats["by_type"]:
                self.collection_stats["by_type"][item_type] = 0
            self.collection_stats["by_type"][item_type] += 1

        # حساب الجلسات عالية المشاركة
        high_engagement = sum(
            1 for item in processed_feedback["all_items"] if item["satisfaction"] > 0.8)
        self.collection_stats["high_engagement_sessions"] += high_engagement

        logger.info(
            f"📈 Updated collection stats: {self.collection_stats['total_collected']} total items collected"
        )
