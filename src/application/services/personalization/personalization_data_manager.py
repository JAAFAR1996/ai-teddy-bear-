#!/usr/bin/env python3
"""
💾 مدير بيانات التخصيص
إدارة تحميل وحفظ بيانات التخصيص - EXTRACT CLASS
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PersonalizationDataManager:
    """مدير بيانات التخصيص - مستخرج من AdvancedPersonalizationService"""
    
    def __init__(self, data_dir: str = "data/personalization"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_all_data(self) -> Dict[str, Any]:
        """تحميل جميع البيانات من الملفات"""
        try:
            data = {
                'personalities': self._load_personalities(),
                'interaction_patterns': self._load_interaction_patterns(),
                'content_performance': self._load_content_performance()
            }
            return data
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات التخصيص: {e}")
            return {'personalities': {}, 'interaction_patterns': {}, 'content_performance': {}}

    def _load_personalities(self) -> Dict[str, Any]:
        """تحميل بيانات الشخصيات"""
        personalities_file = self.data_dir / "personalities.json"
        if personalities_file.exists():
            with open(personalities_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_interaction_patterns(self) -> Dict[str, Any]:
        """تحميل أنماط التفاعل"""
        patterns_file = self.data_dir / "interaction_patterns.json"
        if patterns_file.exists():
            with open(patterns_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_content_performance(self) -> Dict[str, Any]:
        """تحميل بيانات أداء المحتوى"""
        content_file = self.data_dir / "content_performance.json"
        if content_file.exists():
            with open(content_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_all_data(self, personalities: Dict, interaction_patterns: Dict, 
                     content_performance: Dict) -> None:
        """حفظ جميع البيانات في الملفات"""
        try:
            self._save_personalities(personalities)
            self._save_interaction_patterns(interaction_patterns)
            self._save_content_performance(content_performance)
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات التخصيص: {e}")

    def _save_personalities(self, personalities: Dict) -> None:
        """حفظ الشخصيات"""
        personalities_file = self.data_dir / "personalities.json"
        personalities_data = {
            child_id: asdict(personality) if hasattr(personality, '__dict__') else personality
            for child_id, personality in personalities.items()
        }
        with open(personalities_file, "w", encoding="utf-8") as f:
            json.dump(personalities_data, f, ensure_ascii=False, indent=2)

    def _save_interaction_patterns(self, interaction_patterns: Dict) -> None:
        """حفظ أنماط التفاعل"""
        patterns_file = self.data_dir / "interaction_patterns.json"
        patterns_data = {
            child_id: asdict(pattern) if hasattr(pattern, '__dict__') else pattern
            for child_id, pattern in interaction_patterns.items()
        }
        with open(patterns_file, "w", encoding="utf-8") as f:
            json.dump(patterns_data, f, ensure_ascii=False, indent=2)

    def _save_content_performance(self, content_performance: Dict) -> None:
        """حفظ أداء المحتوى"""
        content_file = self.data_dir / "content_performance.json"
        content_data = {
            child_id: [asdict(content) if hasattr(content, '__dict__') else content 
                      for content in contents]
            for child_id, contents in content_performance.items()
        }
        with open(content_file, "w", encoding="utf-8") as f:
            json.dump(content_data, f, ensure_ascii=False, indent=2) 