import asyncio
import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

import openai


class StoryLength(Enum):
    """أطوال القصص"""

    SHORT = "قصيرة"  # 2-3 دقائق
    MEDIUM = "متوسطة"  # 5-7 دقائق
    LONG = "طويلة"  # 10-15 دقيقة


class StoryTheme(Enum):
    """مواضيع القصص"""

    ADVENTURE = "مغامرة"
    FRIENDSHIP = "صداقة"
    LEARNING = "تعليمية"
    BEDTIME = "نوم"
    FAMILY = "عائلة"
    ANIMALS = "حيوانات"
    SPACE = "فضاء"
    FANTASY = "خيال"
    HEROIC = "بطولة"
    PROBLEM_SOLVING = "حل_مشاكل"


class AgeGroup(Enum):
    """الفئات العمرية"""

    TODDLER = "3-4"  # أطفال صغار
    PRESCHOOL = "5-6"  # ما قبل المدرسة
    EARLY_SCHOOL = "7-9"  # بداية المدرسة
    MIDDLE_SCHOOL = "10-12"  # متوسط المدرسة
    TEEN = "13-15"  # مراهقة مبكرة


@dataclass
class StoryContext:
    """سياق القصة للتخصيص"""

    child_name: str
    age: int
    friends: List[str]
    family_members: List[str]
    interests: List[str]
    recent_experiences: List[str]  # تجارب حديثة للطفل
    emotional_state: str  # الحالة العاطفية الحالية
    learning_goals: List[str]  # أهداف تعليمية محددة
    cultural_background: str  # الخلفية الثقافية
    preferred_characters: List[str]  # الشخصيات المفضلة


@dataclass
class GeneratedStory:
    """قصة مولدة"""

    id: str
    title: str
    content: str
    theme: StoryTheme
    length: StoryLength
    age_group: AgeGroup
    characters: List[str]
    moral_lesson: str
    educational_elements: List[str]
    emotional_tags: List[str]
    personalization_score: float  # مدى التخصيص (0-1)
    generated_at: datetime
    audio_cues: List[str]  # إشارات للمؤثرات الصوتية


