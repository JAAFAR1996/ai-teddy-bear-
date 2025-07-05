from dataclasses import dataclass
from typing import List


@dataclass
class LLMRecommendation:
    """LLM-generated recommendation with reasoning"""

    category: str  # "emotional", "cognitive", "social", "learning"
    recommendation: str
    reasoning: str
    expected_impact: str
    implementation_steps: List[str]
    success_metrics: List[str]
    priority_level: int  # 1-5
