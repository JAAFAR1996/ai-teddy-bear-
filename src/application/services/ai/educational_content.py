"""
Educational Content Provider
Manages educational content for children
"""

import random
from typing import Any, Dict, List

import structlog
from opentelemetry import trace

# from src.application.services.core.service_registry import ServiceBase
from src.infrastructure.observability import trace_async

logger = structlog.get_logger()


class EducationalContentProvider(ServiceBase):
    """
    Provides age-appropriate educational content
    """

    def __init__(self, registry, config: Dict):
        super().__init__(registry, config)
        self._content_database = self._load_content_database()
        self._tracer = trace.get_tracer(__name__)

    async def initialize(self) -> None:
        """Initialize the content provider"""
        self.logger.info("Initializing educational content provider")
        self._state = self.ServiceState.READY

    async def shutdown(self) -> None:
        """Shutdown the provider"""
        self._state = self.ServiceState.STOPPED

    async def health_check(self) -> Dict:
        """Health check"""
        return {
            "healthy": self._state == self.ServiceState.READY,
            "service": "educational_content",
        }

    @trace_async("get_educational_content")
    async def get_content(
        self, topic: str, age: int, language: str = "en"
    ) -> Dict[str, Any]:
        """Get educational content for a topic"""
        # Determine age group
        age_group = self._get_age_group(age)

        # Get content for topic
        topic_content = self._content_database.get(topic, {})

        # Filter by age appropriateness
        facts = topic_content.get("facts", {}).get(age_group, [])
        activities = topic_content.get("activities", {}).get(age_group, [])

        # Translate if needed
        if language == "ar":
            facts = self._translate_to_arabic(facts, topic)
            activities = self._translate_to_arabic_activities(activities, topic)

        return {
            "topic": topic,
            "age_group": age_group,
            "facts": random.sample(facts, min(3, len(facts))) if facts else [],
            "activities": (
                random.sample(activities, min(2, len(activities))) if activities else []
            ),
            "learning_objectives": self._get_learning_objectives(topic, age_group),
            "keywords": self._get_topic_keywords(topic, language),
            "next_topics": self._suggest_related_topics(topic),
        }

    def _get_age_group(self, age: int) -> str:
        """Categorize age into groups"""
        if age < 4:
            return "toddler"
        elif age < 7:
            return "preschool"
        elif age < 10:
            return "elementary"
        else:
            return "advanced"

    def _load_content_database(self) -> Dict[str, Dict]:
        """Load educational content database"""
        return {
            "numbers": {
                "facts": {
                    "toddler": [
                        "One is the smallest counting number!",
                        "You have two hands!",
                        "A triangle has three sides!",
                    ],
                    "preschool": [
                        "Zero means nothing at all!",
                        "Ten fingers help us count!",
                        "Even numbers can be shared equally!",
                    ],
                    "elementary": [
                        "Numbers go on forever!",
                        "Prime numbers only divide by 1 and themselves!",
                        "The number Pi helps us measure circles!",
                    ],
                },
                "activities": {
                    "toddler": [
                        "Let's count your toys!",
                        "Show me three jumps!",
                        "Clap your hands five times!",
                    ],
                    "preschool": [
                        "Let's play a counting game!",
                        "Find groups of the same number!",
                        "Make patterns with numbers!",
                    ],
                    "elementary": [
                        "Let's solve a number puzzle!",
                        "Create your own math problem!",
                        "Discover number patterns!",
                    ],
                },
            },
            "animals": {
                "facts": {
                    "toddler": [
                        "Cats say meow!",
                        "Dogs wag their tails when happy!",
                        "Birds can fly!",
                    ],
                    "preschool": [
                        "Elephants are the biggest land animals!",
                        "Fish breathe underwater with gills!",
                        "Some animals sleep all winter!",
                    ],
                    "elementary": [
                        "Dolphins are mammals, not fish!",
                        "Octopuses have three hearts!",
                        "Penguins can't fly but swim very fast!",
                    ],
                },
                "activities": {
                    "toddler": [
                        "Make animal sounds!",
                        "Move like your favorite animal!",
                        "Draw a simple animal!",
                    ],
                    "preschool": [
                        "Let's play animal charades!",
                        "Sort animals by where they live!",
                        "Create an animal story!",
                    ],
                    "elementary": [
                        "Research your favorite animal!",
                        "Design a new animal habitat!",
                        "Learn about endangered species!",
                    ],
                },
            },
            "colors": {
                "facts": {
                    "toddler": [
                        "The sky is blue!",
                        "Grass is green!",
                        "The sun is yellow!",
                    ],
                    "preschool": [
                        "Mixing red and blue makes purple!",
                        "Rainbows have seven colors!",
                        "White light contains all colors!",
                    ],
                    "elementary": [
                        "Colors are different wavelengths of light!",
                        "Some animals see colors we can't!",
                        "Primary colors make all other colors!",
                    ],
                },
                "activities": {
                    "toddler": [
                        "Find something red!",
                        "Point to blue things!",
                        "What color is this?",
                    ],
                    "preschool": [
                        "Let's mix colors!",
                        "Sort objects by color!",
                        "Draw a colorful picture!",
                    ],
                    "elementary": [
                        "Create a color wheel!",
                        "Experiment with color mixing!",
                        "Learn about color in nature!",
                    ],
                },
            },
        }

    def _translate_to_arabic(self, facts: List[str], topic: str) -> List[str]:
        """Translate facts to Arabic (simplified)"""
        # In production, use a real translation service
        arabic_facts = {
            "numbers": [
                "الواحد هو أصغر رقم للعد!",
                "لديك يدان اثنتان!",
                "المثلث له ثلاثة أضلاع!",
            ],
            "animals": [
                "القطط تقول مياو!",
                "الكلاب تهز ذيولها عندما تكون سعيدة!",
                "الطيور تستطيع الطيران!",
            ],
            "colors": ["السماء زرقاء!", "العشب أخضر!", "الشمس صفراء!"],
        }
        return arabic_facts.get(topic, facts)

    def _translate_to_arabic_activities(
        self, activities: List[str], topic: str
    ) -> List[str]:
        """Translate activities to Arabic (simplified)"""
        arabic_activities = {
            "numbers": ["هيا نعد ألعابك!", "أرني ثلاث قفزات!", "صفق بيديك خمس مرات!"],
            "animals": [
                "اصنع أصوات الحيوانات!",
                "تحرك مثل حيوانك المفضل!",
                "ارسم حيواناً بسيطاً!",
            ],
            "colors": ["ابحث عن شيء أحمر!", "أشر إلى الأشياء الزرقاء!", "ما لون هذا؟"],
        }
        return arabic_activities.get(topic, activities)

    def _get_learning_objectives(self, topic: str, age_group: str) -> List[str]:
        """Get learning objectives for topic and age"""
        objectives = {
            "numbers": {
                "toddler": [
                    "Recognize numbers 1-5",
                    "Count objects",
                    "Understand quantity",
                ],
                "preschool": ["Count to 20", "Understand zero", "Simple addition"],
                "elementary": [
                    "Basic arithmetic",
                    "Number patterns",
                    "Problem solving",
                ],
            },
            "animals": {
                "toddler": [
                    "Identify common animals",
                    "Animal sounds",
                    "Basic characteristics",
                ],
                "preschool": ["Animal habitats", "Animal groups", "Life cycles"],
                "elementary": ["Ecosystems", "Adaptations", "Conservation"],
            },
            "colors": {
                "toddler": ["Identify basic colors", "Color matching", "Color names"],
                "preschool": ["Color mixing", "Shades and tints", "Color in nature"],
                "elementary": ["Color theory", "Light and color", "Art applications"],
            },
        }
        return objectives.get(topic, {}).get(age_group, [])

    def _get_topic_keywords(self, topic: str, language: str) -> List[str]:
        """Get keywords for a topic"""
        keywords = {
            "numbers": ["count", "math", "quantity", "numerals"],
            "animals": ["nature", "wildlife", "pets", "habitat"],
            "colors": ["art", "rainbow", "paint", "light"],
        }

        if language == "ar":
            arabic_keywords = {
                "numbers": ["عد", "رياضيات", "كمية", "أرقام"],
                "animals": ["طبيعة", "حياة برية", "حيوانات أليفة", "موطن"],
                "colors": ["فن", "قوس قزح", "طلاء", "ضوء"],
            }
            return arabic_keywords.get(topic, keywords.get(topic, []))

        return keywords.get(topic, [])

    def _suggest_related_topics(self, topic: str) -> List[str]:
        """Suggest related topics for continued learning"""
        related = {
            "numbers": ["shapes", "patterns", "measurement"],
            "animals": ["plants", "habitats", "food chains"],
            "colors": ["shapes", "art", "nature"],
        }
        return related.get(topic, [])
