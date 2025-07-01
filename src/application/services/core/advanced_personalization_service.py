#!/usr/bin/env python3
"""
🎭 خدمة التخصيص المتقدم للطفل
تحليل شخصية الطفل وتعلم تفضيلاته لتخصيص التجربة
"""

import json
import logging
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ChildPersonality:
    """شخصية الطفل"""

    child_id: str
    openness: float = 0.5  # الانفتاح على التجارب الجديدة (0-1)
    conscientiousness: float = 0.5  # الضميرية/المثابرة (0-1)
    extraversion: float = 0.5  # الانبساطية (0-1)
    agreeableness: float = 0.5  # الوداعة/التعاون (0-1)
    neuroticism: float = 0.5  # العصابية/القلق (0-1)
    learning_style: str = "visual"  # visual, auditory, kinesthetic
    attention_span: int = 15  # بالدقائق
    preferred_difficulty: str = "medium"  # easy, medium, hard
    curiosity_level: float = 0.5  # مستوى الفضول (0-1)
    creativity_level: float = 0.5  # مستوى الإبداع (0-1)
    last_updated: str = ""


@dataclass
class InteractionPattern:
    """أنماط التفاعل"""

    child_id: str
    preferred_activities: List[str] = None
    favorite_topics: List[str] = None
    engagement_times: List[str] = None  # أوقات التفاعل النشط
    response_patterns: Dict[str, int] = None  # أنماط الردود
    mood_triggers: Dict[str, List[str]] = None  # محفزات المزاج
    learning_preferences: Dict[str, float] = None  # تفضيلات التعلم
    attention_patterns: Dict[str, int] = None  # أنماط الانتباه
    social_interaction_style: str = "moderate"  # shy, moderate, outgoing

    def __post_init__(self):
        if self.preferred_activities is None:
            self.preferred_activities = []
        if self.favorite_topics is None:
            self.favorite_topics = []
        if self.engagement_times is None:
            self.engagement_times = []
        if self.response_patterns is None:
            self.response_patterns = {}
        if self.mood_triggers is None:
            self.mood_triggers = {"positive": [], "negative": []}
        if self.learning_preferences is None:
            self.learning_preferences = {
                "storytelling": 0.5,
                "games": 0.5,
                "songs": 0.5,
                "questions": 0.5,
            }
        if self.attention_patterns is None:
            self.attention_patterns = {"morning": 0, "afternoon": 0, "evening": 0}


@dataclass
class AdaptiveContent:
    """محتوى متكيف"""

    content_type: str  # story, game, conversation, lesson
    difficulty_level: str
    topic: str
    duration: int  # بالدقائق
    engagement_score: float  # مدى الانخراط (0-1)
    success_rate: float  # معدل النجاح (0-1)
    child_feedback: str  # positive, neutral, negative
    usage_count: int = 0
    last_used: str = ""


