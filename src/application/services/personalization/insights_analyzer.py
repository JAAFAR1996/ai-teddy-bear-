#!/usr/bin/env python3
"""
📊 Personalization Insights Analysis Service
خدمة تحليل الرؤى والإحصائيات للتخصيص
"""

import logging
from collections import defaultdict
from typing import Dict, List

import numpy as np

from .data_models import ChildPersonality, InteractionPattern, AdaptiveContent

logger = logging.getLogger(__name__)


class PersonalizationInsightsAnalyzer:
    """محلل رؤى التخصيص"""

    def get_personalization_insights(
        self,
        personality: ChildPersonality,
        patterns: InteractionPattern,
        content_performance: List[AdaptiveContent]
    ) -> Dict:
        """الحصول على رؤى التخصيص الشاملة"""
        try:
            return {
                "personality_summary": self._get_personality_summary(personality),
                "learning_style_analysis": self._determine_learning_style(personality, patterns),
                "engagement_patterns": self._analyze_engagement_patterns(patterns),
                "content_preferences": self._analyze_content_preferences(content_performance),
                "optimization_suggestions": self._get_optimization_suggestions(personality, patterns),
                "development_areas": self._identify_development_areas(personality, patterns),
                "success_metrics": self._calculate_success_metrics(content_performance),
                "interaction_trends": self._analyze_interaction_trends(patterns)
            }
        except Exception as e:
            logger.error(f"خطأ في تحليل رؤى التخصيص: {e}")
            return {"error": "حدث خطأ في التحليل"}

    def _get_personality_summary(self, personality: ChildPersonality) -> Dict:
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
            "curiosity_level": self._get_level_description(personality.curiosity_level),
            "creativity_level": self._get_level_description(personality.creativity_level),
            "attention_span": f"{personality.attention_span} دقيقة",
            "preferred_difficulty": personality.preferred_difficulty,
            "learning_style": personality.learning_style
        }

    def _determine_learning_style(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> Dict:
        """تحديد أسلوب التعلم"""
        # تحليل تفضيلات التعلم
        learning_prefs = patterns.learning_preferences
        dominant_style = max(learning_prefs.items(), key=lambda x: x[1]) if learning_prefs else ("storytelling", 0.5)

        recommendations_map = {
            "storytelling": "القصص والسرد",
            "games": "الألعاب التفاعلية",
            "songs": "الأغاني والموسيقى",
            "questions": "الأسئلة والحوار",
        }

        return {
            "dominant_style": dominant_style[0],
            "style_description": recommendations_map.get(dominant_style[0], "متنوع"),
            "confidence_score": dominant_style[1],
            "all_preferences": learning_prefs,
            "recommendations": [
                recommendations_map[style]
                for style, score in learning_prefs.items()
                if score > 0.6
            ],
            "learning_efficiency": self._calculate_learning_efficiency(personality, patterns)
        }

    def _analyze_engagement_patterns(self, patterns: InteractionPattern) -> Dict:
        """تحليل أنماط الانخراط"""
        # تحليل أوقات الانتباه
        best_time = (
            max(patterns.attention_patterns.items(), key=lambda x: x[1])
            if patterns.attention_patterns
            else ("morning", 0)
        )

        # تحليل التوزيع الزمني
        total_attention = sum(patterns.attention_patterns.values()) if patterns.attention_patterns else 1
        time_distribution = {
            time_slot: (count / total_attention) * 100
            for time_slot, count in patterns.attention_patterns.items()
        } if patterns.attention_patterns else {}

        return {
            "best_engagement_time": best_time[0],
            "best_time_score": best_time[1],
            "time_distribution": time_distribution,
            "social_style": patterns.social_interaction_style,
            "response_patterns": patterns.response_patterns,
            "most_common_response": self._get_dominant_response_pattern(patterns),
            "engagement_consistency": self._calculate_engagement_consistency(patterns)
        }

    def _analyze_content_preferences(self, content_performance: List[AdaptiveContent]) -> Dict:
        """تحليل تفضيلات المحتوى"""
        if not content_performance:
            return {"message": "لا توجد بيانات كافية"}

        # أفضل أنواع المحتوى
        content_scores = defaultdict(list)
        for content in content_performance:
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
        for content in content_performance:
            if content.topic:
                topic_scores[content.topic].append(content.engagement_score)

        avg_topic_scores = {
            topic: np.mean(scores) for topic, scores in topic_scores.items()
        }
        best_topics = sorted(
            avg_topic_scores.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # تحليل المستوى المفضل
        difficulty_performance = self._analyze_difficulty_performance(content_performance)

        return {
            "preferred_content_type": best_content_type[0],
            "content_type_confidence": best_content_type[1],
            "content_type_scores": avg_scores,
            "preferred_topics": [topic for topic, score in best_topics],
            "topic_scores": dict(best_topics),
            "difficulty_analysis": difficulty_performance,
            "content_diversity": len(set(c.content_type for c in content_performance)),
            "average_engagement": np.mean([c.engagement_score for c in content_performance])
        }

    def _get_optimization_suggestions(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> List[str]:
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

        best_time = self._get_best_engagement_time(patterns)
        if best_time:
            suggestions.append(f"جدولة الأنشطة المهمة في فترة {best_time}")

        # اقتراحات متقدمة
        if personality.creativity_level > 0.7:
            suggestions.append("إضافة المزيد من الأنشطة الإبداعية والتفاعلية")

        if personality.extraversion > 0.7:
            suggestions.append("تشجيع الأنشطة الاجتماعية والتفاعل الصوتي")

        return suggestions

    def _identify_development_areas(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> Dict:
        """تحديد مجالات التطوير"""
        return {
            "strengths": self._identify_child_strengths(personality),
            "growth_areas": self._identify_growth_areas(personality),
            "focus_suggestions": self._generate_focus_suggestions(personality, patterns),
            "developmental_priority": self._get_developmental_priority(personality),
            "skill_recommendations": self._get_skill_recommendations(personality, patterns)
        }

    def _identify_child_strengths(self, personality: ChildPersonality) -> List[str]:
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
        if personality.extraversion > 0.6:
            strengths.append("مهارات تواصل جيدة")
        if personality.openness > 0.6:
            strengths.append("استعداد لتجارب جديدة")
            
        return strengths

    def _identify_growth_areas(self, personality: ChildPersonality) -> List[str]:
        """تحديد مجالات النمو والتطوير"""
        growth_areas = []
        
        if personality.openness < 0.4:
            growth_areas.append("الانفتاح على التجارب الجديدة")
        if personality.extraversion < 0.4:
            growth_areas.append("الثقة في التفاعل الاجتماعي")
        if personality.attention_span < 15:
            growth_areas.append("تطوير فترة التركيز")
        if personality.conscientiousness < 0.4:
            growth_areas.append("تحسين المثابرة والتنظيم")
        if personality.creativity_level < 0.4:
            growth_areas.append("تنمية القدرات الإبداعية")
            
        return growth_areas

    def _generate_focus_suggestions(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> List[str]:
        """توليد اقتراحات التركيز"""
        suggestions = []
        
        if personality.creativity_level < 0.4:
            suggestions.append("أنشطة إبداعية مثل الرسم والقصص التفاعلية")
        if personality.conscientiousness < 0.4:
            suggestions.append("ألعاب تعزز المثابرة والتنظيم")
        if len(patterns.favorite_topics) < 3:
            suggestions.append("استكشاف مواضيع ومجالات معرفية متنوعة")
        if personality.extraversion < 0.4:
            suggestions.append("أنشطة تشجع على التفاعل الاجتماعي")
            
        return suggestions

    # Helper methods
    def _get_level_description(self, level: float) -> str:
        """وصف مستوى معين"""
        if level > 0.7:
            return "عالي"
        elif level > 0.4:
            return "متوسط"
        else:
            return "منخفض"

    def _calculate_learning_efficiency(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> float:
        """حساب كفاءة التعلم"""
        # حساب بسيط يأخذ في الاعتبار عدة عوامل
        efficiency = 0.0
        
        # عامل فترة الانتباه
        efficiency += min(personality.attention_span / 30, 1.0) * 0.3
        
        # عامل الفضول والإبداع
        efficiency += (personality.curiosity_level + personality.creativity_level) / 2 * 0.4
        
        # عامل المثابرة
        efficiency += personality.conscientiousness * 0.3
        
        return min(efficiency, 1.0)

    def _get_dominant_response_pattern(self, patterns: InteractionPattern) -> str:
        """الحصول على نمط الرد المهيمن"""
        if not patterns.response_patterns:
            return "غير محدد"
        
        return max(patterns.response_patterns.items(), key=lambda x: x[1])[0]

    def _calculate_engagement_consistency(self, patterns: InteractionPattern) -> float:
        """حساب ثبات الانخراط"""
        if not patterns.attention_patterns:
            return 0.5
        
        values = list(patterns.attention_patterns.values())
        if len(values) < 2:
            return 1.0
        
        # حساب الانحراف المعياري كمؤشر على الثبات
        std_dev = np.std(values)
        mean_val = np.mean(values)
        
        # كلما قل الانحراف المعياري، زاد الثبات
        consistency = max(0.0, 1.0 - (std_dev / max(mean_val, 1.0)))
        return consistency

    def _analyze_difficulty_performance(self, content_performance: List[AdaptiveContent]) -> Dict:
        """تحليل الأداء حسب مستوى الصعوبة"""
        difficulty_scores = defaultdict(list)
        
        for content in content_performance:
            difficulty_scores[content.difficulty_level].append(content.engagement_score)
        
        return {
            level: {
                "average_engagement": np.mean(scores),
                "count": len(scores),
                "consistency": np.std(scores)
            }
            for level, scores in difficulty_scores.items()
        }

    def _get_best_engagement_time(self, patterns: InteractionPattern) -> str:
        """الحصول على أفضل وقت للانخراط"""
        if not patterns.attention_patterns:
            return None
        
        return max(patterns.attention_patterns.items(), key=lambda x: x[1])[0]

    def _get_developmental_priority(self, personality: ChildPersonality) -> str:
        """تحديد الأولوية التطويرية"""
        priorities = []
        
        if personality.attention_span < 10:
            priorities.append(("attention", personality.attention_span))
        if personality.creativity_level < 0.3:
            priorities.append(("creativity", personality.creativity_level))
        if personality.conscientiousness < 0.3:
            priorities.append(("persistence", personality.conscientiousness))
        
        if not priorities:
            return "تعزيز نقاط القوة الحالية"
        
        # إرجاع الأولوية الأقل درجة
        priority_name = min(priorities, key=lambda x: x[1])[0]
        priority_map = {
            "attention": "تطوير فترة الانتباه",
            "creativity": "تنمية الإبداع",
            "persistence": "تعزيز المثابرة"
        }
        
        return priority_map.get(priority_name, "التطوير الشامل")

    def _get_skill_recommendations(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> List[str]:
        """اقتراحات تطوير المهارات"""
        recommendations = []
        
        # بناءً على نقاط الضعف
        if personality.extraversion < 0.4:
            recommendations.append("مهارات التواصل والتفاعل")
        if personality.creativity_level < 0.4:
            recommendations.append("مهارات التفكير الإبداعي")
        if personality.conscientiousness < 0.4:
            recommendations.append("مهارات التنظيم وإدارة المهام")
        
        # بناءً على الاهتمامات
        if len(patterns.favorite_topics) > 0:
            recommendations.append(f"تعميق المعرفة في {patterns.favorite_topics[0]}")
        
        return recommendations

    def _calculate_success_metrics(self, content_performance: List[AdaptiveContent]) -> Dict:
        """حساب مقاييس النجاح"""
        if not content_performance:
            return {}
        
        engagement_scores = [c.engagement_score for c in content_performance]
        success_rates = [c.success_rate for c in content_performance]
        
        return {
            "average_engagement": np.mean(engagement_scores),
            "engagement_trend": self._calculate_trend(engagement_scores),
            "average_success_rate": np.mean(success_rates),
            "success_trend": self._calculate_trend(success_rates),
            "total_interactions": len(content_performance),
            "high_engagement_percentage": len([s for s in engagement_scores if s > 0.7]) / len(engagement_scores) * 100
        }

    def _analyze_interaction_trends(self, patterns: InteractionPattern) -> Dict:
        """تحليل اتجاهات التفاعل"""
        return {
            "activity_diversity": len(patterns.preferred_activities),
            "topic_diversity": len(patterns.favorite_topics),
            "response_consistency": self._calculate_response_consistency(patterns),
            "social_interaction_level": patterns.social_interaction_style,
            "mood_balance": self._analyze_mood_balance(patterns)
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """حساب الاتجاه العام للقيم"""
        if len(values) < 2:
            return "مستقر"
        
        # حساب الاتجاه باستخدام الانحدار الخطي البسيط
        x = list(range(len(values)))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.05:
            return "متزايد"
        elif slope < -0.05:
            return "متناقص"
        else:
            return "مستقر"

    def _calculate_response_consistency(self, patterns: InteractionPattern) -> float:
        """حساب ثبات الردود"""
        if not patterns.response_patterns:
            return 0.5
        
        total_responses = sum(patterns.response_patterns.values())
        if total_responses == 0:
            return 0.5
        
        # حساب التوزيع
        proportions = [count / total_responses for count in patterns.response_patterns.values()]
        
        # حساب الانتروبيا كمؤشر على التنوع (العكس هو الثبات)
        entropy = -sum(p * np.log2(p) for p in proportions if p > 0)
        max_entropy = np.log2(len(proportions))
        
        # تحويل الانتروبيا إلى مؤشر ثبات
        return 1.0 - (entropy / max_entropy) if max_entropy > 0 else 1.0

    def _analyze_mood_balance(self, patterns: InteractionPattern) -> Dict:
        """تحليل توازن المزاج"""
        positive_triggers = len(patterns.mood_triggers.get("positive", []))
        negative_triggers = len(patterns.mood_triggers.get("negative", []))
        total = positive_triggers + negative_triggers
        
        if total == 0:
            return {"balance": "متوازن", "positive_ratio": 0.5}
        
        positive_ratio = positive_triggers / total
        
        if positive_ratio > 0.7:
            balance = "إيجابي"
        elif positive_ratio < 0.3:
            balance = "يحتاج دعم"
        else:
            balance = "متوازن"
        
        return {
            "balance": balance,
            "positive_ratio": positive_ratio,
            "positive_triggers_count": positive_triggers,
            "negative_triggers_count": negative_triggers
        } 