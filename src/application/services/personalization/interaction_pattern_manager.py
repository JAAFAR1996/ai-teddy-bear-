#!/usr/bin/env python3
"""
🎯 Interaction Pattern Management Service
خدمة إدارة أنماط التفاعل للطفل
"""

import logging
from datetime import datetime
from typing import Dict

from .data_models import InteractionPattern

logger = logging.getLogger(__name__)


class InteractionPatternManager:
    """مدير أنماط التفاعل"""

    def update_interaction_patterns(self, patterns: InteractionPattern, interaction_data: Dict) -> None:
        """تحديث أنماط التفاعل"""
        try:
            self._update_preferred_activities(patterns, interaction_data)
            self._update_favorite_topics(patterns, interaction_data)
            self._update_attention_patterns(patterns, interaction_data)
            self._update_response_patterns(patterns, interaction_data)
            self._update_mood_triggers(patterns, interaction_data)
            self._update_learning_preferences(patterns, interaction_data)
            self._update_social_interaction_style(patterns, interaction_data)
        except Exception as e:
            logger.error(f"خطأ في تحديث أنماط التفاعل: {e}")

    def _update_preferred_activities(self, patterns: InteractionPattern, interaction_data: Dict) -> None:
        """تحديث الأنشطة المفضلة"""
        activity = interaction_data.get("activity_type")
        if activity and activity not in patterns.preferred_activities:
            engagement = interaction_data.get("engagement_score", 0)
            if engagement > 0.7:  # إذا كان الانخراط عالي
                patterns.preferred_activities.append(activity)
                # الاحتفاظ بأفضل 10 أنشطة
                patterns.preferred_activities = patterns.preferred_activities[-10:]

    def _update_favorite_topics(self, patterns: InteractionPattern, interaction_data: Dict) -> None:
        """تحديث المواضيع المفضلة"""
        topic = interaction_data.get("topic")
        if topic:
            if topic not in patterns.favorite_topics:
                patterns.favorite_topics.append(topic)
                patterns.favorite_topics = patterns.favorite_topics[-15:]

    def _update_attention_patterns(self, patterns: InteractionPattern, interaction_data: Dict) -> None:
        """تحديث أوقات التفاعل النشط"""
        current_hour = datetime.now().strftime("%H")
        if interaction_data.get("engagement_score", 0) > 0.6:
            time_slot = self._get_time_slot(current_hour)
            patterns.attention_patterns[time_slot] = (
                patterns.attention_patterns.get(time_slot, 0) + 1
            )

    def _update_response_patterns(self, patterns: InteractionPattern, interaction_data: Dict) -> None:
        """تحديث أنماط الردود"""
        response_type = interaction_data.get("response_type")
        if response_type:
            patterns.response_patterns[response_type] = (
                patterns.response_patterns.get(response_type, 0) + 1
            )

    def _update_mood_triggers(self, patterns: InteractionPattern, interaction_data: Dict) -> None:
        """تحديث محفزات المزاج"""
        emotion = interaction_data.get("emotion")
        trigger = interaction_data.get("trigger")
        if emotion and trigger:
            mood_category = (
                "positive" if emotion in ["happy", "excited", "calm"] else "negative"
            )
            if trigger not in patterns.mood_triggers[mood_category]:
                patterns.mood_triggers[mood_category].append(trigger)
                patterns.mood_triggers[mood_category] = patterns.mood_triggers[
                    mood_category
                ][-10:]

    def _update_learning_preferences(self, patterns: InteractionPattern, interaction_data: Dict) -> None:
        """تحديث تفضيلات التعلم"""
        learning_method = interaction_data.get("learning_method")
        success_rate = interaction_data.get("success_rate", 0)
        if learning_method and success_rate > 0:
            current_pref = patterns.learning_preferences.get(learning_method, 0.5)
            # تحديث تدريجي بناءً على النجاح
            new_pref = current_pref * 0.8 + success_rate * 0.2
            patterns.learning_preferences[learning_method] = min(1.0, new_pref)

    def _update_social_interaction_style(self, patterns: InteractionPattern, interaction_data: Dict) -> None:
        """تحديث أسلوب التفاعل الاجتماعي"""
        conversation_length = interaction_data.get("conversation_length", 0)
        initiation_frequency = interaction_data.get("initiates_conversation", False)
        
        # تحديث أسلوب التفاعل بناءً على السلوك
        if conversation_length > 20 and initiation_frequency:
            patterns.social_interaction_style = "outgoing"
        elif conversation_length < 5 and not initiation_frequency:
            patterns.social_interaction_style = "shy"
        else:
            patterns.social_interaction_style = "moderate"

    def _get_time_slot(self, hour: str) -> str:
        """تحديد فترة اليوم"""
        hour_int = int(hour)
        if 6 <= hour_int < 12:
            return "morning"
        elif 12 <= hour_int < 18:
            return "afternoon"
        else:
            return "evening"

    def get_most_active_time(self, patterns: InteractionPattern) -> str:
        """الحصول على أكثر وقت نشاط"""
        if not patterns.attention_patterns:
            return "morning"
        
        return max(patterns.attention_patterns.items(), key=lambda x: x[1])[0]

    def get_dominant_response_pattern(self, patterns: InteractionPattern) -> str:
        """الحصول على نمط الرد المهيمن"""
        if not patterns.response_patterns:
            return "neutral"
        
        return max(patterns.response_patterns.items(), key=lambda x: x[1])[0]

    def get_learning_style_recommendation(self, patterns: InteractionPattern) -> str:
        """اقتراح أسلوب التعلم المفضل"""
        if not patterns.learning_preferences:
            return "storytelling"
        
        return max(patterns.learning_preferences.items(), key=lambda x: x[1])[0] 