class AdvancedPersonalizationService:
    """خدمة التخصيص المتقدم"""

    def __init__(self, data_dir: str = "data/personalization"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.personalities: Dict[str, ChildPersonality] = {}
        self.interaction_patterns: Dict[str, InteractionPattern] = {}
        self.content_performance: Dict[str, List[AdaptiveContent]] = {}
        self.learning_analytics: Dict[str, Dict] = {}

        self._load_data()

    def _load_data(self) -> Any:
        """تحميل البيانات من الملفات"""
        try:
            # تحميل الشخصيات
            personalities_file = self.data_dir / "personalities.json"
            if personalities_file.exists():
                with open(personalities_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for child_id, personality_data in data.items():
                        self.personalities[child_id] = ChildPersonality(
                            **personality_data
                        )

            # تحميل أنماط التفاعل
            patterns_file = self.data_dir / "interaction_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for child_id, pattern_data in data.items():
                        self.interaction_patterns[child_id] = InteractionPattern(
                            **pattern_data
                        )

            # تحميل أداء المحتوى
            content_file = self.data_dir / "content_performance.json"
            if content_file.exists():
                with open(content_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for child_id, contents in data.items():
                        self.content_performance[child_id] = [
                            AdaptiveContent(**content) for content in contents
                        ]

        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات التخصيص: {e}")

    def _save_data(self) -> Any:
        """حفظ البيانات في الملفات"""
        try:
            # حفظ الشخصيات
            personalities_file = self.data_dir / "personalities.json"
            personalities_data = {
                child_id: asdict(personality)
                for child_id, personality in self.personalities.items()
            }
            with open(personalities_file, "w", encoding="utf-8") as f:
                json.dump(personalities_data, f, ensure_ascii=False, indent=2)

            # حفظ أنماط التفاعل
            patterns_file = self.data_dir / "interaction_patterns.json"
            patterns_data = {
                child_id: asdict(pattern)
                for child_id, pattern in self.interaction_patterns.items()
            }
            with open(patterns_file, "w", encoding="utf-8") as f:
                json.dump(patterns_data, f, ensure_ascii=False, indent=2)

            # حفظ أداء المحتوى
            content_file = self.data_dir / "content_performance.json"
            content_data = {
                child_id: [asdict(content) for content in contents]
                for child_id, contents in self.content_performance.items()
            }
            with open(content_file, "w", encoding="utf-8") as f:
                json.dump(content_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات التخصيص: {e}")

    def get_child_personality(self, child_id: str) -> ChildPersonality:
        """الحصول على شخصية الطفل"""
        if child_id not in self.personalities:
            self.personalities[child_id] = ChildPersonality(
                child_id=child_id, last_updated=datetime.now().isoformat()
            )
            self._save_data()
        return self.personalities[child_id]

    def get_interaction_patterns(self, child_id: str) -> InteractionPattern:
        """الحصول على أنماط تفاعل الطفل"""
        if child_id not in self.interaction_patterns:
            self.interaction_patterns[child_id] = InteractionPattern(child_id=child_id)
            self._save_data()
        return self.interaction_patterns[child_id]

    def analyze_personality_from_interactions(
        self, child_id: str, interactions: List[Dict]
    ) -> ChildPersonality:
        """تحليل الشخصية من التفاعلات"""
        personality = self.get_child_personality(child_id)

        if not interactions:
            return personality

        # تحليل الانفتاح (كم مرة جرب أشياء جديدة)
        new_activities = set()
        total_activities = 0

        # تحليل الانبساطية (طول المحادثات ونشاطية الردود)
        conversation_lengths = []
        response_speeds = []

        # تحليل المثابرة (إكمال المهام والألعاب)
        completed_tasks = 0
        total_tasks = 0

        # تحليل الوداعة (الردود الإيجابية والتعاونية)
        positive_responses = 0
        total_responses = 0

        # تحليل العصابية (مؤشرات القلق أو الإحباط)
        negative_emotions = 0
        total_emotions = 0

        for interaction in interactions:
            activity_type = interaction.get("activity_type", "")

            # تتبع الأنشطة الجديدة
            if activity_type:
                if activity_type not in new_activities:
                    new_activities.add(activity_type)
                total_activities += 1

            # تحليل طول المحادثة
            duration = interaction.get("duration_minutes", 0)
            if duration > 0:
                conversation_lengths.append(duration)

            # تحليل إكمال المهام
            if interaction.get("completed", False):
                completed_tasks += 1
            if "completed" in interaction:
                total_tasks += 1

            # تحليل المشاعر
            emotion = interaction.get("emotion", "")
            if emotion:
                total_emotions += 1
                if emotion in ["sad", "angry", "frustrated"]:
                    negative_emotions += 1

            # تحليل الردود
            response_type = interaction.get("response_type", "")
            if response_type:
                total_responses += 1
                if response_type in ["positive", "enthusiastic", "cooperative"]:
                    positive_responses += 1

        # تحديث النتائج
        if total_activities > 0:
            personality.openness = min(1.0, len(new_activities) / total_activities * 2)

        if conversation_lengths:
            avg_length = np.mean(conversation_lengths)
            personality.extraversion = min(
                1.0, avg_length / 30
            )  # 30 دقيقة = انبساطية كاملة

        if total_tasks > 0:
            personality.conscientiousness = completed_tasks / total_tasks

        if total_responses > 0:
            personality.agreeableness = positive_responses / total_responses

        if total_emotions > 0:
            personality.neuroticism = negative_emotions / total_emotions

        # تحديث مستوى الفضول
        unique_topics = len(
            set(
                interaction.get("topic", "")
                for interaction in interactions
                if interaction.get("topic")
            )
        )
        personality.curiosity_level = min(
            1.0, unique_topics / 10
        )  # 10 مواضيع مختلفة = فضول كامل

        # تحديث مستوى الإبداع
        creative_activities = sum(
            1
            for interaction in interactions
            if interaction.get("activity_type")
            in ["storytelling", "creative_games", "art"]
        )
        personality.creativity_level = min(
            1.0, creative_activities / len(interactions) * 2
        )

        personality.last_updated = datetime.now().isoformat()
        self._save_data()

        return personality

    def update_interaction_patterns(Dict) -> None:
        """تحديث أنماط التفاعل"""
        patterns = self.get_interaction_patterns(child_id)

        # تحديث الأنشطة المفضلة
        activity = interaction_data.get("activity_type")
        if activity and activity not in patterns.preferred_activities:
            engagement = interaction_data.get("engagement_score", 0)
            if engagement > 0.7:  # إذا كان الانخراط عالي
                patterns.preferred_activities.append(activity)
                # الاحتفاظ بأفضل 10 أنشطة
                patterns.preferred_activities = patterns.preferred_activities[-10:]

        # تحديث المواضيع المفضلة
        topic = interaction_data.get("topic")
        if topic:
            if topic not in patterns.favorite_topics:
                patterns.favorite_topics.append(topic)
                patterns.favorite_topics = patterns.favorite_topics[-15:]

        # تحديث أوقات التفاعل النشط
        current_hour = datetime.now().strftime("%H")
        if interaction_data.get("engagement_score", 0) > 0.6:
            time_slot = self._get_time_slot(current_hour)
            patterns.attention_patterns[time_slot] = (
                patterns.attention_patterns.get(time_slot, 0) + 1
            )

        # تحديث أنماط الردود
        response_type = interaction_data.get("response_type")
        if response_type:
            patterns.response_patterns[response_type] = (
                patterns.response_patterns.get(response_type, 0) + 1
            )

        # تحديث محفزات المزاج
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

        # تحديث تفضيلات التعلم
        learning_method = interaction_data.get("learning_method")
        success_rate = interaction_data.get("success_rate", 0)
        if learning_method and success_rate > 0:
            current_pref = patterns.learning_preferences.get(learning_method, 0.5)
            # تحديث تدريجي بناءً على النجاح
            new_pref = current_pref * 0.8 + success_rate * 0.2
            patterns.learning_preferences[learning_method] = min(1.0, new_pref)

        self._save_data()

    def _get_time_slot(self, hour: str) -> str:
        """تحديد فترة اليوم"""
        hour_int = int(hour)
        if 6 <= hour_int < 12:
            return "morning"
        elif 12 <= hour_int < 18:
            return "afternoon"
        else:
            return "evening"

    def recommend_content(self, child_id: str, content_type: str = None) -> List[Dict]:
        """اقتراح محتوى مخصص"""
        personality = self.get_child_personality(child_id)
        patterns = self.get_interaction_patterns(child_id)

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

    def _recommend_stories(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> List[Dict]:
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

    def _recommend_games(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> List[Dict]:
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

    def _recommend_conversations(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> List[Dict]:
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

    def track_content_performance(Dict) -> None:
        """تتبع أداء المحتوى"""
        if child_id not in self.content_performance:
            self.content_performance[child_id] = []

        adaptive_content = AdaptiveContent(
            content_type=content.get("type", ""),
            difficulty_level=content.get("difficulty", "medium"),
            topic=content.get("topic", ""),
            duration=performance_data.get("duration_minutes", 0),
            engagement_score=performance_data.get("engagement_score", 0),
            success_rate=performance_data.get("success_rate", 0),
            child_feedback=performance_data.get("feedback", "neutral"),
            usage_count=1,
            last_used=datetime.now().isoformat(),
        )

        # البحث عن محتوى مشابه لتحديثه
        existing_content = None
        for content_item in self.content_performance[child_id]:
            if (
                content_item.content_type == adaptive_content.content_type
                and content_item.topic == adaptive_content.topic
                and content_item.difficulty_level == adaptive_content.difficulty_level
            ):
                existing_content = content_item
                break

        if existing_content:
            # تحديث المحتوى الموجود
            existing_content.usage_count += 1
            existing_content.engagement_score = (
                existing_content.engagement_score + adaptive_content.engagement_score
            ) / 2
            existing_content.success_rate = (
                existing_content.success_rate + adaptive_content.success_rate
            ) / 2
            existing_content.last_used = adaptive_content.last_used
        else:
            # إضافة محتوى جديد
            self.content_performance[child_id].append(adaptive_content)

        # الاحتفاظ بآخر 100 عنصر
        self.content_performance[child_id] = self.content_performance[child_id][-100:]

        self._save_data()

    def get_personalization_insights(self, child_id: str) -> Dict:
        """الحصول على رؤى التخصيص"""
        personality = self.get_child_personality(child_id)
        patterns = self.get_interaction_patterns(child_id)

        insights = {
            "personality_summary": self._get_personality_summary(personality),
            "learning_style": self._determine_learning_style(personality, patterns),
            "engagement_patterns": self._analyze_engagement_patterns(child_id),
            "content_preferences": self._analyze_content_preferences(child_id),
            "optimization_suggestions": self._get_optimization_suggestions(
                personality, patterns
            ),
            "development_areas": self._identify_development_areas(
                personality, patterns
            ),
        }

        return insights

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

    def _determine_learning_style(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> Dict:
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

    def _analyze_engagement_patterns(self, child_id: str) -> Dict:
        """تحليل أنماط الانخراط"""
        patterns = self.get_interaction_patterns(child_id)

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

    def _analyze_content_preferences(self, child_id: str) -> Dict:
        """تحليل تفضيلات المحتوى"""
        if child_id not in self.content_performance:
            return {"message": "لا توجد بيانات كافية"}

        contents = self.content_performance[child_id]

        # أفضل أنواع المحتوى
        content_scores = defaultdict(list)
        for content in contents:
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
            if content.topic:
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

        best_time = (
            max(patterns.attention_patterns.items(), key=lambda x: x[1])[0]
            if patterns.attention_patterns
            else None
        )
        if best_time:
            suggestions.append(f"جدولة الأنشطة المهمة في فترة {best_time}")

        return suggestions

    def _identify_development_areas(
        self, personality: ChildPersonality, patterns: InteractionPattern
    ) -> Dict:
        """تحديد مجالات التطوير"""
        areas = {"strengths": [], "growth_areas": [], "focus_suggestions": []}

        # نقاط القوة
        if personality.curiosity_level > 0.6:
            areas["strengths"].append("فضول عالي للتعلم")
        if personality.creativity_level > 0.6:
            areas["strengths"].append("قدرة إبداعية مميزة")
        if personality.agreeableness > 0.6:
            areas["strengths"].append("روح تعاونية")
        if personality.conscientiousness > 0.6:
            areas["strengths"].append("مثابرة في إنجاز المهام")

        # مجالات النمو
        if personality.openness < 0.4:
            areas["growth_areas"].append("الانفتاح على التجارب الجديدة")
        if personality.extraversion < 0.4:
            areas["growth_areas"].append("الثقة في التفاعل الاجتماعي")
        if personality.attention_span < 15:
            areas["growth_areas"].append("تطوير فترة التركيز")

        # اقتراحات التركيز
        if personality.creativity_level < 0.4:
            areas["focus_suggestions"].append(
                "أنشطة إبداعية مثل الرسم والقصص التفاعلية"
            )
        if personality.conscientiousness < 0.4:
            areas["focus_suggestions"].append("ألعاب تعزز المثابرة والتنظيم")
        if len(patterns.favorite_topics) < 3:
            areas["focus_suggestions"].append("استكشاف مواضيع ومجالات معرفية متنوعة")

        return areas
