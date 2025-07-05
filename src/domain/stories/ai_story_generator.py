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

    def _get_animal_characters(self) -> List[str]:
        """Returns a list of animal characters."""
        return [
            "أرنب صغير", "قطة لطيفة", "كلب وفي", "طائر مغرد", "فيل حكيم",
            "دولفين ذكي", "سلحفاة صبورة", "نحلة نشيطة", "فراشة جميلة", "أسد شجاع",
        ]

    def _get_fantasy_characters(self) -> List[str]:
        """Returns a list of fantasy characters."""
        return [
            "تنين ودود", "جنية طيبة", "ساحر حكيم", "أميرة شجاعة", "فارس نبيل",
            "عملاق لطيف", "روح الغابة", "ملك الحيوانات", "حورية البحر", "طائر العنقاء",
        ]

    def _get_human_characters(self) -> List[str]:
        """Returns a list of human characters."""
        return [
            "جد حكيم", "جدة محبة", "معلم صبور", "طبيب طيب", "شرطي مساعد",
            "خباز ماهر", "فنان موهوب", "موسيقي مبدع", "رياضي قوي", "عالم ذكي",
        ]

    def _get_object_characters(self) -> List[str]:
        """Returns a list of object characters."""
        return [
            "كتاب سحري", "مصباح عجيب", "شجرة متكلمة", "نجمة لامعة", "قلم ملون",
            "حجر كريم", "مرآة سحرية", "صندوق الكنوز", "بوصلة ذهبية", "خريطة قديمة",
        ]

    def _load_character_bank(self) -> Dict[str, List[str]]:
        """تحميل بنك الشخصيات"""
        return {
            "animals": self._get_animal_characters(),
            "fantasy": self._get_fantasy_characters(),
            "humans": self._get_human_characters(),
            "objects": self._get_object_characters(),
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

    def _get_emotional_theme_map(self) -> Dict[str, StoryTheme]:
        """Returns a mapping of emotional states to story themes."""
        return {
            "قلق": StoryTheme.FRIENDSHIP,  # Friendship stories can be calming
            "متحمس": StoryTheme.ADVENTURE,  # Adventure for high energy
            "حزين": StoryTheme.FAMILY,    # Family stories for comfort
            "فضولي": StoryTheme.LEARNING,  # Learning for a curious mind
        }

    def _get_interest_theme_map(self) -> Dict[str, StoryTheme]:
        """Returns a mapping of interests to story themes."""
        return {
            "فضاء": StoryTheme.SPACE,
            "حيوانات": StoryTheme.ANIMALS,
            "ابطال": StoryTheme.HEROIC,  # Using a keyword for heroes
            "خيال": StoryTheme.FANTASY,
            "حل الألغاز": StoryTheme.PROBLEM_SOLVING,
        }

    def _suggest_theme_for_context(self, context: StoryContext) -> StoryTheme:
        """اقتراح موضوع مناسب للسياق"""
        # 1. Check emotional state first
        emotional_map = self._get_emotional_theme_map()
        if context.emotional_state in emotional_map:
            return emotional_map[context.emotional_state]

        # 2. Check interests
        interest_map = self._get_interest_theme_map()
        for interest, theme in interest_map.items():
            if any(interest in user_interest for user_interest in context.interests):
                return theme

        # 3. Check learning goals
        if context.learning_goals:
            return StoryTheme.LEARNING

        # 4. Default theme based on age
        if context.age < 6:
            return StoryTheme.BEDTIME
        else:
            return StoryTheme.ADVENTURE

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

    def _get_prompt_introduction(self, theme: StoryTheme, length_str: str) -> str:
        """Generates the introduction for the story prompt."""
        return f"Act as a master storyteller for children. Write a personalized, engaging, and age-appropriate story in Arabic. The theme is '{theme.value}' and the length should be '{length_str}'."

    def _get_prompt_context_section(self, context: StoryContext) -> str:
        """Generates the context section for the story prompt."""
        return f"""
### Child's Context
- **Name:** {context.child_name}
- **Age:** {context.age}
- **Friends:** {', '.join(context.friends)}
- **Family:** {', '.join(context.family_members)}
- **Interests:** {', '.join(context.interests)}
- **Emotional State:** {context.emotional_state}
- **Learning Goals:** {', '.join(context.learning_goals)}
"""

    def _get_prompt_story_elements_section(self, theme: StoryTheme, age_group: AgeGroup, context: StoryContext) -> str:
        """Generates the story elements section for the prompt."""
        template = self.story_templates.get(theme.value, {})
        characters = random.sample(self.character_bank.get(
            random.choice(list(self.character_bank.keys())), []), 2)
        if context.preferred_characters:
            characters.extend(context.preferred_characters)
        moral_lesson = random.choice(
            self.moral_lessons.get(age_group.value, []))

        return f"""
### Story Elements
- **Structure:** {template.get('structure', 'A simple beginning, middle, and end.')}
- **Key Elements:** {', '.join(template.get('key_elements', []))}
- **Main Characters:** {', '.join(characters)}
- **Moral Lesson:** {moral_lesson}
"""

    def _get_prompt_style_and_rules_section(self) -> str:
        """Generates the style and rules section for the prompt."""
        return """
### Style and Rules
- **Language:** Modern Standard Arabic, simplified for children.
- **Tone:** Warm, engaging, and positive.
- **Rules:** No violence, scary situations, or complex vocabulary. Keep it simple and direct.
- **Output Format:** Provide only the story content, starting with a title. Example: 'Title: [Story Title]\\n\\n[Story Content...]'
"""

    async def _build_personalized_prompt(
        self,
        context: StoryContext,
        theme: StoryTheme,
        length: StoryLength,
        age_group: AgeGroup,
    ) -> str:
        """بناء prompt مخصص ومفصل لـ GPT-4"""
        length_str = self._get_length_description(length)

        intro = self._get_prompt_introduction(theme, length_str)
        context_section = self._get_prompt_context_section(context)
        elements_section = self._get_prompt_story_elements_section(
            theme, age_group, context)
        style_section = self._get_prompt_style_and_rules_section()

        return f"{intro}{context_section}{elements_section}{style_section}"

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
        except Exception as e:
            print(f"An error occurred during GPT-4 generation: {e}")
            return self._generate_fallback_story(length)

    def _get_fallback_stories(self) -> Dict[str, Dict[str, str]]:
        """Returns a dictionary of pre-written fallback stories."""
        return {
            "short_adventure": {
                "title": "الأرنب الشجاع",
                "content": "كان يا مكان، أرنب صغير اسمه فوفي. قرر فوفي أن يتسلق أعلى تل في الغابة. كان التل عالياً جداً، لكن فوفي لم يخف. قفز وتسلق حتى وصل إلى القمة ورأى كل الغابة من فوق.",
            },
            "short_friendship": {
                "title": "القطة والكلب",
                "content": "في حديقة جميلة، كانت هناك قطة صغيرة وكلب كبير. في البداية، كانا يخافان من بعضهما. لكن عندما بدأت تمطر، احتميا تحت نفس الشجرة وأصبحا صديقين حميمين.",
            },
            "medium_learning": {
                "title": "النجمة اللامعة",
                "content": "كان هناك طفل اسمه سامي يحب النظر إلى النجوم. سأل والده: لماذا تلمع النجوم؟ شرح له والده أن النجوم هي شموس بعيدة جداً، وأن نورها يسافر طويلاً ليصل إلينا. تعلم سامي شيئاً جديداً ومدهشاً ذلك اليوم.",
            },
            "long_fantasy": {
                "title": "تنين الشوكولاتة",
                "content": "في أرض بعيدة، كان هناك تنين لا ينفث النار، بل الشوكولاتة الساخنة. كان كل سكان القرية يحبونه، خاصة في أيام الشتاء الباردة. كان التنين سعيداً لأنه يجلب الدفء والبهجة للجميع. وفي أحد الأيام، ساعد التنين في إذابة جليد كبير كان يغلق الطريق، وأصبح بطلاً محبوباً أكثر.",
            },
        }

    def _generate_fallback_story(self, length: StoryLength) -> str:
        """توليد قصة بديلة في حال فشل GPT-4"""
        fallback_stories = self._get_fallback_stories()

        # Select a story based on length, or randomly
        if length == StoryLength.SHORT:
            story_key = random.choice(["short_adventure", "short_friendship"])
        elif length == StoryLength.MEDIUM:
            story_key = "medium_learning"
        else:  # LONG
            story_key = "long_fantasy"

        story = fallback_stories.get(
            story_key, fallback_stories["short_adventure"])

        return f'Title: {story["title"]}\n\n{story["content"]}'

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
        # This would ideally use a more advanced NLP model
        lessons = self.moral_lessons.get(
            self._determine_age_group(age).value, [])
        for lesson in lessons:
            if lesson.split()[0] in content or lesson.split()[-1] in content:
                return lesson
        return "الاستمتاع بالمغامرة والتعلم"

    def _get_theme_to_keywords_map(self) -> Dict[StoryTheme, List[str]]:
        """Returns a map of story themes to educational keywords."""
        return {
            StoryTheme.LEARNING: ["تعلم", "معرفة", "اكتشاف", "سؤال", "جواب"],
            StoryTheme.ADVENTURE: ["شجاعة", "استكشاف", "خريطة", "كنز", "رحلة"],
            StoryTheme.FRIENDSHIP: ["صداقة", "مشاركة", "تعاون", "مساعدة", "لطف"],
            StoryTheme.SPACE: ["كوكب", "نجم", "فضاء", "صاروخ", "مجرة"],
            StoryTheme.ANIMALS: ["قطة", "كلب", "أرنب", "طائر", "حيوان"],
            StoryTheme.PROBLEM_SOLVING: ["لغز", "حل", "فكرة", "تفكير", "ذكاء"],
        }

    def _extract_educational_elements(
        self, content: str, theme: StoryTheme
    ) -> List[str]:
        """استخراج العناصر التعليمية بناءً على الموضوع"""
        theme_keywords = self._get_theme_to_keywords_map()
        keywords_for_theme = theme_keywords.get(theme, [])

        found_elements = [
            keyword for keyword in keywords_for_theme if keyword in content]

        # Add a default element if none are found
        if not found_elements and keywords_for_theme:
            found_elements.append(f"مفاهيم عامة عن {theme.value}")

        return found_elements

    def _extract_emotional_tags(self, content: str) -> List[str]:
        """استخراج العلامات العاطفية من القصة"""
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
