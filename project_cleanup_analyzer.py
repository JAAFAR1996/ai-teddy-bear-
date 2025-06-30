#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Cleanup Analyzer - تحليل شامل للمشروع لتنظيفه
"""

import os
import hashlib
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def analyze_project():
    """تحليل المشروع بالكامل"""
    print("🚀 بدء تحليل المشروع...")
    
    stats = {
        "total_files": 0,
        "empty_files": [],
        "large_files": [],
        "duplicate_files": [],
        "file_types": defaultdict(int),
        "trash_files": [],
        "misplaced_files": []
    }
    
    # جمع كل الملفات
    all_files = []
    for root, dirs, files in os.walk('.'):
        # تجاهل المجلدات غير المرغوبة
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
        
        for file in files:
            if not file.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file)
                all_files.append(file_path)
    
    print(f"📄 تم العثور على {len(all_files)} ملف")
    
    # تحليل كل ملف
    file_hashes = defaultdict(list)
    
    for file_path in all_files:
        stats["total_files"] += 1
        
        # نوع الملف
        ext = os.path.splitext(file_path)[1]
        stats["file_types"][ext] += 1
        
        try:
            # حجم الملف
            size = os.path.getsize(file_path)
            
            # الملفات الفارغة
            if size == 0:
                stats["empty_files"].append(file_path)
                continue
            
            # قراءة المحتوى للملفات النصية
            if ext in ['.py', '.js', '.json', '.txt', '.md', '.yml', '.yaml']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # عدد الأسطر
                lines = len(content.splitlines())
                
                # الملفات الكبيرة
                if lines > 500:
                    stats["large_files"].append({
                        "path": file_path,
                        "lines": lines
                    })
                
                # حساب hash للبحث عن المكررات
                file_hash = hashlib.md5(content.encode()).hexdigest()
                file_hashes[file_hash].append(file_path)
                
                # فحص الملفات القمامة
                if any(pattern in file_path.lower() for pattern in ['_old', '_backup', '_temp', '_copy']):
                    stats["trash_files"].append(file_path)
                
                # فحص الملفات في أماكن خاطئة
                if ext == '.py':
                    check_file_location(file_path, stats)
                    
        except Exception as e:
            print(f"❌ خطأ في تحليل {file_path}: {e}")
    
    # تحديد الملفات المكررة
    for file_hash, files in file_hashes.items():
        if len(files) > 1:
            stats["duplicate_files"].append({
                "files": files,
                "count": len(files)
            })
    
    return stats

def check_file_location(file_path, stats):
    """فحص موقع الملف"""
    path_lower = file_path.lower()
    
    # تحديد نوع الملف
    if 'model' in path_lower or 'entity' in path_lower:
        if 'domain' not in path_lower:
            stats["misplaced_files"].append({
                "file": file_path,
                "type": "model",
                "suggested": "src/core/domain/entities/"
            })
    elif 'service' in path_lower:
        if 'application' not in path_lower and 'core' not in path_lower:
            stats["misplaced_files"].append({
                "file": file_path,
                "type": "service",
                "suggested": "src/core/services/"
            })
    elif 'repository' in path_lower:
        if 'infrastructure' not in path_lower:
            stats["misplaced_files"].append({
                "file": file_path,
                "type": "repository",
                "suggested": "src/infrastructure/persistence/"
            })

def print_report(stats):
    """طباعة التقرير"""
    print("\n" + "="*60)
    print("📊 تقرير تحليل المشروع")
    print("="*60)
    
    print(f"\n📈 إحصائيات عامة:")
    print(f"- إجمالي الملفات: {stats['total_files']}")
    print(f"- الملفات الفارغة: {len(stats['empty_files'])}")
    print(f"- الملفات الكبيرة: {len(stats['large_files'])}")
    print(f"- الملفات المكررة: {len(stats['duplicate_files'])}")
    print(f"- ملفات القمامة: {len(stats['trash_files'])}")
    print(f"- ملفات في أماكن خاطئة: {len(stats['misplaced_files'])}")
    
    print("\n📂 أنواع الملفات:")
    for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {ext or 'بدون امتداد'}: {count}")
    
    if stats['empty_files']:
        print(f"\n🗑️ ملفات فارغة (أول 10):")
        for file in stats['empty_files'][:10]:
            print(f"  - {file}")
    
    if stats['duplicate_files']:
        print(f"\n🔄 ملفات مكررة (أول 5 مجموعات):")
        for i, dup in enumerate(stats['duplicate_files'][:5]):
            print(f"\n  المجموعة {i+1} ({dup['count']} ملف):")
            for file in dup['files'][:3]:
                print(f"    - {file}")
    
    if stats['trash_files']:
        print(f"\n🚮 ملفات قمامة (أول 10):")
        for file in stats['trash_files'][:10]:
            print(f"  - {file}")
    
    print("\n💡 التوصيات:")
    print(f"1. احذف {len(stats['empty_files'])} ملف فارغ")
    print(f"2. راجع ودمج {len(stats['duplicate_files'])} مجموعة من الملفات المكررة")
    print(f"3. احذف {len(stats['trash_files'])} ملف قمامة")
    print(f"4. انقل {len(stats['misplaced_files'])} ملف للمكان الصحيح")

def save_report(stats):
    """حفظ التقرير"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # حفظ JSON
    with open(f"cleanup_report_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # حفظ Markdown
    with open(f"cleanup_report_{timestamp}.md", 'w', encoding='utf-8') as f:
        f.write("# تقرير تنظيف المشروع\n\n")
        f.write(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## الإحصائيات\n")
        f.write(f"- إجمالي الملفات: {stats['total_files']}\n")
        f.write(f"- الملفات الفارغة: {len(stats['empty_files'])}\n")
        f.write(f"- الملفات المكررة: {len(stats['duplicate_files'])}\n")
        f.write(f"- ملفات القمامة: {len(stats['trash_files'])}\n\n")
        
        f.write("## خطة العمل\n\n")
        f.write("### المرحلة 1: حذف الملفات غير المهمة\n")
        f.write("```bash\n")
        f.write("# حذف الملفات الفارغة\n")
        for file in stats['empty_files'][:20]:
            f.write(f'rm "{file}"\n')
        f.write("```\n\n")
        
        f.write("### المرحلة 2: حذف ملفات القمامة\n")
        f.write("```bash\n")
        for file in stats['trash_files'][:20]:
            f.write(f'rm "{file}"\n')
        f.write("```\n")
    
    print(f"\n✅ تم حفظ التقرير في:")
    print(f"  - cleanup_report_{timestamp}.json")
    print(f"  - cleanup_report_{timestamp}.md")

def main():
    """البرنامج الرئيسي"""
    try:
        stats = analyze_project()
        print_report(stats)
        save_report(stats)
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 