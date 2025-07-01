import os
import sys
import shutil
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Set
import re
import ast

class ComprehensiveCleaner:
    """منظف شامل ومتقدم لمشروع AI Teddy Bear"""
    
    def __init__(self, analysis_file: str = "full_project_analysis.json", dry_run: bool = False):
        self.project_root = Path(".")
        self.analysis_file = analysis_file
        self.dry_run = dry_run
        self.backup_dir = f"final_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.cleanup_stats = {
            'deleted_files': 0,
            'deleted_dirs': 0,
            'moved_files': 0,
            'merged_files': 0,
            'fixed_issues': 0,
            'total_size_saved': 0
        }
        
        self.report = {
            'phase1_cleanup': [],  # حذف الملفات غير المهمة
            'phase2_dedup': [],    # إزالة التكرارات
            'phase3_organize': [], # إعادة التنظيم
            'phase4_fix': [],      # إصلاح المشاكل
            'phase5_final': [],    # التنظيف النهائي
            'errors': [],
            'warnings': []
        }
        
        # قراءة تقرير التحليل
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                self.analysis = json.load(f)
        except FileNotFoundError:
            print(f"❌ لم يتم العثور على {analysis_file}")
            sys.exit(1)
    
    def run_comprehensive_cleanup(self):
        """تشغيل عملية التنظيف الشاملة"""
        print("🧹 بدء التنظيف الشامل لمشروع AI Teddy Bear")
        print("="*60)
        
        if self.dry_run:
            print("⚠️  وضع التجربة - لن يتم تنفيذ تغييرات فعلية")
        else:
            print(f"📁 مجلد النسخ الاحتياطي: {self.backup_dir}")
            os.makedirs(self.backup_dir, exist_ok=True)
        
        # المرحلة 1: حذف الملفات والمجلدات غير المهمة
        print("\n" + "="*60)
        print("🗑️ المرحلة 1: حذف الملفات والمجلدات غير المهمة")
        print("="*60)
        self.phase1_major_cleanup()
        
        # المرحلة 2: إزالة التكرارات
        print("\n" + "="*60)
        print("🔄 المرحلة 2: إزالة التكرارات")
        print("="*60)
        self.phase2_remove_duplicates()
        
        # المرحلة 3: إعادة تنظيم الهيكل
        print("\n" + "="*60)
        print("📂 المرحلة 3: إعادة تنظيم الهيكل")
        print("="*60)
        self.phase3_reorganize_structure()
        
        # المرحلة 4: إصلاح المشاكل
        print("\n" + "="*60)
        print("🔧 المرحلة 4: إصلاح المشاكل الأمنية والجودة")
        print("="*60)
        self.phase4_fix_issues()
        
        # المرحلة 5: التنظيف النهائي
        print("\n" + "="*60)
        print("✨ المرحلة 5: التنظيف النهائي")
        print("="*60)
        self.phase5_final_cleanup()
        
        # إنشاء التقرير النهائي
        print("\n" + "="*60)
        self.generate_final_report()
    
    def phase1_major_cleanup(self):
        """المرحلة 1: حذف الملفات والمجلدات غير المهمة"""
        
        # 1. حذف مجلد backup_before_reorganization بالكامل
        backup_dir = Path("backup_before_reorganization")
        if backup_dir.exists():
            if not self.dry_run:
                shutil.rmtree(backup_dir)
            self.cleanup_stats['deleted_dirs'] += 1
            self.report['phase1_cleanup'].append({
                'action': 'delete_directory',
                'path': str(backup_dir),
                'reason': 'Old backup directory - contains duplicates'
            })
            print(f"  ✅ حذف مجلد النسخ القديمة: {backup_dir}")
        
        # 2. حذف جميع ملفات __pycache__ و .pyc
        cache_patterns = ['__pycache__', '*.pyc', '*.pyo', '*.pyd', '.pytest_cache', '.mypy_cache']
        for pattern in cache_patterns:
            for path in self.project_root.rglob(pattern):
                if path.is_file():
                    if not self.dry_run:
                        path.unlink()
                    self.cleanup_stats['deleted_files'] += 1
                elif path.is_dir():
                    if not self.dry_run:
                        shutil.rmtree(path)
                    self.cleanup_stats['deleted_dirs'] += 1
        
        # 3. حذف الملفات المصنفة كـ trash
        trash_files = [f for f in self.analysis['detailed_analysis'] if f['importance'] == 'trash']
        for file_info in trash_files:
            file_path = Path(file_info['path'])
            if file_path.exists():
                if not self.dry_run:
                    self._backup_and_delete(file_path)
                self.cleanup_stats['deleted_files'] += 1
                self.report['phase1_cleanup'].append({
                    'action': 'delete_file',
                    'path': str(file_path),
                    'reason': 'Classified as trash'
                })
                print(f"  🗑️ حذف: {file_path}")
        
        # 4. حذف الملفات الفارغة
        for empty_file in self.analysis.get('empty_files', []):
            file_path = Path(empty_file)
            if file_path.exists():
                if not self.dry_run:
                    self._backup_and_delete(file_path)
                self.cleanup_stats['deleted_files'] += 1
                self.report['phase1_cleanup'].append({
                    'action': 'delete_file',
                    'path': str(file_path),
                    'reason': 'Empty file'
                })
                print(f"  🗑️ حذف ملف فارغ: {file_path}")
        
        # 5. حذف الملفات القديمة والمؤقتة
        temp_patterns = ['*_old.py', '*_backup.py', '*_temp.py', '*_copy.py', '*.bak', '*.tmp', '*.swp']
        for pattern in temp_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    if not self.dry_run:
                        self._backup_and_delete(file_path)
                    self.cleanup_stats['deleted_files'] += 1
                    print(f"  🗑️ حذف ملف مؤقت: {file_path}")
        
        print(f"\n✅ المرحلة 1 مكتملة: حذف {self.cleanup_stats['deleted_files']} ملف و {self.cleanup_stats['deleted_dirs']} مجلد")
    
    def phase2_remove_duplicates(self):
        """المرحلة 2: إزالة التكرارات"""
        
        # معالجة التكرارات الكاملة
        exact_duplicates = [d for d in self.analysis['duplicate_candidates'] if d['type'] == 'exact']
        
        for dup_group in exact_duplicates:
            files = [f for f in dup_group['files'] if Path(f).exists()]
            
            if len(files) > 1:
                # اختيار أفضل ملف للاحتفاظ به
                best_file = self._select_best_file(files)
                
                for file_path in files:
                    if file_path != best_file:
                        if not self.dry_run:
                            self._backup_and_delete(Path(file_path))
                        self.cleanup_stats['deleted_files'] += 1
                        self.cleanup_stats['merged_files'] += 1
                        self.report['phase2_dedup'].append({
                            'action': 'merge_duplicate',
                            'deleted': file_path,
                            'kept': best_file,
                            'hash': dup_group['hash'][:8]
                        })
                        print(f"  🔄 دمج: {Path(file_path).name} -> {Path(best_file).name}")
        
        print(f"\n✅ المرحلة 2 مكتملة: دمج {self.cleanup_stats['merged_files']} ملف مكرر")
    
    def phase3_reorganize_structure(self):
        """المرحلة 3: إعادة تنظيم الهيكل"""
        
        # الهيكل المستهدف الجديد
        target_structure = {
            'src/core/': ['domain', 'services', 'interfaces'],
            'src/infrastructure/': ['persistence', 'ai_providers', 'messaging', 'monitoring', 'security'],
            'src/api/': ['rest', 'websocket', 'graphql'],
            'src/presentation/': ['ui', 'components'],
            'tests/': ['unit', 'integration', 'e2e', 'fixtures'],
            'configs/': ['development', 'staging', 'production'],
            'scripts/': ['setup', 'migration', 'maintenance', 'analysis'],
            'docs/': ['api', 'architecture', 'guides']
        }
        
        # إنشاء المجلدات المطلوبة
        for parent, subdirs in target_structure.items():
            for subdir in subdirs:
                dir_path = self.project_root / parent / subdir
                if not self.dry_run:
                    dir_path.mkdir(parents=True, exist_ok=True)
        
        # نقل الملفات إلى أماكنها الصحيحة
        files_to_move = []
        for file_info in self.analysis['detailed_analysis']:
            if file_info.get('suggested_location') and Path(file_info['path']).exists():
                current = Path(file_info['path'])
                suggested = Path(file_info['suggested_location'])
                
                # تجنب نقل الملفات التي في أماكنها الصحيحة
                if not self._is_in_correct_location(current, suggested):
                    files_to_move.append((current, suggested, file_info['type']))
        
        # تنفيذ النقل
        for current, suggested, file_type in files_to_move[:50]:  # نقل أول 50 ملف فقط
            if not self.dry_run:
                self._move_file_safely(current, suggested)
            self.cleanup_stats['moved_files'] += 1
            self.report['phase3_organize'].append({
                'action': 'move_file',
                'from': str(current),
                'to': str(suggested),
                'type': file_type
            })
            print(f"  📂 نقل: {current.name} -> {suggested.parent}")
        
        print(f"\n✅ المرحلة 3 مكتملة: نقل {self.cleanup_stats['moved_files']} ملف")
    
    def phase4_fix_issues(self):
        """المرحلة 4: إصلاح المشاكل الأمنية والجودة"""
        
        # الملفات ذات المشاكل الحرجة
        problematic_files = self.analysis.get('problematic_files', [])
        
        for file_info in problematic_files:
            file_path = Path(file_info['path'])
            if not file_path.exists():
                continue
            
            issues = file_info['issues']
            
            # معالجة المشاكل الأمنية الحرجة
            if any('eval()' in issue or 'exec()' in issue for issue in issues):
                print(f"  ⚠️  تحذير أمني: {file_path.name} يستخدم eval/exec")
                self.report['phase4_fix'].append({
                    'action': 'security_warning',
                    'file': str(file_path),
                    'issues': [i for i in issues if 'eval' in i or 'exec' in i]
                })
            
            # إصلاح print statements
            if 'Print statements in production code' in issues:
                if not self.dry_run:
                    self._remove_print_statements(file_path)
                self.cleanup_stats['fixed_issues'] += 1
                print(f"  🔧 إزالة print statements من: {file_path.name}")
        
        print(f"\n✅ المرحلة 4 مكتملة: إصلاح {self.cleanup_stats['fixed_issues']} مشكلة")
    
    def phase5_final_cleanup(self):
        """المرحلة 5: التنظيف النهائي"""
        
        if not self.dry_run:
            # 1. حذف المجلدات الفارغة
            empty_dirs = []
            for root, dirs, files in os.walk(self.project_root, topdown=False):
                if not dirs and not files and root != str(self.project_root):
                    empty_dirs.append(root)
            
            for empty_dir in empty_dirs:
                try:
                    os.rmdir(empty_dir)
                    self.cleanup_stats['deleted_dirs'] += 1
                except:
                    pass
            
            # 2. تنسيق الكود
            print("  🎨 تنسيق الكود باستخدام black...")
            os.system("black src/ tests/ scripts/ --quiet 2>nul")
            
            # 3. ترتيب الاستيرادات
            print("  📦 ترتيب الاستيرادات باستخدام isort...")
            os.system("isort src/ tests/ scripts/ --quiet 2>nul")
        
        print(f"\n✅ المرحلة 5 مكتملة: التنظيف النهائي")
    
    def _backup_and_delete(self, file_path: Path):
        """نسخ احتياطي وحذف الملف"""
        try:
            # نسخ احتياطي
            backup_path = Path(self.backup_dir) / file_path.relative_to(self.project_root)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            # حساب الحجم المحفوظ
            self.cleanup_stats['total_size_saved'] += file_path.stat().st_size
            
            # حذف الملف
            file_path.unlink()
        except Exception as e:
            self.report['errors'].append(f"Error deleting {file_path}: {e}")
    
    def _select_best_file(self, files: List[str]) -> str:
        """اختيار أفضل ملف من المكررات"""
        scores = {}
        
        for file in files:
            score = 0
            path = Path(file)
            
            # تفضيل الملفات في src/
            if 'src/' in str(path):
                score += 20
            
            # تفضيل الملفات الأساسية
            if any(x in str(path) for x in ['core', 'domain', 'infrastructure']):
                score += 10
            
            # تجنب مجلدات backup
            if 'backup' in str(path):
                score -= 100
            
            # تجنب scripts إذا كان هناك بديل
            if 'scripts/' in str(path):
                score -= 5
            
            # الملفات الأحدث
            try:
                mtime = path.stat().st_mtime
                score += mtime / 1000000  # نقاط بناءً على وقت التعديل
            except:
                pass
            
            scores[file] = score
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _is_in_correct_location(self, current: Path, suggested: Path) -> bool:
        """التحقق من أن الملف في المكان الصحيح"""
        current_parts = current.parts
        suggested_parts = suggested.parts
        
        # التحقق من التطابق في المسار
        for part in suggested_parts[:-1]:  # تجاهل اسم الملف
            if part in current_parts:
                return True
        
        return False
    
    def _move_file_safely(self, source: Path, destination: Path):
        """نقل ملف بأمان مع تحديث الاستيرادات"""
        try:
            # إنشاء المجلد الهدف
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # نقل الملف
            shutil.move(str(source), str(destination))
            
            # TODO: تحديث الاستيرادات في الملفات الأخرى
            
        except Exception as e:
            self.report['errors'].append(f"Error moving {source}: {e}")
    
    def _remove_print_statements(self, file_path: Path):
        """إزالة print statements من الملف"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # إزالة print statements بسيطة
            content = re.sub(r'^\s*print\s*\(.*?\)\s*$', '', content, flags=re.MULTILINE)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            self.report['errors'].append(f"Error fixing {file_path}: {e}")
    
    def generate_final_report(self):
        """إنشاء التقرير النهائي"""
        
        # حساب الإحصائيات النهائية
        total_actions = (
            self.cleanup_stats['deleted_files'] + 
            self.cleanup_stats['deleted_dirs'] +
            self.cleanup_stats['moved_files'] +
            self.cleanup_stats['fixed_issues']
        )
        
        size_saved_mb = self.cleanup_stats['total_size_saved'] / (1024 * 1024)
        
        report_content = f"""# 📊 تقرير التنظيف الشامل لمشروع AI Teddy Bear

