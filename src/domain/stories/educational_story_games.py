import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SubjectType(Enum):
    """المواد التعليمية"""

    MATH = "رياضيات"
    SCIENCE = "علوم"
    LANGUAGE = "لغة"
    GEOGRAPHY = "جغرافيا"
    HISTORY = "تاريخ"
    ART = "فن"
    MUSIC = "موسيقى"


class DifficultyLevel(Enum):
    """مستويات الصعوبة التعليمية"""

    BEGINNER = "مبتدئ"
    ELEMENTARY = "ابتدائي"
    INTERMEDIATE = "متوسط"
    ADVANCED = "متقدم"


@dataclass
class EducationalChallenge:
    """تحدي تعليمي داخل القصة"""

    id: str
    subject: SubjectType
    difficulty: DifficultyLevel
    question: str
    correct_answer: str
    wrong_answers: List[str]
    hint: str
    explanation: str
    context_in_story: str  # كيف يرتبط بالقصة
    points: int


@dataclass
class LearningProgress:
    """تقدم التعلم للطفل"""

    child_name: str
    device_id: str
    subject_progress: Dict[str, Dict]  # {subject: {level: score}}
    challenges_completed: List[str]
    total_points: int
    current_level: Dict[str, DifficultyLevel]  # لكل مادة
    strengths: List[str]
    areas_for_improvement: List[str]
    last_updated: datetime


@dataclass
class StoryEducationalInsert:
    """إدراج تعليمي في القصة"""

    story_id: str
    position: str  # "beginning", "middle", "end"
    challenge: EducationalChallenge
    narrative_transition: str  # كيف ندمجه في النص
    success_narrative: str  # ماذا يحدث عند النجاح
    failure_narrative: str  # ماذا يحدث عند الفشل


