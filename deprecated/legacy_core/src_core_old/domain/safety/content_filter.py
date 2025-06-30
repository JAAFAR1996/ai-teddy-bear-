"""
Advanced Multi-Layer Content Filter for Child Safety
Enterprise-grade AI Safety System
"""

import asyncio
import time
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import json

from .models import (
    ContentAnalysisResult, ToxicityResult, RiskLevel, 
    ContentCategory, ContentModification, SafetyConfig
)
from .keyword_filter import KeywordFilter
from .context_analyzer import ContextAnalyzer
from .emotional_impact_analyzer import EmotionalImpactAnalyzer
from .educational_value_evaluator import EducationalValueEvaluator


class AdvancedContentFilter:
    """
    Enterprise-grade Multi-Layer Content Filtering System
    
    5 Security Layers:
    1. Toxicity Detection (AI-powered)
    2. Age-Appropriate Content Validation
    3. Context Analysis & Behavioral Monitoring
    4. Emotional Impact Assessment
    5. Educational Value Evaluation
    """
    
    def __init__(self, config: Optional[SafetyConfig] = None):
        self.config = config or SafetyConfig()
        self._validate_config()
        
        # Initialize all security layers
        self.toxicity_classifier = self._initialize_toxicity_model()
        self.child_safety_model = self._initialize_child_safety_model()
        self.keyword_filter = KeywordFilter()
        self.context_analyzer = ContextAnalyzer()
        self.emotional_analyzer = EmotionalImpactAnalyzer()
        self.educational_evaluator = EducationalValueEvaluator()
        
        # Performance monitoring
        self.performance_metrics = {
            'total_requests': 0,
            'blocked_requests': 0,
            'avg_processing_time': 0.0,
            'high_risk_detections': 0
        }
        
    def _validate_config(self) -> None:
        """Validate safety configuration"""
        if not self.config.validate():
            raise ValueError("Invalid safety configuration")
    
    def _initialize_toxicity_model(self):
        """Initialize toxicity detection model"""
        # Simplified toxicity model for demonstration
        return {
            "toxic_patterns": [
                "hate", "violence", "abuse", "threat", "harmful",
                "dangerous", "inappropriate", "explicit", "adult"
            ],
            "severity_weights": {
                "hate": 0.9,
                "violence": 0.8,
                "abuse": 0.9,
                "threat": 0.7,
                "harmful": 0.6
            }
        }
    
    def _initialize_child_safety_model(self):
        """Initialize child-specific safety model"""
        return {
            "age_restrictions": {
                3: {"forbidden": ["scary", "violence", "adult"], "complexity": 0.2},
                4: {"forbidden": ["violence", "adult"], "complexity": 0.3},
                5: {"forbidden": ["adult"], "complexity": 0.4},
                6: {"forbidden": [], "complexity": 0.5},
                7: {"forbidden": [], "complexity": 0.6},
                8: {"forbidden": [], "complexity": 0.7}
            },
            "privacy_protection": [
                "personal information", "address", "phone", "password",
                "real name", "location", "school name", "parent work"
            ]
        }
    
    async def analyze_content(
        self, 
        text: str, 
        child_age: int,
        conversation_history: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ) -> ContentAnalysisResult:
        """
        Comprehensive content analysis with 5-layer security
        
        Args:
            text: Content to analyze
            child_age: Age of the child (3-12)
            conversation_history: Previous conversation context
            session_id: Session identifier for tracking
            
        Returns:
            ContentAnalysisResult: Comprehensive analysis result
        """
        start_time = time.time()
        self.performance_metrics['total_requests'] += 1
        
        try:
            # Layer 1: Toxicity Detection
            toxicity_result = await self._check_toxicity(text)
            
            # Layer 2: Age-Appropriate Content  
            age_appropriate = await self._check_age_appropriateness(text, child_age)
            
            # Layer 3: Context Analysis
            context_result = await self.context_analyzer.analyze(
                text, conversation_history or [], child_age
            )
            
            # Layer 4: Emotional Impact Assessment
            emotional_result = await self.emotional_analyzer.analyze_emotional_impact(
                text, child_age, conversation_history
            )
            
            # Layer 5: Educational Value Evaluation
            educational_result = await self.educational_evaluator.evaluate_educational_value(
                text, child_age, conversation_history
            )
            
            # Combine all analysis results
            analysis_result = await self._combine_analysis_results(
                text, child_age, toxicity_result, age_appropriate,
                context_result, emotional_result, educational_result
            )
            
            # Update performance metrics
            processing_time = (time.time() - start_time) * 1000
            self._update_metrics(processing_time, analysis_result)
            
            # Log if high risk detected
            if analysis_result.overall_risk_level in [RiskLevel.HIGH_RISK, RiskLevel.CRITICAL]:
                await self._log_high_risk_detection(text, analysis_result, session_id)
            
            return analysis_result
            
        except Exception as e:
            # Fail-safe: Block content if analysis fails
            return self._create_emergency_block_result(text, str(e))
    
    async def _check_toxicity(self, text: str) -> ToxicityResult:
        """Layer 1: Advanced toxicity detection"""
        text_lower = text.lower()
        toxic_categories = []
        confidence_scores = []
        detected_patterns = []
        
        # Check against toxicity patterns
        for pattern, weight in self.toxicity_classifier["severity_weights"].items():
            if pattern in text_lower:
                toxic_categories.append(pattern)
                confidence_scores.append(weight)
                detected_patterns.append(f"toxic_pattern_{pattern}")
        
        # Calculate overall toxicity score
        toxicity_score = max(confidence_scores) if confidence_scores else 0.0
        
        # Apply keyword filter for additional checks
        keyword_result = self.keyword_filter.filter_content(text, 6)  # Default age for toxicity
        if keyword_result.blocked:
            toxicity_score = max(toxicity_score, keyword_result.risk_score)
            detected_patterns.extend(keyword_result.matched_patterns)
        
        confidence = min(1.0, len(detected_patterns) * 0.3 + 0.4)
        
        return ToxicityResult(
            toxicity_score=toxicity_score,
            toxic_categories=toxic_categories,
            confidence=confidence,
            detected_patterns=detected_patterns
        )
    
    async def _check_age_appropriateness(self, text: str, child_age: int) -> bool:
        """Layer 2: Age-appropriate content validation"""
        age_config = self.child_safety_model["age_restrictions"].get(
            child_age, self.child_safety_model["age_restrictions"][6]
        )
        
        text_lower = text.lower()
        
        # Check forbidden content for age
        forbidden_content = age_config["forbidden"]
        for forbidden in forbidden_content:
            if forbidden in text_lower:
                return False
        
        # Check privacy protection patterns
        for privacy_pattern in self.child_safety_model["privacy_protection"]:
            if privacy_pattern in text_lower:
                return False
        
        # Check content complexity
        complexity_score = self._calculate_content_complexity(text)
        max_complexity = age_config["complexity"]
        
        return complexity_score <= max_complexity
    
    def _calculate_content_complexity(self, text: str) -> float:
        """Calculate content complexity score"""
        # Simple complexity calculation
        words = text.split()
        
        # Factors affecting complexity
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        sentence_count = text.count('.') + text.count('!') + text.count('?') + 1
        
        # Complex words indicator
        complex_words = [word for word in words if len(word) > 6]
        complexity_ratio = len(complex_words) / len(words) if words else 0
        
        # Calculate complexity score (0-1)
        complexity = min(1.0, (avg_word_length / 10 + complexity_ratio + sentence_count / 10) / 3)
        
        return complexity
    
    async def _combine_analysis_results(
        self, text: str, child_age: int, toxicity_result, age_appropriate,
        context_result, emotional_result, educational_result
    ) -> ContentAnalysisResult:
        """Combine all layer results into final analysis"""
        
        # Determine overall safety
        is_safe = all([
            toxicity_result.toxicity_score < self.config.toxicity_threshold,
            age_appropriate,
            context_result.context_safe,
            emotional_result.is_positive or emotional_result.overall_sentiment > -0.3
        ])
        
        # Calculate overall risk level
        risk_level = self._calculate_risk_level(toxicity_result, context_result, emotional_result)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            toxicity_result, context_result, emotional_result
        )
        
        # Determine content category
        content_category = self._determine_content_category(text, educational_result)
        
        # Generate modifications if needed
        modifications = await self._suggest_modifications(
            text, toxicity_result, emotional_result, child_age
        )
        
        # Generate safety recommendations
        safety_recommendations = self._generate_safety_recommendations(
            toxicity_result, context_result, emotional_result, child_age
        )
        
        # Determine if parent notification is required
        parent_notification = self._requires_parent_notification(risk_level, child_age)
        
        return ContentAnalysisResult(
            is_safe=is_safe,
            overall_risk_level=risk_level,
            confidence_score=confidence_score,
            toxicity_result=toxicity_result,
            emotional_impact=emotional_result,
            educational_value=educational_result,
            context_analysis=context_result,
            age_appropriate=age_appropriate,
            target_age_range=self._calculate_target_age_range(text, child_age),
            content_category=content_category,
            required_modifications=modifications,
            safety_recommendations=safety_recommendations,
            parent_notification_required=parent_notification,
            analysis_timestamp=datetime.now().isoformat(),
            model_versions=self._get_model_versions(),
            processing_time_ms=0.0  # Will be updated in main function
        )
    
    def _calculate_risk_level(self, toxicity_result, context_result, emotional_result) -> RiskLevel:
        """Calculate overall risk level"""
        toxicity_score = toxicity_result.toxicity_score
        
        if toxicity_score >= self.config.critical_threshold:
            return RiskLevel.CRITICAL
        elif toxicity_score >= self.config.high_risk_threshold:
            return RiskLevel.HIGH_RISK
        elif not context_result.context_safe:
            return RiskLevel.MEDIUM_RISK
        elif not emotional_result.is_positive and emotional_result.overall_sentiment < -0.5:
            return RiskLevel.MEDIUM_RISK
        elif toxicity_score > 0.1:
            return RiskLevel.LOW_RISK
        else:
            return RiskLevel.SAFE
    
    def _calculate_confidence(self, toxicity_result, context_result, emotional_result) -> float:
        """Calculate overall confidence in analysis"""
        confidence_factors = [
            toxicity_result.confidence,
            context_result.conversation_flow_score,
            abs(emotional_result.overall_sentiment)  # Higher sentiment certainty = higher confidence
        ]
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _determine_content_category(self, text: str, educational_result) -> ContentCategory:
        """Determine content category"""
        text_lower = text.lower()
        
        # Educational indicators
        if educational_result.educational_score > 0.5:
            return ContentCategory.EDUCATIONAL
        
        # Story indicators
        story_keywords = ["story", "once upon", "princess", "dragon", "adventure"]
        if any(keyword in text_lower for keyword in story_keywords):
            return ContentCategory.STORY
        
        # Game indicators
        game_keywords = ["play", "game", "toy", "puzzle", "fun"]
        if any(keyword in text_lower for keyword in game_keywords):
            return ContentCategory.GAME
        
        # Question indicators
        if "?" in text or any(q in text_lower for q in ["what", "how", "why", "where", "when"]):
            return ContentCategory.QUESTION
        
        # Default to conversation
        return ContentCategory.CONVERSATION
    
    async def _suggest_modifications(self, text: str, toxicity_result, 
                                   emotional_result, child_age: int) -> List[ContentModification]:
        """Suggest content modifications for safety"""
        modifications = []
        
        # Handle toxicity
        if toxicity_result.toxicity_score > self.config.toxicity_threshold:
            for pattern in toxicity_result.detected_patterns:
                safe_alternative = self._get_safe_alternative(pattern, child_age)
                if safe_alternative:
                    modifications.append(ContentModification(
                        original_text=pattern,
                        modified_text=safe_alternative,
                        modification_type="toxicity_replacement",
                        reason=f"Replaced toxic content: {pattern}",
                        confidence=0.8
                    ))
        
        # Handle negative emotions
        if not emotional_result.is_positive and emotional_result.overall_sentiment < -0.3:
            positive_alternative = self._generate_positive_alternative(text, child_age)
            if positive_alternative:
                modifications.append(ContentModification(
                    original_text=text,
                    modified_text=positive_alternative,
                    modification_type="emotional_enhancement",
                    reason="Enhanced emotional positivity",
                    confidence=0.7
                ))
        
        return modifications
    
    def _get_safe_alternative(self, unsafe_pattern: str, child_age: int) -> Optional[str]:
        """Get safe alternative for unsafe pattern"""
        safe_alternatives = {
            "scary": "interesting" if child_age > 5 else "fun",
            "bad": "not so good",
            "hate": "don't like",
            "stupid": "silly",
            "angry": "upset",
            "hurt": "not feeling well"
        }
        
        return safe_alternatives.get(unsafe_pattern.lower())
    
    def _generate_positive_alternative(self, text: str, child_age: int) -> str:
        """Generate more positive version of text"""
        # Simple positive enhancement
        positive_words = {
            "sad": "a little down, but that's okay",
            "bad": "not perfect, but we can make it better",
            "difficult": "challenging, which helps us learn",
            "wrong": "different, and that's how we discover new things"
        }
        
        enhanced_text = text
        for negative, positive in positive_words.items():
            enhanced_text = enhanced_text.replace(negative, positive)
        
        return enhanced_text
    
    def _generate_safety_recommendations(self, toxicity_result, context_result, 
                                       emotional_result, child_age: int) -> List[str]:
        """Generate safety recommendations"""
        recommendations = []
        
        if toxicity_result.toxicity_score > 0.3:
            recommendations.append("High toxicity detected - content review recommended")
        
        if not context_result.context_safe:
            recommendations.append("Context safety concern - monitor conversation closely")
        
        if not emotional_result.is_positive:
            recommendations.append("Negative emotional impact - add positive reinforcement")
        
        if child_age <= 5 and toxicity_result.toxicity_score > 0.1:
            recommendations.append("Extra caution needed for young child")
        
        return recommendations
    
    def _requires_parent_notification(self, risk_level: RiskLevel, child_age: int) -> bool:
        """Determine if parent notification is required"""
        if risk_level in [RiskLevel.HIGH_RISK, RiskLevel.CRITICAL]:
            return True
        
        if child_age <= 5 and risk_level == RiskLevel.MEDIUM_RISK:
            return True
        
        return False
    
    def _calculate_target_age_range(self, text: str, child_age: int) -> tuple:
        """Calculate appropriate age range for content"""
        complexity = self._calculate_content_complexity(text)
        
        if complexity <= 0.3:
            return (3, 6)
        elif complexity <= 0.5:
            return (4, 8)
        elif complexity <= 0.7:
            return (6, 10)
        else:
            return (8, 12)
    
    def _get_model_versions(self) -> Dict[str, str]:
        """Get versions of all models used"""
        return {
            "toxicity_classifier": "1.0.0",
            "keyword_filter": "1.0.0",
            "context_analyzer": "1.0.0",
            "emotional_analyzer": "1.0.0",
            "educational_evaluator": "1.0.0"
        }
    
    def _update_metrics(self, processing_time: float, result: ContentAnalysisResult) -> None:
        """Update performance metrics"""
        self.performance_metrics['avg_processing_time'] = (
            self.performance_metrics['avg_processing_time'] + processing_time
        ) / 2
        
        if not result.is_safe:
            self.performance_metrics['blocked_requests'] += 1
        
        if result.overall_risk_level in [RiskLevel.HIGH_RISK, RiskLevel.CRITICAL]:
            self.performance_metrics['high_risk_detections'] += 1
    
    async def _log_high_risk_detection(self, text: str, result: ContentAnalysisResult, 
                                     session_id: Optional[str]) -> None:
        """Log high-risk content detection"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "risk_level": result.overall_risk_level.value,
            "toxicity_score": result.toxicity_result.toxicity_score,
            "content_hash": hashlib.sha256(text.encode()).hexdigest()[:16],
            "detected_patterns": result.toxicity_result.detected_patterns
        }
        
        # In production, this would go to a secure logging system
        print(f"HIGH RISK DETECTION: {json.dumps(log_entry)}")
    
    def _create_emergency_block_result(self, text: str, error: str) -> ContentAnalysisResult:
        """Create emergency block result when analysis fails"""
        from .models import ToxicityResult, EmotionalImpactResult, EducationalValueResult, ContextAnalysisResult
        
        return ContentAnalysisResult(
            is_safe=False,
            overall_risk_level=RiskLevel.CRITICAL,
            confidence_score=0.0,
            toxicity_result=ToxicityResult(1.0, ["analysis_error"], 1.0, [error]),
            emotional_impact=EmotionalImpactResult(False, {}, -1.0, 0.0, [error], []),
            educational_value=EducationalValueResult(0.0, [], 0.0, [], 0.0),
            context_analysis=ContextAnalysisResult(False, 0.0, 0.0, [error], 0.0),
            age_appropriate=False,
            target_age_range=(0, 0),
            content_category=ContentCategory.CONVERSATION,
            required_modifications=[],
            safety_recommendations=["Content blocked due to analysis error"],
            parent_notification_required=True,
            analysis_timestamp=datetime.now().isoformat(),
            model_versions=self._get_model_versions(),
            processing_time_ms=0.0
        )
    
    def get_performance_metrics(self) -> Dict[str, any]:
        """Get current performance metrics"""
        return self.performance_metrics.copy()
    
    async def batch_analyze(self, texts: List[str], child_age: int) -> List[ContentAnalysisResult]:
        """Analyze multiple texts in batch for better performance"""
        tasks = [
            self.analyze_content(text, child_age) 
            for text in texts
        ]
        
        return await asyncio.gather(*tasks)
    
    def update_safety_config(self, new_config: SafetyConfig) -> None:
        """Update safety configuration"""
        new_config.validate()
        self.config = new_config 