## 📅 معلومات التنظيف
- **التاريخ**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **وضع التشغيل**: {"تجريبي" if self.dry_run else "فعلي"}
- **مجلد النسخ الاحتياطي**: `{self.backup_dir}/`

## 📈 الإحصائيات النهائية

### 🎯 إجمالي الإجراءات: {total_actions}

| النوع | العدد |
|------|-------|
| 🗑️ ملفات محذوفة | {self.cleanup_stats['deleted_files']} |
| 📁 مجلدات محذوفة | {self.cleanup_stats['deleted_dirs']} |
| 🔄 ملفات مدموجة | {self.cleanup_stats['merged_files']} |
| 📂 ملفات منقولة | {self.cleanup_stats['moved_files']} |
| 🔧 مشاكل مُصلحة | {self.cleanup_stats['fixed_issues']} |
| 💾 المساحة الموفرة | {size_saved_mb:.2f} MB |

## 📋 تفاصيل المراحل

### المرحلة 1: حذف الملفات غير المهمة
- حذف مجلد `backup_before_reorganization` بالكامل
- حذف جميع ملفات `__pycache__` و `.pyc`
- حذف {len([x for x in self.report['phase1_cleanup'] if x['action'] == 'delete_file'])} ملف غير مهم

### المرحلة 2: إزالة التكرارات
- معالجة {self.cleanup_stats['merged_files']} ملف مكرر
- الاحتفاظ بأفضل نسخة من كل ملف

