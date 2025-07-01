import logging

logger = logging.getLogger(__name__)

"""
Fix Imports Checker - مُصحح الاستدعاءات
=========================================
التحقق من صحة الاستدعاءات وإصلاحها
"""
import os
from pathlib import Path
from typing import List


class ImportsChecker:

    def __init__(self):
        self.src_dir = Path("src")
        self.broken_imports = []
        self.fixed_imports = []
        self.missing_files = []

    def scan_all_python_files(self) -> List[Path]:
        """مسح جميع ملفات Python في المشروع"""
        python_files = []
        for root, dirs, files in os.walk(self.src_dir):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)
        return python_files

    def check_imports_in_file(self, file_path: Path) -> List[str]:
        """فحص الاستدعاءات في ملف واحد"""
        broken_imports = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "_ddd" in content:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "_ddd" in line and ("import" in line or "from" in line):
                        broken_imports.append(f"Line {i + 1}: {line.strip()}")
            if "value_objects.py" in content or "from.*value_objects import" in content:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "value_objects" in line and ("import" in line or "from" in line):
                        broken_imports.append(f"Line {i + 1}: {line.strip()}")
        except Exception as e:
            broken_imports.append(f"Error reading file: {e}")
        return broken_imports

    def check_file_exists(self, import_path: str) -> bool:
        """التحقق من وجود الملف المستدعى"""
        if import_path.startswith("src."):
            file_path = import_path.replace("src.", "src/").replace(".", "/") + ".py"
            return Path(file_path).exists()
        return True

    def suggest_fix_for_import(self, broken_import: str) -> str:
        """اقتراح إصلاح للاستدعاء المكسور"""
        if "_ddd" in broken_import:
            fixed = broken_import.replace("_ddd", "")
            return f"Suggested fix: {fixed}"
        if "value_objects" in broken_import:
            if "accessibility" in broken_import:
                return "Suggested fix: from src.domain.accessibility.value_objects.special_need_type import SpecialNeedType"
            elif "memory" in broken_import:
                return "Suggested fix: from src.domain.memory.entities.memory import Memory"
        return "Manual fix required"

    def generate_comprehensive_report(self) -> str:
        """إنشاء تقرير شامل"""
        python_files = self.scan_all_python_files()
        logger.info(f"🔍 فحص {len(python_files)} ملف Python...")
        files_with_issues = {}
        total_broken_imports = 0
        for file_path in python_files:
            broken_imports = self.check_imports_in_file(file_path)
            if broken_imports:
                files_with_issues[str(file_path)] = broken_imports
                total_broken_imports += len(broken_imports)
        report = f"""# تقرير فحص الاستدعاءات والبنية
===============================

## 📊 ملخص الفحص
- إجمالي الملفات المفحوصة: {len(python_files)}
- ملفات تحتوي على مشاكل: {len(files_with_issues)}
- إجمالي الاستدعاءات المكسورة: {total_broken_imports}

## 🚨 الملفات التي تحتوي على مشاكل:

"""
        if files_with_issues:
            for file_path, issues in files_with_issues.items():
                report += f"### 📄 {file_path}\n"
                for issue in issues:
                    report += f"- ❌ {issue}\n"
                    report += f"  💡 {self.suggest_fix_for_import(issue)}\n"
                report += "\n"
        else:
            report += "✅ **لا توجد مشاكل في الاستدعاءات!**\n\n"
        report += self._check_ddd_structure()
        report += self._generate_fix_recommendations()
        return report

    def _check_ddd_structure(self) -> str:
        """فحص بنية DDD"""
        structure_report = "## 🏗️ فحص بنية DDD\n\n### Domain Layer\n"
        domain_dir = self.src_dir / "domain"
        if domain_dir.exists():
            domains = [
                d
                for d in domain_dir.iterdir()
                if d.is_dir() and not d.name.startswith("__")
            ]
            structure_report += f"- عدد الـ Domains: {len(domains)}\n"
            for domain in domains:
                entities_count = (
                    len(list((domain / "entities").glob("*.py")))
                    if (domain / "entities").exists()
                    else 0
                )
                vo_count = (
                    len(list((domain / "value_objects").glob("*.py")))
                    if (domain / "value_objects").exists()
                    else 0
                )
                structure_report += f"""  - {domain.name}: {entities_count} entities, {vo_count} value objects
"""
        else:
            structure_report += "❌ مجلد Domain غير موجود\n"
        structure_report += "\n### Application Layer\n"
        app_dir = self.src_dir / "application"
        if app_dir.exists():
            apps = [
                d
                for d in app_dir.iterdir()
                if d.is_dir() and not d.name.startswith("__")
            ]
            structure_report += f"- عدد Application Domains: {len(apps)}\n"
            for app in apps:
                services_count = (
                    len(list((app / "services").glob("*.py")))
                    if (app / "services").exists()
                    else 0
                )
                uc_count = (
                    len(list((app / "use_cases").glob("*.py")))
                    if (app / "use_cases").exists()
                    else 0
                )
                structure_report += f"""  - {app.name}: {services_count} services, {uc_count} use cases
"""
        else:
            structure_report += "❌ مجلد Application غير موجود\n"
        return structure_report + "\n"

    def _generate_fix_recommendations(self) -> str:
        """إنشاء توصيات الإصلاح"""
        return """## 💡 توصيات الإصلاح

### الخطوات المطلوبة:
1. **إزالة الاستدعاءات المكسورة**: حذف جميع الاستدعاءات التي تحتوي على `_ddd`
2. **تحديث المسارات**: تحديث الاستدعاءات لتشير إلى البنية الجديدة
3. **إنشاء الملفات الناقصة**: إضافة الملفات المطلوبة في البنية الصحيحة
4. **اختبار الاستدعاءات**: التأكد من عمل جميع الاستدعاءات

### مثال على الإصلاح:
```python
# ❌ قبل الإصلاح
from src.application.services.accessibility_ddd.domain import AccessibilityProfile

# ✅ بعد الإصلاح  
from src.domain.accessibility.entities.accessibility_profile import AccessibilityProfile
```

### أولويات الإصلاح:
1. **عالية**: ملفات تحتوي على أكثر من 5 استدعاءات مكسورة
2. **متوسطة**: ملفات تحتوي على 1-5 استدعاءات مكسورة
3. **منخفضة**: ملفات تحتاج تنظيف عام

"""


def main():
    logger.info("=" * 60)
    logger.info("🔍 بدء فحص الاستدعاءات والبنية...")
    logger.info("=" * 60)
    checker = ImportsChecker()
    report = checker.generate_comprehensive_report()
    report_file = Path("IMPORTS_AND_STRUCTURE_REPORT.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info(f"✅ تم إنشاء التقرير: {report_file}")
    lines = report.split("\n")
    summary_lines = [
        line for line in lines if "إجمالي" in line or "ملفات تحتوي" in line
    ]
    logger.info("\n📊 ملخص النتائج:")
    for line in summary_lines:
        if line.strip():
            logger.info(f"  {line.strip()}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
