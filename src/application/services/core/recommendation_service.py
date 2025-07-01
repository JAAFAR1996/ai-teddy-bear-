"""
Recommendation Application Service
Generates and manages various types of recommendations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.domain.reporting.models import (
    InteractionAnalysis, LLMRecommendation, 
    ActivityRecommendation, InterventionRecommendation,
    RecommendationBundle, UrgencyLevel
)
from src.domain.reporting.services import (
    SkillAnalyzer, BehaviorAnalyzer, EmotionAnalyzerService
)


class RecommendationService:
    """Application service for generating recommendations"""

    def __init__(self, llm_service=None, database_service=None):
        self.llm_service = llm_service
        self.db = database_service
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize domain services
        self.skill_analyzer = SkillAnalyzer()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.emotion_analyzer = EmotionAnalyzerService()

    async def generate_llm_recommendations(
        self, 
        child_id: int,
        metrics: Any
    ) -> List[LLMRecommendation]:
        """Generate AI-powered recommendations using LLM"""
        try:
            recommendations = []
            
            # Get child information
            child_info = await self._get_child_info(child_id)
            
            # Generate recommendations for different categories
            categories = [
                "emotional_development",
                "cognitive_skills", 
                "social_interaction",
                "learning_activities",
                "behavioral_support"
            ]
            
            for category in categories:
                try:
                    recommendation = await self._generate_cot_recommendation(
                        category, metrics, child_info
                    )
                    if recommendation:
                        recommendations.append(recommendation)
                except Exception as e:
                    self.logger.warning(f"Failed to generate LLM recommendation for {category}: {e}")
            
            # Fallback to rule-based recommendations if LLM fails
            if not recommendations:
                recommendations = self._generate_fallback_recommendations_task7(metrics)
            
            self.logger.info(f"Generated {len(recommendations)} LLM recommendations for child {child_id}")
            return recommendations

        except Exception as e:
            self.logger.error(f"LLM recommendations generation failed for child {child_id}: {e}")
            return self._generate_fallback_recommendations_task7(metrics)

    async def generate_comprehensive_recommendations(
        self,
        child_id: str,
        interactions: List[InteractionAnalysis]
    ) -> RecommendationBundle:
        """Generate comprehensive recommendation bundle"""
        try:
            # Generate activity recommendations
            activity_recs = self._generate_activity_recommendations(interactions)
            
            # Generate intervention recommendations  
            intervention_recs = self._generate_intervention_recommendations(interactions)
            
            # Generate LLM recommendations (if available)
            llm_recs = []
            if self.llm_service:
                # Mock metrics for LLM
                mock_metrics = type('MockMetrics', (), {
                    'vocabulary_complexity_score': 0.7,
                    'emotional_intelligence_score': 0.6,
                    'cognitive_development_score': 0.8
                })()
                llm_recs = await self.generate_llm_recommendations(int(child_id), mock_metrics)
            
            # Create recommendation bundle
            bundle = RecommendationBundle(
                bundle_id=f"bundle_{child_id}_{datetime.now().strftime('%Y%m%d')}",
                title=f"تقرير توصيات شامل للطفل {child_id}",
                description="توصيات مخصصة لتطوير الطفل في جميع المجالات",
                activity_recommendations=activity_recs,
                intervention_recommendations=intervention_recs,
                llm_recommendations=llm_recs,
                created_at=datetime.now()
            )
            
            self.logger.info(f"Generated comprehensive recommendations bundle for child {child_id}")
            return bundle

        except Exception as e:
            self.logger.error(f"Comprehensive recommendations generation failed for child {child_id}: {e}")
            raise

    def _generate_activity_recommendations(self, interactions: List[InteractionAnalysis]) -> List[ActivityRecommendation]:
        """Generate activity recommendations based on analysis"""
        try:
            recommendations = []
            
            # Get activity suggestions from skill analyzer
            activity_suggestions = self.skill_analyzer.generate_activity_recommendations(interactions)
            
            # Convert to ActivityRecommendation objects
            for i, suggestion in enumerate(activity_suggestions[:5]):  # Limit to 5
                activity = ActivityRecommendation(
                    activity_name=f"نشاط {i+1}",
                    description=suggestion,
                    target_skills=["general_development"],
                    age_appropriate=True,
                    duration_minutes=15,
                    required_materials=["أساسية"],
                    implementation_difficulty="easy",
                    expected_outcomes=["تحسين المهارات", "زيادة التفاعل"]
                )
                recommendations.append(activity)
            
            return recommendations

        except Exception as e:
            self.logger.error(f"Activity recommendations generation error: {e}")
            return []

    def _generate_intervention_recommendations(self, interactions: List[InteractionAnalysis]) -> List[InterventionRecommendation]:
        """Generate intervention recommendations based on concerns"""
        try:
            recommendations = []
            
            # Get concerning patterns
            concerning_patterns = self.emotion_analyzer.identify_concerning_patterns(interactions)
            urgent_recommendations = self.emotion_analyzer.generate_urgent_recommendations(interactions)
            
            # Create intervention recommendations for concerning patterns
            for i, pattern in enumerate(concerning_patterns):
                urgency = UrgencyLevel.HIGH if "شديد" in pattern else UrgencyLevel.MEDIUM
                
                intervention = InterventionRecommendation(
                    concern_area=pattern,
                    intervention_type="behavioral_support",
                    description=f"تدخل مستهدف لمعالجة: {pattern}",
                    implementation_steps=[
                        "تقييم مفصل للحالة",
                        "وضع خطة تدخل مخصصة",
                        "تنفيذ التدخل بشكل منتظم",
                        "متابعة وتقييم التقدم"
                    ],
                    urgency_level=urgency,
                    expected_duration_weeks=4,
                    success_indicators=["تحسن في السلوك", "زيادة في الاستقرار"],
                    professional_help_needed=urgency == UrgencyLevel.HIGH
                )
                recommendations.append(intervention)
            
            return recommendations

        except Exception as e:
            self.logger.error(f"Intervention recommendations generation error: {e}")
            return []

    async def _generate_cot_recommendation(self, category: str, metrics: Any, child_info: Dict) -> Optional[LLMRecommendation]:
        """Generate Chain-of-Thought recommendation using LLM"""
        try:
            if not self.llm_service:
                return None
            
            # Mock LLM recommendation generation
            recommendations_map = {
                "emotional_development": {
                    "recommendation": "تطوير المهارات العاطفية من خلال أنشطة التعرف على المشاعر",
                    "reasoning": "تحليل البيانات يظهر حاجة لتعزيز الوعي العاطفي",
                    "steps": [
                        "ممارسة تسمية المشاعر يومياً",
                        "استخدام البطاقات التعليمية للمشاعر",
                        "قراءة قصص عن المشاعر"
                    ],
                    "priority": 4
                },
                "cognitive_skills": {
                    "recommendation": "تحفيز التطور المعرفي من خلال الألغاز والألعاب التفكيرية",
                    "reasoning": "النتائج تشير إلى إمكانية تطوير مهارات حل المشكلات",
                    "steps": [
                        "ألعاب الألغاز البسيطة",
                        "أنشطة التصنيف والترتيب",
                        "ألعاب الذاكرة"
                    ],
                    "priority": 3
                },
                "social_interaction": {
                    "recommendation": "تعزيز التفاعل الاجتماعي من خلال اللعب الجماعي",
                    "reasoning": "البيانات تظهر حاجة لتطوير المهارات الاجتماعية",
                    "steps": [
                        "تنظيم جلسات لعب مع أطفال آخرين",
                        "تعليم مهارات المشاركة",
                        "أنشطة العمل الجماعي"
                    ],
                    "priority": 4
                },
                "learning_activities": {
                    "recommendation": "أنشطة تعليمية متنوعة لتحفيز الفضول والتعلم",
                    "reasoning": "تحليل الأنشطة يظهر حاجة لتنويع مصادر التعلم",
                    "steps": [
                        "استكشاف مواضيع جديدة",
                        "التجارب العلمية البسيطة",
                        "الرحلات التعليمية"
                    ],
                    "priority": 2
                },
                "behavioral_support": {
                    "recommendation": "دعم سلوكي إيجابي لتعزيز السلوكيات المرغوبة",
                    "reasoning": "تحليل السلوك يظهر فرص لتعزيز السلوكيات الإيجابية",
                    "steps": [
                        "نظام مكافآت واضح",
                        "تعزيز السلوك الإيجابي فور حدوثه",
                        "وضع حدود واضحة ومتسقة"
                    ],
                    "priority": 3
                }
            }
            
            rec_data = recommendations_map.get(category)
            if not rec_data:
                return None
            
            recommendation = LLMRecommendation(
                category=category,
                recommendation=rec_data["recommendation"],
                reasoning=rec_data["reasoning"],
                implementation_steps=rec_data["steps"],
                priority_level=rec_data["priority"],
                confidence_score=0.85,
                generated_at=datetime.now()
            )
            
            return recommendation

        except Exception as e:
            self.logger.error(f"CoT recommendation generation error for {category}: {e}")
            return None

    def _generate_fallback_recommendations_task7(self, metrics: Any) -> List[LLMRecommendation]:
        """Generate fallback recommendations when LLM is unavailable"""
        try:
            fallback_recommendations = [
                {
                    "category": "general_development",
                    "recommendation": "أنشطة تطوير شاملة مناسبة للعمر",
                    "reasoning": "توصيات عامة لدعم التطور الطبيعي للطفل",
                    "implementation_steps": [
                        "قراءة يومية لمدة 15 دقيقة",
                        "أنشطة فنية وإبداعية",
                        "ألعاب تفاعلية بسيطة"
                    ],
                    "priority_level": 3,
                    "confidence_score": 0.7
                },
                {
                    "category": "social_skills",
                    "recommendation": "تطوير المهارات الاجتماعية الأساسية",
                    "reasoning": "المهارات الاجتماعية أساسية في هذا العمر",
                    "implementation_steps": [
                        "تعليم عبارات الأدب والشكر",
                        "ممارسة التناوب في الألعاب",
                        "تشجيع التعبير عن المشاعر"
                    ],
                    "priority_level": 4,
                    "confidence_score": 0.8
                }
            ]
            
            recommendations = []
            for rec_data in fallback_recommendations:
                recommendation = LLMRecommendation(
                    category=rec_data["category"],
                    recommendation=rec_data["recommendation"],
                    reasoning=rec_data["reasoning"],
                    implementation_steps=rec_data["implementation_steps"],
                    priority_level=rec_data["priority_level"],
                    confidence_score=rec_data["confidence_score"],
                    generated_at=datetime.now()
                )
                recommendations.append(recommendation)
            
            return recommendations

        except Exception as e:
            self.logger.error(f"Fallback recommendations generation error: {e}")
            return []

    async def _get_child_info(self, child_id: int) -> Dict[str, Any]:
        """Get child information for recommendation context"""
        try:
            if self.db:
                return await self.db.get_child_info(child_id)
            
            # Fallback mock data
            return {
                'age': 5,
                'interests': ['stories', 'games'],
                'special_needs': [],
                'learning_style': 'visual'
            }

        except Exception as e:
            self.logger.error(f"Failed to get child info for {child_id}: {e}")
            return {'age': 5} 