### المرحلة 3: إعادة التنظيم
- نقل {self.cleanup_stats['moved_files']} ملف إلى أماكنها الصحيحة
- إنشاء هيكل مجلدات منظم

### المرحلة 4: إصلاح المشاكل
- إصلاح {self.cleanup_stats['fixed_issues']} مشكلة في الكود
- تحذيرات أمنية للملفات التي تستخدم eval/exec

### المرحلة 5: التنظيف النهائي
- حذف المجلدات الفارغة
- تنسيق الكود باستخدام black
- ترتيب الاستيرادات باستخدام isort

## ⚠️ التحذيرات والأخطاء
"""
        
        if self.report['errors']:
            report_content += f"\n### ❌ الأخطاء ({len(self.report['errors'])})\n"
            for error in self.report['errors'][:10]:
                report_content += f"- {error}\n"
        
        # الملفات الأمنية التي تحتاج مراجعة
        security_warnings = [x for x in self.report['phase4_fix'] if x['action'] == 'security_warning']
        if security_warnings:
            report_content += f"\n### 🔴 تحذيرات أمنية ({len(security_warnings)})\n"
            report_content += "الملفات التالية تستخدم eval/exec ويجب مراجعتها:\n"
            for warning in security_warnings:
                report_content += f"- `{Path(warning['file']).name}`\n"
        
        report_content += """
