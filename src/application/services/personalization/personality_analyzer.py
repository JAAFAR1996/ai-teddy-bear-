#!/usr/bin/env python3
"""
🧠 محلل الشخصية للطفل
تحليل شخصية الطفل من التفاعلات بشكل متخصص - EXTRACT CLASS
"""

import logging
from datetime import datetime
from typing import Dict, List

import numpy as np

logger = logging.getLogger(__name__)


class PersonalityAnalyzer:
    """محلل الشخصية - مستخرج من AdvancedPersonalizationService"""

    def analyze_personality_from_interactions(
        self, current_personality, interactions: List[Dict]
    ):
        """تحليل الشخصية من التفاعلات - مقسمة لدوال متخصصة"""
        if not interactions:
            return current_personality

        # تحليل كل جانب من جوانب الشخصية منفصلاً
        current_personality.openness = self._analyze_openness(interactions)
        current_personality.extraversion = self._analyze_extraversion(interactions)
        current_personality.conscientiousness = self._analyze_conscientiousness(interactions)
        current_personality.agreeableness = self._analyze_agreeableness(interactions)
        current_personality.neuroticism = self._analyze_neuroticism(interactions)
        current_personality.curiosity_level = self._analyze_curiosity(interactions)
        current_personality.creativity_level = self._analyze_creativity(interactions)

        current_personality.last_updated = datetime.now().isoformat()
        return current_personality

    def _analyze_openness(self, interactions: List[Dict]) -> float:
        """تحليل مستوى الانفتاح على التجارب الجديدة"""
        new_activities = set()
        total_activities = 0

        for interaction in interactions:
            activity_type = interaction.get("activity_type", "")
            if activity_type:
                if activity_type not in new_activities:
                    new_activities.add(activity_type)
                total_activities += 1

        if total_activities > 0:
            return min(1.0, len(new_activities) / total_activities * 2)
        return 0.5

    def _analyze_extraversion(self, interactions: List[Dict]) -> float:
        """تحليل مستوى الانبساطية"""
        conversation_lengths = []

        for interaction in interactions:
            duration = interaction.get("duration_minutes", 0)
            if duration > 0:
                conversation_lengths.append(duration)

        if conversation_lengths:
            avg_length = np.mean(conversation_lengths)
            return min(1.0, avg_length / 30)  # 30 دقيقة = انبساطية كاملة
        return 0.5

    def _analyze_conscientiousness(self, interactions: List[Dict]) -> float:
        """تحليل مستوى المثابرة والضميرية"""
        completed_tasks = 0
        total_tasks = 0

        for interaction in interactions:
            if interaction.get("completed", False):
                completed_tasks += 1
            if "completed" in interaction:
                total_tasks += 1

        if total_tasks > 0:
            return completed_tasks / total_tasks
        return 0.5

    def _analyze_agreeableness(self, interactions: List[Dict]) -> float:
        """تحليل مستوى الوداعة والتعاون"""
        positive_responses = 0
        total_responses = 0

        for interaction in interactions:
            response_type = interaction.get("response_type", "")
            if response_type:
                total_responses += 1
                if response_type in ["positive", "enthusiastic", "cooperative"]:
                    positive_responses += 1

        if total_responses > 0:
            return positive_responses / total_responses
        return 0.5

    def _analyze_neuroticism(self, interactions: List[Dict]) -> float:
        """تحليل مستوى العصابية والقلق"""
        negative_emotions = 0
        total_emotions = 0

        for interaction in interactions:
            emotion = interaction.get("emotion", "")
            if emotion:
                total_emotions += 1
                if emotion in ["sad", "angry", "frustrated"]:
                    negative_emotions += 1

        if total_emotions > 0:
            return negative_emotions / total_emotions
        return 0.5

    def _analyze_curiosity(self, interactions: List[Dict]) -> float:
        """تحليل مستوى الفضول"""
        unique_topics = len(
            set(
                interaction.get("topic", "")
                for interaction in interactions
                if interaction.get("topic")
            )
        )
        return min(1.0, unique_topics / 10)  # 10 مواضيع مختلفة = فضول كامل

    def _analyze_creativity(self, interactions: List[Dict]) -> float:
        """تحليل مستوى الإبداع"""
        creative_activities = sum(
            1
            for interaction in interactions
            if interaction.get("activity_type")
            in ["storytelling", "creative_games", "art"]
        )
        
        if len(interactions) > 0:
            return min(1.0, creative_activities / len(interactions) * 2)
        return 0.5 