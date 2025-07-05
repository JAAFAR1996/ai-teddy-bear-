#!/usr/bin/env python3
"""
👤 مدير تفضيلات المستخدمين AR/VR
مسؤول عن إدارة تفضيلات الأطفال فقط
"""

from typing import Dict


class ARVRPreferencesManager:
    """مدير التفضيلات - مسؤولية واحدة فقط"""

    def __init__(self):
        self.child_preferences: Dict[str, Dict] = {}

    def initialize_child_preferences(self, child_id: str) -> None:
        """تهيئة تفضيلات طفل جديد"""
        if child_id not in self.child_preferences:
            self.child_preferences[child_id] = {
                "preferred_ar_categories": {},
                "preferred_vr_themes": {},
                "optimal_session_duration": 10,
                "comfort_settings": {},
                "difficulty_preferences": "medium",
                "content_filters": {
                    "educational_only": False,
                    "age_appropriate": True,
                    "safe_content": True
                }
            }

    def update_ar_preferences(self, child_id: str, session: Dict) -> None:
        """تحديث تفضيلات AR بناءً على الجلسة"""
        self.initialize_child_preferences(child_id)
        prefs = self.child_preferences[child_id]

        if session["type"] == "ar" and "experience_id" in session:
            # هنا نحتاج للحصول على معلومات التجربة
            # سنفترض أن category متوفرة في session أو يمكن استنتاجها
            category = session.get("category", "educational")  # افتراضي

            if category not in prefs["preferred_ar_categories"]:
                prefs["preferred_ar_categories"][category] = 0

            # زيادة النقاط بناءً على الأداء
            performance = session.get("performance_summary", {})
            if performance.get("engagement_level") == "high":
                prefs["preferred_ar_categories"][category] += 2
            elif performance.get("engagement_level") == "medium":
                prefs["preferred_ar_categories"][category] += 1

    def update_vr_preferences(self, child_id: str, session: Dict) -> None:
        """تحديث تفضيلات VR بناءً على الجلسة"""
        self.initialize_child_preferences(child_id)
        prefs = self.child_preferences[child_id]

        if session["type"] == "vr" and "environment_id" in session:
            # هنا نحتاج للحصول على معلومات البيئة
            theme = session.get("theme", "educational")  # افتراضي

            if theme not in prefs["preferred_vr_themes"]:
                prefs["preferred_vr_themes"][theme] = 0

            performance = session.get("performance_summary", {})
            if performance.get("engagement_level") == "high":
                prefs["preferred_vr_themes"][theme] += 2
            elif performance.get("engagement_level") == "medium":
                prefs["preferred_vr_themes"][theme] += 1

    def update_optimal_duration(self, child_id: str, session: Dict) -> None:
        """تحديث المدة المثلى بناءً على الجلسة"""
        self.initialize_child_preferences(child_id)
        prefs = self.child_preferences[child_id]

        actual_duration = session.get("actual_duration_minutes", 10)
        performance = session.get("performance_summary", {})

        # تحديث المدة إذا كانت الجلسة مريحة ومفيدة
        if (performance.get("comfort_level") == "high" and
                performance.get("engagement_level") in ["medium", "high"]):

            current_optimal = prefs["optimal_session_duration"]
            # متوسط مرجح: 70% القيمة الحالية + 30% الجلسة الجديدة
            prefs["optimal_session_duration"] = (
                current_optimal * 0.7 + actual_duration * 0.3
            )

    def update_comfort_settings(self, child_id: str, session: Dict) -> None:
        """تحديث إعدادات الراحة بناءً على الجلسة"""
        self.initialize_child_preferences(child_id)
        prefs = self.child_preferences[child_id]

        performance = session.get("performance_summary", {})

        # إعدادات الراحة للـ VR
        if session["type"] == "vr":
            comfort_level = performance.get("comfort_level", "high")

            if comfort_level == "low":
                prefs["comfort_settings"]["motion_reduction"] = True
                prefs["comfort_settings"]["frequent_breaks"] = True
                prefs["comfort_settings"]["lower_immersion"] = True
            elif comfort_level == "high":
                # يمكن تخفيف القيود تدريجياً
                if prefs["comfort_settings"].get("motion_reduction"):
                    prefs["comfort_settings"]["motion_reduction"] = False

    def get_child_preferences(self, child_id: str) -> Dict:
        """الحصول على تفضيلات طفل"""
        self.initialize_child_preferences(child_id)
        return self.child_preferences[child_id].copy()

    def set_content_filters(self, child_id: str, filters: Dict) -> None:
        """تعيين مرشحات المحتوى"""
        self.initialize_child_preferences(child_id)
        self.child_preferences[child_id]["content_filters"].update(filters)

    def get_recommended_ar_categories(
    self, child_id: str, top_n: int = 3) -> list:
        """الحصول على فئات AR المفضلة"""
        prefs = self.get_child_preferences(child_id)
        ar_prefs = prefs["preferred_ar_categories"]

        if not ar_prefs:
            return ["educational", "interactive_story", "game"]  # افتراضي

        # ترتيب حسب النقاط
        sorted_categories = sorted(
    ar_prefs.items(),
    key=lambda x: x[1],
     reverse=True)
        return [category for category, _ in sorted_categories[:top_n]]

    def get_recommended_vr_themes(self, child_id: str, top_n: int = 3) -> list:
        """الحصول على موضوعات VR المفضلة"""
        prefs = self.get_child_preferences(child_id)
        vr_prefs = prefs["preferred_vr_themes"]

        if not vr_prefs:
            return ["educational", "space", "underwater"]  # افتراضي

        # ترتيب حسب النقاط
        sorted_themes = sorted(
    vr_prefs.items(),
    key=lambda x: x[1],
     reverse=True)
        return [theme for theme, _ in sorted_themes[:top_n]]

    def should_filter_content(self, child_id: str, content_type: str) -> bool:
        """التحقق من ضرورة تصفية المحتوى"""
        prefs = self.get_child_preferences(child_id)
        filters = prefs["content_filters"]

        if filters.get("educational_only") and content_type != "educational":
            return True

        if not filters.get("safe_content"):
            return False  # لا تصفية إذا كانت معطلة

        return False

    def get_adaptive_settings(self, child_id: str, session_type: str) -> Dict:
        """الحصول على إعدادات تكيفية للطفل"""
        prefs = self.get_child_preferences(child_id)

        settings = {
            "max_duration": prefs["optimal_session_duration"],
            "difficulty": prefs["difficulty_preferences"],
        }

        if session_type == "vr":
            settings.update(prefs["comfort_settings"])

            # تقليل المدة للأطفال الذين يعانون من مشاكل الراحة
            if prefs["comfort_settings"].get("frequent_breaks"):
                settings["max_duration"] = min(settings["max_duration"], 10)
                settings["break_interval"] = 3

        return settings

    def export_preferences(self, child_id: str) -> Dict:
        """تصدير تفضيلات الطفل للنسخ الاحتياطي"""
        return self.get_child_preferences(child_id)

    def import_preferences(self, child_id: str, preferences: Dict) -> bool:
        """استيراد تفضيلات من نسخة احتياطية"""
        try:
            # التحقق من صحة البنية
            required_keys = ["preferred_ar_categories", "preferred_vr_themes",
                             "optimal_session_duration", "comfort_settings"]

            if not all(key in preferences for key in required_keys):
                return False

            self.child_preferences[child_id] = preferences
            return True

        # FIXME: replace with specific exception
except Exception as exc:
    return False

   def reset_preferences(self, child_id: str) -> None:
        """إعادة تعيين تفضيلات الطفل"""
        if child_id in self.child_preferences:
            del self.child_preferences[child_id]
        self.initialize_child_preferences(child_id)

    def get_preferences_summary(self, child_id: str) -> Dict:
        """ملخص تفضيلات الطفل"""
        prefs = self.get_child_preferences(child_id)

        return {
    "top_ar_category": self.get_recommended_ar_categories(
        child_id,
        1)[0] if prefs["preferred_ar_categories"] else "educational",
        "top_vr_theme": self.get_recommended_vr_themes(
            child_id,
            1)[0] if prefs["preferred_vr_themes"] else "educational",
            "optimal_duration": prefs["optimal_session_duration"],
            "requires_comfort_adjustments": bool(
                prefs["comfort_settings"]),
                "content_filtered": prefs["content_filters"]["educational_only"],
                 }
