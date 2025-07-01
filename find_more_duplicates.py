#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find More Duplicates - بحث عن ملفات مكررة إضافية
"""

import os
import hashlib
import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path

def find_duplicates_by_content():
    """البحث عن ملفات مكررة بالمحتوى"""
    print("🔍 البحث عن ملفات مكررة بالمحتوى...")
    
    file_hashes = defaultdict(list)
    
    for root, dirs, files in os.walk('.'):
        # تجاهل المجلدات غير المرغوبة
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if file.endswith(('.py', '.js', '.json', '.yml', '.yaml')):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if content.strip():  # تجاهل الملفات الفارغة
                        file_hash = hashlib.md5(content.encode()).hexdigest()
                        file_hashes[file_hash].append(file_path)
                        
                except Exception as e:
                    print(f"خطأ في قراءة {file_path}: {e}")
    
    # تحديد المكررات
    duplicates = {}
    for file_hash, files in file_hashes.items():
        if len(files) > 1:
            duplicates[file_hash] = files
    
    return duplicates

def find_duplicates_by_name():
    """البحث عن ملفات بنفس الاسم في أماكن مختلفة"""
    print("🔍 البحث عن ملفات بنفس الاسم...")
    
    name_to_files = defaultdict(list)
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if file.endswith(('.py', '.js', '.json', '.yml', '.yaml')):
                file_path = os.path.join(root, file)
                name_to_files[file].append(file_path)
    
    # تحديد المكررات
    duplicates = {}
    for filename, files in name_to_files.items():
        if len(files) > 1:
            duplicates[filename] = files
    
    return duplicates

def find_similar_config_files():
    """البحث عن ملفات إعدادات متشابهة"""
    print("🔍 البحث عن ملفات إعدادات متشابهة...")
    
    config_files = []
    config_patterns = ['config', 'setting', '.env', 'constant', 'default']
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if any(pattern in file.lower() for pattern in config_patterns):
                config_files.append(os.path.join(root, file))
    
    return config_files

def analyze_init_files():
    """تحليل خاص لملفات __init__.py"""
    print("🔍 تحليل ملفات __init__.py...")
    
    init_files = []
    empty_inits = []
    content_inits = []
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if file == '__init__.py':
                file_path = os.path.join(root, file)
                init_files.append(file_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().strip()
                    
                    if content:
                        content_inits.append({
                            'path': file_path,
                            'content': content,
                            'lines': len(content.splitlines())
                        })
                    else:
                        empty_inits.append(file_path)
                        
                except Exception as e:
                    print(f"خطأ في قراءة {file_path}: {e}")
    
    return {
        'total': len(init_files),
        'empty': len(empty_inits),
        'with_content': len(content_inits),
        'empty_files': empty_inits,
        'content_files': content_inits
    }

def check_test_file_duplicates():
    """فحص ملفات الاختبارات المكررة"""
    print("🔍 فحص ملفات الاختبارات...")
    
    test_files = []
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if 'test' in file.lower() and file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    test_files.append({
                        'path': file_path,
                        'size': len(content),
                        'lines': len(content.splitlines()),
                        'hash': hashlib.md5(content.encode()).hexdigest()
                    })
                    
                except Exception as e:
                    print(f"خطأ في قراءة {file_path}: {e}")
    
    # تحديد المكررات
    hash_to_tests = defaultdict(list)
    for test in test_files:
        hash_to_tests[test['hash']].append(test['path'])
    
    duplicates = {h: files for h, files in hash_to_tests.items() if len(files) > 1}
    
    return {
        'total_tests': len(test_files),
        'duplicates': duplicates,
        'all_tests': test_files
    }

def generate_duplicate_report():
    """توليد تقرير شامل عن الملفات المكررة"""
    print("📊 توليد تقرير الملفات المكررة...")
    
    # جمع كل النتائج
    content_duplicates = find_duplicates_by_content()
    name_duplicates = find_duplicates_by_name()
    config_files = find_similar_config_files()
    init_analysis = analyze_init_files()
    test_analysis = check_test_file_duplicates()
    
    # إنشاء التقرير
    report = {
        'timestamp': str(datetime.now()),
        'summary': {
            'content_duplicates': len(content_duplicates),
            'name_duplicates': len(name_duplicates),
            'config_files': len(config_files),
            'init_files_total': init_analysis['total'],
            'init_files_empty': init_analysis['empty'],
            'test_duplicates': len(test_analysis['duplicates'])
        },
        'details': {
            'content_duplicates': content_duplicates,
            'name_duplicates': name_duplicates,
            'config_files': config_files,
            'init_analysis': init_analysis,
            'test_analysis': test_analysis
        }
    }
    
    return report

def print_duplicate_summary(report):
    """طباعة ملخص الملفات المكررة"""
    print("\n" + "="*60)
    print("📊 ملخص الملفات المكررة الإضافية")
    print("="*60)
    
    summary = report['summary']
    details = report['details']
    
    print(f"\n🔍 النتائج:")
    print(f"- مكررات بالمحتوى: {summary['content_duplicates']} مجموعة")
    print(f"- مكررات بالاسم: {summary['name_duplicates']} اسم")
    print(f"- ملفات إعدادات: {summary['config_files']} ملف")
    print(f"- ملفات __init__.py: {summary['init_files_total']} (فارغة: {summary['init_files_empty']})")
    print(f"- مكررات اختبارات: {summary['test_duplicates']} مجموعة")
    
    # تفاصيل المكررات بالمحتوى
    if details['content_duplicates']:
        print(f"\n🔄 مكررات بالمحتوى (أول 5):")
        for i, (file_hash, files) in enumerate(list(details['content_duplicates'].items())[:5]):
            print(f"\n  المجموعة {i+1} ({len(files)} ملف):")
            for file in files[:3]:
                print(f"    - {file}")
            if len(files) > 3:
                print(f"    - ... و {len(files) - 3} ملف آخر")
    
    # تفاصيل المكررات بالاسم
    if details['name_duplicates']:
        print(f"\n📋 مكررات بالاسم (أول 5):")
        for i, (filename, files) in enumerate(list(details['name_duplicates'].items())[:5]):
            if len(files) > 1:
                print(f"\n  {filename} ({len(files)} موقع):")
                for file in files[:3]:
                    print(f"    - {file}")
                if len(files) > 3:
                    print(f"    - ... و {len(files) - 3} موقع آخر")
    
    # ملفات __init__.py الفارغة
    if details['init_analysis']['empty_files']:
        print(f"\n📁 ملفات __init__.py فارغة (أول 10):")
        for file in details['init_analysis']['empty_files'][:10]:
            print(f"  - {file}")
        
        remaining = len(details['init_analysis']['empty_files']) - 10
        if remaining > 0:
            print(f"  - ... و {remaining} ملف آخر")

def generate_cleanup_actions(report):
    """توليد إجراءات التنظيف المقترحة"""
    actions = []
    
    details = report['details']
    
    # إجراءات للمكررات بالمحتوى
    for file_hash, files in details['content_duplicates'].items():
        if len(files) > 1:
            # تحديد أفضل ملف للاحتفاظ به
            best_file = select_best_file(files)
            
            actions.append({
                'type': 'merge_content_duplicates',
                'keep': best_file,
                'remove': [f for f in files if f != best_file],
                'reason': 'نفس المحتوى بالضبط'
            })
    
    # إجراءات لملفات __init__.py الفارغة (معظمها صحيح)
    empty_inits = details['init_analysis']['empty_files']
    if len(empty_inits) > 50:  # إذا كان هناك عدد كبير من الملفات الفارغة
        actions.append({
            'type': 'review_empty_inits',
            'files': empty_inits,
            'reason': 'عدد كبير من ملفات __init__.py فارغة - قد تكون طبيعية أو قد تحتاج مراجعة'
        })
    
    return actions

def select_best_file(files):
    """اختيار أفضل ملف من المجموعة"""
    # تفضيل الملفات في src/ على scripts/
    # تفضيل الملفات في مجلدات أعمق (أكثر تخصصاً)
    
    ranked = []
    for file in files:
        score = 0
        
        # الملف في src/
        if 'src/' in file:
            score += 10
        
        # ليس في scripts/
        if 'scripts/' not in file:
            score += 5
        
        # عمق المجلد
        score += file.count('/')
        
        # ليس test file
        if 'test' not in file.lower():
            score += 3
        
        ranked.append((score, file))
    
    ranked.sort(reverse=True)
    return ranked[0][1]

def main():
    """البرنامج الرئيسي"""
    
    print("🚀 البحث عن ملفات مكررة إضافية...")
    
    # توليد التقرير
    report = generate_duplicate_report()
    
    # طباعة الملخص
    print_duplicate_summary(report)
    
    # توليد إجراءات التنظيف
    actions = generate_cleanup_actions(report)
    
    # حفظ النتائج
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # حفظ التقرير الكامل
    report_file = f"additional_duplicates_report_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # حفظ إجراءات التنظيف
    actions_file = f"cleanup_actions_{timestamp}.json"
    with open(actions_file, 'w', encoding='utf-8') as f:
        json.dump(actions, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ تم حفظ التقرير في: {report_file}")
    print(f"✅ تم حفظ إجراءات التنظيف في: {actions_file}")
    
    # اقتراح الخطوات التالية
    print(f"\n💡 الخطوات التالية:")
    if report['summary']['content_duplicates'] > 0:
        print(f"1. مراجعة {report['summary']['content_duplicates']} مجموعة من المكررات")
    if report['summary']['init_files_empty'] > 20:
        print(f"2. مراجعة {report['summary']['init_files_empty']} ملف __init__.py فارغ")
    if report['summary']['test_duplicates'] > 0:
        print(f"3. مراجعة {report['summary']['test_duplicates']} مكرر في الاختبارات")

if __name__ == "__main__":
    main() 