#!/usr/bin/env python3
"""
AI Teddy Bear Project Deep Cleaner
أداة تنظيف عميقة وشاملة للمشروع
"""

import os
import shutil
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import ast

class ProjectDeepCleaner:
    """منظف المشروع العميق والشامل"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.project_root = Path(".")
        self.backup_dir = Path(f"backup_before_cleaning_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # قراءة تقرير التحليل
        self.analysis_report = self._load_analysis_report()
        
        # إحصائيات
        self.stats = {
            'files_deleted': 0,
            'files_moved': 0,
            'files_merged': 0,
            'security_fixed': 0,
            'imports_updated': 0,
            'errors': []
        }
        
        # خريطة التحويلات للimports
        self.import_mappings = {}
        
    def _load_analysis_report(self) -> Dict:
        """تحميل تقرير التحليل"""
        try:
            with open('cleanup_analysis_report.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ خطأ في قراءة التقرير: {e}")
            return {}
    
    def clean_project(self):
        """تنظيف المشروع بالكامل"""
        print("🧹 بدء تنظيف المشروع العميق...")
        print(f"📦 وضع التشغيل: {'تجريبي (Dry Run)' if self.dry_run else 'حقيقي'}")
        
        if not self.dry_run:
            # إنشاء نسخة احتياطية
            self._create_backup()
        
        # 1. حذف الملفات القمامة والفارغة
        print("\n🗑️ المرحلة 1: حذف الملفات غير المهمة...")
        self._delete_trash_files()
        
        # 2. دمج الملفات المكررة
        print("\n🔄 المرحلة 2: دمج الملفات المكررة...")
        self._merge_duplicate_files()
        
        # 3. نقل الملفات للأماكن الصحيحة
        print("\n📂 المرحلة 3: إعادة تنظيم الهيكل...")
        self._reorganize_structure()
        
        # 4. إصلاح مشاكل الأمان
        print("\n🔐 المرحلة 4: إصلاح مشاكل الأمان...")
        self._fix_security_issues()
        
        # 5. تحديث جميع imports
        print("\n🔗 المرحلة 5: تحديث imports...")
        self._update_all_imports()
        
        # 6. تنظيف نهائي
        print("\n✨ المرحلة 6: تنظيف نهائي...")
        self._final_cleanup()
        
        # 7. إنشاء تقرير النتائج
        print("\n📊 إنشاء تقرير النتائج...")
        self._generate_final_report()
        
    def _create_backup(self):
        """إنشاء نسخة احتياطية"""
        print(f"📦 إنشاء نسخة احتياطية في: {self.backup_dir}")
        
        # نسخ الملفات المهمة فقط
        important_patterns = [
            "**/*.py",
            "**/*.json",
            "**/*.yaml",
            "**/*.yml",
            "**/*.md",
            "**/requirements*.txt",
            "**/Dockerfile*",
            "**/.env*"
        ]
        
        self.backup_dir.mkdir(exist_ok=True)
        
        for pattern in important_patterns:
            for file_path in self.project_root.glob(pattern):
                if '.git' not in str(file_path) and '__pycache__' not in str(file_path):
                    relative_path = file_path.relative_to(self.project_root)
                    backup_path = self.backup_dir / relative_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)
    
    def _delete_trash_files(self):
        """حذف الملفات القمامة والفارغة"""
        trash_files = self.analysis_report.get('trash_files', [])
        
        # إضافة أنماط إضافية للحذف
        additional_patterns = [
            "**/__pycache__/**",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.pyd",
            "**/.pytest_cache/**",
            "**/.mypy_cache/**",
            "**/*.egg-info/**",
            "**/dist/**",
            "**/build/**",
            "**/.coverage",
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/*_old.py",
            "**/*_backup.py",
            "**/*_temp.py",
            "**/*_copy.py"
        ]
        
        # البحث عن ملفات إضافية للحذف
        for pattern in additional_patterns:
            for file_path in self.project_root.glob(pattern):
                trash_files.append(str(file_path))
        
        # البحث عن الملفات الفارغة
        for py_file in self.project_root.glob("**/*.py"):
            try:
                if py_file.stat().st_size == 0:
                    trash_files.append(str(py_file))
                else:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        # ملف يحتوي فقط على تعليقات أو pass
                        if not content or content == 'pass' or all(
                            line.strip().startswith('#') or not line.strip() 
                            for line in content.splitlines()
                        ):
                            trash_files.append(str(py_file))
            except:
                pass
        
        # حذف الملفات
        trash_files = list(set(trash_files))  # إزالة التكرارات
        
        for file_path in trash_files:
            try:
                path = Path(file_path)
                if path.exists():
                    if self.dry_run:
                        print(f"   [DRY RUN] سيتم حذف: {file_path}")
                    else:
                        if path.is_file():
                            path.unlink()
                        else:
                            shutil.rmtree(path)
                        print(f"   ✅ تم حذف: {file_path}")
                    self.stats['files_deleted'] += 1
            except Exception as e:
                self.stats['errors'].append(f"خطأ في حذف {file_path}: {e}")
    
    def _merge_duplicate_files(self):
        """دمج الملفات المكررة"""
        duplicates = self.analysis_report.get('duplicates', [])
        
        for dup_group in duplicates:
            if dup_group['type'] == 'exact' and dup_group['count'] > 1:
                files = dup_group['files']
                
                # اختيار أفضل ملف للاحتفاظ به
                best_file = self._select_best_file(files)
                
                # حذف البقية وتحديث imports
                for file_path in files:
                    if file_path != best_file:
                        # تحديث خريطة imports
                        old_import = self._path_to_import(file_path)
                        new_import = self._path_to_import(best_file)
                        self.import_mappings[old_import] = new_import
                        
                        # حذف الملف
                        try:
                            if self.dry_run:
                                print(f"   [DRY RUN] دمج: {file_path} -> {best_file}")
                            else:
                                Path(file_path).unlink()
                                print(f"   ✅ دمج: {file_path} -> {best_file}")
                            self.stats['files_merged'] += 1
                        except Exception as e:
                            self.stats['errors'].append(f"خطأ في دمج {file_path}: {e}")
    
    def _select_best_file(self, files: List[str]) -> str:
        """اختيار أفضل ملف من المكررات"""
        scores = {}
        
        for file_path in files:
            score = 0
            
            # تفضيل الملفات في src/
            if file_path.startswith('src/'):
                score += 10
            
            # تفضيل الملفات خارج backup
            if 'backup' not in file_path:
                score += 5
            
            # تفضيل الملفات في الأماكن الصحيحة
            if any(correct in file_path for correct in [
                'core/domain', 'core/services', 'infrastructure',
                'api/endpoints', 'tests/'
            ]):
                score += 3
            
            # تفضيل أسماء الملفات الوصفية
            if not file_path.endswith('__init__.py'):
                score += 2
            
            scores[file_path] = score
        
        # إرجاع الملف بأعلى نقاط
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _reorganize_structure(self):
        """إعادة تنظيم هيكل المشروع"""
        moves = self.analysis_report.get('suggested_moves', [])
        
        # إضافة قواعد نقل إضافية
        additional_rules = {
            'esp32/': 'hardware/esp32/',
            'chaos/': 'src/testing/chaos/',
            'api/': 'src/api/',
            'configs/': 'config/',
            'scripts/migration/': 'tools/migration/',
            'scripts/': 'tools/scripts/',
            'observability/': 'src/infrastructure/monitoring/',
            'monitoring/': 'src/infrastructure/monitoring/',
            'deployments/': 'deploy/',
            'frontend/': 'src/presentation/web/'
        }
        
        # تطبيق القواعد الإضافية
        for old_prefix, new_prefix in additional_rules.items():
            for file_path in self.project_root.glob(f"{old_prefix}**/*.py"):
                relative_path = str(file_path.relative_to(self.project_root))
                new_path = relative_path.replace(old_prefix, new_prefix, 1)
                
                if relative_path != new_path:
                    moves.append({
                        'from': relative_path,
                        'to': new_path,
                        'reason': 'Better organization'
                    })
        
        # تنفيذ النقل
        for move in moves:
            old_path = Path(move['from'])
            new_path = Path(move['to'])
            
            if old_path.exists():
                try:
                    # تحديث خريطة imports
                    old_import = self._path_to_import(str(old_path))
                    new_import = self._path_to_import(str(new_path))
                    self.import_mappings[old_import] = new_import
                    
                    if self.dry_run:
                        print(f"   [DRY RUN] نقل: {old_path} -> {new_path}")
                    else:
                        # إنشاء المجلد الهدف
                        new_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # نقل الملف
                        shutil.move(str(old_path), str(new_path))
                        print(f"   ✅ نقل: {old_path} -> {new_path}")
                    
                    self.stats['files_moved'] += 1
                    
                except Exception as e:
                    self.stats['errors'].append(f"خطأ في نقل {old_path}: {e}")
    
    def _fix_security_issues(self):
        """إصلاح مشاكل الأمان"""
        security_issues = self.analysis_report.get('security_issues', [])
        
        for issue in security_issues:
            file_path = Path(issue['file'])
            issue_type = issue['issue']
            
            if file_path.exists() and file_path.suffix == '.py':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # إصلاح eval/exec
                    if 'eval/exec usage' in issue_type:
                        content = re.sub(r'\beval\s*\(', '# SECURITY_FIXED: eval(', content)
                        content = re.sub(r'\bexec\s*\(', '# SECURITY_FIXED: exec(', content)
                    
                    # إصلاح hardcoded secrets
                    if 'hardcoded secrets' in issue_type:
                        # استبدال القيم المشفرة بمتغيرات بيئة
                        content = re.sub(
                            r'(password|token|secret|api_key)\s*=\s*["\']([^"\']+)["\']',
                            r'\1 = os.getenv("\1_ENV", "REDACTED")',
                            content,
                            flags=re.IGNORECASE
                        )
                        
                        # إضافة import os إذا لزم الأمر
                        if 'os.getenv' in content and 'import os' not in content:
                            content = 'import os\n' + content
                    
                    if content != original_content:
                        if self.dry_run:
                            print(f"   [DRY RUN] إصلاح أمان: {file_path}")
                        else:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            print(f"   ✅ إصلاح أمان: {file_path}")
                        self.stats['security_fixed'] += 1
                        
                except Exception as e:
                    self.stats['errors'].append(f"خطأ في إصلاح أمان {file_path}: {e}")
    
    def _update_all_imports(self):
        """تحديث جميع imports في المشروع"""
        if not self.import_mappings:
            print("   ℹ️ لا توجد imports تحتاج تحديث")
            return
        
        # البحث في جميع ملفات Python
        for py_file in self.project_root.glob("**/*.py"):
            if '.git' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # تحديث imports
                for old_import, new_import in self.import_mappings.items():
                    # import statements
                    content = re.sub(
                        f'\\bimport\\s+{re.escape(old_import)}\\b',
                        f'import {new_import}',
                        content
                    )
                    
                    # from ... import statements
                    content = re.sub(
                        f'\\bfrom\\s+{re.escape(old_import)}\\b',
                        f'from {new_import}',
                        content
                    )
                
                if content != original_content:
                    if self.dry_run:
                        print(f"   [DRY RUN] تحديث imports في: {py_file}")
                    else:
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"   ✅ تحديث imports في: {py_file}")
                    self.stats['imports_updated'] += 1
                    
            except Exception as e:
                self.stats['errors'].append(f"خطأ في تحديث imports {py_file}: {e}")
    
    def _path_to_import(self, file_path: str) -> str:
        """تحويل مسار الملف إلى import path"""
        # إزالة .py
        import_path = file_path.replace('.py', '')
        
        # تحويل / إلى .
        import_path = import_path.replace('/', '.').replace('\\', '.')
        
        # إزالة src. من البداية إذا وجدت
        if import_path.startswith('src.'):
            import_path = import_path[4:]
        
        return import_path
    
    def _final_cleanup(self):
        """تنظيف نهائي"""
        # حذف المجلدات الفارغة
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                if not any(dir_path.iterdir()) and '.git' not in str(dir_path):
                    try:
                        if self.dry_run:
                            print(f"   [DRY RUN] حذف مجلد فارغ: {dir_path}")
                        else:
                            dir_path.rmdir()
                            print(f"   ✅ حذف مجلد فارغ: {dir_path}")
                    except:
                        pass
        
        # تنظيف __init__.py الزائدة
        self._cleanup_init_files()
    
    def _cleanup_init_files(self):
        """تنظيف ملفات __init__.py الزائدة"""
        # البحث عن جميع __init__.py
        init_files = list(self.project_root.glob("**/__init__.py"))
        
        for init_file in init_files:
            try:
                # تحقق إذا كان المجلد يحتوي على ملفات Python أخرى
                parent_dir = init_file.parent
                other_py_files = [
                    f for f in parent_dir.glob("*.py") 
                    if f.name != "__init__.py"
                ]
                
                # إذا لم يكن هناك ملفات Python أخرى، احذف __init__.py
                if not other_py_files and not any(parent_dir.glob("*/")):
                    if self.dry_run:
                        print(f"   [DRY RUN] حذف __init__.py زائد: {init_file}")
                    else:
                        init_file.unlink()
                        print(f"   ✅ حذف __init__.py زائد: {init_file}")
                    self.stats['files_deleted'] += 1
                    
            except Exception as e:
                self.stats['errors'].append(f"خطأ في تنظيف {init_file}: {e}")
    
    def _generate_final_report(self):
        """إنشاء تقرير النتائج النهائي"""
        report = f"""# 📊 تقرير تنظيف مشروع AI Teddy Bear

