import asyncio
import json
import random
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class StoryType(Enum):
    """أنواع القصص"""

    AI_GENERATED = "ai_generated"  # قصص قصيرة مولدة بالـ AI
    STORED_ADVENTURE = "stored_adventure"  # قصص طويلة مخزنة مع مسارات
    EDUCATIONAL = "educational"  # قصص تعليمية (Mathemyths)
    BEDTIME = "bedtime"  # قصص النوم
    BEHAVIORAL = "behavioral"  # قصص لقراءة السلوك


class EmotionalTone(Enum):
    """النبرة العاطفية للقصة"""

    HAPPY = "سعيد"
    CALM = "هادئ"
    EXCITING = "مثير"
    MYSTERIOUS = "غامض"
    EDUCATIONAL = "تعليمي"
    ENCOURAGING = "مشجع"


class ChoiceType(Enum):
    """أنواع الاختيارات لتحليل السلوك"""

    COURAGE_VS_CAUTION = "شجاعة_مقابل_حذر"
    COOPERATION_VS_INDEPENDENCE = "تعاون_مقابل_استقلالية"
    HELPING_VS_SELF_FOCUS = "مساعدة_مقابل_تركيز_ذاتي"
    CREATIVE_VS_LOGICAL = "إبداعي_مقابل_منطقي"
    PATIENCE_VS_IMPULSIVENESS = "صبر_مقابل_اندفاع"


@dataclass
class StoryChoice:
    """خيار في القصة"""

    choice_id: str
    text: str
    choice_type: ChoiceType
    behavioral_score: Dict[str, float]  # مثل {"confidence": 0.8, "empathy": 0.6}
    leads_to_scene: str
    educational_content: Optional[str] = None


@dataclass
class StoryScene:
    """مشهد في القصة"""

    scene_id: str
    title: str
    content: str
    audio_effects: List[str]  # مؤثرات صوتية
    choices: List[StoryChoice]
    is_ending: bool = False
    educational_challenge: Optional[Dict] = None


@dataclass
class StoryChoiceLog:
    """سجل اختيارات الطفل"""

    id: str
    device_id: str
    child_name: str
    story_id: str
    scene_id: str
    choice_id: str
    choice_type: ChoiceType
    behavioral_scores: Dict[str, float]
    timestamp: datetime
    voice_analysis: Optional[Dict] = None  # تحليل الصوت
    response_time: Optional[float] = None  # وقت الاستجابة


@dataclass
class BehavioralPattern:
    """نمط سلوكي مكتشف"""

    pattern_type: str
    confidence_level: float
    description: str
    recommendations: List[str]
    parent_alert: bool = False


