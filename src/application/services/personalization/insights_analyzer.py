#!/usr/bin/env python3
"""
📊 محلل رؤى التخصيص
تحليل وتوليد الرؤى والتقارير - EXTRACT CLASS
"""

import logging
from collections import defaultdict
from typing import Dict, List

import numpy as np

logger = logging.getLogger(__name__)


class PersonalizationInsightsAnalyzer:
    """محلل رؤى التخصيص - مستخرج من AdvancedPersonalizationService"""

    def get_personalization_insights(self, personality, patterns, 
                                   content_performance: Dict) -> Dict:
        """الحصول على رؤى التخصيص الشاملة"""
        insights = {
            "personality_summary": self._get_personality_summary(personality),
            "learning_style": self._determine_learning_style(personality, patterns),
            "engagement_patterns": self._analyze_engagement_patterns(patterns),
            "content_preferences": self._analyze_content_preferences(content_performance),
            "optimization_suggestions": self._get_optimization_suggestions(personality, patterns),
            "development_areas": self._identify_development_areas(personality, patterns),
        }
        return insights

    def _get_personality_summary(self, personality) -> Dict:
        """ملخص الشخصية"""
        traits = {
            "openness": (
                "منفتح على التجارب" if personality.openness > 0.6 else "يفضل المألوف"
            ),
            "conscientiousness": (
                "مثابر ومنظم"
                if personality.conscientiousness > 0.6
                else "يحتاج تشجيع للإكمال"
            ),
            "extraversion": (
                "اجتماعي ونشط" if personality.extraversion > 0.6 else "هادئ ومتأمل"
            ),
            "agreeableness": (
                "متعاون ودود" if personality.agreeableness > 0.6 else "مستقل في الرأي"
            ),
            "neuroticism": (
                "حساس عاطفياً" if personality.neuroticism > 0.6 else "مستقر عاطفياً"
            ),
        }

        return {
            "dominant_traits": [
                trait
                for trait, desc in traits.items()
                if getattr(personality, trait) > 0.6
            ],
            "trait_descriptions": traits,
            "curiosity_level": (
                "عالي"
                if personality.curiosity_level > 0.6
                else "متوسط" if personality.curiosity_level > 0.3 else "منخفض"
            ),
            "creativity_level": (
                "عالي"
                if personality.creativity_level > 0.6
                else "متوسط" if personality.creativity_level > 0.3 else "منخفض"
            ),
        }

    def _determine_learning_style(self, personality, patterns) -> Dict:
        """تحديد أسلوب التعلم"""
        # تحليل تفضيلات التعلم
        learning_prefs = patterns.learning_preferences
        dominant_style = max(learning_prefs.items(), key=lambda x: x[1])

        recommendations = {
            "storytelling": "القصص والسرد",
            "games": "الألعاب التفاعلية",
            "songs": "الأغاني والموسيقى",
            "questions": "الأسئلة والحوار",
        }

        return {
            "dominant_style": dominant_style[0],
            "style_description": recommendations.get(dominant_style[0], "متنوع"),
            "all_preferences": learning_prefs,
            "recommendations": [
                recommendations[style]
                for style, score in learning_prefs.items()
                if score > 0.6
            ],
        }

    def _analyze_engagement_patterns(self, patterns) -> Dict:
        """تحليل أنماط الانخراط"""
        # تحليل أوقات الانتباه
        best_time = (
            max(patterns.attention_patterns.items(), key=lambda x: x[1])
            if patterns.attention_patterns
            else ("morning", 0)
        )

        return {
            "best_engagement_time": best_time[0],
            "attention_distribution": patterns.attention_patterns,
            "social_style": patterns.social_interaction_style,
            "response_patterns": patterns.response_patterns,
        }

    def _analyze_content_preferences(self, content_performance: List) -> Dict:
        """تحليل تفضيلات المحتوى"""
        if not content_performance:
            return {"message": "لا توجد بيانات كافية"}

        contents = content_performance

        # أفضل أنواع المحتوى
        content_scores = defaultdict(list)
        for content in contents:
            if hasattr(content, 'content_type') and hasattr(content, 'engagement_score'):
                content_scores[content.content_type].append(content.engagement_score)

        avg_scores = {
            content_type: np.mean(scores)
            for content_type, scores in content_scores.items()
        }
        best_content_type = (
            max(avg_scores.items(), key=lambda x: x[1])
            if avg_scores
            else ("unknown", 0)
        )

        # أفضل مواضيع
        topic_scores = defaultdict(list)
        for content in contents:
            if hasattr(content, 'topic') and content.topic and hasattr(content, 'engagement_score'):
                topic_scores[content.topic].append(content.engagement_score)

        avg_topic_scores = {
            topic: np.mean(scores) for topic, scores in topic_scores.items()
        }
        best_topics = sorted(
            avg_topic_scores.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "preferred_content_type": best_content_type[0],
            "content_type_scores": avg_scores,
            "preferred_topics": [topic for topic, score in best_topics],
            "topic_scores": dict(best_topics),
        }

    def _get_optimization_suggestions(self, personality, patterns) -> List[str]:
        """اقتراحات التحسين"""
        suggestions = []

        # اقتراحات بناءً على الشخصية
        if personality.attention_span < 10:
            suggestions.append("تقليل مدة الأنشطة لتناسب فترة الانتباه القصيرة")

        if personality.openness < 0.4:
            suggestions.append(
                "تقديم تجارب جديدة تدريجياً مع التأكيد على العناصر المألوفة"
            )

        if personality.conscientiousness < 0.4:
            suggestions.append("تقسيم المهام الكبيرة إلى خطوات صغيرة مع مكافآت متكررة")

        if personality.neuroticism > 0.6:
            suggestions.append("التركيز على الأنشطة المهدئة وتجنب المحتوى المثير للقلق")

        # اقتراحات بناءً على الأنماط
        if len(patterns.preferred_activities) < 3:
            suggestions.append("تجربة أنواع أنشطة متنوعة لاكتشاف تفضيلات جديدة")

        best_time = (
            max(patterns.attention_patterns.items(), key=lambda x: x[1])[0]
            if patterns.attention_patterns
            else None
        )
        if best_time:
            suggestions.append(f"جدولة الأنشطة المهمة في فترة {best_time}")

        return suggestions

    def _identify_development_areas(self, personality, patterns) -> Dict:
        """تحديد مجالات التطوير - تم تبسيطه من Complex Method (cc=11) إلى دوال منفصلة"""
        areas = {
            "strengths": self._identify_child_strengths(personality),
            "growth_areas": self._identify_growth_areas(personality),
            "focus_suggestions": self._generate_focus_suggestions(personality, patterns),
        }
        return areas

    def _identify_child_strengths(self, personality) -> List[str]:
        """تحديد نقاط القوة للطفل"""
        strengths = []
        
        if personality.curiosity_level > 0.6:
            strengths.append("فضول عالي للتعلم")
        if personality.creativity_level > 0.6:
            strengths.append("قدرة إبداعية مميزة")
        if personality.agreeableness > 0.6:
            strengths.append("روح تعاونية")
        if personality.conscientiousness > 0.6:
            strengths.append("مثابرة في إنجاز المهام")
            
        return strengths

    def _identify_growth_areas(self, personality) -> List[str]:
        """تحديد مجالات النمو والتطوير"""
        growth_areas = []
        
        if personality.openness < 0.4:
            growth_areas.append("الانفتاح على التجارب الجديدة")
        if personality.extraversion < 0.4:
            growth_areas.append("الثقة في التفاعل الاجتماعي")
        if personality.attention_span < 15:
            growth_areas.append("تطوير فترة التركيز")
            
        return growth_areas

    def _generate_focus_suggestions(self, personality, patterns) -> List[str]:
        """توليد اقتراحات التركيز"""
        suggestions = []
        
        if personality.creativity_level < 0.4:
            suggestions.append("أنشطة إبداعية مثل الرسم والقصص التفاعلية")
        if personality.conscientiousness < 0.4:
            suggestions.append("ألعاب تعزز المثابرة والتنظيم")
        if len(patterns.favorite_topics) < 3:
            suggestions.append("استكشاف مواضيع ومجالات معرفية متنوعة")
            
        return suggestions 