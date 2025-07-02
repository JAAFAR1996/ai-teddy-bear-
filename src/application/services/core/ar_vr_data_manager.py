#!/usr/bin/env python3
"""
💾 مدير بيانات AR/VR
مسؤول عن حفظ وتحميل البيانات فقط
"""

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from .ar_experience_manager import ARExperience
from .vr_environment_manager import VREnvironment

logger = logging.getLogger(__name__)


class ARVRDataManager:
    """مدير البيانات - مسؤولية واحدة فقط"""

    def __init__(self, data_dir: str = "data/ar_vr"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save_ar_experiences(self, experiences: Dict[str, ARExperience]) -> bool:
        """حفظ تجارب AR (المخصصة فقط)"""
        try:
            ar_file = self.data_dir / "ar_experiences.json"
            custom_ar = {
                exp_id: asdict(exp)
                for exp_id, exp in experiences.items()
                if not exp_id.startswith("ar_")  # تجنب حفظ الافتراضية
            }
            
            with open(ar_file, "w", encoding="utf-8") as f:
                json.dump(custom_ar, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"خطأ في حفظ تجارب AR: {e}")
            return False

    def load_ar_experiences(self) -> Dict[str, ARExperience]:
        """تحميل تجارب AR من الملف"""
        experiences = {}
        
        try:
            ar_file = self.data_dir / "ar_experiences.json"
            if ar_file.exists():
                with open(ar_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for exp_id, exp_data in data.items():
                        experiences[exp_id] = ARExperience(**exp_data)
        except Exception as e:
            logger.error(f"خطأ في تحميل تجارب AR: {e}")
        
        return experiences

    def save_vr_environments(self, environments: Dict[str, VREnvironment]) -> bool:
        """حفظ بيئات VR (المخصصة فقط)"""
        try:
            vr_file = self.data_dir / "vr_environments.json"
            custom_vr = {
                env_id: asdict(env)
                for env_id, env in environments.items()
                if not env_id.startswith("vr_")  # تجنب حفظ الافتراضية
            }
            
            with open(vr_file, "w", encoding="utf-8") as f:
                json.dump(custom_vr, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"خطأ في حفظ بيئات VR: {e}")
            return False

    def load_vr_environments(self) -> Dict[str, VREnvironment]:
        """تحميل بيئات VR من الملف"""
        environments = {}
        
        try:
            vr_file = self.data_dir / "vr_environments.json"
            if vr_file.exists():
                with open(vr_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for env_id, env_data in data.items():
                        environments[env_id] = VREnvironment(**env_data)
        except Exception as e:
            logger.error(f"خطأ في تحميل بيئات VR: {e}")
        
        return environments

    def save_user_sessions(self, user_sessions: Dict[str, List[Dict]]) -> bool:
        """حفظ جلسات المستخدمين"""
        try:
            sessions_file = self.data_dir / "user_sessions.json"
            with open(sessions_file, "w", encoding="utf-8") as f:
                json.dump(user_sessions, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"خطأ في حفظ جلسات المستخدمين: {e}")
            return False

    def load_user_sessions(self) -> Dict[str, List[Dict]]:
        """تحميل جلسات المستخدمين"""
        sessions = {}
        
        try:
            sessions_file = self.data_dir / "user_sessions.json"
            if sessions_file.exists():
                with open(sessions_file, "r", encoding="utf-8") as f:
                    sessions = json.load(f)
        except Exception as e:
            logger.error(f"خطأ في تحميل جلسات المستخدمين: {e}")
        
        return sessions

    def save_child_preferences(self, child_preferences: Dict[str, Dict]) -> bool:
        """حفظ تفضيلات الأطفال"""
        try:
            preferences_file = self.data_dir / "child_preferences.json"
            with open(preferences_file, "w", encoding="utf-8") as f:
                json.dump(child_preferences, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"خطأ في حفظ تفضيلات الأطفال: {e}")
            return False

    def load_child_preferences(self) -> Dict[str, Dict]:
        """تحميل تفضيلات الأطفال"""
        preferences = {}
        
        try:
            preferences_file = self.data_dir / "child_preferences.json"
            if preferences_file.exists():
                with open(preferences_file, "r", encoding="utf-8") as f:
                    preferences = json.load(f)
        except Exception as e:
            logger.error(f"خطأ في تحميل تفضيلات الأطفال: {e}")
        
        return preferences

    def backup_all_data(self, backup_suffix: str = None) -> bool:
        """إنشاء نسخة احتياطية من جميع البيانات"""
        try:
            if backup_suffix is None:
                from datetime import datetime
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            backup_dir = self.data_dir / f"backup_{backup_suffix}"
            backup_dir.mkdir(exist_ok=True)
            
            # نسخ جميع ملفات JSON
            for json_file in self.data_dir.glob("*.json"):
                backup_file = backup_dir / json_file.name
                backup_file.write_text(json_file.read_text(encoding="utf-8"), encoding="utf-8")
            
            logger.info(f"تم إنشاء نسخة احتياطية في: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return False

    def restore_from_backup(self, backup_suffix: str) -> bool:
        """استعادة البيانات من نسخة احتياطية"""
        try:
            backup_dir = self.data_dir / f"backup_{backup_suffix}"
            if not backup_dir.exists():
                logger.error(f"النسخة الاحتياطية غير موجودة: {backup_dir}")
                return False
            
            # استعادة جميع ملفات JSON
            for backup_file in backup_dir.glob("*.json"):
                original_file = self.data_dir / backup_file.name
                original_file.write_text(backup_file.read_text(encoding="utf-8"), encoding="utf-8")
            
            logger.info(f"تم استعادة البيانات من: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في استعادة النسخة الاحتياطية: {e}")
            return False

    def get_data_statistics(self) -> Dict:
        """إحصائيات البيانات المحفوظة"""
        stats = {
            "ar_experiences_count": 0,
            "vr_environments_count": 0,
            "children_with_sessions": 0,
            "children_with_preferences": 0,
            "total_sessions": 0,
            "data_size_mb": 0
        }
        
        try:
            # إحصائيات تجارب AR
            ar_file = self.data_dir / "ar_experiences.json"
            if ar_file.exists():
                with open(ar_file, "r", encoding="utf-8") as f:
                    ar_data = json.load(f)
                    stats["ar_experiences_count"] = len(ar_data)
            
            # إحصائيات بيئات VR
            vr_file = self.data_dir / "vr_environments.json"
            if vr_file.exists():
                with open(vr_file, "r", encoding="utf-8") as f:
                    vr_data = json.load(f)
                    stats["vr_environments_count"] = len(vr_data)
            
            # إحصائيات الجلسات
            sessions_file = self.data_dir / "user_sessions.json"
            if sessions_file.exists():
                with open(sessions_file, "r", encoding="utf-8") as f:
                    sessions_data = json.load(f)
                    stats["children_with_sessions"] = len(sessions_data)
                    stats["total_sessions"] = sum(len(sessions) for sessions in sessions_data.values())
            
            # إحصائيات التفضيلات
            preferences_file = self.data_dir / "child_preferences.json"
            if preferences_file.exists():
                with open(preferences_file, "r", encoding="utf-8") as f:
                    preferences_data = json.load(f)
                    stats["children_with_preferences"] = len(preferences_data)
            
            # حجم البيانات الإجمالي
            total_size = sum(f.stat().st_size for f in self.data_dir.glob("*.json"))
            stats["data_size_mb"] = round(total_size / (1024 * 1024), 2)
            
        except Exception as e:
            logger.error(f"خطأ في حساب إحصائيات البيانات: {e}")
        
        return stats

    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """تنظيف الجلسات القديمة"""
        try:
            from datetime import datetime, timedelta
            
            sessions_data = self.load_user_sessions()
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            for child_id, sessions in sessions_data.items():
                original_count = len(sessions)
                # الاحتفاظ بالجلسات الحديثة فقط
                sessions_data[child_id] = [
                    session for session in sessions
                    if datetime.fromisoformat(session.get("start_time", "")) > cutoff_date
                ]
                cleaned_count += original_count - len(sessions_data[child_id])
            
            # حفظ البيانات المنظفة
            self.save_user_sessions(sessions_data)
            logger.info(f"تم تنظيف {cleaned_count} جلسة قديمة")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف الجلسات القديمة: {e}")
            return 0 