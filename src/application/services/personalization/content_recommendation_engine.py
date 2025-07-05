#!/usr/bin/env python3
"""
🎪 Content Recommendation Engine Service
محرك اقتراح المحتوى المخصص للطفل
"""

import logging
from typing import Dict, List

from .data_models import ChildPersonality, InteractionPattern

logger = logging.getLogger(__name__)


class ContentRecommendationEngine:
    """محرك اقتراح المحتوى المخصص"""

    def recommend_content(
        self,
        personality: ChildPersonality,
        patterns: InteractionPattern,
        content_type: str = None,
    ) -> List[Dict]:
        """اقتراح محتوى مخصص بناءً على الشخصية والأنماط"""
        recommendations = []

        try:
            if content_type is None or content_type == "story":
                recommendations.extend(
                    self._recommend_stories(
                        personality, patterns))

            if content_type is None or content_type == "game":
                recommendations.extend(
                    self._recommend_games(
                        personality, patterns))

            if content_type is None or content_type == "conversation":
                recommendations.extend(
                    self._recommend_conversations(personality, patterns)
                )

            if content_type is None or content_type == "lesson":
                recommendations.extend(
                    self._recommend_lessons(
                        personality, patterns))

            # ترتيب الاقتراحات حسب درجة الملاءمة
            recommendations.sort(
                key=lambda x: x.get("suitability_score", 0), reverse=True
            )

            return recommendations[:10]  # أفضل 10 اقتراحات

        except Exception as e:
            logger.error(f"خطأ في اقتراح المحتوى: {e}")
            return []

    def _recommend_stories(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> List[Dict]:
        """اقتراح قصص مخصصة"""
        stories = []

        # قصص بناءً على الانفتاح
        if personality.openness > 0.7:
            stories.append(self._create_adventure_story(personality))
        elif personality.openness < 0.3:
            stories.append(self._create_familiar_story(personality))

        # قصص بناءً على المواضيع المفضلة
        for topic in patterns.favorite_topics[:3]:
            stories.append(self._create_topic_story(personality, topic))

        # قصص بناءً على الإبداع
        if personality.creativity_level > 0.6:
            stories.append(self._create_interactive_story(personality))

        return stories

    def _recommend_games(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> List[Dict]:
        """اقتراح ألعاب مخصصة"""
        games = []

        # ألعاب بناءً على الانبساطية
        if personality.extraversion > 0.6:
            games.append(self._create_social_game(personality))
        elif personality.extraversion < 0.4:
            games.append(self._create_quiet_game(personality))

        # ألعاب بناءً على المثابرة
        if personality.conscientiousness > 0.7:
            games.append(self._create_challenge_game(personality))

        # ألعاب بناءً على الأنشطة المفضلة
        for activity in patterns.preferred_activities[:3]:
            games.append(self._create_activity_game(personality, activity))

        return games

    def _recommend_conversations(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> List[Dict]:
        """اقتراح مواضيع محادثة مخصصة"""
        conversations = []

        # محادثات بناءً على الفضول
        if personality.curiosity_level > 0.6:
            conversations.append(
                self._create_exploration_conversation(personality))

        # محادثات بناءً على المواضيع المفضلة
        for topic in patterns.favorite_topics[:2]:
            conversations.append(
                self._create_topic_conversation(
                    personality, topic))

        # محادثات بناءً على الحالة العاطفية
        if personality.neuroticism > 0.6:
            conversations.append(
                self._create_supportive_conversation(personality))

        return conversations

    def _recommend_lessons(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> List[Dict]:
        """اقتراح دروس تعليمية مخصصة"""
        lessons = []

        # دروس بناءً على أسلوب التعلم
        if personality.learning_style == "visual":
            lessons.append(self._create_visual_lesson(personality))
        elif personality.learning_style == "auditory":
            lessons.append(self._create_audio_lesson(personality))
        elif personality.learning_style == "kinesthetic":
            lessons.append(self._create_interactive_lesson(personality))

        # دروس بناءً على المستوى المفضل
        lessons.append(self._create_difficulty_appropriate_lesson(personality))

        return lessons

    # Story creation methods
    def _create_adventure_story(self, personality: ChildPersonality) -> Dict:
        """إنشاء قصة مغامرة"""
        return {
            "type": "story",
            "title": "مغامرة في عالم غريب",
            "theme": "exploration",
            "difficulty": personality.preferred_difficulty,
            "duration": personality.attention_span,
            "suitability_score": 0.9,
            "description": "قصة مليئة بالاستكشاف والمغامرات الجديدة",
        }

    def _create_familiar_story(self, personality: ChildPersonality) -> Dict:
        """إنشاء قصة مألوفة"""
        return {
            "type": "story",
            "title": "حكاية مألوفة مع لمسة جديدة",
            "theme": "familiar",
            "difficulty": "easy",
            "duration": min(15, personality.attention_span),
            "suitability_score": 0.8,
            "description": "قصة تقليدية مع عناصر مألوفة ومريحة",
        }

    def _create_topic_story(
            self,
            personality: ChildPersonality,
            topic: str) -> Dict:
        """إنشاء قصة حول موضوع محدد"""
        return {
            "type": "story",
            "title": f"قصة عن {topic}",
            "theme": topic,
            "difficulty": personality.preferred_difficulty,
            "duration": personality.attention_span,
            "suitability_score": 0.85,
            "description": f"قصة مخصصة حول موضوع {topic} المفضل",
        }

    def _create_interactive_story(self, personality: ChildPersonality) -> Dict:
        """إنشاء قصة تفاعلية"""
        return {
            "type": "interactive_story",
            "title": "اصنع قصتك الخاصة",
            "theme": "creative",
            "difficulty": personality.preferred_difficulty,
            "duration": personality.attention_span + 10,
            "suitability_score": 0.87,
            "description": "قصة تفاعلية يمكن للطفل المشاركة في إنشائها",
        }

    # Game creation methods
    def _create_social_game(self, personality: ChildPersonality) -> Dict:
        """إنشاء لعبة اجتماعية"""
        return {
            "type": "social_game",
            "title": "لعبة التفاعل والأصوات",
            "category": "social",
            "difficulty": personality.preferred_difficulty,
            "duration": personality.attention_span,
            "suitability_score": 0.9,
            "description": "لعبة تشجع على التفاعل والمشاركة",
        }

    def _create_quiet_game(self, personality: ChildPersonality) -> Dict:
        """إنشاء لعبة هادئة"""
        return {
            "type": "quiet_game",
            "title": "لعبة الألغاز الهادئة",
            "category": "puzzle",
            "difficulty": personality.preferred_difficulty,
            "duration": personality.attention_span,
            "suitability_score": 0.85,
            "description": "لعبة هادئة تركز على التفكير والتأمل",
        }

    def _create_challenge_game(self, personality: ChildPersonality) -> Dict:
        """إنشاء لعبة تحدي"""
        return {
            "type": "challenge_game",
            "title": "تحدي المثابرة",
            "category": "challenge",
            "difficulty": "hard",
            "duration": personality.attention_span + 15,
            "suitability_score": 0.88,
            "description": "لعبة تحدي تتطلب المثابرة والصبر",
        }

    def _create_activity_game(
        self, personality: ChildPersonality, activity: str
    ) -> Dict:
        """إنشاء لعبة بناءً على نشاط محدد"""
        return {
            "type": f"{activity}_game",
            "title": f"لعبة {activity}",
            "category": activity,
            "difficulty": personality.preferred_difficulty,
            "duration": personality.attention_span,
            "suitability_score": 0.83,
            "description": f"لعبة مخصصة حول نشاط {activity}",
        }

    # Conversation creation methods
    def _create_exploration_conversation(
            self, personality: ChildPersonality) -> Dict:
        """إنشاء محادثة استكشافية"""
        return {
            "type": "exploration_conversation",
            "title": "دعنا نكتشف شيئاً جديداً",
            "category": "discovery",
            "complexity": "high" if personality.openness > 0.6 else "medium",
            "duration": personality.attention_span,
            "suitability_score": 0.92,
            "description": "محادثة تشجع على الاستكشاف والتعلم",
        }

    def _create_topic_conversation(
        self, personality: ChildPersonality, topic: str
    ) -> Dict:
        """إنشاء محادثة حول موضوع محدد"""
        return {
            "type": "topic_conversation",
            "title": f"دعنا نتحدث عن {topic}",
            "category": topic,
            "complexity": personality.preferred_difficulty,
            "duration": personality.attention_span,
            "suitability_score": 0.86,
            "description": f"محادثة ممتعة حول موضوع {topic}",
        }

    def _create_supportive_conversation(
            self, personality: ChildPersonality) -> Dict:
        """إنشاء محادثة داعمة"""
        return {
            "type": "supportive_conversation",
            "title": "محادثة داعمة ومهدئة",
            "category": "emotional_support",
            "complexity": "easy",
            "duration": personality.attention_span - 5,
            "suitability_score": 0.89,
            "description": "محادثة مهدئة وداعمة عاطفياً",
        }

    # Lesson creation methods
    def _create_visual_lesson(self, personality: ChildPersonality) -> Dict:
        """إنشاء درس بصري"""
        return {
            "type": "visual_lesson",
            "title": "درس بصري تفاعلي",
            "learning_style": "visual",
            "difficulty": personality.preferred_difficulty,
            "duration": personality.attention_span,
            "suitability_score": 0.88,
            "description": "درس يعتمد على العناصر البصرية والصور",
        }

    def _create_audio_lesson(self, personality: ChildPersonality) -> Dict:
        """إنشاء درس صوتي"""
        return {
            "type": "audio_lesson",
            "title": "درس صوتي ممتع",
            "learning_style": "auditory",
            "difficulty": personality.preferred_difficulty,
            "duration": personality.attention_span,
            "suitability_score": 0.86,
            "description": "درس يعتمد على الأصوات والموسيقى",
        }

    def _create_interactive_lesson(
            self, personality: ChildPersonality) -> Dict:
        """إنشاء درس تفاعلي"""
        return {
            "type": "interactive_lesson",
            "title": "درس تفاعلي عملي",
            "learning_style": "kinesthetic",
            "difficulty": personality.preferred_difficulty,
            "duration": personality.attention_span,
            "suitability_score": 0.90,
            "description": "درس يتطلب المشاركة والتفاعل العملي",
        }

    def _create_difficulty_appropriate_lesson(
        self, personality: ChildPersonality
    ) -> Dict:
        """إنشاء درس مناسب للمستوى"""
        return {
            "type": "adaptive_lesson",
            "title": f"درس مستوى {personality.preferred_difficulty}",
            "learning_style": personality.learning_style,
            "difficulty": personality.preferred_difficulty,
            "duration": personality.attention_span,
            "suitability_score": 0.84,
            "description": "درس مصمم خصيصاً لمستوى الطفل",
        }
