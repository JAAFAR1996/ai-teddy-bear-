#!/usr/bin/env python3
"""
🔍 Advanced Duplicate Finder - AI Teddy Bear Project
محلل متقدم للملفات المكررة والأنماط المتكررة

Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise Grade AI Teddy Bear Project 2025
"""

import ast
import hashlib
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


@dataclass
class FileInfo:
    """معلومات الملف"""
    path: str
    size: int
    hash: str
    lines: int
    content: str
    imports: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    similarity_score: float = 0.0


@dataclass
class DuplicateGroup:
    """مجموعة ملفات مكررة"""
    type: str  # exact, similar, functional
    files: List[FileInfo]
    similarity: float
    recommendation: str


class AdvancedDuplicateFinder:
    """محلل متقدم للملفات المكررة"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.files_info: Dict[str, FileInfo] = {}
        self.duplicate_groups: List[DuplicateGroup] = []
        self.ignore_patterns = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', 'dist', 'build'
        }

    def scan_project(self) -> None:
        """مسح المشروع وجمع معلومات الملفات"""
        print("🔍 بدء مسح المشروع...")

        for file_path in self.project_root.rglob("*.py"):
            if self._should_ignore(file_path):
                continue

            try:
                file_info = self._analyze_file(file_path)
                if file_info:
                    self.files_info[str(file_path)] = file_info
            except Exception as e:
                print(f"❌ خطأ في تحليل {file_path}: {e}")

        print(f"✅ تم مسح {len(self.files_info)} ملف Python")

    def _should_ignore(self, file_path: Path) -> bool:
        """التحقق من أن الملف يجب تجاهله"""
        path_str = str(file_path)
        return any(pattern in path_str for pattern in self.ignore_patterns)

    def _analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        """تحليل ملف واحد بعمق"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # تجاهل الملفات الفارغة
            if len(content.strip()) == 0:
                return None

            # معلومات أساسية
            lines = len(content.splitlines())
            size = len(content)
            file_hash = hashlib.sha256(content.encode()).hexdigest()

            # تحليل AST
            imports, classes, functions = self._parse_ast(content)

            return FileInfo(
                path=str(file_path),
                size=size,
                hash=file_hash,
                lines=lines,
                content=content,
                imports=imports,
                classes=classes,
                functions=functions
            )

        except Exception as e:
            print(f"⚠️ خطأ في قراءة {file_path}: {e}")
            return None

    def _parse_ast(self, content: str) -> Tuple[List[str], List[str], List[str]]:
        """تحليل AST واستخراج الإيمبورتات والكلاسات والدوال"""
        try:
            tree = ast.parse(content)
            imports = []
            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    elif node.module:
                        imports.append(node.module)

                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

            return imports, classes, functions

        except:
            return [], [], []

    def find_exact_duplicates(self) -> None:
        """البحث عن الملفات المطابقة تماماً"""
        print("🔍 البحث عن الملفات المطابقة تماماً...")

        hash_groups = defaultdict(list)
        for file_info in self.files_info.values():
            hash_groups[file_info.hash].append(file_info)

        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                # تحديد أفضل ملف للاحتفاظ به
                best_file = self._select_best_file(files)
                recommendation = f"احتفظ بـ {best_file.path} واحذف الباقي"

                self.duplicate_groups.append(DuplicateGroup(
                    type="exact",
                    files=files,
                    similarity=1.0,
                    recommendation=recommendation
                ))

    def find_similar_files(self, threshold: float = 0.7) -> None:
        """البحث عن الملفات المشابهة"""
        print("🔍 البحث عن الملفات المشابهة...")

        files_list = list(self.files_info.values())
        processed_pairs = set()

        for i, file1 in enumerate(files_list):
            for j, file2 in enumerate(files_list[i+1:], i+1):
                pair_key = tuple(sorted([file1.path, file2.path]))
                if pair_key in processed_pairs:
                    continue
                processed_pairs.add(pair_key)

                similarity = self._calculate_similarity(file1, file2)
                if similarity >= threshold:
                    recommendation = self._generate_similarity_recommendation(
                        file1, file2, similarity)

                    self.duplicate_groups.append(DuplicateGroup(
                        type="similar",
                        files=[file1, file2],
                        similarity=similarity,
                        recommendation=recommendation
                    ))

    def find_functional_duplicates(self) -> None:
        """البحث عن الملفات المكررة وظيفياً"""
        print("🔍 البحث عن الملفات المكررة وظيفياً...")

        # تجميع الملفات بحسب الوظيفة
        function_groups = defaultdict(list)
        class_groups = defaultdict(list)

        for file_info in self.files_info.values():
            # تجميع حسب الدوال المشتركة
            if file_info.functions:
                func_signature = tuple(sorted(file_info.functions))
                if len(func_signature) > 2:  # فقط الملفات التي لها أكثر من دالتين
                    function_groups[func_signature].append(file_info)

            # تجميع حسب الكلاسات المشتركة
            if file_info.classes:
                class_signature = tuple(sorted(file_info.classes))
                if len(class_signature) > 0:
                    class_groups[class_signature].append(file_info)

        # إضافة المجموعات المكررة
        for signature, files in function_groups.items():
            if len(files) > 1:
                self.duplicate_groups.append(DuplicateGroup(
                    type="functional",
                    files=files,
                    similarity=0.8,
                    recommendation=f"دمج الدوال المشتركة: {', '.join(signature[:3])}..."
                ))

        for signature, files in class_groups.items():
            if len(files) > 1:
                self.duplicate_groups.append(DuplicateGroup(
                    type="functional",
                    files=files,
                    similarity=0.8,
                    recommendation=f"دمج الكلاسات المشتركة: {', '.join(signature[:3])}..."
                ))

    def _calculate_similarity(self, file1: FileInfo, file2: FileInfo) -> float:
        """حساب التشابه بين ملفين"""
        # تشابه الإيمبورتات
        imports1 = set(file1.imports)
        imports2 = set(file2.imports)
        import_similarity = len(imports1 & imports2) / \
            max(len(imports1 | imports2), 1)

        # تشابه الكلاسات
        classes1 = set(file1.classes)
        classes2 = set(file2.classes)
        class_similarity = len(classes1 & classes2) / \
            max(len(classes1 | classes2), 1)

        # تشابه الدوال
        functions1 = set(file1.functions)
        functions2 = set(file2.functions)
        function_similarity = len(
            functions1 & functions2) / max(len(functions1 | functions2), 1)

        # تشابه النص
        content_similarity = self._calculate_content_similarity(
            file1.content, file2.content)

        # متوسط مرجح
        return (import_similarity * 0.3 +
                class_similarity * 0.3 +
                function_similarity * 0.3 +
                content_similarity * 0.1)

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """حساب تشابه المحتوى النصي"""
        # تقسيم النص إلى كلمات
        words1 = set(re.findall(r'\b\w+\b', content1.lower()))
        words2 = set(re.findall(r'\b\w+\b', content2.lower()))

        # حساب التشابه
        return len(words1 & words2) / max(len(words1 | words2), 1)

    def _select_best_file(self, files: List[FileInfo]) -> FileInfo:
        """اختيار أفضل ملف للاحتفاظ به"""
        # الأولوية للملفات في src/
        for file_info in files:
            if 'src/' in file_info.path and 'test' not in file_info.path.lower():
                return file_info

        # ثم الملفات الأكبر (أكثر محتوى)
        return max(files, key=lambda f: f.size)

    def _generate_similarity_recommendation(self, file1: FileInfo, file2: FileInfo, similarity: float) -> str:
        """إنشاء توصية للملفات المتشابهة"""
        if similarity > 0.9:
            return f"دمج الملفين - تشابه عالي جداً ({similarity:.1%})"
        elif similarity > 0.8:
            return f"مراجعة الدمج - تشابه عالي ({similarity:.1%})"
        else:
            return f"مراجعة التشابه - ({similarity:.1%})"

    def analyze_service_duplicates(self) -> None:
        """تحليل الخدمات المكررة"""
        print("🔍 تحليل الخدمات المكررة...")

        service_types = {
            'ai': ['ai_service', 'ai_processor', 'ai_handler'],
            'audio': ['audio_service', 'voice_service', 'speech_service'],
            'emotion': ['emotion_service', 'emotion_analyzer', 'emotion_detector'],
            'transcription': ['transcription_service', 'speech_to_text', 'stt_service'],
            'synthesis': ['synthesis_service', 'text_to_speech', 'tts_service'],
            'cache': ['cache_service', 'caching_service', 'cache_manager'],
            'database': ['database_service', 'db_service', 'repository'],
            'security': ['security_service', 'auth_service', 'encryption_service']
        }

        service_groups = defaultdict(list)

        for file_info in self.files_info.values():
            filename = Path(file_info.path).name.lower()

            for service_type, patterns in service_types.items():
                if any(pattern in filename for pattern in patterns):
                    service_groups[service_type].append(file_info)
                    break

        # إضافة الخدمات المكررة
        for service_type, files in service_groups.items():
            if len(files) > 1:
                self.duplicate_groups.append(DuplicateGroup(
                    type="service",
                    files=files,
                    similarity=0.9,
                    recommendation=f"دمج خدمات {service_type} - عثر على {len(files)} نسخة"
                ))

    def generate_report(self) -> None:
        """إنشاء تقرير شامل"""
        print("📊 إنشاء التقرير...")

        # تقسيم المجموعات حسب النوع
        exact_duplicates = [
            g for g in self.duplicate_groups if g.type == "exact"]
        similar_files = [
            g for g in self.duplicate_groups if g.type == "similar"]
        functional_duplicates = [
            g for g in self.duplicate_groups if g.type == "functional"]
        service_duplicates = [
            g for g in self.duplicate_groups if g.type == "service"]

        # إنشاء التقرير
        report = {
            "timestamp": "2025-01-15T10:30:00",
            "total_files": len(self.files_info),
            "summary": {
                "exact_duplicates": len(exact_duplicates),
                "similar_files": len(similar_files),
                "functional_duplicates": len(functional_duplicates),
                "service_duplicates": len(service_duplicates),
                "total_issues": len(self.duplicate_groups)
            },
            "duplicates": {
                "exact": [self._serialize_group(g) for g in exact_duplicates],
                "similar": [self._serialize_group(g) for g in similar_files],
                "functional": [self._serialize_group(g) for g in functional_duplicates],
                "services": [self._serialize_group(g) for g in service_duplicates]
            }
        }

        # حفظ التقرير JSON
        with open("advanced_duplicate_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # إنشاء تقرير Markdown
        self._create_markdown_report(report)

        # طباعة الملخص
        self._print_summary(report)

    def _serialize_group(self, group: DuplicateGroup) -> Dict:
        """تسلسل مجموعة مكررة"""
        return {
            "type": group.type,
            "files": [f.path for f in group.files],
            "similarity": group.similarity,
            "recommendation": group.recommendation,
            "total_size": sum(f.size for f in group.files),
            "wasted_space": sum(f.size for f in group.files[1:]) if len(group.files) > 1 else 0
        }

    def _create_markdown_report(self, report: Dict) -> None:
        """إنشاء تقرير Markdown"""
        md_content = f"""# 🔍 تقرير الملفات المكررة المتقدم

## 📊 الملخص العام
- **إجمالي الملفات**: {report['total_files']}
- **الملفات المطابقة تماماً**: {report['summary']['exact_duplicates']}
- **الملفات المشابهة**: {report['summary']['similar_files']}
- **التكرار الوظيفي**: {report['summary']['functional_duplicates']}
- **الخدمات المكررة**: {report['summary']['service_duplicates']}

## 🎯 الملفات المطابقة تماماً
"""

        for group in report['duplicates']['exact']:
            md_content += f"""
### مجموعة مكررة ({len(group['files'])} ملفات)
**التوصية**: {group['recommendation']}
**المساحة المهدرة**: {group['wasted_space']} بايت

**الملفات**:
"""
            for file_path in group['files']:
                md_content += f"- `{file_path}`\n"

        md_content += "\n## 🔗 الملفات المشابهة\n"
        for group in report['duplicates']['similar']:
            md_content += f"""
### تشابه {group['similarity']:.1%}
**التوصية**: {group['recommendation']}
**الملفات**: {', '.join(f'`{f}`' for f in group['files'])}
"""

        md_content += "\n## ⚙️ الخدمات المكررة\n"
        for group in report['duplicates']['services']:
            md_content += f"""
### خدمة مكررة
**التوصية**: {group['recommendation']}
**الملفات**: {', '.join(f'`{f}`' for f in group['files'])}
"""

        with open("advanced_duplicate_report.md", "w", encoding="utf-8") as f:
            f.write(md_content)

    def _print_summary(self, report: Dict) -> None:
        """طباعة ملخص التقرير"""
        print("\n" + "="*80)
        print("🔍 تقرير الملفات المكررة المتقدم")
        print("="*80)
        print(f"📁 إجمالي الملفات: {report['total_files']}")
        print(
            f"🔄 الملفات المطابقة تماماً: {report['summary']['exact_duplicates']}")
        print(f"🔗 الملفات المشابهة: {report['summary']['similar_files']}")
        print(
            f"⚙️ التكرار الوظيفي: {report['summary']['functional_duplicates']}")
        print(f"🛠️ الخدمات المكررة: {report['summary']['service_duplicates']}")
        print("="*80)

        if report['summary']['total_issues'] > 0:
            print(
                f"\n💡 إجمالي المشاكل المكتشفة: {report['summary']['total_issues']}")
            print("📋 راجع التقرير للحصول على التوصيات التفصيلية")
        else:
            print("\n✅ لم يتم العثور على ملفات مكررة!")

    def create_cleanup_script(self) -> None:
        """إنشاء سكريبت تنظيف"""
        exact_duplicates = [
            g for g in self.duplicate_groups if g.type == "exact"]

        if not exact_duplicates:
            print("✅ لا توجد ملفات مطابقة تماماً لحذفها")
            return

        script_content = """#!/usr/bin/env python3
# سكريبت تنظيف الملفات المكررة - تم إنشاؤه تلقائياً
import os
import shutil
from pathlib import Path

def backup_and_delete(file_path: str):
    '''إنشاء نسخة احتياطية وحذف الملف'''
    backup_dir = Path("backup_duplicates")
    backup_dir.mkdir(exist_ok=True)
    
    file_path = Path(file_path)
    if file_path.exists():
        # إنشاء نسخة احتياطية
        backup_file = backup_dir / file_path.name
        shutil.copy2(file_path, backup_file)
        print(f"✅ نسخة احتياطية: {backup_file}")
        
        # حذف الملف الأصلي
        os.remove(file_path)
        print(f"🗑️ تم حذف: {file_path}")
    else:
        print(f"❌ الملف غير موجود: {file_path}")

def main():
    print("🧹 بدء تنظيف الملفات المكررة...")
    
"""

        for group in exact_duplicates:
            # الاحتفاظ بالملف الأول وحذف الباقي
            files_to_delete = group.files[1:]
            script_content += f"""
    # مجموعة مكررة - الاحتفاظ بـ {group.files[0].path}
    print("📦 معالجة مجموعة مكررة...")
"""
            for file_info in files_to_delete:
                script_content += f'    backup_and_delete(r"{file_info.path}")\n'

        script_content += """
    print("✅ تم الانتهاء من التنظيف!")

if __name__ == "__main__":
    main()
"""

        with open("cleanup_duplicates.py", "w", encoding="utf-8") as f:
            f.write(script_content)

        print("✅ تم إنشاء سكريبت التنظيف: cleanup_duplicates.py")

    def run_analysis(self) -> None:
        """تشغيل التحليل الكامل"""
        print("🚀 بدء التحليل المتقدم للملفات المكررة...")

        # مسح المشروع
        self.scan_project()

        # البحث عن أنواع مختلفة من التكرار
        self.find_exact_duplicates()
        self.find_similar_files()
        self.find_functional_duplicates()
        self.analyze_service_duplicates()

        # إنشاء التقارير
        self.generate_report()
        self.create_cleanup_script()

        print("✅ تم الانتهاء من التحليل!")


def main():
    """الدالة الرئيسية"""
    finder = AdvancedDuplicateFinder()
    finder.run_analysis()


if __name__ == "__main__":
    main()
