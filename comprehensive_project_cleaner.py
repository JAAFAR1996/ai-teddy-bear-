#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Project Cleaner
تنظيف شامل للمشروع بناءً على التحليل
"""

import os
import shutil
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib

class ComprehensiveProjectCleaner:
    def __init__(self, analysis_file="cleanup_report_20250630_225358.json"):
        """تهيئة منظف المشروع"""
        self.analysis_file = analysis_file
        self.backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.actions_log = []
        self.dry_run = True  # افتراضياً في وضع المعاينة
        
        # قراءة تقرير التحليل
        with open(analysis_file, 'r', encoding='utf-8') as f:
            self.analysis = json.load(f)
    
    def create_backup(self):
        """إنشاء نسخة احتياطية من المشروع"""
        print("📦 إنشاء نسخة احتياطية...")
        if not self.dry_run:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # نسخ الملفات المهمة فقط
            important_files = [
                ".py", ".js", ".json", ".yml", ".yaml", 
                ".txt", ".md", ".ini", ".cfg", ".toml"
            ]
            
            for root, dirs, files in os.walk('.'):
                # تجاهل المجلدات غير المرغوبة
                dirs[:] = [d for d in dirs if d not in [
                    '.git', '__pycache__', 'node_modules', '.venv', 
                    'venv', 'backup_*'
                ]]
                
                for file in files:
                    if any(file.endswith(ext) for ext in important_files):
                        src_path = os.path.join(root, file)
                        
                        # إنشاء المسار في النسخة الاحتياطية
                        rel_path = os.path.relpath(src_path, '.')
                        dst_path = os.path.join(self.backup_dir, rel_path)
                        
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
            
            print(f"✅ تم إنشاء النسخة الاحتياطية في: {self.backup_dir}")
        else:
            print("🔍 [وضع المعاينة] سيتم إنشاء نسخة احتياطية")
    
    def clean_empty_files(self):
        """حذف الملفات الفارغة"""
        print("\n🗑️ حذف الملفات الفارغة...")
        empty_files = self.analysis.get('empty_files', [])
        
        for file_path in empty_files:
            if os.path.exists(file_path):
                if not self.dry_run:
                    os.remove(file_path)
                    self.actions_log.append(f"حذف ملف فارغ: {file_path}")
                else:
                    print(f"  📄 سيتم حذف: {file_path}")
        
        print(f"✅ تم التعامل مع {len(empty_files)} ملف فارغ")
    
    def merge_duplicate_init_files(self):
        """دمج ملفات __init__.py المكررة"""
        print("\n🔄 دمج ملفات __init__.py المكررة...")
        
        duplicates = self.analysis.get('duplicate_files', [])
        
        # معالجة ملفات __init__.py الفارغة
        init_groups = [d for d in duplicates if any('__init__.py' in f for f in d['files'])]
        
        for group in init_groups:
            files = group['files']
            
            # تحليل محتوى كل ملف
            file_contents = {}
            for file_path in files:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().strip()
                    file_contents[file_path] = content
            
            # إذا كانت جميعها فارغة، احتفظ بها (مهمة لـ Python packages)
            if all(not content for content in file_contents.values()):
                continue
            
            # إذا كان هناك محتوى مختلف، احتفظ بالملف الأكثر محتوى
            if len(set(file_contents.values())) > 1:
                # اختر الملف مع أكثر محتوى
                best_file = max(file_contents.items(), key=lambda x: len(x[1]))[0]
                
                for file_path, content in file_contents.items():
                    if file_path != best_file and content != file_contents[best_file]:
                        print(f"  ⚠️ تحذير: {file_path} يحتوي على محتوى مختلف")
                        self.actions_log.append(f"تحذير: محتوى مختلف في {file_path}")
    
    def reorganize_misplaced_files(self):
        """إعادة تنظيم الملفات في أماكن خاطئة"""
        print("\n📂 إعادة تنظيم الملفات...")
        
        misplaced = self.analysis.get('misplaced_files', [])
        
        # تجميع حسب النوع
        by_type = defaultdict(list)
        for item in misplaced:
            by_type[item['type']].append(item)
        
        # معالجة كل نوع
        for file_type, files in by_type.items():
            print(f"\n  📁 نقل ملفات {file_type} ({len(files)} ملف):")
            
            for item in files[:5]:  # أول 5 فقط للعرض
                current = item['file']
                suggested = item['suggested']
                filename = os.path.basename(current)
                new_path = os.path.join(suggested, filename)
                
                print(f"    {current} → {new_path}")
                
                if not self.dry_run:
                    # إنشاء المجلد الهدف
                    os.makedirs(suggested, exist_ok=True)
                    
                    # نقل الملف
                    if os.path.exists(current):
                        shutil.move(current, new_path)
                        self.actions_log.append(f"نقل: {current} → {new_path}")
                        
                        # تحديث imports
                        self._update_imports(current, new_path)
    
    def _update_imports(self, old_path, new_path):
        """تحديث imports بعد نقل الملف"""
        # تحويل المسارات إلى module names
        old_module = self._path_to_module(old_path)
        new_module = self._path_to_module(new_path)
        
        # البحث في جميع ملفات Python
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # استبدال imports
                        updated = False
                        patterns = [
                            (f'from {old_module} import', f'from {new_module} import'),
                            (f'import {old_module}', f'import {new_module}'),
                            (f'"{old_module}"', f'"{new_module}"'),
                            (f"'{old_module}'", f"'{new_module}'")
                        ]
                        
                        for old_pattern, new_pattern in patterns:
                            if old_pattern in content:
                                content = content.replace(old_pattern, new_pattern)
                                updated = True
                        
                        if updated and not self.dry_run:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            self.actions_log.append(f"تحديث imports في: {file_path}")
                    
                    except Exception as e:
                        print(f"    ❌ خطأ في تحديث {file_path}: {e}")
    
    def _path_to_module(self, path):
        """تحويل مسار الملف إلى اسم module"""
        # إزالة .\ من البداية و .py من النهاية
        module = path.replace('.\\', '').replace('/', '.').replace('\\', '.')
        if module.endswith('.py'):
            module = module[:-3]
        return module
    
    def analyze_large_files(self):
        """تحليل الملفات الكبيرة واقتراح تقسيمها"""
        print("\n📊 تحليل الملفات الكبيرة...")
        
        large_files = self.analysis.get('large_files', [])
        
        # تصنيف الملفات الكبيرة
        categories = {
            'split_recommended': [],  # يُنصح بتقسيمها
            'ok_as_is': [],          # مقبولة كما هي
            'needs_refactor': []     # تحتاج إعادة هيكلة
        }
        
        for file_info in large_files:
            file_path = file_info['path']
            lines = file_info['lines']
            
            # تجاهل ملفات معينة
            if any(skip in file_path for skip in ['package-lock.json', '.json', 'test_', 'migrations']):
                categories['ok_as_is'].append(file_info)
            elif lines > 1000:
                categories['split_recommended'].append(file_info)
            elif lines > 700:
                categories['needs_refactor'].append(file_info)
            else:
                categories['ok_as_is'].append(file_info)
        
        # عرض التوصيات
        if categories['split_recommended']:
            print(f"\n  🔴 ملفات يجب تقسيمها ({len(categories['split_recommended'])}):")
            for file_info in categories['split_recommended'][:5]:
                print(f"    - {file_info['path']} ({file_info['lines']} سطر)")
        
        if categories['needs_refactor']:
            print(f"\n  🟠 ملفات تحتاج إعادة هيكلة ({len(categories['needs_refactor'])}):")
            for file_info in categories['needs_refactor'][:5]:
                print(f"    - {file_info['path']} ({file_info['lines']} سطر)")
        
        return categories
    
    def generate_cleanup_script(self):
        """توليد سكريبت للتنظيف اليدوي"""
        print("\n📝 توليد سكريبت التنظيف...")
        
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        empty_cmds = '\n'.join(f'rm -f "{f}"' for f in self.analysis.get('empty_files', []))
        
        script_content = f"""#!/bin/bash
