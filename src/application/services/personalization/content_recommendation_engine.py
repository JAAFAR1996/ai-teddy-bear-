#!/usr/bin/env python3
"""
🎮 محرك اقتراح المحتوى
اقتراح المحتوى المخصص للطفل - EXTRACT CLASS
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ContentRecommendationEngine:
    """محرك اقتراح المحتوى - مستخرج من AdvancedPersonalizationService"""

    def recommend_content(self, personality, patterns, content_type: str = None) -> List[Dict]:
        """اقتراح محتوى مخصص"""
        recommendations = []

        # أساس التوصيات
        if not content_type or content_type == "story":
            story_recs = self._recommend_stories(personality, patterns)
            recommendations.extend(story_recs)

        if not content_type or content_type == "game":
            game_recs = self._recommend_games(personality, patterns)
            recommendations.extend(game_recs)

        if not content_type or content_type == "conversation":
            conv_recs = self._recommend_conversations(personality, patterns)
            recommendations.extend(conv_recs)

        # ترتيب التوصيات حسب الملاءمة
        recommendations = sorted(
            recommendations, key=lambda x: x["suitability_score"], reverse=True
        )

        return recommendations[:10]  # أفضل 10 توصيات

    def _recommend_stories(self, personality, patterns) -> List[Dict]:
        """اقتراح قصص مخصصة"""
        stories = []

        # قصص بناءً على الانفتاح
        if personality.openness > 0.7:
            stories.append(
                {
                    "type": "story",
                    "title": "مغامرة في عالم غريب",
                    "theme": "exploration",
                    "difficulty": (
                        "hard"
                        if personality.preferred_difficulty == "hard"
                        else "medium"
                    ),
                    "duration": personality.attention_span,
                    "suitability_score": 0.9,
                }
            )
        elif personality.openness < 0.3:
            stories.append(
                {
                    "type": "story",
                    "title": "حكاية مألوفة مع لمسة جديدة",
                    "theme": "familiar",
                    "difficulty": "easy",
                    "duration": min(15, personality.attention_span),
                    "suitability_score": 0.8,
                }
            )

        # قصص بناءً على المواضيع المفضلة
        for topic in patterns.favorite_topics[:3]:
            stories.append(
                {
                    "type": "story",
                    "title": f"قصة عن {topic}",
                    "theme": topic,
                    "difficulty": personality.preferred_difficulty,
                    "duration": personality.attention_span,
                    "suitability_score": 0.85,
                }
            )

        # قصص بناءً على الإبداع
        if personality.creativity_level > 0.6:
            stories.append(
                {
                    "type": "interactive_story",
                    "title": "اصنع قصتك الخاصة",
                    "theme": "creative",
                    "difficulty": personality.preferred_difficulty,
                    "duration": personality.attention_span + 10,
                    "suitability_score": 0.87,
                }
            )

        return stories

    def _recommend_games(self, personality, patterns) -> List[Dict]:
        """اقتراح ألعاب مخصصة"""
        games = []

        # ألعاب بناءً على الانبساطية
        if personality.extraversion > 0.6:
            games.append(
                {
                    "type": "social_game",
                    "title": "لعبة التفاعل والأصوات",
                    "category": "social",
                    "difficulty": personality.preferred_difficulty,
                    "duration": personality.attention_span,
                    "suitability_score": 0.9,
                }
            )
        elif personality.extraversion < 0.4:
            games.append(
                {
                    "type": "quiet_game",
                    "title": "لعبة الألغاز الهادئة",
                    "category": "puzzle",
                    "difficulty": personality.preferred_difficulty,
                    "duration": personality.attention_span,
                    "suitability_score": 0.85,
                }
            )

        # ألعاب بناءً على المثابرة
        if personality.conscientiousness > 0.7:
            games.append(
                {
                    "type": "challenge_game",
                    "title": "تحدي المثابرة",
                    "category": "challenge",
                    "difficulty": "hard",
                    "duration": personality.attention_span + 15,
                    "suitability_score": 0.88,
                }
            )

        # ألعاب بناءً على الأنشطة المفضلة
        for activity in patterns.preferred_activities[:3]:
            games.append(
                {
                    "type": f"{activity}_game",
                    "title": f"لعبة {activity}",
                    "category": activity,
                    "difficulty": personality.preferred_difficulty,
                    "duration": personality.attention_span,
                    "suitability_score": 0.83,
                }
            )

        return games

    def _recommend_conversations(self, personality, patterns) -> List[Dict]:
        """اقتراح مواضيع محادثة مخصصة"""
        conversations = []

        # محادثات بناءً على الفضول
        if personality.curiosity_level > 0.6:
            conversations.append(
                {
                    "type": "exploration_conversation",
                    "title": "دعنا نكتشف شيئاً جديداً",
                    "category": "discovery",
                    "complexity": "high" if personality.openness > 0.6 else "medium",
                    "duration": personality.attention_span,
                    "suitability_score": 0.92,
                }
            )

        # محادثات بناءً على المواضيع المفضلة
        for topic in patterns.favorite_topics[:2]:
            conversations.append(
                {
                    "type": "topic_conversation",
                    "title": f"دعنا نتحدث عن {topic}",
                    "category": topic,
                    "complexity": personality.preferred_difficulty,
                    "duration": personality.attention_span,
                    "suitability_score": 0.86,
                }
            )

        # محادثات بناءً على الحالة العاطفية
        if personality.neuroticism > 0.6:
            conversations.append(
                {
                    "type": "supportive_conversation",
                    "title": "محادثة داعمة ومهدئة",
                    "category": "emotional_support",
                    "complexity": "easy",
                    "duration": personality.attention_span - 5,
                    "suitability_score": 0.89,
                }
            )

        return conversations 