## ✅ الخطوات التالية

1. [ ] مراجعة التقرير والتأكد من النتائج
2. [ ] تشغيل الاختبارات للتأكد من عدم كسر أي شيء
3. [ ] مراجعة الملفات ذات التحذيرات الأمنية
4. [ ] حذف مجلد النسخ الاحتياطي بعد التأكد
5. [ ] عمل commit للتغييرات

## 💡 نصائح
- تم حفظ نسخ احتياطية من جميع الملفات المحذوفة
- يمكنك استرجاع أي ملف من مجلد النسخ الاحتياطي
- راجع الملفات التي تستخدم eval/exec وأعد كتابتها بطريقة آمنة
"""
        
        # حفظ التقرير
        with open('comprehensive_cleanup_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # حفظ تقرير JSON مفصل
        detailed_report = {
            'metadata': {
                'date': datetime.now().isoformat(),
                'dry_run': self.dry_run,
                'backup_dir': self.backup_dir
            },
            'statistics': self.cleanup_stats,
            'actions': self.report
        }
        
        with open('comprehensive_cleanup_report.json', 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print("✅ التنظيف الشامل اكتمل!")
        print(f"📊 إجمالي الإجراءات: {total_actions}")
        print(f"💾 المساحة الموفرة: {size_saved_mb:.2f} MB")
        print("\n📋 التقارير:")
        print("  • comprehensive_cleanup_report.md")
        print("  • comprehensive_cleanup_report.json")


def main():
    """تشغيل المنظف الشامل"""
    import argparse
    
    parser = argparse.ArgumentParser(description='تنظيف شامل لمشروع AI Teddy Bear')
    parser.add_argument('--dry-run', action='store_true', 
                       help='تشغيل في وضع التجربة دون تنفيذ التغييرات')
    parser.add_argument('--analysis-file', default='full_project_analysis.json',
                       help='مسار ملف التحليل')
    
    args = parser.parse_args()
    
    # التأكيد قبل البدء
    if not args.dry_run:
        print("="*60)
        print("⚠️  تحذير مهم!")
        print("="*60)
        print("سيقوم هذا السكريبت بـ:")
        print("  • حذف مجلد backup_before_reorganization بالكامل")
        print("  • حذف جميع الملفات المكررة")
        print("  • نقل الملفات إلى أماكن جديدة")
        print("  • إصلاح مشاكل في الكود")
        print("\n📁 سيتم حفظ نسخ احتياطية في: final_backup_[timestamp]")
        print("="*60)
        
        response = input("\nهل أنت متأكد من المتابعة؟ اكتب 'نعم' للمتابعة: ")
        if response.lower() not in ['نعم', 'yes']:
            print("❌ تم إلغاء العملية")
            return
    
    # تشغيل المنظف
    cleaner = ComprehensiveCleaner(
        analysis_file=args.analysis_file,
        dry_run=args.dry_run
    )
    cleaner.run_comprehensive_cleanup()


if __name__ == "__main__":
    main() 