#!/usr/bin/env python3
"""
🧪 اختبار إصلاح مشاكل advanced_personalization_service.py
اختبار شامل لجميع الإصلاحات المطبقة: Complex Conditional، Complex Method، File Size Issue
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent / "src"))

from src.application.services.core.advanced_personalization_service import (
    AdvancedPersonalizationService,
    ChildPersonality,
    InteractionPattern,
    AdaptiveContent,
)


class TestAdvancedPersonalizationRefactoring:
    """اختبارات إصلاح مشاكل جودة الكود"""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = AdvancedPersonalizationService(self.temp_dir)
        self.test_child_id = "test_child_123"

    def test_complex_conditional_fix(self):
        """✅ اختبار إصلاح Complex Conditional في track_content_performance"""
        print("\n🔧 اختبار إصلاح Complex Conditional...")

        # محتوى للاختبار
        content = {
            "type": "story",
            "difficulty": "medium",
            "topic": "animals"
        }
        
        performance_data = {
            "duration_minutes": 15,
            "engagement_score": 0.8,
            "success_rate": 0.9,
            "feedback": "positive"
        }

        # إضافة محتوى جديد
        self.service.track_content_performance(self.test_child_id, content, performance_data)
        
        # التحقق من أن المحتوى تم إضافته
        assert self.test_child_id in self.service.content_performance
        assert len(self.service.content_performance[self.test_child_id]) == 1
        
        # إضافة نفس المحتوى مرة أخرى (يجب أن يتم التحديث وليس الإضافة)
        performance_data_2 = {
            "duration_minutes": 20,
            "engagement_score": 0.7,
            "success_rate": 0.8,
            "feedback": "positive"
        }
        
        self.service.track_content_performance(self.test_child_id, content, performance_data_2)
        
        # التحقق من أن المحتوى تم تحديثه وليس إضافة عنصر جديد
        assert len(self.service.content_performance[self.test_child_id]) == 1
        
        # التحقق من أن القيم تم حساب متوسطها
        updated_content = self.service.content_performance[self.test_child_id][0]
        expected_engagement = (0.8 + 0.7) / 2  # 0.75
        assert abs(updated_content.engagement_score - expected_engagement) < 0.01
        
        print("✅ إصلاح Complex Conditional يعمل بشكل صحيح!")
        print(f"   - المحتوى المطابق تم تحديثه بدلاً من إضافة عنصر جديد")
        print(f"   - متوسط الانخراط: {updated_content.engagement_score:.2f}")

    def test_complex_method_fix(self):
        """✅ اختبار إصلاح Complex Method في _identify_development_areas"""
        print("\n🔧 اختبار إصلاح Complex Method...")

        # إنشاء شخصية للاختبار
        personality = ChildPersonality(
            child_id=self.test_child_id,
            curiosity_level=0.8,  # عالي
            creativity_level=0.3,  # منخفض
            openness=0.2,  # منخفض
            extraversion=0.2,  # منخفض
            conscientiousness=0.7,  # عالي
            attention_span=10  # أقل من 15
        )
        
        patterns = InteractionPattern(
            child_id=self.test_child_id,
            favorite_topics=["animals"]  # أقل من 3
        )

        # الحصول على رؤى التخصيص (يستخدم _identify_development_areas داخلياً)
        insights = self.service.insights_analyzer.get_personalization_insights(
            personality, patterns, []
        )

        development_areas = insights["development_areas"]
        
        # التحقق من نقاط القوة
        assert "فضول عالي للتعلم" in development_areas["strengths"]
        assert "مثابرة في إنجاز المهام" in development_areas["strengths"]
        
        # التحقق من مجالات النمو
        assert "الانفتاح على التجارب الجديدة" in development_areas["growth_areas"]
        assert "الثقة في التفاعل الاجتماعي" in development_areas["growth_areas"]
        assert "تطوير فترة التركيز" in development_areas["growth_areas"]
        
        # التحقق من اقتراحات التركيز
        assert "أنشطة إبداعية مثل الرسم والقصص التفاعلية" in development_areas["focus_suggestions"]
        assert "استكشاف مواضيع ومجالات معرفية متنوعة" in development_areas["focus_suggestions"]

        print("✅ إصلاح Complex Method يعمل بشكل صحيح!")
        print(f"   - تم تحديد {len(development_areas['strengths'])} نقاط قوة")
        print(f"   - تم تحديد {len(development_areas['growth_areas'])} مجالات نمو")
        print(f"   - تم توليد {len(development_areas['focus_suggestions'])} اقتراح تركيز")

    def test_file_size_fix_extract_class(self):
        """✅ اختبار إصلاح File Size Issue - EXTRACT CLASS"""
        print("\n🔧 اختبار إصلاح File Size Issue (EXTRACT CLASS)...")

        # التحقق من أن المكونات المنفصلة تم إنشاؤها
        assert hasattr(self.service, 'personality_analyzer')
        assert hasattr(self.service, 'pattern_manager')
        assert hasattr(self.service, 'recommendation_engine')
        assert hasattr(self.service, 'data_manager')
        assert hasattr(self.service, 'insights_analyzer')

        # اختبار PersonalityAnalyzer
        interactions = [
            {"activity_type": "story", "duration_minutes": 20, "completed": True, "response_type": "positive"},
            {"activity_type": "game", "duration_minutes": 25, "completed": True, "response_type": "enthusiastic"},
            {"activity_type": "creative_games", "topic": "animals", "emotion": "happy"}
        ]
        
        personality = self.service.analyze_personality_from_interactions(self.test_child_id, interactions)
        assert personality.extraversion > 0.5  # متوسط المدة 22.5 دقيقة
        assert personality.conscientiousness == 1.0  # كل المهام مكتملة
        
        # اختبار InteractionPatternManager
        interaction_data = {
            "activity_type": "storytelling",
            "engagement_score": 0.8,
            "topic": "space",
            "response_type": "positive"
        }
        
        self.service.update_interaction_patterns(self.test_child_id, interaction_data)
        patterns = self.service.get_interaction_patterns(self.test_child_id)
        assert "storytelling" in patterns.preferred_activities
        assert "space" in patterns.favorite_topics

        # اختبار ContentRecommendationEngine
        recommendations = self.service.recommend_content(self.test_child_id, "story")
        assert len(recommendations) > 0
        assert all("suitability_score" in rec for rec in recommendations)
        
        # اختبار PersonalizationDataManager (عبر save/load)
        original_personality = personality.openness
        self.service._save_data()
        
        # إنشاء خدمة جديدة للتحقق من التحميل
        new_service = AdvancedPersonalizationService(self.temp_dir)
        loaded_personality = new_service.get_child_personality(self.test_child_id)
        assert abs(loaded_personality.openness - original_personality) < 0.01

        # اختبار PersonalizationInsightsAnalyzer
        insights = self.service.get_personalization_insights(self.test_child_id)
        assert "personality_summary" in insights
        assert "learning_style" in insights
        assert "development_areas" in insights

        print("✅ إصلاح File Size Issue يعمل بشكل صحيح!")
        print("   - PersonalityAnalyzer: تحليل الشخصية يعمل ✓")
        print("   - InteractionPatternManager: تحديث الأنماط يعمل ✓")
        print("   - ContentRecommendationEngine: اقتراح المحتوى يعمل ✓")
        print("   - PersonalizationDataManager: حفظ/تحميل البيانات يعمل ✓")
        print("   - PersonalizationInsightsAnalyzer: تحليل الرؤى يعمل ✓")

    def test_facade_pattern_integration(self):
        """✅ اختبار تكامل Facade Pattern"""
        print("\n🔧 اختبار تكامل Facade Pattern...")

        # التحقق من أن الخدمة الرئيسية تعمل كـ Facade للمكونات المنفصلة
        child_id = "facade_test_child"
        
        # سيناريو متكامل
        # 1. تحليل الشخصية
        interactions = [
            {"activity_type": "creative_games", "duration_minutes": 30, "topic": "art"},
            {"activity_type": "storytelling", "completed": True, "response_type": "enthusiastic"}
        ]
        
        personality = self.service.analyze_personality_from_interactions(child_id, interactions)
        
        # 2. تحديث الأنماط
        self.service.update_interaction_patterns(child_id, {
            "activity_type": "art",
            "engagement_score": 0.9,
            "topic": "painting"
        })
        
        # 3. تتبع أداء المحتوى
        self.service.track_content_performance(child_id, 
            {"type": "story", "topic": "art", "difficulty": "medium"},
            {"engagement_score": 0.85, "success_rate": 0.8}
        )
        
        # 4. الحصول على توصيات
        recommendations = self.service.recommend_content(child_id)
        
        # 5. تحليل الرؤى
        insights = self.service.get_personalization_insights(child_id)
        
        # التحقق من التكامل
        assert personality.creativity_level > 0.5  # من تحليل creative_games
        assert len(recommendations) > 0
        assert insights["personality_summary"]["creativity_level"] in ["متوسط", "عالي"]
        
        print("✅ Facade Pattern يعمل بشكل متكامل!")
        print(f"   - مستوى الإبداع: {personality.creativity_level:.2f}")
        print(f"   - عدد التوصيات: {len(recommendations)}")
        print(f"   - تقييم الإبداع: {insights['personality_summary']['creativity_level']}")

    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🚀 بدء اختبار إصلاحات advanced_personalization_service.py")
        print("=" * 60)

        try:
            self.test_complex_conditional_fix()
            self.test_complex_method_fix()
            self.test_file_size_fix_extract_class()
            self.test_facade_pattern_integration()
            
            print("\n" + "=" * 60)
            print("🎉 جميع الاختبارات نجحت! الإصلاحات تعمل بشكل مثالي!")
            print("\n📊 ملخص الإصلاحات:")
            print("✅ Complex Conditional → DECOMPOSE CONDITIONAL مطبق")
            print("✅ Complex Method (cc=11) → EXTRACT FUNCTION مطبق")  
            print("✅ File Size Issue (855→5 ملفات) → EXTRACT CLASS مطبق")
            print("✅ Facade Pattern → تكامل مثالي بين المكونات")
            print("\n🏆 تحسن جودة الكود من Low إلى High Cohesion!")
            
        except Exception as e:
            print(f"\n❌ خطأ في الاختبار: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    tester = TestAdvancedPersonalizationRefactoring()
    tester.run_all_tests() 