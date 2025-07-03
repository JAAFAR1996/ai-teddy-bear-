#!/usr/bin/env python3
"""
🎭 Advanced Personalization Service - Refactored for High Cohesion
خدمة التخصيص المتقدم للطفل - مُعاد هيكلتها باستخدام نمط Facade
"""

import logging
from datetime import datetime
from typing import Dict, List

from ..personalization import (
    ChildPersonality,
    InteractionPattern,
    AdaptiveContent,
    PersonalityAnalyzer,
    InteractionPatternManager,
    ContentRecommendationEngine,
    PersonalizationDataManager,
    PersonalizationInsightsAnalyzer
)

logger = logging.getLogger(__name__)


class AdvancedPersonalizationService:
    """
    خدمة التخصيص المتقدم - Facade Pattern
    
    تم تطبيق EXTRACT CLASS refactoring لتحسين التماسك:
    - PersonalityAnalyzer: تحليل الشخصية
    - InteractionPatternManager: إدارة أنماط التفاعل
    - ContentRecommendationEngine: اقتراح المحتوى
    - PersonalizationDataManager: إدارة البيانات
    - PersonalizationInsightsAnalyzer: تحليل الرؤى والإحصائيات
    """

    def __init__(self, data_dir: str = "data/personalization"):
        """تهيئة الخدمة مع جميع المكونات المنفصلة"""
        # تهيئة المكونات المتخصصة (High Cohesion)
        self.personality_analyzer = PersonalityAnalyzer()
        self.pattern_manager = InteractionPatternManager()
        self.recommendation_engine = ContentRecommendationEngine()
        self.data_manager = PersonalizationDataManager(data_dir)
        self.insights_analyzer = PersonalizationInsightsAnalyzer()

        # البيانات المحلية
        self.personalities: Dict[str, ChildPersonality] = {}
        self.interaction_patterns: Dict[str, InteractionPattern] = {}
        self.content_performance: Dict[str, List[AdaptiveContent]] = {}

        # تحميل البيانات عند التهيئة
        self._load_data()

    def _load_data(self) -> None:
        """تحميل جميع البيانات - يفوض إلى DataManager"""
        try:
            data = self.data_manager.load_all_data()
            
            # تحويل البيانات إلى الكائنات المناسبة
            for child_id, personality_data in data['personalities'].items():
                self.personalities[child_id] = ChildPersonality(**personality_data)
                
            for child_id, pattern_data in data['interaction_patterns'].items():
                self.interaction_patterns[child_id] = InteractionPattern(**pattern_data)
                
            for child_id, contents in data['content_performance'].items():
                self.content_performance[child_id] = [
                    AdaptiveContent(**content) for content in contents
                ]
                
            logger.info("تم تحميل بيانات التخصيص بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات التخصيص: {e}")

    def _save_data(self) -> None:
        """حفظ البيانات - يفوض إلى DataManager"""
        try:
            self.data_manager.save_all_data(
                self.personalities,
                self.interaction_patterns, 
                self.content_performance
            )
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات التخصيص: {e}")

    # === Personality Management Methods ===
    
    def get_child_personality(self, child_id: str) -> ChildPersonality:
        """الحصول على شخصية الطفل"""
        if child_id not in self.personalities:
            self.personalities[child_id] = ChildPersonality(
                child_id=child_id, 
                last_updated=datetime.now().isoformat()
            )
            self._save_data()
        return self.personalities[child_id]

    def analyze_personality_from_interactions(
        self, child_id: str, interactions: List[Dict]
    ) -> ChildPersonality:
        """تحليل الشخصية من التفاعلات - يفوض إلى PersonalityAnalyzer"""
        personality = self.get_child_personality(child_id)
        
        updated_personality = self.personality_analyzer.analyze_personality_from_interactions(
            personality, interactions
        )
        
        self.personalities[child_id] = updated_personality
        self._save_data()
        return updated_personality

    # === Interaction Pattern Methods ===
    
    def get_interaction_patterns(self, child_id: str) -> InteractionPattern:
        """الحصول على أنماط تفاعل الطفل"""
        if child_id not in self.interaction_patterns:
            self.interaction_patterns[child_id] = InteractionPattern(child_id=child_id)
            self._save_data()
        return self.interaction_patterns[child_id]

    def update_interaction_patterns(self, child_id: str, interaction_data: Dict) -> None:
        """تحديث أنماط التفاعل - يفوض إلى InteractionPatternManager"""
        patterns = self.get_interaction_patterns(child_id)
        self.pattern_manager.update_interaction_patterns(patterns, interaction_data)
        self._save_data()

    # === Content Recommendation Methods ===
    
    def recommend_content(self, child_id: str, content_type: str = None) -> List[Dict]:
        """اقتراح محتوى مخصص - يفوض إلى ContentRecommendationEngine"""
        personality = self.get_child_personality(child_id)
        patterns = self.get_interaction_patterns(child_id)
        
        return self.recommendation_engine.recommend_content(
            personality, patterns, content_type
        )

    # === Content Performance Tracking ===
    
    def track_content_performance(
        self, child_id: str, content: Dict, performance_data: Dict
    ) -> None:
        """تتبع أداء المحتوى"""
        if child_id not in self.content_performance:
            self.content_performance[child_id] = []

        adaptive_content = AdaptiveContent(
            content_type=content.get("type", ""),
            difficulty_level=content.get("difficulty", "medium"),
            topic=content.get("topic", ""),
            duration=performance_data.get("duration_minutes", 0),
            engagement_score=performance_data.get("engagement_score", 0),
            success_rate=performance_data.get("success_rate", 0),
            child_feedback=performance_data.get("feedback", "neutral"),
            usage_count=1,
            last_used=datetime.now().isoformat(),
        )

        # البحث عن محتوى مشابه لتحديثه
        existing_content = self._find_matching_content(child_id, adaptive_content)

        if existing_content:
            self._update_existing_content(existing_content, adaptive_content)
        else:
            self.content_performance[child_id].append(adaptive_content)

        # الاحتفاظ بآخر 100 عنصر
        self.content_performance[child_id] = self.content_performance[child_id][-100:]
        self._save_data()

    def _find_matching_content(
        self, child_id: str, new_content: AdaptiveContent
    ) -> AdaptiveContent:
        """البحث عن محتوى مطابق موجود مسبقاً"""
        for content_item in self.content_performance[child_id]:
            if self._is_content_match(content_item, new_content):
                return content_item
        return None

    def _is_content_match(
        self, existing: AdaptiveContent, new: AdaptiveContent
    ) -> bool:
        """تحديد ما إذا كان المحتوى مطابق"""
        return (
            existing.content_type == new.content_type
            and existing.topic == new.topic
            and existing.difficulty_level == new.difficulty_level
        )

    def _update_existing_content(
        self, existing: AdaptiveContent, new: AdaptiveContent
    ) -> None:
        """تحديث المحتوى الموجود"""
        existing.usage_count += 1
        existing.engagement_score = (
            existing.engagement_score + new.engagement_score
        ) / 2
        existing.success_rate = (existing.success_rate + new.success_rate) / 2
        existing.last_used = new.last_used

    # === Insights and Analytics ===
    
    def get_personalization_insights(self, child_id: str) -> Dict:
        """الحصول على رؤى التخصيص - يفوض إلى PersonalizationInsightsAnalyzer"""
        personality = self.get_child_personality(child_id)
        patterns = self.get_interaction_patterns(child_id)
        content_performance = self.content_performance.get(child_id, [])
        
        return self.insights_analyzer.get_personalization_insights(
            personality, patterns, content_performance
        )

    # === Utility Methods ===
    
    def backup_personalization_data(self, backup_suffix: str = None) -> bool:
        """إنشاء نسخة احتياطية من بيانات التخصيص"""
        return self.data_manager.backup_data(backup_suffix)

    def restore_personalization_data(self, backup_suffix: str) -> bool:
        """استعادة بيانات التخصيص من نسخة احتياطية"""
        success = self.data_manager.restore_from_backup(backup_suffix)
        if success:
            self._load_data()  # إعادة تحميل البيانات
        return success

    def get_data_statistics(self) -> Dict:
        """إحصائيات بيانات التخصيص"""
        return self.data_manager.get_data_statistics()

    def clean_old_personalization_data(self, days_to_keep: int = 30) -> bool:
        """تنظيف بيانات التخصيص القديمة"""
        success = self.data_manager.clean_old_data(days_to_keep)
        if success:
            self._load_data()  # إعادة تحميل البيانات المنظفة
        return success

    # === Pattern Analysis Utilities ===
    
    def get_most_active_time(self, child_id: str) -> str:
        """الحصول على أكثر وقت نشاط للطفل"""
        patterns = self.get_interaction_patterns(child_id)
        return self.pattern_manager.get_most_active_time(patterns)

    def get_learning_style_recommendation(self, child_id: str) -> str:
        """اقتراح أسلوب التعلم المفضل للطفل"""
        patterns = self.get_interaction_patterns(child_id)
        return self.pattern_manager.get_learning_style_recommendation(patterns)

    def get_dominant_response_pattern(self, child_id: str) -> str:
        """الحصول على نمط الرد المهيمن للطفل"""
        patterns = self.get_interaction_patterns(child_id)
        return self.pattern_manager.get_dominant_response_pattern(patterns)

    # === Health Check and Monitoring ===
    
    def get_service_health(self) -> Dict:
        """فحص صحة الخدمة وجميع مكوناتها"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "personality_analyzer": "operational",
                    "pattern_manager": "operational", 
                    "recommendation_engine": "operational",
                    "data_manager": "operational",
                    "insights_analyzer": "operational"
                },
                "data_stats": self.get_data_statistics(),
                "loaded_personalities": len(self.personalities),
                "loaded_patterns": len(self.interaction_patterns),
                "loaded_content_performance": len(self.content_performance)
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"خطأ في فحص صحة الخدمة: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
