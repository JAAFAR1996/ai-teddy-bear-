import ast
import hashlib
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ProjectCleaner:
    """منظف شامل لمشروع AI Teddy Bear"""

    def __init__(
        self,
        project_root: str = ".",
        analysis_file: str = "scripts/project_analysis.json",
    ):
        self.project_root = Path(project_root)
        self.analysis_file = analysis_file
        self.backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.report = {
            "deleted_files": [],
            "moved_files": [],
            "merged_files": [],
            "errors": [],
            "warnings": [],
        }

        # قراءة تقرير التحليل
        try:
            with open(analysis_file, "r", encoding="utf-8") as f:
                self.analysis = json.load(f)
        except FileNotFoundError:
            print(
                "❌ لم يتم العثور على تقرير التحليل. يرجى تشغيل project_analyzer.py أولاً"
            )
            sys.exit(1)

    def run_full_cleanup(self, dry_run: bool = False):
        """تشغيل عملية التنظيف الكاملة"""
        print("🧹 بدء تنظيف مشروع AI Teddy Bear...")
        print(f"📁 مجلد النسخ الاحتياطي: {self.backup_dir}")

        if dry_run:
            print("⚠️  وضع التجربة - لن يتم تنفيذ أي تغييرات فعلية")

        # إنشاء مجلد النسخ الاحتياطي
        if not dry_run:
            os.makedirs(self.backup_dir, exist_ok=True)

        # 1. حذف الملفات غير المهمة
        print("\n🗑️ المرحلة 1: حذف الملفات غير المهمة...")
        self.remove_trash_files(dry_run)

        # 2. دمج الملفات المكررة
        print("\n🔄 المرحلة 2: دمج الملفات المكررة...")
        self.merge_duplicates(dry_run)

        # 3. إعادة تنظيم الهيكل
        print("\n📂 المرحلة 3: إعادة تنظيم الهيكل...")
        self.reorganize_structure(dry_run)

        # 4. تنظيف نهائي
        print("\n✨ المرحلة 4: التنظيف النهائي...")
        self.final_cleanup(dry_run)

        # 5. إنشاء التقرير
        print("\n📋 إنشاء التقرير النهائي...")
        self.generate_report()

        print("\n✅ اكتملت عملية التنظيف!")

    def remove_trash_files(self, dry_run: bool = False):
        """حذف الملفات غير المهمة"""
        trash_patterns = [
            "*_old.py",
            "*_backup.py",
            "*_temp.py",
            "*_copy.py",
            "*_bak.py",
            "*.pyc",
            "__pycache__/",
            ".pytest_cache/",
            ".mypy_cache/",
            "*.log",
            "*.tmp",
            "*.swp",
            ".DS_Store",
            "Thumbs.db",
        ]

        deleted_count = 0

        # حذف الملفات الفارغة
        for empty_file in self.analysis.get("empty_files", []):
            if os.path.exists(empty_file):
                if not dry_run:
                    self._backup_and_delete(empty_file)
                self.report["deleted_files"].append(
                    {"file": empty_file, "reason": "Empty file"}
                )
                deleted_count += 1
                print(f"  🗑️ حذف ملف فارغ: {empty_file}")

        # حذف الملفات بناءً على الأنماط
        for pattern in trash_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    if not dry_run:
                        self._backup_and_delete(str(file_path))
                    self.report["deleted_files"].append(
                        {
                            "file": str(file_path),
                            "reason": f"Matches pattern: {pattern}",
                        }
                    )
                    deleted_count += 1
                    print(f"  🗑️ حذف: {file_path}")

        # حذف الملفات المصنفة كـ trash في التحليل
        for file_info in self.analysis.get("detailed_analysis", []):
            if file_info.get("importance") == "trash":
                file_path = file_info["path"]
                if os.path.exists(file_path):
                    if not dry_run:
                        self._backup_and_delete(file_path)
                    self.report["deleted_files"].append(
                        {
                            "file": file_path,
                            "reason": f"Classified as trash: {', '.join(file_info.get('issues', []))}",
                        }
                    )
                    deleted_count += 1
                    print(f"  🗑️ حذف ملف غير مهم: {file_path}")

        print(f"\n✅ تم حذف {deleted_count} ملف غير مهم")

    def merge_duplicates(self, dry_run: bool = False):
        """دمج الملفات المكررة"""
        merged_count = 0

        for duplicate_group in self.analysis.get("duplicate_candidates", []):
            if duplicate_group["type"] == "exact":
                # دمج التكرارات الكاملة
                files = duplicate_group["files"]
                if len(files) > 1:
                    best_file = self._select_best_file(files)

                    for file in files:
                        if file != best_file and os.path.exists(file):
                            if not dry_run:
                                self._update_imports(file, best_file)
                                self._backup_and_delete(file)

                            self.report["merged_files"].append(
                                {
                                    "deleted": file,
                                    "kept": best_file,
                                    "type": "exact_duplicate",
                                }
                            )
                            merged_count += 1
                            print(f"  🔄 دمج: {file} -> {best_file}")

        print(f"\n✅ تم دمج {merged_count} ملف مكرر")

    def reorganize_structure(self, dry_run: bool = False):
        """إعادة تنظيم هيكل المشروع"""
        moved_count = 0

        # إنشاء الهيكل الجديد
        new_structure = {
            "src/core/domain/entities/": [],
            "src/core/domain/value_objects/": [],
            "src/core/domain/exceptions/": [],
            "src/core/services/": [],
            "src/core/interfaces/": [],
            "src/infrastructure/persistence/models/": [],
            "src/infrastructure/persistence/repositories/": [],
            "src/infrastructure/ai_providers/": [],
            "src/infrastructure/messaging/": [],
            "src/infrastructure/monitoring/": [],
            "src/api/rest/endpoints/": [],
            "src/api/rest/middleware/": [],
            "src/api/rest/schemas/": [],
            "src/api/websocket/": [],
            "src/esp32/": [],
            "src/shared/utils/": [],
            "src/shared/constants/": [],
            "tests/unit/": [],
            "tests/integration/": [],
            "tests/e2e/": [],
            "tests/fixtures/": [],
            "scripts/": [],
            "docs/": [],
            "configs/": [],
        }

        # تصنيف الملفات وتحديد أماكنها الجديدة
        for file_info in self.analysis.get("detailed_analysis", []):
            if file_info.get("importance") in ["critical", "high", "medium"]:
                current_path = file_info["path"]
                suggested_location = file_info.get("suggested_location")

                if suggested_location and os.path.exists(current_path):
                    # التحقق من أن الملف ليس في المكان الصحيح
                    if not Path(current_path).is_relative_to(
                        Path(suggested_location).parent
                    ):
                        if not dry_run:
                            self._move_file_with_imports(
                                current_path, suggested_location
                            )

                        self.report["moved_files"].append(
                            {
                                "from": current_path,
                                "to": suggested_location,
                                "type": file_info["type"],
                            }
                        )
                        moved_count += 1
                        print(f"  📂 نقل: {current_path} -> {suggested_location}")

        print(f"\n✅ تم نقل {moved_count} ملف إلى أماكنها الصحيحة")

    def final_cleanup(self, dry_run: bool = False):
        """التنظيف النهائي"""
        if not dry_run:
            print("  🎨 تنسيق الكود باستخدام black...")
            os.system("black src/ tests/ scripts/ --quiet")

            print("  📦 ترتيب الاستيرادات باستخدام isort...")
            os.system("isort src/ tests/ scripts/ --quiet")

            print("  🧹 حذف المجلدات الفارغة...")
            self._remove_empty_dirs()

        print("\n✅ اكتمل التنظيف النهائي")

    def _backup_and_delete(self, file_path: str):
        """نسخ احتياطي وحذف الملف"""
        try:
            # إنشاء مسار النسخ الاحتياطي
            backup_path = os.path.join(
                self.backup_dir, os.path.relpath(file_path, self.project_root)
            )
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)

            # نسخ الملف
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
                os.remove(file_path)
        except Exception as e:
            self.report["errors"].append(f"Error deleting {file_path}: {e}")

    def _select_best_file(self, files: List[str]) -> str:
        """اختيار أفضل ملف من المكررات"""
        # معايير الاختيار
        scores = {}

        for file in files:
            score = 0

            # الملف في المكان الصحيح يحصل على نقاط أكثر
            if "src/" in file:
                score += 10
            if "core/" in file:
                score += 5

            # الملف الأكبر (أكثر اكتمالاً)
            try:
                size = os.path.getsize(file)
                score += size // 1000  # نقطة لكل KB
            except:
                pass

            # الملف مع اختبارات
            test_file = file.replace(".py", "_test.py")
            if os.path.exists(test_file):
                score += 20

            # تجنب الملفات القديمة
            if any(x in file for x in ["old", "backup", "temp", "copy"]):
                score -= 50

            scores[file] = score

        # اختيار الملف مع أعلى نقاط
        return max(scores.items(), key=lambda x: x[1])[0]

    def _update_imports(self, old_file: str, new_file: str):
        """تحديث الاستيرادات في جميع الملفات"""
        # تحويل المسارات إلى استيرادات Python
        old_import = self._path_to_import(old_file)
        new_import = self._path_to_import(new_file)

        if old_import == new_import:
            return

        # البحث عن جميع ملفات Python
        for py_file in self.project_root.rglob("*.py"):
            if py_file.is_file():
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # استبدال الاستيرادات
                    updated_content = content
                    updated_content = re.sub(
                        f"from {old_import} import",
                        f"from {new_import} import",
                        updated_content,
                    )
                    updated_content = re.sub(
                        f"import {old_import}", f"import {new_import}", updated_content
                    )

                    if updated_content != content:
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(updated_content)
                except:
                    pass

    def _path_to_import(self, file_path: str) -> str:
        """تحويل مسار الملف إلى استيراد Python"""
        # إزالة .py
        import_path = file_path.replace(".py", "")

        # تحويل المسارات إلى نقاط
        import_path = import_path.replace(os.sep, ".")
        import_path = import_path.replace("/", ".")

        # إزالة المسار النسبي
        if import_path.startswith("."):
            import_path = import_path[1:]

        return import_path

    def _move_file_with_imports(self, old_path: str, new_path: str):
        """نقل ملف مع تحديث جميع الاستيرادات"""
        try:
            # إنشاء المجلد الجديد
            os.makedirs(os.path.dirname(new_path), exist_ok=True)

            # تحديث الاستيرادات أولاً
            self._update_imports(old_path, new_path)

            # نقل الملف
            shutil.move(old_path, new_path)
        except Exception as e:
            self.report["errors"].append(f"Error moving {old_path}: {e}")

    def _remove_empty_dirs(self):
        """حذف المجلدات الفارغة"""
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # المجلد فارغ
                        os.rmdir(dir_path)
                except:
                    pass

    def generate_report(self):
        """إنشاء تقرير التنظيف"""
        report_content = f"""# 📊 تقرير تنظيف مشروع AI Teddy Bear

## 📅 معلومات التنظيف
- **التاريخ**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **مجلد النسخ الاحتياطي**: `{self.backup_dir}/`

## 📈 الإحصائيات

### 🗑️ الملفات المحذوفة: {len(self.report['deleted_files'])}
"""

        # تفاصيل الملفات المحذوفة
        if self.report["deleted_files"]:
            report_content += "\n| الملف | السبب |\n|-------|-------|\n"
            for item in self.report["deleted_files"][:10]:  # أول 10 فقط
                report_content += (
                    f"| `{Path(item['file']).name}` | {item['reason']} |\n"
                )

            if len(self.report["deleted_files"]) > 10:
                report_content += (
                    f"\n... و {len(self.report['deleted_files']) - 10} ملف آخر\n"
                )

        report_content += (
            f"\n### 📂 الملفات المنقولة: {len(self.report['moved_files'])}\n"
        )

        # تفاصيل الملفات المنقولة
        if self.report["moved_files"]:
            report_content += "\n| من | إلى | النوع |\n|-----|------|-------|\n"
            for item in self.report["moved_files"][:10]:  # أول 10 فقط
                from_name = Path(item["from"]).name
                to_dir = Path(item["to"]).parent
                report_content += f"| `{from_name}` | `{to_dir}/` | {item['type']} |\n"

        report_content += (
            f"\n### 🔄 الملفات المدموجة: {len(self.report['merged_files'])}\n"
        )

        # تفاصيل الملفات المدموجة
        if self.report["merged_files"]:
            report_content += "\n| الملف المحذوف | الملف المحتفظ به | النوع |\n|----------------|------------------|-------|\n"
            for item in self.report["merged_files"][:10]:  # أول 10 فقط
                deleted_name = Path(item["deleted"]).name
                kept_name = Path(item["kept"]).name
                report_content += (
                    f"| `{deleted_name}` | `{kept_name}` | {item['type']} |\n"
                )

        # الأخطاء والتحذيرات
        if self.report["errors"]:
            report_content += f"\n## ❌ الأخطاء: {len(self.report['errors'])}\n"
            for error in self.report["errors"]:
                report_content += f"- {error}\n"

        report_content += """
## ✅ الخطوات التالية

1. [ ] مراجعة التغييرات في مجلد النسخ الاحتياطي
2. [ ] تشغيل جميع الاختبارات للتأكد من عدم كسر أي شيء
3. [ ] تحديث ملفات الاستيراد إذا لزم الأمر
4. [ ] commit التغييرات في Git
5. [ ] حذف مجلد النسخ الاحتياطي بعد التأكد من نجاح التنظيف

## 📝 ملاحظات
- جميع الملفات المحذوفة محفوظة في مجلد النسخ الاحتياطي
- يمكنك استرجاع أي ملف من النسخ الاحتياطي إذا لزم الأمر
- تم تحديث جميع الاستيرادات تلقائياً
"""

        # حفظ التقرير
        with open("cleanup_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)

        # حفظ تقرير JSON مفصل
        with open("cleanup_report.json", "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)

        print("\n✅ تم إنشاء التقارير:")
        print("  • cleanup_report.md - تقرير مقروء")
        print("  • cleanup_report.json - تقرير مفصل")


def main():
    """تشغيل منظف المشروع"""
    import argparse

    parser = argparse.ArgumentParser(description="تنظيف مشروع AI Teddy Bear")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="تشغيل في وضع التجربة دون تنفيذ التغييرات",
    )
    parser.add_argument(
        "--analysis-file",
        default="scripts/project_analysis.json",
        help="مسار ملف تقرير التحليل",
    )

    args = parser.parse_args()

    # التأكيد قبل البدء
    if not args.dry_run:
        print("⚠️  تحذير: سيقوم هذا السكريبت بحذف ونقل الملفات!")
        print("📁 سيتم حفظ نسخ احتياطية في مجلد backup_[timestamp]")
        response = input("\nهل تريد المتابعة؟ (yes/no): ")
        if response.lower() != "yes":
            print("❌ تم إلغاء العملية")
            return

    # تشغيل المنظف
    cleaner = ProjectCleaner(analysis_file=args.analysis_file)
    cleaner.run_full_cleanup(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
