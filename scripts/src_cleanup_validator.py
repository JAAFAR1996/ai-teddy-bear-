#!/usr/bin/env python3
"""
سكربت التحقق من سلامة المشروع بعد عملية تنظيف مجلد src
يتبع المعايير المؤسسية لعام 2025
"""

import ast
import importlib.util
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """نتيجة فحص السلامة"""

    file_path: str
    status: str  # "OK", "WARNING", "ERROR"
    message: str
    details: str = ""


class ProjectValidator:
    """فاحص سلامة المشروع المتقدم"""

    def __init__(self, src_directory: str = "src"):
        self.src_dir = Path(src_directory)
        self.results: List[ValidationResult] = []
        self.errors_count = 0
        self.warnings_count = 0
        self.success_count = 0

    def validate_imports(self) -> List[ValidationResult]:
        """فحص جميع الاستيرادات في ملفات Python"""
        logger.info("[VALIDATING] فحص الاستيرادات...")
        import_results = []

        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # تحليل الملف للحصول على الاستيرادات
                try:
                    tree = ast.parse(content)
                    imports = []

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            module = node.module or ""
                            for alias in node.names:
                                imports.append(
                                    f"{module}.{alias.name}" if module else alias.name
                                )

                    # فحص كل استيراد
                    broken_imports = []
                    for imp in imports:
                        if not self._can_import(imp):
                            broken_imports.append(imp)

                    if broken_imports:
                        import_results.append(
                            ValidationResult(
                                file_path=str(py_file),
                                status="ERROR",
                                message="استيرادات مكسورة",
                                details=f"Broken imports: {', '.join(broken_imports)}",
                            )
                        )
                        self.errors_count += 1
                    else:
                        import_results.append(
                            ValidationResult(
                                file_path=str(py_file),
                                status="OK",
                                message="جميع الاستيرادات تعمل بشكل صحيح",
                            )
                        )
                        self.success_count += 1

                except SyntaxError as e:
                    import_results.append(
                        ValidationResult(
                            file_path=str(py_file),
                            status="ERROR",
                            message="خطأ في بناء الملف",
                            details=str(e),
                        )
                    )
                    self.errors_count += 1

            except Exception as e:
                import_results.append(
                    ValidationResult(
                        file_path=str(py_file),
                        status="ERROR",
                        message="لا يمكن قراءة الملف",
                        details=str(e),
                    )
                )
                self.errors_count += 1

        return import_results

    def _can_import(self, module_name: str) -> bool:
        """فحص إمكانية استيراد وحدة معينة"""
        try:
            # تجاهل الوحدات النسبية والمحلية للمشروع
            if module_name.startswith(".") or module_name.startswith("src."):
                return True

            # فحص الوحدات المعيارية
            if module_name in sys.builtin_module_names:
                return True

            # محاولة استيراد الوحدة
            spec = importlib.util.find_spec(module_name.split(".")[0])
            return spec is not None

        except (ImportError, ValueError, AttributeError):
            return False

    def validate_file_structure(self) -> List[ValidationResult]:
        """فحص بنية الملفات"""
        logger.info("[VALIDATING] فحص بنية الملفات...")
        structure_results = []

        # فحص المجلدات الأساسية المطلوبة
        required_dirs = [
            "domain",
            "application",
            "infrastructure",
            "presentation",
            "shared",
        ]

        for dir_name in required_dirs:
            dir_path = self.src_dir / dir_name
            if not dir_path.exists():
                structure_results.append(
                    ValidationResult(
                        file_path=str(dir_path),
                        status="WARNING",
                        message=f"مجلد مطلوب مفقود: {dir_name}",
                        details="Clean Architecture structure",
                    )
                )
                self.warnings_count += 1
            else:
                structure_results.append(
                    ValidationResult(
                        file_path=str(dir_path),
                        status="OK",
                        message=f"مجلد موجود: {dir_name}",
                    )
                )
                self.success_count += 1

        # فحص ملفات __init__.py
        for dir_path in self.src_dir.rglob("*/"):
            if dir_path.is_dir() and not str(dir_path).endswith("__pycache__"):
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    structure_results.append(
                        ValidationResult(
                            file_path=str(init_file),
                            status="WARNING",
                            message="ملف __init__.py مفقود",
                            details=f"Directory: {dir_path}",
                        )
                    )
                    self.warnings_count += 1

        return structure_results

    def validate_config_files(self) -> List[ValidationResult]:
        """فحص ملفات التكوين"""
        logger.info("[VALIDATING] فحص ملفات التكوين...")
        config_results = []

        # فحص ملفات التكوين الأساسية
        config_files = [
            "config/config.json",
            "config/environments/production.json",
            "config/environments/development.json",
        ]

        for config_file in config_files:
            config_path = Path(config_file)
            if not config_path.exists():
                config_results.append(
                    ValidationResult(
                        file_path=str(config_path),
                        status="WARNING",
                        message="ملف تكوين مفقود",
                        details="قد يؤثر على عمل النظام",
                    )
                )
                self.warnings_count += 1
            else:
                config_results.append(
                    ValidationResult(
                        file_path=str(config_path),
                        status="OK",
                        message="ملف تكوين موجود",
                    )
                )
                self.success_count += 1

        return config_results

    def validate_empty_files(self) -> List[ValidationResult]:
        """فحص الملفات الفارغة"""
        logger.info("[VALIDATING] فحص الملفات الفارغة...")
        empty_results = []

        for file_path in self.src_dir.rglob("*"):
            if file_path.is_file() and file_path.stat().st_size == 0:
                # تجاهل ملفات __init__.py الفارغة (مقبولة)
                if file_path.name == "__init__.py":
                    empty_results.append(
                        ValidationResult(
                            file_path=str(file_path),
                            status="OK",
                            message="ملف __init__.py فارغ (مقبول)",
                        )
                    )
                    self.success_count += 1
                else:
                    empty_results.append(
                        ValidationResult(
                            file_path=str(file_path),
                            status="WARNING",
                            message="ملف فارغ",
                            details="قد يكون ملف غير مكتمل أو غير مطلوب",
                        )
                    )
                    self.warnings_count += 1

        return empty_results

    def check_database_paths(self) -> List[ValidationResult]:
        """فحص مسارات قواعد البيانات"""
        logger.info("[VALIDATING] فحص مسارات قواعد البيانات...")
        db_results = []

        # البحث عن ملفات .db في src (لا يجب أن تكون هناك)
        db_files_in_src = list(self.src_dir.rglob("*.db"))

        for db_file in db_files_in_src:
            db_results.append(
                ValidationResult(
                    file_path=str(db_file),
                    status="ERROR",
                    message="ملف قاعدة بيانات في src",
                    details="يجب نقل ملفات قواعد البيانات إلى مجلد data/",
                )
            )
            self.errors_count += 1

        if not db_files_in_src:
            db_results.append(
                ValidationResult(
                    file_path="src/",
                    status="OK",
                    message="لا توجد ملفات قواعد بيانات في src",
                )
            )
            self.success_count += 1

        return db_results

    def run_full_validation(self) -> Dict[str, any]:
        """تشغيل فحص شامل للسلامة"""
        logger.info("[START] بدء فحص سلامة المشروع...")

        # تجميع جميع نتائج الفحص
        all_results = []
        all_results.extend(self.validate_imports())
        all_results.extend(self.validate_file_structure())
        all_results.extend(self.validate_config_files())
        all_results.extend(self.validate_empty_files())
        all_results.extend(self.check_database_paths())

        self.results = all_results

        # إنشاء التقرير
        report = self.generate_validation_report()

        logger.info(
            f"[COMPLETE] انتهى الفحص - النجاح: {self.success_count}, تحذيرات: {self.warnings_count}, أخطاء: {self.errors_count}"
        )

        return {
            "success_count": self.success_count,
            "warnings_count": self.warnings_count,
            "errors_count": self.errors_count,
            "results": all_results,
            "report_path": report,
            "overall_status": "PASS" if self.errors_count == 0 else "FAIL",
        }

    def generate_validation_report(self) -> str:
        """إنشاء تقرير فحص السلامة"""
        report_path = (
            Path("deleted/reports")
            / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report_content = f"""# 🔐 تقرير فحص سلامة المشروع

## ملخص النتائج
- **تاريخ الفحص**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **الحالة العامة**: {"✅ PASS" if self.errors_count == 0 else "❌ FAIL"}
- **النجاح**: {self.success_count}
- **التحذيرات**: {self.warnings_count}
- **الأخطاء**: {self.errors_count}

## تفاصيل النتائج

### ✅ النجاح ({self.success_count})
"""

        for result in self.results:
            if result.status == "OK":
                report_content += f"- **{result.file_path}**: {result.message}\n"

        report_content += f"\n### ⚠️ التحذيرات ({self.warnings_count})\n"
        for result in self.results:
            if result.status == "WARNING":
                report_content += f"- **{result.file_path}**: {result.message}\n"
                if result.details:
                    report_content += f"  - التفاصيل: {result.details}\n"

        report_content += f"\n### ❌ الأخطاء ({self.errors_count})\n"
        for result in self.results:
            if result.status == "ERROR":
                report_content += f"- **{result.file_path}**: {result.message}\n"
                if result.details:
                    report_content += f"  - التفاصيل: {result.details}\n"

        report_content += """
## التوصيات

### أولوية عالية (الأخطاء)
- إصلاح جميع الأخطاء قبل النشر
- التأكد من عمل جميع الاستيرادات
- نقل ملفات قواعد البيانات خارج src/

### أولوية متوسطة (التحذيرات)
- إنشاء ملفات التكوين المفقودة
- إضافة ملفات __init__.py للمجلدات
- مراجعة الملفات الفارغة

---
*تم إنشاء هذا التقرير بواسطة أداة فحص سلامة المشروع v1.0*
"""

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"[REPORT] تم إنشاء تقرير السلامة: {report_path}")
            return str(report_path)
        except Exception as e:
            logger.error(f"[ERROR] خطأ في إنشاء التقرير: {e}")
            return ""


def main():
    """الدالة الرئيسية"""
    try:
        validator = ProjectValidator()
        results = validator.run_full_validation()

        print(f"\n{'='*60}")
        print("🔐 تقرير فحص سلامة المشروع")
        print(f"{'='*60}")
        print(f"✅ النجاح: {results['success_count']}")
        print(f"⚠️  التحذيرات: {results['warnings_count']}")
        print(f"❌ الأخطاء: {results['errors_count']}")
        print(f"📊 الحالة العامة: {results['overall_status']}")
        print(f"📄 التقرير: {results['report_path']}")
        print(f"{'='*60}")

        # إنهاء مع كود الخطأ إذا كانت هناك أخطاء
        sys.exit(0 if results["errors_count"] == 0 else 1)

    except Exception as e:
        logger.error(f"[ERROR] خطأ في تشغيل فحص السلامة: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
