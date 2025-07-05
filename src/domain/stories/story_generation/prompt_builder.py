import random
from typing import Dict, List

from .models import AgeGroup, StoryContext, StoryLength, StoryTheme
from .data_service import load_character_bank, load_moral_lessons, load_story_templates


class StoryPromptBuilder:
    def __init__(self):
        self.story_templates = load_story_templates()
        self.character_bank = load_character_bank()
        self.moral_lessons = load_moral_lessons()

    def build(self, context: StoryContext, theme: StoryTheme, length: StoryLength) -> str:
        age_group = self._determine_age_group(context.age)
        theme = theme or self._suggest_theme_for_context(context)
        length_str = self._get_length_description(length)

        intro = self._get_prompt_introduction(theme, length_str)
        context_section = self._get_prompt_context_section(context)
        elements_section = self._get_prompt_story_elements_section(
            theme, age_group, context)
        style_section = self._get_prompt_style_and_rules_section()

        return f"{intro}{context_section}{elements_section}{style_section}"

    def _suggest_theme_for_context(self, context: StoryContext) -> StoryTheme:
        if context.emotional_state in self._get_emotional_theme_map():
            return self._get_emotional_theme_map()[context.emotional_state]
        for interest, theme in self._get_interest_theme_map().items():
            if any(interest in user_interest for user_interest in context.interests):
                return theme
        return StoryTheme.LEARNING if context.learning_goals else StoryTheme.ADVENTURE

    def _determine_age_group(self, age: int) -> AgeGroup:
        if age <= 4:
            return AgeGroup.TODDLER
        if age <= 6:
            return AgeGroup.PRESCHOOL
        if age <= 9:
            return AgeGroup.EARLY_SCHOOL
        if age <= 12:
            return AgeGroup.MIDDLE_SCHOOL
        return AgeGroup.TEEN

    def _get_length_description(self, length: StoryLength) -> str:
        return {
            StoryLength.SHORT: "300-500 words",
            StoryLength.MEDIUM: "500-800 words",
            StoryLength.LONG: "800-1200 words",
        }[length]

    def _get_prompt_introduction(self, theme: StoryTheme, length_str: str) -> str:
        return f"Act as a master storyteller for children. Write a personalized story in Arabic. Theme: '{theme.value}', Length: '{length_str}'."

    def _get_prompt_context_section(self, context: StoryContext) -> str:
        return f"""
### Child's Context
- Name: {context.child_name}, Age: {context.age}
- Friends: {', '.join(context.friends)}
- Interests: {', '.join(context.interests)}
- Emotional State: {context.emotional_state}
"""

    def _get_prompt_story_elements_section(self, theme: StoryTheme, age_group: AgeGroup, context: StoryContext) -> str:
        template = self.story_templates.get(theme.value, {})
        characters = random.sample(self.character_bank.get(
            random.choice(list(self.character_bank.keys())), []), 2)
        if context.preferred_characters:
            characters.extend(context.preferred_characters)
        moral_lesson = random.choice(
            self.moral_lessons.get(age_group.value, []))
        return f"""
### Story Elements
- Structure: {template.get('structure', 'A simple beginning, middle, and end.')}
- Main Characters: {', '.join(characters)}
- Moral Lesson: {moral_lesson}
"""

    def _get_prompt_style_and_rules_section(self) -> str:
        return """
### Style and Rules
- Language: Simplified Modern Standard Arabic.
- Tone: Warm, engaging, and positive.
- Rules: No violence or complex vocabulary.
- Output Format: 'Title: [Story Title]\\n\\n[Story Content...]'
"""

    def _get_emotional_theme_map(self) -> Dict[str, StoryTheme]:
        return {"sad": StoryTheme.FRIENDSHIP, "excited": StoryTheme.ADVENTURE, "curious": StoryTheme.LEARNING}

    def _get_interest_theme_map(self) -> Dict[str, StoryTheme]:
        return {"space": StoryTheme.SPACE, "animals": StoryTheme.ANIMALS, "heroes": StoryTheme.HEROIC}