# سكريبت تنظيف المشروع - تم توليده تلقائياً
# تاريخ: {date_str}

echo "🚀 بدء تنظيف المشروع..."

# حذف الملفات الفارغة
echo "🗑️ حذف الملفات الفارغة..."
{empty_cmds}

# حذف مجلدات __pycache__
echo "🗑️ حذف مجلدات __pycache__..."
find . -type d -name "__pycache__" -exec rm -rf {{}} + 2>/dev/null

# تنسيق الكود
echo "🎨 تنسيق الكود..."
black src/ --line-length 120 2>/dev/null || echo "تحذير: black غير مثبت"
isort src/ 2>/dev/null || echo "تحذير: isort غير مثبت"

echo "✅ اكتمل التنظيف!"
"""
        
        with open('cleanup_script.sh', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print("✅ تم إنشاء cleanup_script.sh")
    
    def generate_final_report(self):
        """توليد التقرير النهائي"""
        report_content = f"""# 📊 تقرير تنظيف المشروع النهائي

## 📅 معلومات التنظيف
- **التاريخ**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **وضع التشغيل**: {'معاينة' if self.dry_run else 'تنفيذ فعلي'}

## 📈 الإجراءات المتخذة
- **إجمالي الإجراءات**: {len(self.actions_log)}

