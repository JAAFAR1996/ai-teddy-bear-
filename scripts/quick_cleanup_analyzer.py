#!/usr/bin/env python3
"""محلل سريع للتنظيف والترتيب"""

import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def analyze_project():
    """تحليل سريع للمشروع"""
    print("\n🧹 محلل التنظيف السريع - AI Teddy Bear")
    print("="*60)

    results = {
        "timestamp": datetime.now().isoformat(),
        "total_files": 0,
        "files_by_type": defaultdict(int),
        "empty_files": [],
        "large_files": [],
        "trash_files": [],
        "duplicates": defaultdict(list),
        "misplaced_files": []
    }

    # patterns للملفات القمامة
    trash_patterns = ['_old.py', '_backup.py', '_temp.py', '_copy.py', '.pyc']

    # جمع كل ملفات Python
    for root, dirs, files in os.walk('.'):
        # تجاهل المجلدات غير المهمة
        dirs[:] = [d for d in dirs if d not in [
            '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'backup_']]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                results["total_files"] += 1

                try:
                    # قراءة الملف
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # حساب hash
                    file_hash = hashlib.sha256(content.encode()).hexdigest()
                    results["duplicates"][file_hash].append(file_path)

                    # فحص الملف
                    file_size = len(content)

                    # ملفات فارغة
                    if file_size == 0 and '__init__.py' not in file:
                        results["empty_files"].append(file_path)
                        results["trash_files"].append(file_path)

                    # ملفات كبيرة
                    elif file_size > 50000:  # أكبر من 50KB
                        results["large_files"].append((file_path, file_size))

                    # ملفات قمامة
                    if any(pattern in file for pattern in trash_patterns):
                        results["trash_files"].append(file_path)

                    # تحديد النوع
                    if 'test' in file_path:
                        results["files_by_type"]["test"] += 1
                    elif 'service' in file_path:
                        results["files_by_type"]["service"] += 1
                    elif 'model' in file_path or 'entity' in file_path:
                        results["files_by_type"]["model"] += 1
                    elif 'config' in file_path:
                        results["files_by_type"]["config"] += 1
                    else:
                        results["files_by_type"]["other"] += 1

                except Exception as e:
                    print(f"⚠️ خطأ في قراءة {file_path}: {e}")

    # طباعة النتائج
    print(f"\n📊 النتائج:")
    print(f"إجمالي الملفات: {results['total_files']}")
    print(f"ملفات فارغة: {len(results['empty_files'])}")
    print(f"ملفات كبيرة: {len(results['large_files'])}")
    print(f"ملفات قمامة: {len(set(results['trash_files']))}")

    # البحث عن المكررات
    exact_duplicates = []
    for file_hash, files in results["duplicates"].items():
        if len(files) > 1:
            exact_duplicates.append(files)

    print(f"مجموعات مكررة: {len(exact_duplicates)}")

    # حفظ النتائج
    with open('quick_cleanup_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # إنشاء تقرير سريع
    with open('quick_cleanup_report.md', 'w', encoding='utf-8') as f:
        f.write("# تقرير التنظيف السريع\n\n")
        f.write(f"التاريخ: {results['timestamp']}\n\n")

        f.write("## ملفات للحذف الفوري\n\n")
        trash_files_unique = list(set(results["trash_files"]))
        for trash_file in trash_files_unique[:20]:
            f.write(f"- `{trash_file}`\n")

        if exact_duplicates:
            f.write("\n## ملفات مكررة\n\n")
            for idx, dup_group in enumerate(exact_duplicates[:10], 1):
                f.write(f"### المجموعة {idx}\n")
                for file in dup_group:
                    f.write(f"- `{file}`\n")

    print("\n✅ تم حفظ التقرير في: quick_cleanup_report.md")
    return results


if __name__ == "__main__":
    analyze_project()