## 📅 معلومات التنظيف
- **التاريخ**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **وضع التشغيل**: {'تجريبي (Dry Run)' if self.dry_run else 'حقيقي'}
- **مجلد النسخ الاحتياطي**: {self.backup_dir if not self.dry_run else 'N/A'}

## 📈 الإحصائيات النهائية

### ✅ العمليات المنجزة
- **ملفات محذوفة**: {self.stats['files_deleted']}
- **ملفات منقولة**: {self.stats['files_moved']}
- **ملفات مدموجة**: {self.stats['files_merged']}
- **مشاكل أمان مُصلحة**: {self.stats['security_fixed']}
- **imports محدثة**: {self.stats['imports_updated']}

### ❌ الأخطاء ({len(self.stats['errors'])})
"""
        
        for error in self.stats['errors'][:10]:
            report += f"- {error}\n"
        
        if len(self.stats['errors']) > 10:
            report += f"\n... و {len(self.stats['errors']) - 10} خطأ آخر\n"
        
        report += f"""
## 🎯 الخطوات التالية

1. **مراجعة التغييرات**: تحقق من أن كل شيء يعمل بشكل صحيح
2. **تشغيل الاختبارات**: `python -m pytest`
3. **تحديث requirements.txt**: إزالة المكتبات غير المستخدمة
4. **تشغيل linters**: `black .` و `isort .` و `flake8 .`
5. **Commit التغييرات**: `git add -A && git commit -m "Major project cleanup"`