### 📋 سجل الإجراءات:
"""
        
        for i, action in enumerate(self.actions_log[:50], 1):
            report_content += f"{i}. {action}\n"
        
        if len(self.actions_log) > 50:
            report_content += f"\n... و {len(self.actions_log) - 50} إجراء آخر\n"
        
        # حفظ التقرير
        report_file = f"cleanup_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n✅ تم حفظ التقرير النهائي: {report_file}")
    
    def run_cleanup(self, dry_run=True):
        """تشغيل عملية التنظيف"""
        self.dry_run = dry_run
        
        print(f"🚀 بدء تنظيف المشروع ({'وضع المعاينة' if dry_run else 'التنفيذ الفعلي'})...")
        print("=" * 60)
        
        # 1. إنشاء نسخة احتياطية
        if not dry_run:
            self.create_backup()
        
        # 2. حذف الملفات الفارغة
        self.clean_empty_files()
        
        # 3. دمج الملفات المكررة
        self.merge_duplicate_init_files()
        
        # 4. إعادة تنظيم الملفات
        self.reorganize_misplaced_files()
        
        # 5. تحليل الملفات الكبيرة
        self.analyze_large_files()
        
        # 6. توليد سكريبت التنظيف
        self.generate_cleanup_script()
        
        # 7. التقرير النهائي
        self.generate_final_report()
        
        print("\n" + "=" * 60)
        print("✅ اكتمل التنظيف!")
        
        if dry_run:
            print("\n💡 لتنفيذ التنظيف الفعلي، شغل:")
            print("   python comprehensive_project_cleaner.py --execute")

def main():
    """البرنامج الرئيسي"""
    import argparse
    
    parser = argparse.ArgumentParser(description='تنظيف شامل للمشروع')
    parser.add_argument('--execute', action='store_true', 
                       help='تنفيذ التنظيف الفعلي (افتراضياً: معاينة فقط)')
    parser.add_argument('--analysis', default='cleanup_report_20250630_225358.json',
                       help='ملف تقرير التحليل')
    
    args = parser.parse_args()
    
    try:
        cleaner = ComprehensiveProjectCleaner(args.analysis)
        cleaner.run_cleanup(dry_run=not args.execute)
    except FileNotFoundError:
        print("❌ لم يتم العثور على ملف التحليل. شغل project_cleanup_analyzer.py أولاً")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 