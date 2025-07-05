#!/usr/bin/env python3
"""
💾 Personalization Data Management Service
خدمة إدارة بيانات التخصيص
"""

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any

from .data_models import ChildPersonality, InteractionPattern, AdaptiveContent

logger = logging.getLogger(__name__)


class PersonalizationDataManager:
    """مدير بيانات التخصيص"""

    def __init__(self, data_dir: str = "data/personalization"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # مسارات الملفات
        self.personalities_file = self.data_dir / "personalities.json"
        self.patterns_file = self.data_dir / "interaction_patterns.json"
        self.content_file = self.data_dir / "content_performance.json"

    def load_all_data(self) -> Dict[str, Dict]:
        """تحميل جميع البيانات"""
        try:
            return {
                "personalities": self._load_personalities(),
                "interaction_patterns": self._load_interaction_patterns(),
                "content_performance": self._load_content_performance(),
            }
        except Exception as e:
            logger.error(f"خطأ في تحميل البيانات: {e}")
            return {
                "personalities": {},
                "interaction_patterns": {},
                "content_performance": {},
            }

    def save_all_data(
        self,
        personalities: Dict[str, ChildPersonality],
        patterns: Dict[str, InteractionPattern],
        content_performance: Dict[str, list],
    ) -> None:
        """حفظ جميع البيانات"""
        try:
            self._save_personalities(personalities)
            self._save_interaction_patterns(patterns)
            self._save_content_performance(content_performance)
        except Exception as e:
            logger.error(f"خطأ في حفظ البيانات: {e}")

    def _load_personalities(self) -> Dict[str, Dict]:
        """تحميل بيانات الشخصيات"""
        if not self.personalities_file.exists():
            return {}

        try:
            with open(self.personalities_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات الشخصيات: {e}")
            return {}

    def _load_interaction_patterns(self) -> Dict[str, Dict]:
        """تحميل بيانات أنماط التفاعل"""
        if not self.patterns_file.exists():
            return {}

        try:
            with open(self.patterns_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"خطأ في تحميل أنماط التفاعل: {e}")
            return {}

    def _load_content_performance(self) -> Dict[str, list]:
        """تحميل بيانات أداء المحتوى"""
        if not self.content_file.exists():
            return {}

        try:
            with open(self.content_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات أداء المحتوى: {e}")
            return {}

    def _save_personalities(self,
                            personalities: Dict[str,
                                                ChildPersonality]) -> None:
        """حفظ بيانات الشخصيات"""
        try:
            data = {
                child_id: asdict(personality)
                for child_id, personality in personalities.items()
            }
            with open(self.personalities_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات الشخصيات: {e}")

    def _save_interaction_patterns(
        self, patterns: Dict[str, InteractionPattern]
    ) -> None:
        """حفظ بيانات أنماط التفاعل"""
        try:
            data = {child_id: asdict(pattern)
                    for child_id, pattern in patterns.items()}
            with open(self.patterns_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"خطأ في حفظ أنماط التفاعل: {e}")

    def _save_content_performance(
            self, content_performance: Dict[str, list]) -> None:
        """حفظ بيانات أداء المحتوى"""
        try:
            # تحويل كائنات AdaptiveContent إلى قواميس
            data = {}
            for child_id, contents in content_performance.items():
                data[child_id] = [
                    asdict(content) if isinstance(content, AdaptiveContent) else content
                    for content in contents
                ]

            with open(self.content_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات أداء المحتوى: {e}")

    def backup_data(self, backup_suffix: str = None) -> bool:
        """إنشاء نسخة احتياطية من البيانات"""
        try:
            if backup_suffix is None:
                from datetime import datetime

                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")

            backup_dir = self.data_dir / f"backup_{backup_suffix}"
            backup_dir.mkdir(exist_ok=True)

            # نسخ الملفات
            import shutil

            for file_path in [
                self.personalities_file,
                self.patterns_file,
                self.content_file,
            ]:
                if file_path.exists():
                    backup_file = backup_dir / file_path.name
                    shutil.copy2(file_path, backup_file)

            logger.info(f"تم إنشاء النسخة الاحتياطية في: {backup_dir}")
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

            import shutil

            for file_name in [
                "personalities.json",
                "interaction_patterns.json",
                "content_performance.json",
            ]:
                backup_file = backup_dir / file_name
                if backup_file.exists():
                    target_file = self.data_dir / file_name
                    shutil.copy2(backup_file, target_file)

            logger.info(f"تم استعادة البيانات من: {backup_dir}")
            return True

        except Exception as e:
            logger.error(f"خطأ في استعادة البيانات: {e}")
            return False

    def get_data_statistics(self) -> Dict[str, Any]:
        """إحصائيات البيانات المحفوظة"""
        try:
            stats = {
                "personalities_count": 0,
                "patterns_count": 0,
                "content_entries_count": 0,
                "total_interactions": 0,
                "file_sizes": {},
            }

            # إحصائيات الملفات
            for file_path, key in [
                (self.personalities_file, "personalities"),
                (self.patterns_file, "patterns"),
                (self.content_file, "content"),
            ]:
                if file_path.exists():
                    stats["file_sizes"][key] = file_path.stat().st_size

                    # إحصائيات المحتوى
                    if key == "personalities":
                        data = self._load_personalities()
                        stats["personalities_count"] = len(data)
                    elif key == "patterns":
                        data = self._load_interaction_patterns()
                        stats["patterns_count"] = len(data)
                    elif key == "content":
                        data = self._load_content_performance()
                        stats["content_entries_count"] = sum(
                            len(contents) for contents in data.values()
                        )
                        stats["total_interactions"] = stats["content_entries_count"]

            return stats

        except Exception as e:
            logger.error(f"خطأ في جمع الإحصائيات: {e}")
            return {}

    def clean_old_data(self, days_to_keep: int = 30) -> bool:
        """تنظيف البيانات القديمة"""
        try:
            from datetime import datetime, timedelta

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.isoformat()

            # تنظيف المحتوى القديم
            content_data = self._load_content_performance()
            cleaned_count = 0

            for child_id, contents in content_data.items():
                original_count = len(contents)
                # إبقاء المحتوى الحديث فقط
                contents[:] = [
                    content
                    for content in contents
                    if content.get("last_used", "") > cutoff_str
                ]
                cleaned_count += original_count - len(contents)

            # حفظ البيانات المنظفة
            self._save_content_performance(content_data)

            logger.info(f"تم تنظيف {cleaned_count} عنصر من البيانات القديمة")
            return True

        except Exception as e:
            logger.error(f"خطأ في تنظيف البيانات: {e}")
            return False