class MathemythsEngine:
    """محرك القصص التعليمية - Mathemyths"""

    def __init__(self):
        self.educational_content = self._load_educational_content()
        self.learning_progress: Dict[str, LearningProgress] = {}
        self.story_inserts: List[StoryEducationalInsert] = []

    def _load_educational_content(self) -> Dict[str, Dict]:
        """تحميل المحتوى التعليمي حسب المواد والمستويات"""
        return {
            SubjectType.MATH.value: {
                DifficultyLevel.BEGINNER.value: [
                    {
                        "question": "كم يد لديك؟",
                        "answer": "2",
                        "wrong_answers": ["1", "3", "4"],
                        "hint": "انظر إلى يديك وعدها",
                        "explanation": "لدى كل إنسان يدان - يد يمنى ويد يسرى",
                    },
                    {
                        "question": "كم عين للقطة؟",
                        "answer": "2",
                        "wrong_answers": ["1", "3", "4"],
                        "hint": "مثل الإنسان تماماً",
                        "explanation": "القطط لها عينان مثل البشر",
                    },
                ],
                DifficultyLevel.ELEMENTARY.value: [
                    {
                        "question": "5 + 3 = ؟",
                        "answer": "8",
                        "wrong_answers": ["7", "9", "6"],
                        "hint": "عد على أصابعك من 5 إلى 8",
                        "explanation": "عندما نجمع 5 + 3، نحصل على 8",
                    },
                    {
                        "question": "في الحديقة 6 ورود، قطفنا 2، كم بقي؟",
                        "answer": "4",
                        "wrong_answers": ["3", "5", "2"],
                        "hint": "نطرح عدد الورود المقطوفة من العدد الكلي",
                        "explanation": "6 - 2 = 4 ورود باقية",
                    },
                ],
                DifficultyLevel.INTERMEDIATE.value: [
                    {
                        "question": "7 × 4 = ؟",
                        "answer": "28",
                        "wrong_answers": ["24", "32", "21"],
                        "hint": "7 + 7 + 7 + 7 أو 4 + 4 + 4 + 4 + 4 + 4 + 4",
                        "explanation": "الضرب هو جمع متكرر: 7 × 4 = 28",
                    }
                ],
            },
            SubjectType.SCIENCE.value: {
                DifficultyLevel.BEGINNER.value: [
                    {
                        "question": "أي لون تحصل عليه عند خلط الأحمر والأزرق؟",
                        "answer": "البنفسجي",
                        "wrong_answers": ["الأخضر", "الأصفر", "البرتقالي"],
                        "hint": "فكر في ألوان قوس قزح",
                        "explanation": "الأحمر + الأزرق = البنفسجي",
                    }
                ],
                DifficultyLevel.ELEMENTARY.value: [
                    {
                        "question": "كم عدد أرجل العنكبوت؟",
                        "answer": "8",
                        "wrong_answers": ["6", "10", "4"],
                        "hint": "أكثر من الحشرة العادية",
                        "explanation": "العناكب لها 8 أرجل دائماً",
                    }
                ],
            },
            SubjectType.LANGUAGE.value: {
                DifficultyLevel.BEGINNER.value: [
                    {
                        "question": "ما عكس كلمة 'كبير'؟",
                        "answer": "صغير",
                        "wrong_answers": ["طويل", "عريض", "ضخم"],
                        "hint": "فكر في الحجم المقابل",
                        "explanation": "كبير وصغير كلمتان متضادتان",
                    }
                ]
            },
        }

    def get_appropriate_challenge(
        self, child_age: int, subject: SubjectType, child_name: str, device_id: str
    ) -> Optional[EducationalChallenge]:
        """الحصول على تحدي مناسب للطفل"""

        # تحديد المستوى بناءً على العمر والتقدم الحالي
        progress_key = f"{device_id}_{child_name}"

        if progress_key in self.learning_progress:
            current_level = self.learning_progress[progress_key].current_level.get(
                subject.value, self._determine_level_by_age(child_age)
            )
        else:
            current_level = self._determine_level_by_age(child_age)

        # البحث عن تحديات مناسبة
        subject_content = self.educational_content.get(subject.value, {})
        level_content = subject_content.get(current_level.value, [])

        if not level_content:
            return None

        # اختيار تحدي عشوائي من المستوى المناسب
        challenge_data = random.choice(level_content)

        challenge = EducationalChallenge(
            id=f"challenge_{datetime.now().timestamp()}",
            subject=subject,
            difficulty=current_level,
            question=challenge_data["question"],
            correct_answer=challenge_data["answer"],
            wrong_answers=challenge_data["wrong_answers"],
            hint=challenge_data["hint"],
            explanation=challenge_data["explanation"],
            context_in_story="",  # سيتم تحديده عند الدمج
            points=self._calculate_challenge_points(current_level),
        )

        return challenge

    def _determine_level_by_age(self, age: int) -> DifficultyLevel:
        """تحديد المستوى بناءً على العمر"""
        if age <= 5:
            return DifficultyLevel.BEGINNER
        elif age <= 8:
            return DifficultyLevel.ELEMENTARY
        elif age <= 12:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.ADVANCED

    def _calculate_challenge_points(self, level: DifficultyLevel) -> int:
        """حساب نقاط التحدي بناءً على المستوى"""
        points_map = {
            DifficultyLevel.BEGINNER: 10,
            DifficultyLevel.ELEMENTARY: 20,
            DifficultyLevel.INTERMEDIATE: 35,
            DifficultyLevel.ADVANCED: 50,
        }
        return points_map[level]

    def integrate_challenge_into_story(
        self,
        story_content: str,
        challenge: EducationalChallenge,
        child_name: str,
        position: str = "middle",
    ) -> StoryEducationalInsert:
        """دمج التحدي التعليمي في القصة"""

        # إنشاء انتقالات سردية مناسبة
        narrative_transitions = {
            SubjectType.MATH.value: [
                f"فجأة، وجد {child_name} لوحة سحرية عليها رقم. لفتح الباب السحري، يجب حل هذا اللغز:",
                f"قال الساحر الحكيم: '{child_name}، لتحصل على المفتاح الذهبي، أجب على هذا السؤال:'",
                f"أمام {child_name} صندوق مغلق بقفل رقمي. الرقم السري هو إجابة هذا السؤال:",
            ],
            SubjectType.SCIENCE.value: [
                f"سأل الأرنب الحكيم {child_name}: 'قبل أن أدلك على الطريق، أخبرني:'",
                f"لتنشط الآلة السحرية، يحتاج {child_name} للإجابة على سؤال علمي:",
                f"قالت الجنية: '{child_name}، معرفتك بالعلوم ستساعدك هنا:'",
            ],
            SubjectType.LANGUAGE.value: [
                f"تحدت الملكة {child_name} في لعبة الكلمات:",
                f"لفك رموز الخريطة القديمة، يحتاج {child_name} لحل هذا اللغز اللغوي:",
                f"قال الببغاء الملون: '{child_name}، أتقن اللغة وسأعطيك الدليل:'",
            ],
        }

        # اختيار انتقال مناسب
        subject_transitions = narrative_transitions.get(
            challenge.subject.value, [f"واجه {child_name} تحدياً جديداً:"]
        )

        narrative_transition = random.choice(subject_transitions)

        # إنشاء ردود فعل للنجاح والفشل
        success_narratives = [
            f"'ممتاز يا {child_name}!' صرخ الجميع بفرح. فتح الطريق أمامه بسحر جميل.",
            f"أضاءت الأنوار السحرية! لقد أثبت {child_name} ذكاءه وحصل على مكافأة رائعة.",
            f"ابتسم الحكيم وقال: 'أحسنت يا {child_name}! ذكاؤك سيأخذك بعيداً.'",
        ]

        failure_narratives = [
            f"لا بأس يا {child_name}، المحاولة مهمة! دعني أعطيك تلميحاً...",
            f"قال المعلم الطيب: 'تعلمنا من أخطائنا يا {child_name}. دعنا نحاول مرة أخرى.'",
            f"ابتسم {child_name} وقال: 'سأفكر أكثر!' الشجاعة في المحاولة هي الأهم.",
        ]

        story_insert = StoryEducationalInsert(
            story_id=f"story_{datetime.now().timestamp()}",
            position=position,
            challenge=challenge,
            narrative_transition=narrative_transition,
            success_narrative=random.choice(success_narratives),
            failure_narrative=random.choice(failure_narratives),
        )

        return story_insert

    async def process_challenge_response(
        self, challenge_id: str, user_answer: str, child_name: str, device_id: str
    ) -> Dict[str, Any]:
        """معالجة إجابة التحدي التعليمي"""

        # البحث عن التحدي
        challenge = None
        for insert in self.story_inserts:
            if insert.challenge.id == challenge_id:
                challenge = insert.challenge
                break

        if not challenge:
            return {"error": "التحدي غير موجود"}

        # فحص الإجابة
        correct = user_answer.strip().lower() == challenge.correct_answer.lower()

        # تحديث تقدم التعلم
        await self._update_learning_progress(child_name, device_id, challenge, correct)

        # إنشاء الرد
        response = {
            "challenge_id": challenge_id,
            "correct": correct,
            "explanation": challenge.explanation,
            "points_earned": challenge.points if correct else 0,
        }

        if correct:
            response["feedback"] = "ممتاز! إجابة صحيحة!"
            response["narrative"] = self._get_success_narrative(challenge, child_name)
        else:
            response["feedback"] = (
                f"محاولة جيدة! الإجابة الصحيحة هي: {challenge.correct_answer}"
            )
            response["hint"] = challenge.hint
            response["narrative"] = self._get_failure_narrative(challenge, child_name)

        return response

    async def _update_learning_progress(
        self,
        child_name: str,
        device_id: str,
        challenge: EducationalChallenge,
        correct: bool,
    ):
        """تحديث تقدم التعلم للطفل"""

        progress_key = f"{device_id}_{child_name}"

        if progress_key not in self.learning_progress:
            self.learning_progress[progress_key] = LearningProgress(
                child_name=child_name,
                device_id=device_id,
                subject_progress={},
                challenges_completed=[],
                total_points=0,
                current_level={},
                strengths=[],
                areas_for_improvement=[],
                last_updated=datetime.now(),
            )

        progress = self.learning_progress[progress_key]

        # تحديث نقاط التقدم للمادة
        subject = challenge.subject.value
        level = challenge.difficulty.value

        if subject not in progress.subject_progress:
            progress.subject_progress[subject] = {}

        if level not in progress.subject_progress[subject]:
            progress.subject_progress[subject][level] = {"correct": 0, "total": 0}

        progress.subject_progress[subject][level]["total"] += 1
        if correct:
            progress.subject_progress[subject][level]["correct"] += 1
            progress.total_points += challenge.points

        # تحديث المستوى الحالي إذا لزم الأمر
        if correct and self._should_level_up(progress, subject, level):
            progress.current_level[subject] = self._get_next_level(challenge.difficulty)

        # تحديث نقاط القوة والضعف
        await self._update_strengths_and_weaknesses(progress)

        # إضافة التحدي للمكتملة
        if challenge.id not in progress.challenges_completed:
            progress.challenges_completed.append(challenge.id)

        progress.last_updated = datetime.now()

    def _should_level_up(
        self, progress: LearningProgress, subject: str, level: str
    ) -> bool:
        """تحديد ما إذا كان يجب الانتقال للمستوى التالي"""
        subject_data = progress.subject_progress[subject][level]
        success_rate = subject_data["correct"] / subject_data["total"]

        # الانتقال للمستوى التالي عند نجاح 80% ومحاولة 5 على الأقل
        return success_rate >= 0.8 and subject_data["total"] >= 5

    def _get_next_level(self, current_level: DifficultyLevel) -> DifficultyLevel:
        """الحصول على المستوى التالي"""
        level_progression = {
            DifficultyLevel.BEGINNER: DifficultyLevel.ELEMENTARY,
            DifficultyLevel.ELEMENTARY: DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.INTERMEDIATE: DifficultyLevel.ADVANCED,
            DifficultyLevel.ADVANCED: DifficultyLevel.ADVANCED,  # أعلى مستوى
        }
        return level_progression[current_level]

    async def _update_strengths_and_weaknesses(self, progress: LearningProgress):
        """تحديث نقاط القوة ومجالات التحسين"""

        strengths = []
        weaknesses = []

        for subject, levels in progress.subject_progress.items():
            total_correct = sum(data["correct"] for data in levels.values())
            total_attempts = sum(data["total"] for data in levels.values())

            if total_attempts > 0:
                success_rate = total_correct / total_attempts

                if success_rate >= 0.8:
                    strengths.append(subject)
                elif success_rate < 0.5:
                    weaknesses.append(subject)

        progress.strengths = strengths
        progress.areas_for_improvement = weaknesses

    def _get_success_narrative(
        self, challenge: EducationalChallenge, child_name: str
    ) -> str:
        """الحصول على نص النجاح"""
        for insert in self.story_inserts:
            if insert.challenge.id == challenge.id:
                return insert.success_narrative
        return f"أحسنت يا {child_name}!"

    def _get_failure_narrative(
        self, challenge: EducationalChallenge, child_name: str
    ) -> str:
        """الحصول على نص الفشل"""
        for insert in self.story_inserts:
            if insert.challenge.id == challenge.id:
                return insert.failure_narrative
        return f"لا بأس يا {child_name}، المحاولة مهمة!"

    def generate_adaptive_story_with_challenges(
        self, child_name: str, age: int, interests: List[str], device_id: str
    ) -> Dict[str, Any]:
        """توليد قصة تكيفية مع تحديات تعليمية"""

        # اختيار مواد تعليمية بناءً على الاهتمامات
        selected_subjects = self._select_subjects_by_interests(interests)

        # إنشاء تحديات لكل مادة
        challenges = []
        for subject in selected_subjects:
            challenge = self.get_appropriate_challenge(
                age, subject, child_name, device_id
            )
            if challenge:
                challenges.append(challenge)

        # إنشاء قصة أساسية
        base_story = self._generate_base_educational_story(child_name, age, interests)

        # دمج التحديات في القصة
        enhanced_story = self._integrate_challenges_into_story(
            base_story, challenges, child_name
        )

        return {
            "story_content": enhanced_story,
            "challenges": [challenge.id for challenge in challenges],
            "subjects_covered": [challenge.subject.value for challenge in challenges],
            "total_possible_points": sum(challenge.points for challenge in challenges),
        }

    def _select_subjects_by_interests(self, interests: List[str]) -> List[SubjectType]:
        """اختيار المواد التعليمية بناءً على الاهتمامات"""

        interest_mapping = {
            "رياضيات": SubjectType.MATH,
            "أرقام": SubjectType.MATH,
            "حساب": SubjectType.MATH,
            "علوم": SubjectType.SCIENCE,
            "طبيعة": SubjectType.SCIENCE,
            "حيوانات": SubjectType.SCIENCE,
            "لغة": SubjectType.LANGUAGE,
            "كلمات": SubjectType.LANGUAGE,
            "قراءة": SubjectType.LANGUAGE,
            "جغرافيا": SubjectType.GEOGRAPHY,
            "خرائط": SubjectType.GEOGRAPHY,
            "تاريخ": SubjectType.HISTORY,
            "فن": SubjectType.ART,
            "رسم": SubjectType.ART,
            "موسيقى": SubjectType.MUSIC,
        }

        selected = []
        for interest in interests:
            if interest.lower() in interest_mapping:
                subject = interest_mapping[interest.lower()]
                if subject not in selected:
                    selected.append(subject)

        # إضافة مواد افتراضية إذا لم تُحدد
        if not selected:
            selected = [SubjectType.MATH, SubjectType.SCIENCE]

        return selected[:3]  # حد أقصى 3 مواد لتجنب الإفراط

    def _generate_base_educational_story(
        self, child_name: str, age: int, interests: List[str]
    ) -> str:
        """توليد قصة أساسية تعليمية"""

        # قوالب قصص تعليمية
        story_templates = [
            f"""
كان {child_name} يستكشف مكتبة سحرية قديمة مليئة بالكتب المتوهجة.
كل كتاب يحتوي على سر مختلف ولغز يحتاج لحل.

{{challenge_1}}

بعد حل اللغز الأول، فتح {child_name} الباب إلى غرفة الاكتشافات العلمية.

{{challenge_2}}

مع كل إجابة صحيحة، كان {child_name} يقترب أكثر من الكنز المعرفي المخفي.

{{challenge_3}}

وأخيراً، وصل {child_name} إلى الكنز الحقيقي - ليس ذهباً أو فضة، بل معرفة ثمينة ستبقى معه إلى الأبد!
            """,
            f"""
انطلق {child_name} في رحلة عبر أرض العجائب التعليمية حيث كل شيء يتكلم ويعلم!

التقى أولاً بالبومة الحكيمة التي أحبت الألغاز:

{{challenge_1}}

ثم قابل العالم الصغير في معمله المليء بالتجارب:

{{challenge_2}}

وأخيراً، وصل إلى حديقة الكلمات حيث الشاعر القديم:

{{challenge_3}}

عاد {child_name} إلى البيت وهو أكثر علماً وحكمة!
            """,
        ]

        return random.choice(story_templates)

    def _integrate_challenges_into_story(
        self, base_story: str, challenges: List[EducationalChallenge], child_name: str
    ) -> str:
        """دمج التحديات في القصة الأساسية"""

        story = base_story

        for i, challenge in enumerate(challenges, 1):
            placeholder = f"{{challenge_{i}}}"

            if placeholder in story:
                # إنشاء إدراج للتحدي
                insert = self.integrate_challenge_into_story(
                    story, challenge, child_name, f"position_{i}"
                )

                # حفظ الإدراج
                self.story_inserts.append(insert)

                # تكوين نص التحدي
                challenge_text = f"""
{insert.narrative_transition}

"{challenge.question}"

أ) {challenge.wrong_answers[0]}
ب) {challenge.correct_answer}
ج) {challenge.wrong_answers[1] if len(challenge.wrong_answers) > 1 else challenge.wrong_answers[0]}

فكر {child_name} قليلاً...
[انتظار إجابة الطفل - معرف التحدي: {challenge.id}]
                """

                story = story.replace(placeholder, challenge_text)

        return story

    def get_learning_report(self, child_name: str, device_id: str) -> Dict[str, Any]:
        """الحصول على تقرير التعلم للطفل"""

        progress_key = f"{device_id}_{child_name}"

        if progress_key not in self.learning_progress:
            return {"message": "لا توجد بيانات تعلم للطفل"}

        progress = self.learning_progress[progress_key]

        # حساب الإحصائيات العامة
        total_challenges = len(progress.challenges_completed)
        subjects_studied = len(progress.subject_progress)

        # حساب معدل النجاح الإجمالي
        total_correct = sum(
            sum(level_data["correct"] for level_data in subject_data.values())
            for subject_data in progress.subject_progress.values()
        )
        total_attempts = sum(
            sum(level_data["total"] for level_data in subject_data.values())
            for subject_data in progress.subject_progress.values()
        )

        overall_success_rate = (
            (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        )

        # تحليل التقدم بكل مادة
        subject_analysis = {}
        for subject, levels in progress.subject_progress.items():
            subject_correct = sum(data["correct"] for data in levels.values())
            subject_total = sum(data["total"] for data in levels.values())
            subject_rate = (
                (subject_correct / subject_total * 100) if subject_total > 0 else 0
            )

            subject_analysis[subject] = {
                "success_rate": round(subject_rate, 1),
                "challenges_completed": subject_total,
                "current_level": progress.current_level.get(subject, "مبتدئ"),
                "performance": (
                    "ممتاز"
                    if subject_rate >= 80
                    else "جيد" if subject_rate >= 60 else "يحتاج تحسين"
                ),
            }

        return {
            "child_name": child_name,
            "overview": {
                "total_points": progress.total_points,
                "total_challenges": total_challenges,
                "subjects_studied": subjects_studied,
                "overall_success_rate": round(overall_success_rate, 1),
            },
            "subject_analysis": subject_analysis,
            "strengths": progress.strengths,
            "areas_for_improvement": progress.areas_for_improvement,
            "recommendations": self._generate_learning_recommendations(progress),
            "last_updated": progress.last_updated.isoformat(),
        }

    def _generate_learning_recommendations(
        self, progress: LearningProgress
    ) -> List[str]:
        """توليد توصيات تعليمية"""
        recommendations = []

        # توصيات بناءً على نقاط القوة
        for strength in progress.strengths:
            recommendations.append(f"ممتاز في {strength}! حاول تحديات أكثر صعوبة")

        # توصيات للتحسين
        for weakness in progress.areas_for_improvement:
            recommendations.append(f"مارس المزيد من تمارين {weakness} لتحسين الأداء")

        # توصيات عامة
        if progress.total_points < 100:
            recommendations.append("استمر في حل التحديات اليومية لزيادة نقاطك")

        if len(progress.challenges_completed) < 10:
            recommendations.append("جرب قصصاً تعليمية أكثر لاكتساب خبرة أوسع")

        return recommendations
