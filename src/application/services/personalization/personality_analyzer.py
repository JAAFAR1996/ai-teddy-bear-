#!/usr/bin/env python3
"""
🧠 Personality Analysis Service
خدمة تحليل شخصية الطفل من التفاعلات
"""

import logging
from datetime import datetime
from typing import Dict, List

from .data_models import ChildPersonality

logger = logging.getLogger(__name__)


class PersonalityAnalyzer:
    """محلل شخصية الطفل"""

    def analyze_personality_from_interactions(
        self, personality: ChildPersonality, interactions: List[Dict]
    ) -> ChildPersonality:
        """تحليل الشخصية من التفاعلات"""
        if not interactions:
            return personality

        # تحليل مختلف جوانب الشخصية
        self._analyze_openness(personality, interactions)
        self._analyze_conscientiousness(personality, interactions)
        self._analyze_extraversion(personality, interactions)
        self._analyze_agreeableness(personality, interactions)
        self._analyze_neuroticism(personality, interactions)
        self._analyze_curiosity_and_creativity(personality, interactions)
        self._update_learning_preferences(personality, interactions)

        personality.last_updated = datetime.now().isoformat()
        return personality

    def _analyze_openness(self, personality: ChildPersonality, interactions: List[Dict]) -> None:
        """تحليل الانفتاح على التجارب الجديدة"""
        novelty_seeking = 0
        total_interactions = len(interactions)

        for interaction in interactions:
            # البحث عن مؤشرات الانفتاح
            if interaction.get("content_type") == "new_experience":
                novelty_seeking += 1
            if interaction.get("response_to_new_content", "").lower() in ["positive", "interested"]:
                novelty_seeking += 1
            if interaction.get("asks_follow_up_questions", False):
                novelty_seeking += 1

        openness_score = novelty_seeking / (total_interactions * 3) if total_interactions > 0 else 0.5
        personality.openness = self._weighted_update(personality.openness, openness_score)

    def _analyze_conscientiousness(self, personality: ChildPersonality, interactions: List[Dict]) -> None:
        """تحليل المثابرة والضميرية"""
        completion_rate = 0
        task_persistence = 0
        total_tasks = 0

        for interaction in interactions:
            if interaction.get("task_type"):
                total_tasks += 1
                if interaction.get("task_completed", False):
                    completion_rate += 1
                if interaction.get("gave_up_early", False):
                    task_persistence -= 1
                else:
                    task_persistence += 1

        if total_tasks > 0:
            conscientiousness_score = (completion_rate + task_persistence) / (total_tasks * 2)
            personality.conscientiousness = self._weighted_update(
                personality.conscientiousness, conscientiousness_score
            )

    def _analyze_extraversion(self, personality: ChildPersonality, interactions: List[Dict]) -> None:
        """تحليل الانبساطية"""
        social_indicators = 0
        total_interactions = len(interactions)

        for interaction in interactions:
            # مؤشرات الانبساطية
            if interaction.get("engagement_level", 0) > 0.7:
                social_indicators += 1
            if interaction.get("initiates_conversation", False):
                social_indicators += 1
            if interaction.get("response_length", 0) > 10:  # ردود طويلة
                social_indicators += 1

        extraversion_score = social_indicators / (total_interactions * 3) if total_interactions > 0 else 0.5
        personality.extraversion = self._weighted_update(personality.extraversion, extraversion_score)

    def _analyze_agreeableness(self, personality: ChildPersonality, interactions: List[Dict]) -> None:
        """تحليل الوداعة والتعاون"""
        cooperation_score = 0
        total_interactions = len(interactions)

        for interaction in interactions:
            # مؤشرات التعاون
            if interaction.get("follows_instructions", False):
                cooperation_score += 1
            if interaction.get("polite_responses", False):
                cooperation_score += 1
            if interaction.get("shows_empathy", False):
                cooperation_score += 1

        agreeableness_score = cooperation_score / (total_interactions * 3) if total_interactions > 0 else 0.5
        personality.agreeableness = self._weighted_update(personality.agreeableness, agreeableness_score)

    def _analyze_neuroticism(self, personality: ChildPersonality, interactions: List[Dict]) -> None:
        """تحليل العصابية والقلق"""
        anxiety_indicators = 0
        total_interactions = len(interactions)

        for interaction in interactions:
            # مؤشرات القلق
            if interaction.get("shows_anxiety", False):
                anxiety_indicators += 1
            if interaction.get("needs_reassurance", False):
                anxiety_indicators += 1
            if interaction.get("mood") in ["sad", "worried", "anxious"]:
                anxiety_indicators += 1

        neuroticism_score = anxiety_indicators / (total_interactions * 3) if total_interactions > 0 else 0.5
        personality.neuroticism = self._weighted_update(personality.neuroticism, neuroticism_score)

    def _analyze_curiosity_and_creativity(self, personality: ChildPersonality, interactions: List[Dict]) -> None:
        """تحليل الفضول والإبداع"""
        curiosity_score = 0
        creativity_score = 0
        total_interactions = len(interactions)

        for interaction in interactions:
            # مؤشرات الفضول
            if interaction.get("asks_questions", False):
                curiosity_score += 1
            if interaction.get("explores_further", False):
                curiosity_score += 1

            # مؤشرات الإبداع
            if interaction.get("creative_response", False):
                creativity_score += 1
            if interaction.get("suggests_alternatives", False):
                creativity_score += 1

        if total_interactions > 0:
            curiosity_level = curiosity_score / (total_interactions * 2)
            creativity_level = creativity_score / (total_interactions * 2)
            
            personality.curiosity_level = self._weighted_update(personality.curiosity_level, curiosity_level)
            personality.creativity_level = self._weighted_update(personality.creativity_level, creativity_level)

    def _update_learning_preferences(self, personality: ChildPersonality, interactions: List[Dict]) -> None:
        """تحديث تفضيلات التعلم"""
        learning_style_count = {"visual": 0, "auditory": 0, "kinesthetic": 0}
        attention_span_data = []

        for interaction in interactions:
            # تحليل أسلوب التعلم المفضل
            if interaction.get("prefers_visual", False):
                learning_style_count["visual"] += 1
            if interaction.get("prefers_audio", False):
                learning_style_count["auditory"] += 1
            if interaction.get("prefers_interactive", False):
                learning_style_count["kinesthetic"] += 1

            # تحليل فترة الانتباه
            duration = interaction.get("attention_duration", 0)
            if duration > 0:
                attention_span_data.append(duration)

        # تحديث أسلوب التعلم
        if any(learning_style_count.values()):
            dominant_style = max(learning_style_count.items(), key=lambda x: x[1])
            personality.learning_style = dominant_style[0]

        # تحديث فترة الانتباه
        if attention_span_data:
            avg_attention = sum(attention_span_data) / len(attention_span_data)
            personality.attention_span = int(avg_attention)

    def _weighted_update(self, current_value: float, new_value: float, weight: float = 0.3) -> float:
        """تحديث مرجح للقيم"""
        return min(1.0, max(0.0, current_value * (1 - weight) + new_value * weight)) 