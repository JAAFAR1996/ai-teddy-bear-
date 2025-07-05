import re
from typing import Dict, List, Any

from .models import StoryContext, StoryTheme
from .data_service import load_moral_lessons


class StoryEnhancer:
    def __init__(self):
        self.moral_lessons = load_moral_lessons()

    def enhance(self, raw_content: str, context: StoryContext, theme: StoryTheme) -> Dict[str, Any]:
        title = self._extract_title(raw_content, context)
        content = self._clean_content(raw_content)
        content = self._personalize_names(content, context)

        story_data = {
            "title": title,
            "content": content,
            "characters": self._extract_characters(content, context),
            "moral_lesson": self._extract_moral_lesson(content, context.age),
            "educational_elements": self._extract_educational_elements(content, theme),
            "emotional_tags": self._extract_emotional_tags(content),
            "audio_cues": self._extract_audio_cues(content),
        }
        story_data["personalization_score"] = self._calculate_personalization_score(
            story_data, context)
        return story_data

    def _extract_title(self, raw_content: str, context: StoryContext) -> str:
        match = re.search(r"Title:\s*(.*)", raw_content, re.IGNORECASE)
        return match.group(1).strip() if match else f"Adventure of {context.child_name}"

    def _clean_content(self, raw_content: str) -> str:
        content = re.sub(r"Title:\s*.*\n*", "", raw_content,
                         count=1, flags=re.IGNORECASE)
        return content.strip()

    def _personalize_names(self, content: str, context: StoryContext) -> str:
        replacements = {"{child_name}": context.child_name}
        if context.friends:
            replacements["{friend1}"] = context.friends[0]
        for placeholder, name in replacements.items():
            content = content.replace(placeholder, name)
        return content

    def _extract_characters(self, content: str, context: StoryContext) -> List[str]:
        characters = {context.child_name}
        for friend in context.friends:
            if friend in content:
                characters.add(friend)
        # Add more logic to find other characters if needed
        return list(characters)

    def _extract_moral_lesson(self, content: str, age: int) -> str:
        # Simplified logic
        from .models import AgeGroup
        age_group_str = AgeGroup.TODDLER.value if age <= 4 else AgeGroup.PRESCHOOL.value if age <= 6 else AgeGroup.EARLY_SCHOOL.value
        lessons = self.moral_lessons.get(age_group_str, [])
        for lesson in lessons:
            if lesson.split()[0] in content:
                return lesson
        return "Enjoying the adventure and learning new things."

    def _extract_educational_elements(self, content: str, theme: StoryTheme) -> List[str]:
        # Simplified logic
        return [f"General concepts about {theme.value}"]

    def _extract_emotional_tags(self, content: str) -> List[str]:
        emotion_words = {"happy": ["happy", "joy"],
                         "courage": ["brave", "courage"]}
        tags = [emotion for emotion, words in emotion_words.items() if any(
            word in content.lower() for word in words)]
        return tags

    def _extract_audio_cues(self, content: str) -> List[str]:
        return re.findall(r"\[(.*?)\]", content)

    def _calculate_personalization_score(self, story_data: Dict, context: StoryContext) -> float:
        score = 0.0
        if context.child_name in story_data["content"]:
            score += 2.0
        if any(friend in story_data["content"] for friend in context.friends):
            score += 1.0
        if any(interest in story_data["content"].lower() for interest in context.interests):
            score += 1.0
        return min(score / 10.0, 1.0)