class FairyLandAIGenerator:
    """مولد القصص الذكي بأسلوب FairyLandAI"""

    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        self.story_templates = self._load_story_templates()
        self.character_bank = self._load_character_bank()
        self.moral_lessons = self._load_moral_lessons()

    def _load_story_templates(self) -> Dict[str, Dict]:
        """تحميل قوالب القصص حسب المواضيع"""
        return {
            StoryTheme.ADVENTURE.value: {
                "structure": "introduction → challenge → journey → climax → resolution",
                "key_elements": [
                    "explorer",
                    "obstacle",
                    "courage",
                    "discovery",
                    "triumph",
                ],
                "emotional_arc": "curiosity → excitement → tension → relief → satisfaction",
            },
            StoryTheme.FRIENDSHIP.value: {
                "structure": "meeting → conflict → understanding → cooperation → bond",
                "key_elements": [
                    "new_friend",
                    "misunderstanding",
                    "empathy",
                    "teamwork",
                    "loyalty",
                ],
                "emotional_arc": "loneliness → hope → conflict → understanding → joy",
            },
            StoryTheme.LEARNING.value: {
                "structure": "problem → research → experimentation → failure → success",
                "key_elements": [
                    "question",
                    "investigation",
                    "trial_error",
                    "perseverance",
                    "knowledge",
                ],
                "emotional_arc": "confusion → curiosity → frustration → determination → pride",
            },
            StoryTheme.BEDTIME.value: {
                "structure": "peaceful_setting → gentle_adventure → calming_resolution → sleep",
                "key_elements": ["comfort", "gentle_magic", "safety", "dreams", "rest"],
                "emotional_arc": "alertness → wonder → contentment → sleepiness → peace",
            },
        }

    def _load_character_bank(self) -> Dict[str, List[str]]:
        """تحميل بنك الشخصيات"""
        return {
            "animals": [
                "أرنب صغير",
                "قطة لطيفة",
                "كلب وفي",
                "طائر مغرد",
                "فيل حكيم",
                "دولفين ذكي",
                "سلحفاة صبورة",
                "نحلة نشيطة",
                "فراشة جميلة",
                "أسد شجاع",
            ],
            "fantasy": [
                "تنين ودود",
                "جنية طيبة",
                "ساحر حكيم",
                "أميرة شجاعة",
                "فارس نبيل",
                "عملاق لطيف",
                "روح الغابة",
                "ملك الحيوانات",
                "حورية البحر",
                "طائر العنقاء",
            ],
            "humans": [
                "جد حكيم",
                "جدة محبة",
                "معلم صبور",
                "طبيب طيب",
                "شرطي مساعد",
                "خباز ماهر",
                "فنان موهوب",
                "موسيقي مبدع",
                "رياضي قوي",
                "عالم ذكي",
            ],
            "objects": [
                "كتاب سحري",
                "مصباح عجيب",
                "شجرة متكلمة",
                "نجمة لامعة",
                "قلم ملون",
                "حجر كريم",
                "مرآة سحرية",
                "صندوق الكنوز",
                "بوصلة ذهبية",
                "خريطة قديمة",
            ],
        }

    def _load_moral_lessons(self) -> Dict[str, List[str]]:
        """تحميل الدروس الأخلاقية حسب العمر"""
        return {
            "3-6": [
                "المشاركة تجعل اللعب أكثر متعة",
                "الصدق أفضل من الكذب دائماً",
                "مساعدة الآخرين تشعرنا بالسعادة",
                "الصبر يساعدنا في تحقيق أهدافنا",
                "كل شخص مميز بطريقته الخاصة",
            ],
            "7-10": [
                "العمل الجماعي يحقق نتائج أفضل",
                "المثابرة مفتاح النجاح",
                "احترام الاختلافات يثري حياتنا",
                "الشجاعة لا تعني عدم الخوف، بل مواجهته",
                "التعلم من الأخطاء يجعلنا أقوى",
            ],
            "11-15": [
                "المسؤولية تجعلنا أشخاصاً أفضل",
                "العدالة أساس المجتمع السليم",
                "التعاطف يربط القلوب",
                "الإبداع يحل المشاكل المعقدة",
                "القيادة تعني خدمة الآخرين",
            ],
        }

    async def generate_personalized_story(
        self,
        context: StoryContext,
        theme: StoryTheme = None,
        length: StoryLength = StoryLength.SHORT,
    ) -> GeneratedStory:
        """توليد قصة مخصصة للطفل"""

        # تحديد الموضوع إذا لم يُحدد
        if not theme:
            theme = self._suggest_theme_for_context(context)

        # تحديد الفئة العمرية
        age_group = self._determine_age_group(context.age)

        # بناء prompt مخصص
        story_prompt = await self._build_personalized_prompt(
            context, theme, length, age_group
        )

        # توليد القصة باستخدام GPT-4
        generated_content = await self._generate_with_gpt4(story_prompt, length)

        # تحليل وتحسين القصة
        enhanced_story = await self._enhance_story_content(
            generated_content, context, theme
        )

        # إنشاء كائن القصة
        story = GeneratedStory(
            id=f"ai_story_{datetime.now().timestamp()}",
            title=enhanced_story["title"],
            content=enhanced_story["content"],
            theme=theme,
            length=length,
            age_group=age_group,
            characters=enhanced_story["characters"],
            moral_lesson=enhanced_story["moral_lesson"],
            educational_elements=enhanced_story["educational_elements"],
            emotional_tags=enhanced_story["emotional_tags"],
            personalization_score=self._calculate_personalization_score(
                enhanced_story, context
            ),
            generated_at=datetime.now(),
            audio_cues=enhanced_story["audio_cues"],
        )

        return story

    def _suggest_theme_for_context(self, context: StoryContext) -> StoryTheme:
        """اقتراح موضوع مناسب للسياق"""

        # اقتراح بناءً على الحالة العاطفية
        if context.emotional_state == "قلق":
            return StoryTheme.FRIENDSHIP  # قصص الصداقة مهدئة
        elif context.emotional_state == "متحمس":
            return StoryTheme.ADVENTURE  # مغامرات للطاقة العالية
        elif context.emotional_state == "حزين":
            return StoryTheme.FAMILY  # قصص عائلية دافئة
        elif context.emotional_state == "فضولي":
            return StoryTheme.LEARNING  # قصص تعليمية

        # اقتراح بناءً على الاهتمامات
        if "علوم" in context.interests:
            return StoryTheme.LEARNING
        elif "حيوانات" in context.interests:
            return StoryTheme.ANIMALS
        elif "فضاء" in context.interests:
            return StoryTheme.SPACE

        # اقتراح بناءً على العمر
        if context.age <= 6:
            return random.choice([StoryTheme.ANIMALS, StoryTheme.FRIENDSHIP])
        elif context.age <= 10:
            return random.choice([StoryTheme.ADVENTURE, StoryTheme.LEARNING])
        else:
            return random.choice([StoryTheme.HEROIC, StoryTheme.PROBLEM_SOLVING])

    def _determine_age_group(self, age: int) -> AgeGroup:
        """تحديد الفئة العمرية"""
        if age <= 4:
            return AgeGroup.TODDLER
        elif age <= 6:
            return AgeGroup.PRESCHOOL
        elif age <= 9:
            return AgeGroup.EARLY_SCHOOL
        elif age <= 12:
            return AgeGroup.MIDDLE_SCHOOL
        else:
            return AgeGroup.TEEN

    async def _build_personalized_prompt(
        self,
        context: StoryContext,
        theme: StoryTheme,
        length: StoryLength,
        age_group: AgeGroup,
    ) -> str:
        """بناء prompt مخصص للطفل"""

        # اختيار درس أخلاقي مناسب
        age_range = age_group.value
        if age_range in self.moral_lessons:
            moral_lesson = random.choice(self.moral_lessons[age_range])
        else:
            moral_lesson = "أهمية الصداقة والتعاون"

        # اختيار شخصيات من البنك
        theme_characters = []
        if theme in [StoryTheme.ANIMALS, StoryTheme.FRIENDSHIP]:
            theme_characters = random.sample(
                self.character_bank["animals"], 2)
        elif theme in [StoryTheme.FANTASY, StoryTheme.ADVENTURE]:
            theme_characters = random.sample(
                self.character_bank["fantasy"], 2)
        else:
            theme_characters = random.sample(
                self.character_bank["humans"], 2)

        # بناء الـ prompt
        prompt = f"""
أنت كاتب قصص أطفال محترف متخصص في إنشاء قصص مخصصة وتفاعلية.

معلومات الطفل:
- الاسم: {context.child_name}
- العمر: {context.age} سنوات
- الأصدقاء: {', '.join(context.friends) if context.friends else 'لا يوجد أصدقاء مذكورين'}
- أفراد العائلة: {', '.join(context.family_members) if context.family_members else 'العائلة'}
- الاهتمامات: {', '.join(context.interests) if context.interests else 'متنوعة'}
- الحالة العاطفية: {context.emotional_state}
- الخلفية الثقافية: {context.cultural_background}

مواصفات القصة:
- الموضوع: {theme.value}
- الطول: {length.value} ({self._get_length_description(length)})
- الفئة العمرية: {age_group.value} سنوات
- الدرس الأخلاقي: {moral_lesson}

الشخصيات المقترحة: {', '.join(theme_characters)}

متطلبات القصة:
1. اجعل {context.child_name} البطل الرئيسي للقصة
2. أدرج أصدقاءه {', '.join(context.friends[:2]) if context.friends else ''} كشخصيات مهمة
3. اربط القصة بحالته العاطفية الحالية ({context.emotional_state})
4. استخدم لغة مناسبة لعمر {context.age} سنوات
5. أدرج الدرس الأخلاقي بشكل طبيعي في القصة
6. أضف عناصر تفاعلية أو تعليمية مناسبة
7. اختتم بنهاية إيجابية ومشجعة
8. أضف إشارات للمؤثرات الصوتية في [أقواس معقوفة]

هيكل القصة:
{self.story_templates[theme.value]['structure']}

العناصر المطلوبة:
{', '.join(self.story_templates[theme.value]['key_elements'])}

ابدأ القصة الآن:
"""

        return prompt

    def _get_length_description(self, length: StoryLength) -> str:
        """وصف طول القصة"""
        descriptions = {
            StoryLength.SHORT: "300-500 كلمة، 2-3 دقائق قراءة",
            StoryLength.MEDIUM: "500-800 كلمة، 5-7 دقائق قراءة",
            StoryLength.LONG: "800-1200 كلمة، 10-15 دقيقة قراءة",
        }
        return descriptions[length]

    async def _generate_with_gpt4(self, prompt: str, length: StoryLength) -> str:
        """توليد القصة باستخدام GPT-4"""

        # تحديد عدد التوكنز حسب الطول
        max_tokens = {
            StoryLength.SHORT: 800,
            StoryLength.MEDIUM: 1200,
            StoryLength.LONG: 1800,
        }

        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "أنت كاتب قصص أطفال محترف ومبدع."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens[length],
                temperature=0.8,
                presence_penalty=0.6,
                frequency_penalty=0.3,
            )

            return response.choices[0].message.content
        except Exception as exc:  # التراجع إلى قصة افتراضية في حالة الخطأ
            return self._generate_fallback_story(length)

    def _generate_fallback_story(self, length: StoryLength) -> str:
        """توليد قصة احتياطية في حالة فشل الـ AI"""

        fallback_stories = {
            StoryLength.SHORT: """
عنوان: مغامرة {child_name} الصغيرة

[موسيقى هادئة]

كان {child_name} يلعب في الحديقة عندما رأى قطة صغيرة عالقة في الشجرة. 

[صوت مواء القطة]

"لا تخافي أيتها القطة الصغيرة، سأساعدك!" قال {child_name} بثقة.

فكر {child_name} في طريقة آمنة لمساعدة القطة. استدعى {friend1} للمساعدة، وحضرا سلماً صغيراً.

[أصوات تعاون]

بعمل جماعي رائع، نجحا في إنقاذ القطة الصغيرة. شعر {child_name} بسعادة كبيرة لمساعدة حيوان محتاج.

[موسيقى سعيدة]

وهكذا تعلم {child_name} أن مساعدة الآخرين تجعلنا نشعر بالفخر والسعادة.

النهاية.
            """,
            StoryLength.MEDIUM: """
عنوان: كنز {child_name} المفقود

[موسيقى مغامرات]

في يوم مشمس جميل، كان {child_name} و{friend1} يلعبان في الحديقة عندما وجدا خريطة غامضة.

[صوت ورق قديم]

"انظر! هذه خريطة كنز حقيقية!" صرخ {child_name} بحماس.

قرر الصديقان اتباع الخريطة. أولاً، مرا بجسر صغير فوق الجدول.

[صوت مياه جارية]

ثم وصلا إلى غابة صغيرة حيث التقيا بأرنب حكيم.

"لتجدا الكنز، يجب أن تحلا هذا اللغز،" قال الأرنب. "ما هو الشيء الذي كلما أخذت منه كبر؟"

فكر {child_name} قليلاً ثم أجاب: "الحفرة!"

"أحسنت!" قال الأرنب، وأعطاهما المفتاح الذهبي.

[صوت مفاتيح]

وصل الأصدقاء أخيراً إلى صندوق الكنز. فتحاه بالمفتاح الذهبي، ووجدا بداخله... كتباً ملونة وألعاباً تعليمية!

[موسيقى احتفالية]

فهم {child_name} أن الكنز الحقيقي هو المعرفة والصداقة. وهكذا انتهت مغامرتهما الرائعة.

النهاية.
            """,
        }

        return fallback_stories.get(length, fallback_stories[StoryLength.SHORT])

    async def _enhance_story_content(
        self, raw_content: str, context: StoryContext, theme: StoryTheme
    ) -> Dict[str, Any]:
        """تحسين محتوى القصة وتحليلها"""

        # استخراج العنوان
        lines = raw_content.strip().split("\n")
        title_line = next(
            (line for line in lines if line.startswith("عنوان:")), "")
        title = (
            title_line.replace("عنوان:", "").strip(
            ) or f"مغامرة {context.child_name}"
        )

        # إزالة سطر العنوان من المحتوى
        content = raw_content.replace(title_line, "").strip()

        # تخصيص الأسماء
        content = self._personalize_names(content, context)

        # استخراج الشخصيات
        characters = self._extract_characters(content, context)

        # تحديد الدرس الأخلاقي
        moral_lesson = self._extract_moral_lesson(content, context.age)

        # تحديد العناصر التعليمية
        educational_elements = self._extract_educational_elements(
            content, theme)

        # تحديد العلامات العاطفية
        emotional_tags = self._extract_emotional_tags(content)

        # استخراج إشارات الصوت
        audio_cues = self._extract_audio_cues(content)

        return {
            "title": title,
            "content": content,
            "characters": characters,
            "moral_lesson": moral_lesson,
            "educational_elements": educational_elements,
            "emotional_tags": emotional_tags,
            "audio_cues": audio_cues,
        }

    def _personalize_names(self, content: str, context: StoryContext) -> str:
        """تخصيص الأسماء في القصة"""

        # استبدال الأسماء العامة بأسماء حقيقية
        replacements = {
            "{child_name}": context.child_name,
            "{friend1}": context.friends[0] if context.friends else "صديقه المفضل",
            "{friend2}": context.friends[1] if len(context.friends) > 1 else "صديق آخر",
            "{family}": (
                ", ".join(context.family_members[:2])
                if context.family_members
                else "عائلته"
            ),
        }

        for placeholder, replacement in replacements.items():
            content = content.replace(placeholder, replacement)

        return content

    def _extract_characters(self, content: str, context: StoryContext) -> List[str]:
        """استخراج الشخصيات من القصة"""
        characters = [context.child_name]

        # إضافة الأصدقاء
        for friend in context.friends:
            if friend in content:
                characters.append(friend)

        # البحث عن شخصيات أخرى
        character_keywords = [
            "قطة",
            "كلب",
            "أرنب",
            "طائر",
            "فيل",
            "أسد",
            "جدة",
            "جد",
            "معلم",
            "طبيب",
            "أمير",
            "أميرة",
        ]

        for keyword in character_keywords:
            if keyword in content and keyword not in characters:
                characters.append(keyword)

        return characters

    def _extract_moral_lesson(self, content: str, age: int) -> str:
        """استخراج الدرس الأخلاقي من القصة"""

        moral_indicators = {
            "مساعدة": "أهمية مساعدة الآخرين",
            "صداقة": "قيمة الصداقة الحقيقية",
            "تعاون": "قوة العمل الجماعي",
            "صبر": "فوائد الصبر والمثابرة",
            "شجاع": "الشجاعة في مواجهة التحديات",
            "صدق": "أهمية الصدق والأمانة",
            "مشاركة": "متعة المشاركة مع الآخرين",
        }

        for indicator, lesson in moral_indicators.items():
            if indicator in content:
                return lesson

        return "أهمية القيم الإيجابية في الحياة"

    def _extract_educational_elements(
        self, content: str, theme: StoryTheme
    ) -> List[str]:
        """استخراج العناصر التعليمية"""

        elements = []

        # العناصر التعليمية حسب الموضوع
        if theme == StoryTheme.LEARNING:
            if "لغز" in content or "سؤال" in content:
                elements.append("حل المشكلات")
            if any(word in content for word in ["رقم", "عدد", "حساب"]):
                elements.append("الرياضيات")

        if theme == StoryTheme.ANIMALS:
            elements.append("تعلم عن الحيوانات")

        if theme == StoryTheme.SPACE:
            elements.append("استكشاف الفضاء")

        # عناصر عامة
        if "لون" in content:
            elements.append("تعلم الألوان")
        if any(word in content for word in ["كبير", "صغير", "طويل", "قصير"]):
            elements.append("المفاهيم المكانية")

        return elements

    def _extract_emotional_tags(self, content: str) -> List[str]:
        """استخراج العلامات العاطفية"""

        emotion_words = {
            "سعادة": ["سعيد", "فرح", "مبتهج", "مرح"],
            "شجاعة": ["شجاع", "قوي", "بطل", "جرئ"],
            "حب": ["أحب", "محبة", "عاطفة", "حنان"],
            "صداقة": ["صديق", "رفيق", "زميل", "أخ"],
            "فضول": ["فضولي", "يتساءل", "يستكشف", "يبحث"],
            "ثقة": ["واثق", "قادر", "قوي", "متأكد"],
        }

        tags = []
        content_lower = content.lower()

        for emotion, words in emotion_words.items():
            if any(word in content_lower for word in words):
                tags.append(emotion)

        return tags

    def _extract_audio_cues(self, content: str) -> List[str]:
        """استخراج إشارات المؤثرات الصوتية"""

        import re

        # البحث عن النصوص بين أقواس معقوفة
        audio_cues = re.findall(r"\[([^\]]+)\]", content)

        return audio_cues

    def _calculate_personalization_score(
        self, story: Dict, context: StoryContext
    ) -> float:
        """حساب درجة التخصيص للقصة"""

        score = 0.0
        max_score = 10.0

        # نقاط لذكر اسم الطفل
        if context.child_name in story["content"]:
            score += 2.0

        # نقاط لذكر الأصدقاء
        friends_mentioned = sum(
            1 for friend in context.friends if friend in story["content"]
        )
        score += min(friends_mentioned * 1.0, 2.0)

        # نقاط للاهتمامات
        interests_included = sum(
            1
            for interest in context.interests
            if interest.lower() in story["content"].lower()
        )
        score += min(interests_included * 0.5, 2.0)

        # نقاط للحالة العاطفية
        emotional_alignment = len(
            [tag for tag in story["emotional_tags"]
                if context.emotional_state in tag]
        )
        if emotional_alignment > 0:
            score += 1.5

        # نقاط للعناصر التعليمية
        if story["educational_elements"]:
            score += 1.0

        # نقاط للدرس الأخلاقي
        if story["moral_lesson"]:
            score += 1.5

        return min(score / max_score, 1.0)

    async def generate_quick_bedtime_story(
        self, child_name: str, age: int
    ) -> GeneratedStory:
        """توليد قصة نوم سريعة"""

        context = StoryContext(
            child_name=child_name,
            age=age,
            friends=[],
            family_members=[],
            interests=[],
            recent_experiences=[],
            emotional_state="هادئ",
            learning_goals=[],
            cultural_background="عربي",
            preferred_characters=[],
        )

        return await self.generate_personalized_story(
            context, StoryTheme.BEDTIME, StoryLength.SHORT
        )

    def get_story_suggestions(self, context: StoryContext) -> List[Dict[str, Any]]:
        """الحصول على اقتراحات قصص مخصصة"""

        suggestions = []

        # اقتراح بناءً على العمر
        age_appropriate_themes = self._get_age_appropriate_themes(context.age)

        for theme in age_appropriate_themes:
            suggestion = {
                "theme": theme.value,
                "title": f"مغامرة {context.child_name} في {theme.value}",
                "description": self._get_theme_description(theme, context),
                "estimated_length": "5-7 دقائق",
                "educational_value": self._get_educational_value(theme),
                "emotional_benefit": self._get_emotional_benefit(
                    theme, context.emotional_state
                ),
            }
            suggestions.append(suggestion)

        return suggestions

    def _get_age_appropriate_themes(self, age: int) -> List[StoryTheme]:
        """الحصول على المواضيع المناسبة للعمر"""

        if age <= 5:
            return [StoryTheme.ANIMALS, StoryTheme.FRIENDSHIP, StoryTheme.FAMILY]
        elif age <= 8:
            return [
                StoryTheme.ADVENTURE,
                StoryTheme.LEARNING,
                StoryTheme.ANIMALS,
                StoryTheme.FRIENDSHIP,
            ]
        elif age <= 12:
            return [
                StoryTheme.ADVENTURE,
                StoryTheme.HEROIC,
                StoryTheme.PROBLEM_SOLVING,
                StoryTheme.SPACE,
            ]
        else:
            return [
                StoryTheme.HEROIC,
                StoryTheme.PROBLEM_SOLVING,
                StoryTheme.SPACE,
                StoryTheme.FANTASY,
            ]

    def _get_theme_description(self, theme: StoryTheme, context: StoryContext) -> str:
        """وصف الموضوع مخصص للطفل"""

        descriptions = {
            StoryTheme.ADVENTURE: f"انضم إلى {context.child_name} في مغامرة مثيرة مليئة بالاكتشافات",
            StoryTheme.FRIENDSHIP: f"اكتشف مع {context.child_name} معنى الصداقة الحقيقية",
            StoryTheme.LEARNING: f"تعلم مع {context.child_name} أشياء جديدة ومثيرة",
            StoryTheme.ANIMALS: f"استكشف عالم الحيوانات مع {context.child_name}",
            StoryTheme.SPACE: f"سافر مع {context.child_name} إلى النجوم والكواكب",
        }

        return descriptions.get(theme, f"قصة رائعة مع {context.child_name}")

    def _get_educational_value(self, theme: StoryTheme) -> str:
        """القيمة التعليمية للموضوع"""

        values = {
            StoryTheme.LEARNING: "تطوير حب الاستطلاع والتعلم",
            StoryTheme.ANIMALS: "تعلم عن الطبيعة والحيوانات",
            StoryTheme.SPACE: "استكشاف العلوم والفضاء",
            StoryTheme.FRIENDSHIP: "تطوير المهارات الاجتماعية",
            StoryTheme.PROBLEM_SOLVING: "تنمية مهارات التفكير النقدي",
        }

        return values.get(theme, "تطوير الخيال والإبداع")

    def _get_emotional_benefit(self, theme: StoryTheme, emotional_state: str) -> str:
        """الفائدة العاطفية للموضوع"""

        benefits = {
            ("قلق", StoryTheme.FRIENDSHIP): "تهدئة القلق من خلال الدعم الاجتماعي",
            ("حزين", StoryTheme.FAMILY): "الشعور بالدفء والانتماء",
            ("متحمس", StoryTheme.ADVENTURE): "توجيه الطاقة بشكل إيجابي",
            ("ملل", StoryTheme.LEARNING): "إثارة الفضول والاهتمام",
        }

        return benefits.get((emotional_state, theme), "تعزيز المشاعر الإيجابية")
