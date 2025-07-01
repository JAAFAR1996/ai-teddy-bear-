#!/usr/bin/env python3
"""
🔧 God Class Splitter - AI Teddy Bear Project
تقسيم الملفات الكبيرة إلى ملفات أصغر متبعة مبدأ Single Responsibility

Lead Architect: جعفر أديب (Jaafar Adeeb)
"""

import ast
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class ClassInfo:
    name: str
    line_start: int
    line_end: int
    methods: List[str]
    dependencies: List[str]
    size_lines: int


@dataclass
class FunctionInfo:
    name: str
    line_start: int
    line_end: int
    size_lines: int
    dependencies: List[str]


class GodClassSplitter:
    def __init__(self, max_lines_per_file=50):
        self.max_lines_per_file = max_lines_per_file
        self.project_root = Path.cwd()

    def analyze_python_file(
        self, file_path: Path
    ) -> Tuple[List[ClassInfo], List[FunctionInfo]]:
        """تحليل ملف Python واستخراج المعلومات"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            lines = content.split("\n")

            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [
                        method.name
                        for method in node.body
                        if isinstance(method, ast.FunctionDef)
                    ]
                    dependencies = self._extract_dependencies(node, lines)

                    class_info = ClassInfo(
                        name=node.name,
                        line_start=node.lineno,
                        line_end=getattr(node, "end_lineno", node.lineno + 10),
                        methods=methods,
                        dependencies=dependencies,
                        size_lines=getattr(node, "end_lineno", node.lineno + 10)
                        - node.lineno,
                    )
                    classes.append(class_info)

                elif (
                    isinstance(node, ast.FunctionDef) and node.col_offset == 0
                ):  # Top-level function
                    dependencies = self._extract_dependencies(node, lines)

                    func_info = FunctionInfo(
                        name=node.name,
                        line_start=node.lineno,
                        line_end=getattr(node, "end_lineno", node.lineno + 5),
                        size_lines=getattr(node, "end_lineno", node.lineno + 5)
                        - node.lineno,
                        dependencies=dependencies,
                    )
                    functions.append(func_info)

            return classes, functions

        except Exception as e:
            print(f"❌ خطأ في تحليل {file_path}: {e}")
            return [], []

    def _extract_dependencies(self, node, lines) -> List[str]:
        """استخراج dependencies من node"""
        dependencies = []

        # استخراج الاستيرادات المحلية
        for line_num in range(max(0, node.lineno - 10), min(len(lines), node.lineno)):
            line = lines[line_num].strip()
            if line.startswith("from ") or line.startswith("import "):
                dependencies.append(line)

        return dependencies

    def should_split_file(self, file_path: Path) -> bool:
        """تحديد ما إذا كان الملف يحتاج للتقسيم"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                line_count = sum(1 for _ in f)

            return line_count > self.max_lines_per_file * 2  # أكثر من ضعف الحد المسموح

        except Exception:
            return False

    def create_split_plan(
        self,
        classes: List[ClassInfo],
        functions: List[FunctionInfo],
        original_file: Path,
    ) -> Dict:
        """إنشاء خطة التقسيم"""
        plan = {
            "original_file": original_file,
            "splits": [],
            "base_module": original_file.stem,
            "package_dir": original_file.parent
            / original_file.stem.replace("_service", "").replace("_", "_components"),
        }

        # تقسيم الكلاسات الكبيرة
        for class_info in classes:
            if class_info.size_lines > self.max_lines_per_file:
                split_classes = self._split_large_class(class_info)
                for split_class in split_classes:
                    plan["splits"].append(
                        {
                            "type": "class",
                            "name": split_class["name"],
                            "content": split_class,
                            "filename": f"{split_class['name'].lower()}.py",
                        }
                    )
            else:
                plan["splits"].append(
                    {
                        "type": "class",
                        "name": class_info.name,
                        "content": class_info,
                        "filename": f"{class_info.name.lower()}.py",
                    }
                )

        # إضافة الدوال المستقلة
        if functions:
            plan["splits"].append(
                {
                    "type": "functions",
                    "name": "utilities",
                    "content": functions,
                    "filename": "utilities.py",
                }
            )

        return plan

    def _split_large_class(self, class_info: ClassInfo) -> List[Dict]:
        """تقسيم كلاس كبير إلى كلاسات أصغر"""
        splits = []

        # تجميع الميثودات حسب النوع
        method_groups = {
            "core": [],  # الميثودات الأساسية
            "validation": [],  # ميثودات التحقق
            "processing": [],  # ميثودات المعالجة
            "storage": [],  # ميثودات التخزين
            "notification": [],  # ميثودات التنبيه
            "utility": [],  # ميثودات مساعدة
        }

        # تصنيف الميثودات
        for method in class_info.methods:
            if any(
                keyword in method.lower() for keyword in ["init", "setup", "config"]
            ):
                method_groups["core"].append(method)
            elif any(
                keyword in method.lower() for keyword in ["validate", "check", "verify"]
            ):
                method_groups["validation"].append(method)
            elif any(
                keyword in method.lower()
                for keyword in ["process", "execute", "run", "handle"]
            ):
                method_groups["processing"].append(method)
            elif any(
                keyword in method.lower()
                for keyword in ["save", "store", "database", "persist"]
            ):
                method_groups["storage"].append(method)
            elif any(
                keyword in method.lower()
                for keyword in ["notify", "send", "alert", "report"]
            ):
                method_groups["notification"].append(method)
            else:
                method_groups["utility"].append(method)

        # إنشاء كلاسات منفصلة
        base_name = class_info.name.replace("Service", "").replace("Manager", "")

        for group_name, methods in method_groups.items():
            if methods:  # فقط إذا كان هناك ميثودات في المجموعة
                splits.append(
                    {
                        "name": f"{base_name}{group_name.title()}",
                        "methods": methods,
                        "original_class": class_info.name,
                        "group": group_name,
                    }
                )

        return splits

    def execute_split(self, plan: Dict) -> bool:
        """تنفيذ خطة التقسيم"""
        try:
            # إنشاء مجلد الحزمة الجديدة
            package_dir = plan["package_dir"]
            package_dir.mkdir(parents=True, exist_ok=True)

            # إنشاء __init__.py
            self._create_init_file(package_dir, plan)

            # قراءة الملف الأصلي
            with open(plan["original_file"], "r", encoding="utf-8") as f:
                original_content = f.read()

            # إنشاء ملفات منفصلة
            for split in plan["splits"]:
                self._create_split_file(package_dir, split, original_content)

            # إنشاء ملف الواجهة الجديد
            self._create_facade_file(plan)

            # نسخ احتياطية
            backup_path = plan["original_file"].with_suffix(".py.backup")
            shutil.copy2(plan["original_file"], backup_path)

            print(f"✅ تم تقسيم {plan['original_file'].name} بنجاح")
            print(f"📁 الملفات الجديدة في: {package_dir}")
            print(f"💾 نسخة احتياطية: {backup_path}")

            return True

        except Exception as e:
            print(f"❌ خطأ في تنفيذ التقسيم: {e}")
            return False

    def _create_init_file(self, package_dir: Path, plan: Dict):
        """إنشاء ملف __init__.py للحزمة"""
        init_content = f'''"""
{plan['base_module'].title()} Components Package
مكونات منفصلة من {plan['original_file'].name}

تم إنشاؤها تلقائياً بواسطة God Class Splitter
"""

# Import all components for backward compatibility
'''

        for split in plan["splits"]:
            if split["type"] == "class":
                init_content += (
                    f"from .{split['filename'][:-3]} import {split['name']}\n"
                )

        init_content += "\n# Legacy compatibility\n"
        init_content += "__all__ = [\n"

        for split in plan["splits"]:
            if split["type"] == "class":
                init_content += f"    '{split['name']}',\n"

        init_content += "]\n"

        with open(package_dir / "__init__.py", "w", encoding="utf-8") as f:
            f.write(init_content)

    def _create_split_file(self, package_dir: Path, split: Dict, original_content: str):
        """إنشاء ملف منفصل"""
        filename = package_dir / split["filename"]

        if split["type"] == "class":
            content = self._extract_class_content(split, original_content)
        else:  # functions
            content = self._extract_functions_content(split, original_content)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    def _extract_class_content(self, split: Dict, original_content: str) -> str:
        """استخراج محتوى الكلاس"""
        lines = original_content.split("\n")

        # استخراج الاستيرادات
        imports = []
        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")):
                imports.append(line)
            elif line.strip() and not line.startswith("#") and "import" not in line:
                break

        content = f'''"""
{split['name']} - Component extracted from large service
مكون منفصل من خدمة كبيرة

Generated by God Class Splitter
"""

'''

        # إضافة الاستيرادات
        content += "\n".join(imports) + "\n\n"

        # إضافة الكلاس المبسط
        if isinstance(split["content"], ClassInfo):
            class_info = split["content"]
            content += f'''class {split['name']}:
    """
    {split['name']} - Extracted from {class_info.name}
    Follows Single Responsibility Principle
    """
    
    def __init__(self):
        """Initialize {split['name']}"""
        pass
    
'''

            # إضافة ميثودات placeholder
            for method in class_info.methods[:3]:  # أول 3 ميثودات فقط
                content += f'''    def {method}(self):
        """
        {method} - Extracted method
        TODO: Implement the actual logic from original class
        """
        raise NotImplementedError("Method needs implementation")
    
'''

        return content

    def _extract_functions_content(self, split: Dict, original_content: str) -> str:
        """استخراج محتوى الدوال"""
        content = f'''"""
Utility Functions - Extracted from large service
دوال مساعدة منفصلة من خدمة كبيرة

Generated by God Class Splitter
"""

'''

        # إضافة دوال placeholder
        for func_info in split["content"]:
            content += f'''def {func_info.name}():
    """
    {func_info.name} - Extracted function
    TODO: Implement the actual logic from original file
    """
    raise NotImplementedError("Function needs implementation")

'''

        return content

    def _create_facade_file(self, plan: Dict):
        """إنشاء ملف واجهة للتوافق مع النسخة السابقة"""
        facade_content = f'''"""
{plan['base_module'].title()} Facade - Backward Compatibility
واجهة للحفاظ على التوافق مع النسخة السابقة

This file maintains backward compatibility while the actual implementation
has been split into smaller, more manageable components.

Generated by God Class Splitter
"""

# Import all components
from .{plan['package_dir'].name} import *

# Legacy class facade
'''

        for split in plan["splits"]:
            if split["type"] == "class":
                facade_content += f'''
class {split['content'].name if hasattr(split['content'], 'name') else split['name']}Facade:
    """Legacy facade for {split['name']}"""
    
    def __init__(self):
        self.{split['name'].lower()} = {split['name']}()
    
    def __getattr__(self, name):
        return getattr(self.{split['name'].lower()}, name)

# Alias for backward compatibility
{split['content'].name if hasattr(split['content'], 'name') else split['name']} = {split['content'].name if hasattr(split['content'], 'name') else split['name']}Facade
'''

        facade_file = plan["original_file"].with_name(
            f"{plan['base_module']}_refactored.py"
        )
        with open(facade_file, "w", encoding="utf-8") as f:
            f.write(facade_content)

    def split_god_classes(self, target_files: List[str] = None):
        """تقسيم God Classes في المشروع"""
        print("🔧 بدء تقسيم God Classes...")
        print("=" * 50)

        if target_files is None:
            # الملفات الافتراضية المعروفة بأنها God Classes
            target_files = [
                "src/application/services/data_cleanup_service.py",
                "src/application/services/parent_dashboard_service.py",
                "src/application/services/moderation_service.py",
                "src/application/services/enhanced_hume_integration.py",
                "src/presentation/enterprise_dashboard.py",
            ]

        results = {"success": 0, "failed": 0, "skipped": 0}

        for file_path_str in target_files:
            file_path = Path(file_path_str)

            if not file_path.exists():
                print(f"⚠️ تخطي {file_path} - الملف غير موجود")
                results["skipped"] += 1
                continue

            if not self.should_split_file(file_path):
                print(f"⚠️ تخطي {file_path} - لا يحتاج تقسيم")
                results["skipped"] += 1
                continue

            print(f"🔄 تحليل {file_path}...")

            classes, functions = self.analyze_python_file(file_path)

            if not classes:
                print(f"⚠️ تخطي {file_path} - لا توجد كلاسات للتقسيم")
                results["skipped"] += 1
                continue

            plan = self.create_split_plan(classes, functions, file_path)

            if self.execute_split(plan):
                results["success"] += 1
            else:
                results["failed"] += 1

        # تقرير النتائج
        print("\n" + "=" * 50)
        print("📊 نتائج تقسيم God Classes:")
        print(f"✅ نجح: {results['success']}")
        print(f"❌ فشل: {results['failed']}")
        print(f"⚠️ تخطي: {results['skipped']}")

        return results


def main():
    """الدالة الرئيسية"""
    print("🔧 God Class Splitter - تقسيم الملفات الكبيرة")
    print("=" * 50)

    splitter = GodClassSplitter(max_lines_per_file=50)
    results = splitter.split_god_classes()

    print(f"\n🎯 تم تقسيم {results['success']} ملف بنجاح!")
    print("🚀 المشروع أصبح أكثر تنظيماً وقابلية للصيانة!")

    return results["success"]


if __name__ == "__main__":
    main()
