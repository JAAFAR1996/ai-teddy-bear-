#!/usr/bin/env python3
"""
🔍 Duplicate and Unnecessary Files Analyzer
محلل الملفات المكررة وغير المهمة في المشروع

Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise Grade AI Teddy Bear Project 2025
"""

import hashlib
import json
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuplicateAnalyzer:
    """محلل الملفات المكررة وغير المهمة"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.duplicates = defaultdict(list)
        self.unnecessary_files = []
        self.project_files = []
        self.venv_files = []
        self.test_files = []
        self.script_files = []

    def analyze_project_structure(self):
        """تحليل هيكل المشروع"""
        logger.info("🔍 بدء تحليل هيكل المشروع...")

        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                self._categorize_file(file_path)

        self._find_duplicates()
        self._identify_unnecessary_files()
        self._generate_report()

    def _categorize_file(self, file_path: Path):
        """تصنيف الملفات"""
        relative_path = file_path.relative_to(self.project_root)

        # تجاهل ملفات النظام
        if any(part.startswith('.') for part in relative_path.parts):
            return

        # تصنيف الملفات
        if "venv" in str(file_path) or ".venv" in str(file_path):
            self.venv_files.append(str(relative_path))
        elif "test" in file_path.name or "tests" in str(file_path):
            self.test_files.append(str(relative_path))
        elif "scripts" in str(file_path):
            self.script_files.append(str(relative_path))
        elif file_path.suffix in ['.py', '.json', '.yaml', '.yml', '.md', '.txt']:
            self.project_files.append(str(relative_path))

    def _calculate_file_hash(self, file_path: Path) -> str:
        """حساب hash للملف"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def _find_duplicates(self):
        """البحث عن الملفات المكررة"""
        logger.info("🔍 البحث عن الملفات المكررة...")

        hash_to_files = defaultdict(list)

        for file_path_str in self.project_files:
            file_path = self.project_root / file_path_str
            if file_path.exists():
                file_hash = self._calculate_file_hash(file_path)
                if file_hash:
                    hash_to_files[file_hash].append(file_path_str)

        # إيجاد الملفات المكررة
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                self.duplicates[file_hash] = files

    def _identify_unnecessary_files(self):
        """تحديد الملفات غير المهمة"""
        logger.info("🔍 تحديد الملفات غير المهمة...")

        unnecessary_patterns = [
            # ملفات مؤقتة
            "*.tmp", "*.temp", "*.bak", "*.backup",
            # ملفات نظام
            ".DS_Store", "Thumbs.db", "desktop.ini",
            # ملفات IDE
            "*.swp", "*.swo", "*~", ".vscode/", ".idea/",
            # ملفات Python
            "*.pyc", "__pycache__/", "*.pyo",
            # ملفات logs
            "*.log", "logs/",
            # ملفات بيانات مؤقتة
            "*.cache", ".cache/",
            # ملفات اختبار قديمة
            "test_*.py.bak", "*_test_old.py",
            # ملفات تجريبية
            "demo_*.py", "example_*.py", "sample_*.py",
            # ملفات تحليل قديمة
            "*_analyzer_old.py", "*_audit_old.py",
            # ملفات PDF
            "*.pdf",
            # ملفات ZIP
            "*.zip", "*.tar.gz",
            # ملفات صور
            "*.png", "*.jpg", "*.jpeg", "*.gif"
        ]

        for file_path_str in self.project_files:
            file_path = Path(file_path_str)

            # فحص الأنماط
            for pattern in unnecessary_patterns:
                if file_path.match(pattern):
                    self.unnecessary_files.append(file_path_str)
                    break

            # فحص أسماء الملفات المشبوهة
            suspicious_names = [
                "temp", "tmp", "old", "backup", "copy", "duplicate",
                "test_old", "demo", "example", "sample", "trial"
            ]

            if any(name in file_path.name.lower() for name in suspicious_names):
                self.unnecessary_files.append(file_path_str)

    def _generate_report(self):
        """توليد التقرير"""
        report = {
            "timestamp": "2025-07-03T23:58:00",
            "summary": {
                "total_project_files": len(self.project_files),
                "total_venv_files": len(self.venv_files),
                "total_test_files": len(self.test_files),
                "total_script_files": len(self.script_files),
                "duplicate_groups": len(self.duplicates),
                "unnecessary_files": len(self.unnecessary_files)
            },
            "duplicates": {
                hash_val: {
                    "files": files,
                    "count": len(files),
                    "size_mb": self._get_total_size_mb(files)
                }
                for hash_val, files in self.duplicates.items()
            },
            "unnecessary_files": [
                {
                    "file": file_path,
                    "reason": self._get_unnecessary_reason(file_path)
                }
                for file_path in self.unnecessary_files
            ],
            "recommendations": self._generate_recommendations()
        }

        # حفظ التقرير
        with open("duplicate_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # عرض الملخص
        self._display_summary(report)

    def _get_total_size_mb(self, files: List[str]) -> float:
        """حساب الحجم الإجمالي بالـ MB"""
        total_size = 0
        for file_path_str in files:
            file_path = self.project_root / file_path_str
            if file_path.exists():
                total_size += file_path.stat().st_size
        return round(total_size / (1024 * 1024), 2)

    def _get_unnecessary_reason(self, file_path: str) -> str:
        """تحديد سبب عدم أهمية الملف"""
        path = Path(file_path)

        if "temp" in path.name.lower() or "tmp" in path.name.lower():
            return "ملف مؤقت"
        elif "old" in path.name.lower() or "backup" in path.name.lower():
            return "ملف قديم أو نسخة احتياطية"
        elif "demo" in path.name.lower() or "example" in path.name.lower():
            return "ملف تجريبي أو مثال"
        elif "test_old" in path.name.lower():
            return "اختبار قديم"
        elif path.suffix in ['.pdf', '.zip', '.png', '.jpg']:
            return "ملف غير ضروري للمشروع"
        else:
            return "ملف مشبوه"

    def _generate_recommendations(self) -> List[str]:
        """توليد التوصيات"""
        recommendations = []

        if self.duplicates:
            recommendations.append("🗑️ حذف الملفات المكررة لتوفير المساحة")

        if self.unnecessary_files:
            recommendations.append("🧹 تنظيف الملفات غير المهمة")

        if len(self.venv_files) > 100:
            recommendations.append("📁 إضافة venv/ إلى .gitignore")

        if len(self.test_files) > 200:
            recommendations.append("🧪 تنظيم ملفات الاختبار")

        recommendations.extend([
            "📋 مراجعة الملفات التجريبية",
            "🗂️ تنظيم هيكل المجلدات",
            "📝 تحديث .gitignore"
        ])

        return recommendations

    def _display_summary(self, report: Dict):
        """عرض ملخص التقرير"""
        print("\n" + "="*80)
        print("🔍 تقرير تحليل الملفات المكررة وغير المهمة")
        print("="*80)
        print(
            f"📁 إجمالي ملفات المشروع: {report['summary']['total_project_files']}")
        print(f"🐍 ملفات venv: {report['summary']['total_venv_files']}")
        print(f"🧪 ملفات اختبار: {report['summary']['total_test_files']}")
        print(f"📜 ملفات سكريبت: {report['summary']['total_script_files']}")
        print(f"🔄 مجموعات مكررة: {report['summary']['duplicate_groups']}")
        print(f"🗑️ ملفات غير مهمة: {report['summary']['unnecessary_files']}")
        print("="*80)

        if report['duplicates']:
            print("\n🔄 الملفات المكررة:")
            for hash_val, info in report['duplicates'].items():
                print(
                    f"  📦 {info['count']} ملفات متطابقة ({info['size_mb']} MB):")
                for file_path in info['files']:
                    print(f"    • {file_path}")

        if report['unnecessary_files']:
            print("\n🗑️ الملفات غير المهمة (أول 20):")
            for item in report['unnecessary_files'][:20]:
                print(f"  • {item['file']} - {item['reason']}")

        print("\n💡 التوصيات:")
        for rec in report['recommendations']:
            print(f"  {rec}")


def main():
    """الدالة الرئيسية"""
    analyzer = DuplicateAnalyzer()
    analyzer.analyze_project_structure()


if __name__ == "__main__":
    main()
