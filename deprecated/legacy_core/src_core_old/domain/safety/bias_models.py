"""
Bias Detection Models for AI Safety System
Security Team Implementation
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class BiasType(Enum):
    """Types of bias that can be detected"""
    GENDER = "gender"
    CULTURAL = "cultural"
    SOCIOECONOMIC = "socioeconomic"
    ABILITY = "ability"
    AGE = "age"
    EDUCATIONAL = "educational"
    RACIAL = "racial"
    RELIGIOUS = "religious"


@dataclass
class BiasAnalysisResult:
    """Comprehensive result of bias analysis"""
    has_bias: bool
    overall_bias_score: float
    bias_scores: Dict[str, float]  # category -> score
    contextual_bias: Dict[str, float]  # context-specific bias scores
    detected_patterns: List[str]
    bias_categories: List[str]
    mitigation_suggestions: List[str]
    confidence: float
    analysis_timestamp: str
    risk_level: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'has_bias': self.has_bias,
            'overall_bias_score': self.overall_bias_score,
            'bias_scores': self.bias_scores,
            'contextual_bias': self.contextual_bias,
            'detected_patterns': self.detected_patterns,
            'bias_categories': self.bias_categories,
            'mitigation_suggestions': self.mitigation_suggestions,
            'confidence': self.confidence,
            'analysis_timestamp': self.analysis_timestamp,
            'risk_level': self.risk_level
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ConversationContext:
    """Context information for bias analysis"""
    child_age: int
    child_gender: Optional[str] = None
    child_name: Optional[str] = None
    conversation_history: List[str] = None
    previous_ai_responses: List[str] = None
    interaction_count: int = 0
    session_duration: float = 0.0
    topics_discussed: List[str] = None
    cultural_background: Optional[str] = None
    preferred_language: str = "en"
    accessibility_needs: List[str] = None
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.conversation_history is None:
            self.conversation_history = []
        if self.previous_ai_responses is None:
            self.previous_ai_responses = []
        if self.topics_discussed is None:
            self.topics_discussed = []
        if self.accessibility_needs is None:
            self.accessibility_needs = []


@dataclass
class BiasMitigationSuggestion:
    """Suggestion for mitigating detected bias"""
    bias_type: BiasType
    original_phrase: str
    suggested_replacement: str
    explanation: str
    confidence: float
    priority: str  # "HIGH", "MEDIUM", "LOW"


@dataclass
class BiasDetectionReport:
    """Comprehensive bias detection report"""
    total_responses_analyzed: int
    biased_responses_count: int
    bias_rate_percentage: float
    bias_breakdown_by_category: Dict[str, int]
    risk_level_distribution: Dict[str, int]
    common_bias_patterns: List[str]
    mitigation_recommendations: List[str]
    analysis_period: str
    report_timestamp: str 