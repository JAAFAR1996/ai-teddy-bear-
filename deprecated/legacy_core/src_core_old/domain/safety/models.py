"""
Data models for AI Safety Content Filtering system
Enhanced with Bias Detection Models
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class RiskLevel(Enum):
    """Risk levels for content analysis"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"


class ContentCategory(Enum):
    """Categories of content for filtering"""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    CONVERSATION = "conversation"
    STORY = "story"
    GAME = "game"
    QUESTION = "question"


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
class EmotionalImpactResult:
    """Result of emotional impact analysis"""
    is_positive: bool
    emotion_scores: Dict[str, float]  # joy, sadness, fear, anger, etc.
    overall_sentiment: float  # -1 to 1
    age_appropriateness: float  # 0 to 1
    potential_triggers: List[str]
    recommendations: List[str]


@dataclass
class EducationalValueResult:
    """Result of educational value evaluation"""
    educational_score: float  # 0 to 1
    learning_categories: List[str]
    cognitive_complexity: float  # 0 to 1
    skill_development: List[str]
    age_alignment: float  # 0 to 1


@dataclass
class ToxicityResult:
    """Result of toxicity analysis"""
    toxicity_score: float  # 0 to 1
    toxic_categories: List[str]
    confidence: float
    detected_patterns: List[str]


@dataclass
class ContextAnalysisResult:
    """Result of context analysis"""
    context_safe: bool
    conversation_flow_score: float
    topic_appropriateness: float
    behavioral_concerns: List[str]
    conversation_quality: float


@dataclass
class ContentModification:
    """Suggested modification for unsafe content"""
    original_text: str
    modified_text: str
    modification_type: str
    reason: str
    confidence: float


@dataclass
class ContentAnalysisResult:
    """Comprehensive result of content analysis"""
    is_safe: bool
    overall_risk_level: RiskLevel
    confidence_score: float
    
    # Individual analysis results
    toxicity_result: ToxicityResult
    emotional_impact: EmotionalImpactResult
    educational_value: EducationalValueResult
    context_analysis: ContextAnalysisResult
    
    # Content properties
    age_appropriate: bool
    target_age_range: tuple  # (min_age, max_age)
    content_category: ContentCategory
    
    # Recommendations
    required_modifications: List[ContentModification]
    safety_recommendations: List[str]
    parent_notification_required: bool
    
    # Metadata
    analysis_timestamp: str
    model_versions: Dict[str, str]
    processing_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'is_safe': self.is_safe,
            'overall_risk_level': self.overall_risk_level.value,
            'confidence_score': self.confidence_score,
            'age_appropriate': self.age_appropriate,
            'target_age_range': self.target_age_range,
            'content_category': self.content_category.value,
            'parent_notification_required': self.parent_notification_required,
            'analysis_timestamp': self.analysis_timestamp,
            'processing_time_ms': self.processing_time_ms,
            'safety_recommendations': self.safety_recommendations,
            'toxicity_score': self.toxicity_result.toxicity_score,
            'emotional_positivity': self.emotional_impact.is_positive,
            'educational_score': self.educational_value.educational_score
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class FilterResult:
    """Result of keyword/pattern filtering"""
    blocked: bool
    matched_patterns: List[str]
    risk_score: float
    category: str
    suggestions: List[str]


@dataclass
class SafetyConfig:
    """Configuration for safety filtering"""
    # Age-based settings
    min_child_age: int = 3
    max_child_age: int = 12
    
    # Toxicity thresholds
    toxicity_threshold: float = 0.1
    high_risk_threshold: float = 0.3
    critical_threshold: float = 0.7
    
    # Content filtering
    enable_strict_mode: bool = True
    enable_educational_boost: bool = True
    
    # Model settings
    use_local_models: bool = False
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    
    # Notification settings
    notify_parents_on_risk: bool = True
    log_all_interactions: bool = True
    
    # Performance settings
    max_processing_time_ms: float = 500.0
    enable_async_processing: bool = True
    
    # NEW: Bias detection settings
    enable_bias_detection: bool = True
    bias_threshold: float = 0.6
    bias_detection_method: str = "advanced"  # "advanced" or "fallback"
    
    def validate(self) -> bool:
        """Validate configuration parameters"""
        if self.min_child_age < 1 or self.max_child_age > 18:
            return False
        if not 0 <= self.toxicity_threshold <= 1:
            return False
        if not 0 <= self.high_risk_threshold <= 1:
            return False
        if not 0 <= self.critical_threshold <= 1:
            return False
        if not 0 <= self.bias_threshold <= 1:
            return False
        return True


# NEW: Bias Detection Models

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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'total_responses_analyzed': self.total_responses_analyzed,
            'biased_responses_count': self.biased_responses_count,
            'bias_rate_percentage': self.bias_rate_percentage,
            'bias_breakdown_by_category': self.bias_breakdown_by_category,
            'risk_level_distribution': self.risk_level_distribution,
            'common_bias_patterns': self.common_bias_patterns,
            'mitigation_recommendations': self.mitigation_recommendations,
            'analysis_period': self.analysis_period,
            'report_timestamp': self.report_timestamp
        }


@dataclass
class IntegratedSafetyResult:
    """Combined result of content safety and bias analysis"""
    content_analysis: ContentAnalysisResult
    bias_analysis: Optional[BiasAnalysisResult]
    overall_safety_score: float
    combined_risk_level: RiskLevel
    integrated_recommendations: List[str]
    requires_human_review: bool
    processing_time_total_ms: float
    
    def is_completely_safe(self) -> bool:
        """Check if content is completely safe (both content and bias)"""
        content_safe = self.content_analysis.is_safe
        bias_safe = not self.bias_analysis.has_bias if self.bias_analysis else True
        return content_safe and bias_safe
    
    def get_all_concerns(self) -> List[str]:
        """Get all safety and bias concerns"""
        concerns = []
        
        if not self.content_analysis.is_safe:
            concerns.extend(self.content_analysis.safety_recommendations)
        
        if self.bias_analysis and self.bias_analysis.has_bias:
            concerns.extend([f"Bias detected: {pattern}" for pattern in self.bias_analysis.detected_patterns])
        
        return concerns 