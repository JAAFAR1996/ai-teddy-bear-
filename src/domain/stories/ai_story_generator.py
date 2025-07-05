import asyncio
import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

import openai

from .story_generation.models import GeneratedStory, StoryContext, StoryLength, StoryTheme
from .story_generation.prompt_builder import StoryPromptBuilder
from .story_generation.enhancer import StoryEnhancer


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


class StoryOrchestrator:
    """Orchestrates the story generation process by coordinating different services."""

    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        self.prompt_builder = StoryPromptBuilder()
        self.enhancer = StoryEnhancer()

    async def generate_personalized_story(
        self,
        context: StoryContext,
        theme: StoryTheme = None,
        length: StoryLength = StoryLength.SHORT,
    ) -> GeneratedStory:
        """Generates a personalized story by orchestrating prompt building, generation, and enhancement."""

        theme = theme or self.prompt_builder._suggest_theme_for_context(
            context)

        story_prompt = self.prompt_builder.build(context, theme, length)

        generated_content = await self._generate_with_gpt4(story_prompt, length)

        enhanced_story_data = self.enhancer.enhance(
            generated_content, context, theme)

        return GeneratedStory(
            id=f"ai_story_{datetime.now().timestamp()}",
            theme=theme,
            length=length,
            age_group=self.prompt_builder._determine_age_group(context.age),
            generated_at=datetime.now(),
            **enhanced_story_data
        )

    async def _generate_with_gpt4(self, prompt: str, length: StoryLength) -> str:
        """Generates story content using a GPT model."""
        max_tokens = {StoryLength.SHORT: 800,
                      StoryLength.MEDIUM: 1200, StoryLength.LONG: 1800}
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system",
                        "content": "You are a creative storyteller for children."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens.get(length, 800),
                temperature=0.8,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during GPT-4 generation: {e}")
            return self._generate_fallback_story()

    def _generate_fallback_story(self) -> str:
        """Provides a simple fallback story."""
        return "Title: The Brave Rabbit\\n\\nOnce upon a time, there was a brave rabbit who climbed the tallest hill."

    async def generate_quick_bedtime_story(self, child_name: str, age: int) -> GeneratedStory:
        """Facade method for generating a quick bedtime story."""
        context = StoryContext(
            child_name=child_name, age=age, friends=[], family_members=[], interests=[],
            recent_experiences=[], emotional_state="calm", learning_goals=[],
            cultural_background="general", preferred_characters=[]
        )
        return await self.generate_personalized_story(context, StoryTheme.BEDTIME, StoryLength.SHORT)

    def get_story_suggestions(
            self, context: StoryContext) -> List[Dict[str, Any]]:
        """الحصول على اقتراحات قصص مخصصة"""

        suggestions = []

        # اقتراح بناءً على العمر
        age_appropriate_themes = self.prompt_builder._get_age_appropriate_themes(
            context.age)

        for theme in age_appropriate_themes:
            suggestion = {
                "theme": theme.value,
                "title": f"مغامرة {context.child_name} في {theme.value}",
                "description": self.prompt_builder._get_theme_description(theme, context),
                "estimated_length": "5-7 دقائق",
                "educational_value": self.prompt_builder._get_educational_value(theme),
                "emotional_benefit": self.prompt_builder._get_emotional_benefit(
                    theme, context.emotional_state
                ),
            }
            suggestions.append(suggestion)

        return suggestions
