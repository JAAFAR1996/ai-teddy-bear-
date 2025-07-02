#!/usr/bin/env python3
"""
🛡️ مدير الأمان والراحة في AR/VR
مسؤول عن جميع جوانب الأمان فقط
"""

from typing import Dict, List
from .ar_experience_manager import ARExperience
from .vr_environment_manager import VREnvironment


class ARVRSafetyManager:
    """مدير الأمان والراحة - مسؤولية واحدة فقط"""

    def check_ar_safety_requirements(self, experience: ARExperience) -> Dict:
        """فحص متطلبات الأمان للواقع المعزز"""
        safety_check = {"safe": True, "issues": []}

        # فحص المساحة المطلوبة
        for requirement in experience.safety_requirements:
            if "مساحة" in requirement:
                safety_check["issues"].append(f"تأكد من توفر {requirement}")

        # فحص الأجسام المطلوبة
        if experience.required_objects:
            safety_check["issues"].append(
                f"تأكد من وجود: {', '.join(experience.required_objects)}"
            )

        return safety_check

    def validate_vr_age_appropriateness(self, child_age: int) -> Dict:
        """التحقق من ملاءمة VR للعمر"""
        if child_age < 6:
            return {
                "appropriate": False,
                "reason": "الواقع الافتراضي غير مناسب للأطفال تحت 6 سنوات"
            }
        
        return {"appropriate": True, "reason": "العمر مناسب"}

    def get_vr_safety_guidelines(self, child_age: int) -> List[str]:
        """إرشادات الأمان للواقع الافتراضي"""
        guidelines = [
            "تأكد من وجود إشراف بالغ دائم",
            "خذ راحة كل 5 دقائق",
            "توقف فوراً إذا شعرت بدوار أو غثيان",
            "تأكد من أن المساحة خالية من العوائق",
            "لا تستخدم VR أكثر من 15 دقيقة متواصلة",
        ]

        if child_age < 8:
            guidelines.extend([
                "استخدم أقل إعدادات الحركة",
                "راحة كل 3 دقائق",
                "مدة قصوى 10 دقائق"
            ])

        return guidelines

    def get_vr_comfort_reminders(self) -> List[str]:
        """تذكيرات الراحة للواقع الافتراضي"""
        return [
            "ارمش عينيك بشكل طبيعي",
            "اجلس إذا شعرت بالتعب",
            "اشرب الماء بانتظام",
            "تحرك ببطء وتجنب الحركات المفاجئة",
            "أخبر الكبار إذا شعرت بأي إزعاج",
        ]

    def assess_safety_compliance(self, sessions: List[Dict]) -> Dict:
        """تقييم الالتزام بمعايير الأمان"""
        safety_assessment = {
            "average_session_duration": 0,
            "comfort_issues_count": 0,
            "technical_issues_count": 0,
            "safety_score": "excellent",
        }

        if not sessions:
            return safety_assessment

        total_duration = sum(s.get("actual_duration_minutes", 0) for s in sessions)
        safety_assessment["average_session_duration"] = total_duration / len(sessions)

        comfort_issues = sum(
            1 for s in sessions
            if s.get("performance_summary", {}).get("comfort_level") == "low"
        )
        technical_issues = sum(
            s.get("performance_summary", {}).get("technical_issues", 0)
            for s in sessions
        )

        safety_assessment["comfort_issues_count"] = comfort_issues
        safety_assessment["technical_issues_count"] = technical_issues

        # تقييم النتيجة
        if comfort_issues > len(sessions) * 0.3 or technical_issues > len(sessions) * 2:
            safety_assessment["safety_score"] = "needs_improvement"
        elif comfort_issues > 0 or technical_issues > 0:
            safety_assessment["safety_score"] = "good"

        return safety_assessment

    def validate_session_duration(self, session_type: str, duration: int, child_age: int) -> Dict:
        """التحقق من مدة الجلسة المناسبة"""
        max_duration = 15  # افتراضي

        if session_type == "vr":
            if child_age < 8:
                max_duration = 10
            elif child_age < 12:
                max_duration = 15
        elif session_type == "ar":
            max_duration = 20  # AR أكثر أماناً

        return {
            "valid": duration <= max_duration,
            "max_recommended": max_duration,
            "warning": f"المدة الموصى بها لا تتجاوز {max_duration} دقيقة" if duration > max_duration else None
        }

    def generate_safety_alerts(self, session: Dict) -> List[str]:
        """توليد تنبيهات الأمان"""
        alerts = []
        
        performance = session.get("performance_summary", {})
        
        if performance.get("comfort_level") == "low":
            alerts.append("مستوى راحة منخفض - قلل مدة الجلسات القادمة")
        
        if performance.get("technical_issues", 0) > 2:
            alerts.append("مشاكل تقنية متكررة - تحقق من البيئة والمعدات")
            
        if session.get("actual_duration_minutes", 0) > 20:
            alerts.append("جلسة طويلة - احرص على الراحة المنتظمة")
            
        return alerts 