## 💡 نصائح للحفاظ على النظافة

1. استخدم pre-commit hooks
2. اتبع هيكل المجلدات الموصى به
3. لا تكرر الكود - استخدم DRY principle
4. احذف الكود الميت فوراً
5. اكتب اختبارات لكل ميزة جديدة

---
تم بواسطة: AI Teddy Bear Deep Cleaner 🧹
"""
        
        # حفظ التقرير
        report_path = f"cleanup_report_{'dry_run' if self.dry_run else 'final'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 تم حفظ التقرير في: {report_path}")
        
        # طباعة ملخص
        print("\n" + "="*50)
        print("📊 ملخص التنظيف:")
        print(f"   🗑️ ملفات محذوفة: {self.stats['files_deleted']}")
        print(f"   📂 ملفات منقولة: {self.stats['files_moved']}")
        print(f"   🔄 ملفات مدموجة: {self.stats['files_merged']}")
        print(f"   🔐 مشاكل أمان مُصلحة: {self.stats['security_fixed']}")
        print(f"   🔗 imports محدثة: {self.stats['imports_updated']}")
        
        if self.stats['errors']:
            print(f"   ❌ أخطاء: {len(self.stats['errors'])}")
        else:
            print("   ✅ لا توجد أخطاء!")
        
        print("="*50)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Teddy Bear Project Deep Cleaner")
    parser.add_argument(
        '--execute', 
        action='store_true',
        help='تنفيذ التنظيف فعلياً (بدون هذا الخيار سيعمل في وضع تجريبي)'
    )
    
    args = parser.parse_args()
    
    cleaner = ProjectDeepCleaner(dry_run=not args.execute)
    cleaner.clean_project() 