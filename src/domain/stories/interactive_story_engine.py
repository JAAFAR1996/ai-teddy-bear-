import random
import uuid
import json
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


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
    # مثل {"confidence": 0.8, "empathy": 0.6}
    behavioral_score: Dict[str, float]
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

    def _load_stored_stories(self) -> None:
        """تحميل القصص المخزنة المسبقاً من ملف JSON."""
        stories_path = Path(__file__).parent / "stored_stories.json"
        try:
            with stories_path.open("r", encoding="utf-8") as f:
                stories_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading stored stories: {e}")
            return

        for story_id, story_data in stories_data.items():
            story_data["type"] = StoryType(story_data["type"])

            deserialized_scenes = {}
            for scene_id, scene_data in story_data.get("scenes", {}).items():
                deserialized_choices = []
                for choice_data in scene_data.get("choices", []):
                    choice_data["choice_type"] = ChoiceType(
                        choice_data["choice_type"])
                    deserialized_choices.append(StoryChoice(**choice_data))

                scene_data["choices"] = deserialized_choices
                deserialized_scenes[scene_id] = StoryScene(**scene_data)

            story_data["scenes"] = deserialized_scenes
            self.stories[story_id] = story_data

    def _find_suitable_story(
        self, age: int, story_type: Optional[StoryType] = None
    ) -> Optional[Dict]:
        """Finds a story suitable for the child's age and requested type."""
        if story_type:
            suitable_stories = [
                s
                for s in self.stories.values()
                if s["type"] == story_type
                and s["age_range"][0] <= age <= s["age_range"][1]
            ]
        else:
            suitable_stories = [
                s
                for s in self.stories.values()
                if s["age_range"][0] <= age <= s["age_range"][1]
            ]

        return random.choice(suitable_stories) if suitable_stories else None

    def _prepare_story_state(
        self, story: Dict, child_name: str, friends: List[str], device_id: str
    ) -> Dict:
        """Initializes the state for the story session."""
        first_scene_id = (
            "start" if "start" in story["scenes"] else list(
                story["scenes"].keys())[0])

        return {
            "story_id": story["story_id"],
            "title": story["title"],
            "current_scene": first_scene_id,
            "child_name": child_name,
            "friends": friends,
            "device_id": device_id,
            "start_time": datetime.now().isoformat(),
            "choices_made": [],
            "behavioral_data": {},
        }

    def _format_scene_for_display(
            self,
            scene: StoryScene,
            story_state: Dict) -> Dict:
        """Formats a scene's content for the user."""
        personalized_content = scene.content.format(
            child_name=story_state["child_name"],
            friend1=story_state["friends"][0] if story_state["friends"] else "صديقك",
            friend2=(
                story_state["friends"][1] if len(
                    story_state["friends"]) > 1 else "صديق آخر"),
        )

        return {
            "title": scene.title,
            "content": personalized_content,
            "audio_effects": scene.audio_effects,
            "choices": [
                {
                    "choice_id": choice.choice_id,
                    "text": choice.text,
                    "educational_content": choice.educational_content,
                }
                for choice in scene.choices
            ],
            "educational_challenge": scene.educational_challenge,
            "is_ending": scene.is_ending,
        }

    async def start_interactive_story(
        self,
        child_name: str,
        friends: List[str],
        age: int,
        story_type: StoryType = None,
        device_id: str = None,
    ) -> Dict[str, Any]:
        """بدء قصة تفاعلية"""
        selected_story = self._find_suitable_story(age, story_type)

        if not selected_story:
            return {"error": "لا توجد قصص مناسبة لهذا العمر"}

        story_state = self._prepare_story_state(
            selected_story, child_name, friends, device_id
        )

        first_scene_id = story_state["current_scene"]
        current_scene = selected_story["scenes"][first_scene_id]

        scene_for_display = self._format_scene_for_display(
            current_scene, story_state)

        return {
            "story_state": story_state,
            "scene": scene_for_display,
        }

    def _find_selected_choice(
        self, scene: StoryScene, choice_id: str
    ) -> Optional[StoryChoice]:
        """Finds the selected choice object from a scene."""
        for choice in scene.choices:
            if choice.choice_id == choice_id:
                return choice
        return None

    def _log_choice(
        self,
        story_state: Dict,
        choice: StoryChoice,
        voice_analysis: Optional[Dict],
        response_time: Optional[float],
    ) -> None:
        """Logs the child's choice."""
        choice_log = StoryChoiceLog(
            id=str(uuid.uuid4()),
            device_id=story_state["device_id"],
            child_name=story_state["child_name"],
            story_id=story_state["story_id"],
            scene_id=story_state["current_scene"],
            choice_id=choice.choice_id,
            choice_type=choice.choice_type,
            behavioral_scores=choice.behavioral_score,
            timestamp=datetime.now(),
            voice_analysis=voice_analysis,
            response_time=response_time,
        )
        self.choice_logs.append(choice_log)

    def _update_story_state(
            self,
            story_state: Dict,
            choice: StoryChoice) -> None:
        """Updates the story state after a choice is made."""
        story_state["current_scene"] = choice.leads_to_scene
        story_state["choices_made"].append(
            {
                "scene": story_state["current_scene"],
                "choice": choice.choice_id,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._update_behavioral_data(story_state, choice)

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

        selected_choice = self._find_selected_choice(current_scene, choice_id)

        if not selected_choice:
            return {"error": "الاختيار غير صحيح"}

        self._log_choice(
            story_state,
            selected_choice,
            voice_analysis,
            response_time)
        self._update_story_state(story_state, selected_choice)

        next_scene_id = selected_choice.leads_to_scene
        if next_scene_id not in story["scenes"]:
            return {"error": "المشهد التالي غير موجود"}

        next_scene = story["scenes"][next_scene_id]
        scene_for_display = self._format_scene_for_display(
            next_scene, story_state)

        return {
            "story_state": story_state,
            "scene": scene_for_display,
            "behavioral_feedback": self._generate_behavioral_feedback(selected_choice),
            "choice_recorded": True,
        }

    def _update_behavioral_data(
            self,
            story_state: Dict,
            choice: StoryChoice) -> None:
        """تحديث البيانات السلوكية"""
        if "behavioral_data" not in story_state:
            story_state["behavioral_data"] = {}

        for trait, score in choice.behavioral_score.items():
            if trait not in story_state["behavioral_data"]:
                story_state["behavioral_data"][trait] = []
            story_state["behavioral_data"][trait].append(score)

    def _generate_behavioral_feedback(
            self, choice: StoryChoice) -> Dict[str, Any]:
        """توليد تعليقات سلوكية للاختيار"""
        feedback_map = {
            ChoiceType.COURAGE_VS_CAUTION: {
                "bravery": "أحسنت! تُظهر شجاعة رائعة!",
                "caution": "خيار حكيم! التفكير قبل التصرف أمر ممتاز!",
            },
            ChoiceType.HELPING_VS_SELF_FOCUS: {
                "empathy": "قلبك طيب! مساعدة الآخرين أمر جميل!",
            },
            ChoiceType.COOPERATION_VS_INDEPENDENCE: {
                "teamwork": "العمل الجماعي يحقق أفضل النتائج!",
                "independence": "الاعتماد على النفس مهارة مهمة!",
            },
        }

        encouragement = ""
        # Get the encouragement message from the map
        trait_messages = feedback_map.get(choice.choice_type)
        if trait_messages:
            for trait, message in trait_messages.items():
                if choice.behavioral_score.get(trait, 0) > 0.7:
                    encouragement = message
                    break

        return {
            "choice_type": choice.choice_type.value,
            "traits_observed": list(choice.behavioral_score.keys()),
            "encouragement": encouragement,
        }

    def _filter_logs(
        self, child_name: str, device_id: str, days_back: int
    ) -> List[StoryChoiceLog]:
        """Filters choice logs for a specific child and timeframe."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        return [
            log
            for log in self.choice_logs
            if log.child_name == child_name
            and log.device_id == device_id
            and log.timestamp >= cutoff_date
        ]

    def _aggregate_scores(self, logs: List[StoryChoiceLog]) -> (Dict, Dict):
        """Aggregates behavioral scores and choice types from logs."""
        behavioral_scores = {}
        choice_type_distribution = {}

        for log in logs:
            for trait, score in log.behavioral_scores.items():
                behavioral_scores.setdefault(trait, []).append(score)

            choice_type = log.choice_type.value
            choice_type_distribution[choice_type] = (
                choice_type_distribution.get(choice_type, 0) + 1
            )

        behavioral_averages = {
            trait: sum(scores) / len(scores)
            for trait, scores in behavioral_scores.items()
        }
        return behavioral_averages, choice_type_distribution

    def analyze_behavioral_patterns(
        self, child_name: str, device_id: str, days_back: int = 30
    ) -> Dict[str, Any]:
        """تحليل الأنماط السلوكية للطفل"""
        relevant_logs = self._filter_logs(child_name, device_id, days_back)

        if not relevant_logs:
            return {"message": "لا توجد بيانات كافية للتحليل"}

        behavioral_averages, choice_distribution = self._aggregate_scores(
            relevant_logs)
        patterns = self._identify_patterns(
            behavioral_averages, choice_distribution)
        recommendations = self._generate_parent_recommendations(
            patterns, behavioral_averages
        )

        return {
            "child_name": child_name,
            "analysis_period": f"{days_back} days",
            "total_choices": len(relevant_logs),
            "behavioral_averages": behavioral_averages,
            "choice_distribution": choice_distribution,
            "patterns_identified": patterns,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat(),
        }

    def _identify_patterns(
        self, behavioral_averages: Dict, choice_distribution: Dict
    ) -> List[BehavioralPattern]:
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
                        recommendations=[
                            "شجع المغامرات الآمنة",
                            "علم إدارة المخاطر"],
                    ))
            elif behavioral_averages["caution"] > 0.7:
                patterns.append(
                    BehavioralPattern(
                        pattern_type="حذر_ومتأني",
                        confidence_level=0.8,
                        description="الطفل يميل للحذر والتفكير قبل التصرف",
                        recommendations=[
                            "شجع على اتخاذ مخاطر محسوبة",
                            "عزز الثقة بالنفس",
                        ],
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
                        recommendations=[
                            "شجع الأنشطة التطوعية",
                            "علم الحدود الصحية"],
                    ))

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
            recommendations.append(
                "ممتاز: الطفل يُظهر تعاطفاً عالياً مع الآخرين")

        if behavioral_averages.get("problem_solving", 0) > 0.7:
            recommendations.append(
                "رائع: الطفل لديه مهارات جيدة في حل المشكلات")

        # توصيات من الأنماط
        for pattern in patterns:
            recommendations.extend(pattern.recommendations)

        return recommendations

    def get_story_choice_history(
            self,
            child_name: str,
            device_id: str) -> List[Dict]:
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

        return sorted(
            relevant_logs,
            key=lambda x: x["timestamp"],
            reverse=True)

    def generate_story_report(self, child_name: str,
                              device_id: str) -> Dict[str, Any]:
        """توليد تقرير شامل عن القصص والسلوك"""
        choice_history = self.get_story_choice_history(child_name, device_id)
        behavioral_analysis = self.analyze_behavioral_patterns(
            child_name, device_id)

        # إحصائيات القصص
        stories_played = len(set(choice["story_id"]
                             for choice in choice_history))
        total_choices = len(choice_history)

        # أكثر أنواع الاختيارات
        choice_types = {}
        for choice in choice_history:
            choice_type = choice["choice_type"]
            choice_types[choice_type] = choice_types.get(choice_type, 0) + 1

        most_common_choice = (max(choice_types.items(),
                                  key=lambda x: x[1]) if choice_types else None)

        return {
            "child_name": child_name,
            "device_id": device_id,
            "summary": {
                "stories_played": stories_played,
                "total_choices": total_choices,
                "most_common_choice_type": (
                    most_common_choice[0] if most_common_choice else None
                ),
                "last_story_date": (
                    choice_history[0]["timestamp"] if choice_history else None
                ),
            },
            "behavioral_analysis": behavioral_analysis,
            "recent_choices": choice_history[:10],  # آخر 10 اختيارات
            "generated_at": datetime.now().isoformat(),
        }
