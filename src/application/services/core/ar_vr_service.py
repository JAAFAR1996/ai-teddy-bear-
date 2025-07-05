#!/usr/bin/env python3
"""
🥽 خدمة الواقع المعزز والافتراضي المحسنة
Facade Pattern - يجمع جميع المكونات المنفصلة
"""

import logging
from dataclasses import asdict
from typing import Dict, List

from .ar_experience_manager import ARExperience, ARExperienceManager
from .vr_environment_manager import VREnvironment, VREnvironmentManager
from .ar_vr_session_manager import ARVRSessionManager
from .ar_vr_safety_manager import ARVRSafetyManager
from .ar_vr_data_manager import ARVRDataManager
from .ar_vr_analytics import ARVRAnalytics
from .ar_vr_preferences_manager import ARVRPreferencesManager

logger = logging.getLogger(__name__)


class ARVRService:
    """
    خدمة AR/VR المحسنة - High Cohesion
    كل مكون له مسؤولية واحدة واضحة
    """

    def __init__(self, data_dir: str = "data/ar_vr"):
        # تهيئة جميع المكونات المنفصلة
        self.ar_manager = ARExperienceManager()
        self.vr_manager = VREnvironmentManager()
        self.session_manager = ARVRSessionManager()
        self.safety_manager = ARVRSafetyManager()
        self.data_manager = ARVRDataManager(data_dir)
        self.analytics = ARVRAnalytics()
        self.preferences_manager = ARVRPreferencesManager()

        # تحميل البيانات المحفوظة
        self._load_all_data()

    def _load_all_data(self) -> None:
        """تحميل جميع البيانات من الملفات"""
        try:
            # تحميل تجارب AR المخصصة
            custom_ar = self.data_manager.load_ar_experiences()
            for exp_id, experience in custom_ar.items():
                self.ar_manager.add_custom_experience(experience)

            # تحميل بيئات VR المخصصة
            custom_vr = self.data_manager.load_vr_environments()
            for env_id, environment in custom_vr.items():
                self.vr_manager.add_custom_environment(environment)

            # تحميل جلسات المستخدمين
            user_sessions = self.data_manager.load_user_sessions()
            self.session_manager.session_history = user_sessions

            # تحميل تفضيلات الأطفال
            child_preferences = self.data_manager.load_child_preferences()
            self.preferences_manager.child_preferences = child_preferences

        except Exception as e:
            logger.error(f"خطأ في تحميل البيانات: {e}")

    def _save_all_data(self) -> None:
        """حفظ جميع البيانات"""
        try:
            # حفظ تجارب AR
            self.data_manager.save_ar_experiences(self.ar_manager.ar_experiences)

            # حفظ بيئات VR
            self.data_manager.save_vr_environments(self.vr_manager.vr_environments)

            # حفظ جلسات المستخدمين
            self.data_manager.save_user_sessions(self.session_manager.session_history)

            # حفظ تفضيلات الأطفال
            self.data_manager.save_child_preferences(self.preferences_manager.child_preferences)

        except Exception as e:
            logger.error(f"خطأ في حفظ البيانات: {e}")

    # ==================== AR Experience Methods ====================

    def get_available_ar_experiences(
        self, child_age: int = None, difficulty: str = None
    ) -> List[ARExperience]:
        """الحصول على تجارب الواقع المعزز المتاحة"""
        return self.ar_manager.get_available_experiences(child_age, difficulty)

    def add_custom_ar_experience(self, experience: ARExperience) -> bool:
        """إضافة تجربة AR مخصصة"""
        success = self.ar_manager.add_custom_experience(experience)
        if success:
            self._save_all_data()
        return success

    # ==================== VR Environment Methods ====================

    def get_available_vr_environments(
        self, child_age: int = None, theme: str = None
    ) -> List[VREnvironment]:
        """الحصول على بيئات الواقع الافتراضي المتاحة"""
        return self.vr_manager.get_available_environments(child_age, theme)

    def add_custom_vr_environment(self, environment: VREnvironment) -> bool:
        """إضافة بيئة VR مخصصة"""
        success = self.vr_manager.add_custom_environment(environment)
        if success:
            self._save_all_data()
        return success

    # ==================== Session Management Methods ====================

    def start_ar_session(self, child_id: str, experience_id: str) -> Dict:
        """بدء جلسة واقع معزز"""
        # الحصول على التجربة
        experience = self.ar_manager.get_experience_by_id(experience_id)
        if not experience:
            return {"error": "التجربة غير موجودة"}

        # فحص الأمان
        safety_check = self.safety_manager.check_ar_safety_requirements(experience)
        if not safety_check["safe"]:
            return {
                "error": "متطلبات الأمان غير مستوفاة",
                "details": safety_check["issues"],
            }

        # إنشاء الجلسة
        session = self.session_manager.create_ar_session(
            child_id, experience_id, experience.duration_minutes
        )

        self._save_all_data()

        return {
            "session_id": session["session_id"],
            "experience": asdict(experience),
            "setup_instructions": self.ar_manager.get_setup_instructions(experience),
            "safety_reminders": experience.safety_requirements,
            "estimated_duration": experience.duration_minutes,
        }

    def start_vr_session(
        self, child_id: str, environment_id: str, child_age: int
    ) -> Dict:
        """بدء جلسة واقع افتراضي"""
        # الحصول على البيئة
        environment = self.vr_manager.get_environment_by_id(environment_id)
        if not environment:
            return {"error": "البيئة غير موجودة"}

        # فحص العمر
        age_check = self.safety_manager.validate_vr_age_appropriateness(child_age)
        if not age_check["appropriate"]:
            return {"error": age_check["reason"]}

        # تكييف الإعدادات
        adapted_settings = self.vr_manager.adapt_for_age(environment, child_age)

        # إنشاء الجلسة
        session = self.session_manager.create_vr_session(
            child_id, 
            environment_id, 
            adapted_settings["max_duration"],
            adapted_settings["comfort_settings"]
        )

        self._save_all_data()

        return {
            "session_id": session["session_id"],
            "environment": asdict(environment),
            "adapted_settings": adapted_settings,
            "safety_guidelines": self.safety_manager.get_vr_safety_guidelines(child_age),
            "comfort_reminders": self.safety_manager.get_vr_comfort_reminders(),
        }

    def log_interaction(self, session_id: str, interaction_data: Dict) -> bool:
        """تسجيل تفاعل في الجلسة"""
        return self.session_manager.log_interaction(session_id, interaction_data)

    def end_session(self, session_id: str) -> Dict:
        """إنهاء جلسة AR/VR"""
        result = self.session_manager.end_session(session_id)
        
        if "error" not in result:
            # الحصول على الجلسة للتحليل
            session = self.session_manager.get_session_by_id(session_id)
            if session:
                # تحليل الأداء
                performance = self.session_manager.analyze_session_performance(session)
                session["performance_summary"] = performance

                # تحديث التفضيلات
                self._update_child_preferences_from_session(session["child_id"], session)

                # توليد التوصيات
                recommendations = self.analytics.generate_session_recommendations(session)
                result["recommendations"] = recommendations

                self._save_all_data()

        return result

    # ==================== Analytics & Reporting Methods ====================

    def get_child_ar_vr_report(self, child_id: str) -> Dict:
        """تقرير شامل لاستخدام الطفل لـ AR/VR"""
        sessions = self.session_manager.get_child_sessions(child_id)
        preferences = self.preferences_manager.get_child_preferences(child_id)

        if not sessions:
            return {"message": "لا توجد جلسات مسجلة لهذا الطفل"}

        # إنشاء التقرير باستخدام Analytics
        report = self.analytics.generate_child_report(child_id, sessions, preferences)
        
        # إضافة تقييم الأمان
        safety_assessment = self.safety_manager.assess_safety_compliance(sessions)
        report["safety_compliance"] = safety_assessment

        return report

    def analyze_usage_patterns(self, child_id: str) -> Dict:
        """تحليل أنماط استخدام الطفل"""
        sessions = self.session_manager.get_child_sessions(child_id)
        return self.analytics.analyze_usage_patterns(sessions)

    # ==================== Preferences Management ====================

    def update_child_content_filters(self, child_id: str, filters: Dict) -> None:
        """تحديث مرشحات المحتوى للطفل"""
        self.preferences_manager.set_content_filters(child_id, filters)
        self._save_all_data()

    def get_child_preferences(self, child_id: str) -> Dict:
        """الحصول على تفضيلات الطفل"""
        return self.preferences_manager.get_child_preferences(child_id)

    def get_personalized_recommendations(self, child_id: str) -> Dict:
        """توصيات مخصصة للطفل"""
        return {
            "recommended_ar_categories": self.preferences_manager.get_recommended_ar_categories(child_id),
            "recommended_vr_themes": self.preferences_manager.get_recommended_vr_themes(child_id),
            "adaptive_settings": self.preferences_manager.get_adaptive_settings(child_id, "ar"),
            "preferences_summary": self.preferences_manager.get_preferences_summary(child_id),
        }

    # ==================== Data Management ====================

    def backup_data(self) -> bool:
        """إنشاء نسخة احتياطية من البيانات"""
        return self.data_manager.backup_all_data()

    def get_data_statistics(self) -> Dict:
        """إحصائيات البيانات"""
        stats = self.data_manager.get_data_statistics()
        
        # إضافة إحصائيات الجلسات النشطة
        active_sessions = len(self.session_manager.active_sessions)
        stats["active_sessions"] = active_sessions
        
        return stats

    def cleanup_old_data(self, days_old: int = 30) -> Dict:
        """تنظيف البيانات القديمة"""
        cleaned_sessions = self.data_manager.cleanup_old_sessions(days_old)
        return {"cleaned_sessions": cleaned_sessions}

    # ==================== Private Helper Methods ====================

    def _update_child_preferences_from_session(self, child_id: str, session: Dict) -> None:
        """تحديث تفضيلات الطفل بناءً على الجلسة"""
        if session["type"] == "ar":
            self.preferences_manager.update_ar_preferences(child_id, session)
        elif session["type"] == "vr":
            self.preferences_manager.update_vr_preferences(child_id, session)

        # تحديث المدة المثلى وإعدادات الراحة
        self.preferences_manager.update_optimal_duration(child_id, session)
        self.preferences_manager.update_comfort_settings(child_id, session)

    # ==================== Legacy Compatibility Methods ====================
    # هذه الدوال للحفاظ على التوافق مع الواجهة القديمة

    def get_available_ar_experiences_legacy(self, child_age: int = None, difficulty: str = None) -> List[Dict]:
        """نسخة متوافقة مع الواجهة القديمة"""
        experiences = self.get_available_ar_experiences(child_age, difficulty)
        return [asdict(exp) for exp in experiences]

    def get_available_vr_environments_legacy(self, child_age: int = None, theme: str = None) -> List[Dict]:
        """نسخة متوافقة مع الواجهة القديمة"""
        environments = self.get_available_vr_environments(child_age, theme)
        return [asdict(env) for env in environments] 