class InteractiveStoryEngine:
    """محرك القصص التفاعلي المتقدم"""

    def __init__(self):
        self.stories: Dict[str, Dict] = {}
        self.choice_logs: List[StoryChoiceLog] = []
        self.behavioral_patterns: Dict[str, List[BehavioralPattern]] = {}
        self._load_stored_stories()

    def _load_stored_stories(self) -> Any:
        """تحميل القصص المخزنة المسبقاً"""

        # قصة مغامرة الكنز المفقود
        treasure_story = {
            "story_id": "treasure_adventure",
            "title": "مغامرة الكنز المفقود",
            "type": StoryType.STORED_ADVENTURE,
            "age_range": (6, 12),
            "scenes": {
                "start": StoryScene(
                    scene_id="start",
                    title="بداية المغامرة",
                    content="كان {child_name} يتجول في الحديقة مع {friend1} عندما وجدا خريطة قديمة مدفونة تحت شجرة كبيرة. الخريطة تُظهر مكان كنز مخفي!",
                    audio_effects=["wind", "rustling_leaves", "mysterious_music"],
                    choices=[
                        StoryChoice(
                            choice_id="follow_map_immediately",
                            text="دعنا نتبع الخريطة فوراً!",
                            choice_type=ChoiceType.COURAGE_VS_CAUTION,
                            behavioral_score={"confidence": 0.8, "impulsiveness": 0.7, "adventure_seeking": 0.9},
                            leads_to_scene="forest_entrance",
                        ),
                        StoryChoice(
                            choice_id="tell_parents_first",
                            text="يجب أن نخبر الوالدين أولاً",
                            choice_type=ChoiceType.COURAGE_VS_CAUTION,
                            behavioral_score={"caution": 0.8, "responsibility": 0.9, "rule_following": 0.7},
                            leads_to_scene="parents_advice",
                        ),
                        StoryChoice(
                            choice_id="study_map_carefully",
                            text="دعنا نفحص الخريطة بعناية أولاً",
                            choice_type=ChoiceType.CREATIVE_VS_LOGICAL,
                            behavioral_score={"analytical_thinking": 0.8, "patience": 0.7, "planning": 0.9},
                            leads_to_scene="map_analysis",
                        ),
                    ],
                ),
                "forest_entrance": StoryScene(
                    scene_id="forest_entrance",
                    title="مدخل الغابة",
                    content="وصل {child_name} و{friend1} إلى مدخل غابة مظلمة. يمكنهما سماع أصوات غريبة من الداخل، لكن الخريطة تشير إلى أن الكنز في عمق الغابة.",
                    audio_effects=["forest_sounds", "owl_hooting", "tension_music"],
                    choices=[
                        StoryChoice(
                            choice_id="enter_forest_bravely",
                            text="ندخل الغابة بشجاعة!",
                            choice_type=ChoiceType.COURAGE_VS_CAUTION,
                            behavioral_score={"bravery": 0.9, "leadership": 0.7, "risk_taking": 0.8},
                            leads_to_scene="deep_forest",
                        ),
                        StoryChoice(
                            choice_id="bring_flashlight",
                            text="نعود لنحضر مصباحاً وحبلاً",
                            choice_type=ChoiceType.PATIENCE_VS_IMPULSIVENESS,
                            behavioral_score={"preparation": 0.9, "patience": 0.8, "practical_thinking": 0.8},
                            leads_to_scene="prepared_adventure",
                        ),
                        StoryChoice(
                            choice_id="invite_more_friends",
                            text="نستدعي المزيد من الأصدقاء للمساعدة",
                            choice_type=ChoiceType.COOPERATION_VS_INDEPENDENCE,
                            behavioral_score={"teamwork": 0.9, "social_skills": 0.8, "collaboration": 0.9},
                            leads_to_scene="team_adventure",
                        ),
                    ],
                ),
                "deep_forest": StoryScene(
                    scene_id="deep_forest",
                    title="عمق الغابة",
                    content="في عمق الغابة، وجد {child_name} صندوقاً قديماً، لكنه محاط بألغاز رياضية! يجب حل اللغز لفتح الصندوق.",
                    audio_effects=["magical_chimes", "puzzle_music"],
                    choices=[
                        StoryChoice(
                            choice_id="solve_puzzle_alone",
                            text="سأحل اللغز بنفسي!",
                            choice_type=ChoiceType.COOPERATION_VS_INDEPENDENCE,
                            behavioral_score={"independence": 0.8, "self_confidence": 0.9, "problem_solving": 0.7},
                            leads_to_scene="math_challenge",
                            educational_content="math_puzzle",
                        ),
                        StoryChoice(
                            choice_id="work_together",
                            text="دعنا نحله معاً!",
                            choice_type=ChoiceType.COOPERATION_VS_INDEPENDENCE,
                            behavioral_score={"cooperation": 0.9, "teamwork": 0.8, "humility": 0.7},
                            leads_to_scene="team_puzzle",
                            educational_content="collaborative_math",
                        ),
                    ],
                    educational_challenge={
                        "type": "math_puzzle",
                        "question": "إذا كان في الصندوق 3 أكياس، وفي كل كيس 4 جواهر، كم جوهرة في المجموع؟",
                        "answer": 12,
                        "hint": "اضرب عدد الأكياس في عدد الجواهر في كل كيس",
                    },
                ),
                "treasure_found": StoryScene(
                    scene_id="treasure_found",
                    title="اكتشاف الكنز",
                    content="رائع! فتح {child_name} الصندوق ووجد كنزاً حقيقياً - ليس ذهباً، بل كتباً سحرية تحتوي على قصص وألغاز ممتعة! الكنز الحقيقي هو المعرفة والصداقة.",
                    audio_effects=["success_fanfare", "magical_sparkles", "happy_music"],
                    choices=[],
                    is_ending=True,
                ),
            },
        }

        # قصة الصداقة والمشاركة
        friendship_story = {
            "story_id": "friendship_sharing",
            "title": "قصة الصداقة الحقيقية",
            "type": StoryType.BEHAVIORAL,
            "age_range": (4, 10),
            "scenes": {
                "playground": StoryScene(
                    scene_id="playground",
                    title="في الملعب",
                    content="كان {child_name} يلعب في الملعب عندما رأى طفلاً جديداً يجلس وحيداً. يبدو حزيناً ولا يعرف أحداً.",
                    audio_effects=["playground_sounds", "children_laughing"],
                    choices=[
                        StoryChoice(
                            choice_id="approach_new_kid",
                            text="أذهب إليه وأدعوه للعب معي",
                            choice_type=ChoiceType.HELPING_VS_SELF_FOCUS,
                            behavioral_score={"empathy": 0.9, "social_initiative": 0.8, "kindness": 0.9},
                            leads_to_scene="making_friend",
                        ),
                        StoryChoice(
                            choice_id="continue_playing",
                            text="أستمر في اللعب مع أصدقائي",
                            choice_type=ChoiceType.HELPING_VS_SELF_FOCUS,
                            behavioral_score={"self_focus": 0.7, "comfort_zone": 0.8},
                            leads_to_scene="missed_opportunity",
                        ),
                        StoryChoice(
                            choice_id="tell_friends_to_include",
                            text="أطلب من أصدقائي دعوته للعب معنا",
                            choice_type=ChoiceType.COOPERATION_VS_INDEPENDENCE,
                            behavioral_score={"leadership": 0.8, "inclusion": 0.9, "teamwork": 0.8},
                            leads_to_scene="group_friendship",
                        ),
                    ],
                )
            },
        }

        self.stories["treasure_adventure"] = treasure_story
        self.stories["friendship_sharing"] = friendship_story

    async def start_interactive_story(
        self, child_name: str, friends: List[str], age: int, story_type: StoryType = None, device_id: str = None
    ) -> Dict[str, Any]:
        """بدء قصة تفاعلية"""

        # اختيار القصة المناسبة
        if story_type:
            suitable_stories = [
                s
                for s in self.stories.values()
                if s["type"] == story_type and s["age_range"][0] <= age <= s["age_range"][1]
            ]
        else:
            suitable_stories = [s for s in self.stories.values() if s["age_range"][0] <= age <= s["age_range"][1]]

        if not suitable_stories:
            return {"error": "لا توجد قصص مناسبة لهذا العمر"}

        selected_story = random.choice(suitable_stories)

        # تخصيص القصة بأسماء الأطفال
        friend1 = friends[0] if friends else "صديقك"
        friend2 = friends[1] if len(friends) > 1 else "صديق آخر"

        # بدء القصة من المشهد الأول
        first_scene_id = "start" if "start" in selected_story["scenes"] else list(selected_story["scenes"].keys())[0]
        current_scene = selected_story["scenes"][first_scene_id]

        # تخصيص المحتوى
        personalized_content = current_scene.content.format(child_name=child_name, friend1=friend1, friend2=friend2)

        # إنشاء حالة القصة
        story_state = {
            "story_id": selected_story["story_id"],
            "title": selected_story["title"],
            "current_scene": first_scene_id,
            "child_name": child_name,
            "friends": friends,
            "device_id": device_id,
            "start_time": datetime.now().isoformat(),
            "choices_made": [],
            "behavioral_data": {},
        }

        return {
            "story_state": story_state,
            "scene": {
                "title": current_scene.title,
                "content": personalized_content,
                "audio_effects": current_scene.audio_effects,
                "choices": [
                    {
                        "choice_id": choice.choice_id,
                        "text": choice.text,
                        "educational_content": choice.educational_content,
                    }
                    for choice in current_scene.choices
                ],
                "educational_challenge": current_scene.educational_challenge,
                "is_ending": current_scene.is_ending,
            },
        }

    async def process_story_choice(
        self,
        story_state: Dict,
        choice_id: str,
        voice_analysis: Optional[Dict] = None,
        response_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """معالجة اختيار الطفل في القصة"""

        story_id = story_state["story_id"]
        current_scene_id = story_state["current_scene"]

        if story_id not in self.stories:
            return {"error": "القصة غير موجودة"}

        story = self.stories[story_id]
        current_scene = story["scenes"][current_scene_id]

        # العثور على الاختيار
        selected_choice = None
        for choice in current_scene.choices:
            if choice.choice_id == choice_id:
                selected_choice = choice
                break

        if not selected_choice:
            return {"error": "الاختيار غير صحيح"}

        # تسجيل الاختيار في السجل
        choice_log = StoryChoiceLog(
            id=str(uuid.uuid4()),
            device_id=story_state["device_id"],
            child_name=story_state["child_name"],
            story_id=story_id,
            scene_id=current_scene_id,
            choice_id=choice_id,
            choice_type=selected_choice.choice_type,
            behavioral_scores=selected_choice.behavioral_score,
            timestamp=datetime.now(),
            voice_analysis=voice_analysis,
            response_time=response_time,
        )

        self.choice_logs.append(choice_log)

        # تحديث البيانات السلوكية
        self._update_behavioral_data(story_state, selected_choice)

        # الانتقال للمشهد التالي
        next_scene_id = selected_choice.leads_to_scene

        if next_scene_id in story["scenes"]:
            next_scene = story["scenes"][next_scene_id]

            # تخصيص المحتوى
            personalized_content = next_scene.content.format(
                child_name=story_state["child_name"],
                friend1=story_state["friends"][0] if story_state["friends"] else "صديقك",
                friend2=story_state["friends"][1] if len(story_state["friends"]) > 1 else "صديق آخر",
            )

            # تحديث حالة القصة
            story_state["current_scene"] = next_scene_id
            story_state["choices_made"].append(
                {"scene": current_scene_id, "choice": choice_id, "timestamp": datetime.now().isoformat()}
            )

            return {
                "story_state": story_state,
                "scene": {
                    "title": next_scene.title,
                    "content": personalized_content,
                    "audio_effects": next_scene.audio_effects,
                    "choices": [
                        {
                            "choice_id": choice.choice_id,
                            "text": choice.text,
                            "educational_content": choice.educational_content,
                        }
                        for choice in next_scene.choices
                    ],
                    "educational_challenge": next_scene.educational_challenge,
                    "is_ending": next_scene.is_ending,
                },
                "behavioral_feedback": self._generate_behavioral_feedback(selected_choice),
                "choice_recorded": True,
            }
        else:
            return {"error": "المشهد التالي غير موجود"}

    def _update_behavioral_data(StoryChoice) -> None:
        """تحديث البيانات السلوكية"""
        if "behavioral_data" not in story_state:
            story_state["behavioral_data"] = {}

        for trait, score in choice.behavioral_score.items():
            if trait not in story_state["behavioral_data"]:
                story_state["behavioral_data"][trait] = []
            story_state["behavioral_data"][trait].append(score)

    def _generate_behavioral_feedback(self, choice: StoryChoice) -> Dict[str, Any]:
        """توليد تعليقات سلوكية للاختيار"""
        feedback = {
            "choice_type": choice.choice_type.value,
            "traits_observed": list(choice.behavioral_score.keys()),
            "encouragement": "",
        }

        # توليد رسالة تشجيعية بناءً على الاختيار
        if choice.choice_type == ChoiceType.COURAGE_VS_CAUTION:
            if "bravery" in choice.behavioral_score and choice.behavioral_score["bravery"] > 0.7:
                feedback["encouragement"] = "أحسنت! تُظهر شجاعة رائعة!"
            elif "caution" in choice.behavioral_score:
                feedback["encouragement"] = "خيار حكيم! التفكير قبل التصرف أمر ممتاز!"

        elif choice.choice_type == ChoiceType.HELPING_VS_SELF_FOCUS:
            if "empathy" in choice.behavioral_score and choice.behavioral_score["empathy"] > 0.7:
                feedback["encouragement"] = "قلبك طيب! مساعدة الآخرين أمر جميل!"

        elif choice.choice_type == ChoiceType.COOPERATION_VS_INDEPENDENCE:
            if "teamwork" in choice.behavioral_score:
                feedback["encouragement"] = "العمل الجماعي يحقق أفضل النتائج!"
            elif "independence" in choice.behavioral_score:
                feedback["encouragement"] = "الاعتماد على النفس مهارة مهمة!"

        return feedback

    def analyze_behavioral_patterns(self, child_name: str, device_id: str, days_back: int = 30) -> Dict[str, Any]:
        """تحليل الأنماط السلوكية للطفل"""

        # فلترة السجلات للطفل المحدد
        cutoff_date = datetime.now() - timedelta(days=days_back)
        relevant_logs = [
            log
            for log in self.choice_logs
            if log.child_name == child_name and log.device_id == device_id and log.timestamp >= cutoff_date
        ]

        if not relevant_logs:
            return {"message": "لا توجد بيانات كافية للتحليل"}

        # تجميع النقاط السلوكية
        behavioral_scores = {}
        choice_type_distribution = {}

        for log in relevant_logs:
            # تجميع النقاط
            for trait, score in log.behavioral_scores.items():
                if trait not in behavioral_scores:
                    behavioral_scores[trait] = []
                behavioral_scores[trait].append(score)

            # توزيع أنواع الاختيارات
            choice_type = log.choice_type.value
            if choice_type not in choice_type_distribution:
                choice_type_distribution[choice_type] = 0
            choice_type_distribution[choice_type] += 1

        # حساب المتوسطات
        behavioral_averages = {trait: sum(scores) / len(scores) for trait, scores in behavioral_scores.items()}

        # تحديد الأنماط
        patterns = self._identify_patterns(behavioral_averages, choice_type_distribution)

        # توصيات للوالدين
        recommendations = self._generate_parent_recommendations(patterns, behavioral_averages)

        return {
            "child_name": child_name,
            "analysis_period": f"{days_back} days",
            "total_choices": len(relevant_logs),
            "behavioral_averages": behavioral_averages,
            "choice_distribution": choice_type_distribution,
            "patterns_identified": patterns,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat(),
        }

    def _identify_patterns(self, behavioral_averages: Dict, choice_distribution: Dict) -> List[BehavioralPattern]:
        """تحديد الأنماط السلوكية"""
        patterns = []

        # نمط الشجاعة vs الحذر
        if "bravery" in behavioral_averages and "caution" in behavioral_averages:
            if behavioral_averages["bravery"] > 0.7:
                patterns.append(
                    BehavioralPattern(
                        pattern_type="شجاع_ومغامر",
                        confidence_level=0.8,
                        description="الطفل يُظهر مستوى عالي من الشجاعة والاستعداد للمغامرة",
                        recommendations=["شجع المغامرات الآمنة", "علم إدارة المخاطر"],
                    )
                )
            elif behavioral_averages["caution"] > 0.7:
                patterns.append(
                    BehavioralPattern(
                        pattern_type="حذر_ومتأني",
                        confidence_level=0.8,
                        description="الطفل يميل للحذر والتفكير قبل التصرف",
                        recommendations=["شجع على اتخاذ مخاطر محسوبة", "عزز الثقة بالنفس"],
                    )
                )

        # نمط التعاطف والمساعدة
        if "empathy" in behavioral_averages:
            if behavioral_averages["empathy"] > 0.8:
                patterns.append(
                    BehavioralPattern(
                        pattern_type="متعاطف_ومساعد",
                        confidence_level=0.9,
                        description="الطفل يُظهر مستوى عالي من التعاطف ومساعدة الآخرين",
                        recommendations=["شجع الأنشطة التطوعية", "علم الحدود الصحية"],
                    )
                )

        # نمط القلق أو التردد
        if "response_time" in behavioral_averages:  # إذا كان وقت الاستجابة طويل جداً
            # هذا يحتاج لمعالجة أكثر تعقيداً للوقت
            pass

        return patterns

    def _generate_parent_recommendations(
        self, patterns: List[BehavioralPattern], behavioral_averages: Dict
    ) -> List[str]:
        """توليد توصيات للوالدين"""
        recommendations = []

        # توصيات عامة بناءً على النقاط
        if behavioral_averages.get("confidence", 0) < 0.5:
            recommendations.append("انتبه: قد يحتاج الطفل لبناء الثقة بالنفس")

        if behavioral_averages.get("empathy", 0) > 0.8:
            recommendations.append("ممتاز: الطفل يُظهر تعاطفاً عالياً مع الآخرين")

        if behavioral_averages.get("problem_solving", 0) > 0.7:
            recommendations.append("رائع: الطفل لديه مهارات جيدة في حل المشكلات")

        # توصيات من الأنماط
        for pattern in patterns:
            recommendations.extend(pattern.recommendations)

        return recommendations

    def get_story_choice_history(self, child_name: str, device_id: str) -> List[Dict]:
        """الحصول على تاريخ اختيارات الطفل"""
        relevant_logs = [
            {
                "story_id": log.story_id,
                "scene_id": log.scene_id,
                "choice_type": log.choice_type.value,
                "behavioral_scores": log.behavioral_scores,
                "timestamp": log.timestamp.isoformat(),
                "voice_analysis": log.voice_analysis,
            }
            for log in self.choice_logs
            if log.child_name == child_name and log.device_id == device_id
        ]

        return sorted(relevant_logs, key=lambda x: x["timestamp"], reverse=True)

    def generate_story_report(self, child_name: str, device_id: str) -> Dict[str, Any]:
        """توليد تقرير شامل عن القصص والسلوك"""
        choice_history = self.get_story_choice_history(child_name, device_id)
        behavioral_analysis = self.analyze_behavioral_patterns(child_name, device_id)

        # إحصائيات القصص
        stories_played = len(set(choice["story_id"] for choice in choice_history))
        total_choices = len(choice_history)

        # أكثر أنواع الاختيارات
        choice_types = {}
        for choice in choice_history:
            choice_type = choice["choice_type"]
            choice_types[choice_type] = choice_types.get(choice_type, 0) + 1

        most_common_choice = max(choice_types.items(), key=lambda x: x[1]) if choice_types else None

        return {
            "child_name": child_name,
            "device_id": device_id,
            "summary": {
                "stories_played": stories_played,
                "total_choices": total_choices,
                "most_common_choice_type": most_common_choice[0] if most_common_choice else None,
                "last_story_date": choice_history[0]["timestamp"] if choice_history else None,
            },
            "behavioral_analysis": behavioral_analysis,
            "recent_choices": choice_history[:10],  # آخر 10 اختيارات
            "generated_at": datetime.now().isoformat(),
        }
