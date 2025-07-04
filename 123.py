#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Teddy Bear - Duplicate Files Finder
يقوم هذا البرنامج بفحص جميع ملفات المشروع للبحث عن الملفات المكررة
ومقارنة محتوياتها والميزات المتشابهة
"""

import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict
import difflib
from datetime import datetime


class DuplicateFileFinder:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path)
        self.files_data = defaultdict(list)
        self.duplicates = defaultdict(list)
        self.similar_files = []
        self.excluded_dirs = {'.git', '__pycache__',
                              'node_modules', '.venv', 'venv'}
        self.excluded_extensions = {'.pyc', '.pyo', '.so', '.dll', '.exe'}

    def calculate_file_hash(self, filepath):
        """حساب hash للملف"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"خطأ في قراءة الملف {filepath}: {e}")
            return None

    def get_file_info(self, filepath):
        """الحصول على معلومات الملف"""
        stat = os.stat(filepath)
        return {
            'path': str(filepath),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'extension': filepath.suffix
        }

    def analyze_python_file(self, filepath):
        """تحليل ملف Python لاستخراج الميزات"""
        features = {
            'functions': [],
            'classes': [],
            'imports': [],
            'decorators': [],
            'async_functions': []
        }

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                for line in lines:
                    stripped = line.strip()

                    # استخراج الـ imports
                    if stripped.startswith('import ') or stripped.startswith('from '):
                        features['imports'].append(stripped)

                    # استخراج الـ functions
                    elif stripped.startswith('def '):
                        func_name = stripped.split('(')[0].replace('def ', '')
                        features['functions'].append(func_name)

                    # استخراج الـ async functions
                    elif stripped.startswith('async def '):
                        func_name = stripped.split(
                            '(')[0].replace('async def ', '')
                        features['async_functions'].append(func_name)

                    # استخراج الـ classes
                    elif stripped.startswith('class '):
                        class_name = stripped.split(
                            '(')[0].split(':')[0].replace('class ', '')
                        features['classes'].append(class_name)

                    # استخراج الـ decorators
                    elif stripped.startswith('@'):
                        features['decorators'].append(stripped)

        except Exception as e:
            print(f"خطأ في تحليل الملف {filepath}: {e}")

        return features

    def compare_files_content(self, file1, file2):
        """مقارنة محتوى ملفين"""
        try:
            with open(file1, 'r', encoding='utf-8') as f1:
                content1 = f1.readlines()
            with open(file2, 'r', encoding='utf-8') as f2:
                content2 = f2.readlines()

            # حساب نسبة التشابه
            similarity = difflib.SequenceMatcher(
                None, content1, content2).ratio()

            # الحصول على الاختلافات
            differ = difflib.unified_diff(content1, content2,
                                          fromfile=str(file1),
                                          tofile=str(file2))
            differences = list(differ)

            return {
                'similarity': similarity * 100,
                'differences_count': len(differences),
                'identical': similarity == 1.0
            }
        except Exception as e:
            print(f"خطأ في مقارنة الملفات: {e}")
            return None

    def scan_project(self):
        """فحص جميع ملفات المشروع"""
        print(f"بدء فحص المشروع في: {self.project_path}")

        for root, dirs, files in os.walk(self.project_path):
            # استبعاد المجلدات غير المرغوبة
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

            for filename in files:
                filepath = Path(root) / filename

                # استبعاد الملفات غير المرغوبة
                if filepath.suffix in self.excluded_extensions:
                    continue

                # حساب hash الملف
                file_hash = self.calculate_file_hash(filepath)
                if file_hash:
                    file_info = self.get_file_info(filepath)
                    file_info['hash'] = file_hash

                    # تحليل ملفات Python
                    if filepath.suffix == '.py':
                        file_info['features'] = self.analyze_python_file(
                            filepath)

                    self.files_data[file_hash].append(file_info)

    def find_duplicates(self):
        """البحث عن الملفات المكررة"""
        print("\nالبحث عن الملفات المكررة...")

        for file_hash, files_list in self.files_data.items():
            if len(files_list) > 1:
                self.duplicates[file_hash] = files_list

    def find_similar_files(self, threshold=80):
        """البحث عن الملفات المتشابهة (غير المتطابقة تماماً)"""
        print(f"\nالبحث عن الملفات المتشابهة (نسبة التشابه > {threshold}%)...")

        all_files = []
        for files_list in self.files_data.values():
            all_files.extend([f['path'] for f in files_list])

        # مقارنة الملفات من نفس النوع
        py_files = [f for f in all_files if f.endswith('.py')]

        for i, file1 in enumerate(py_files):
            for file2 in py_files[i+1:]:
                comparison = self.compare_files_content(file1, file2)
                if comparison and comparison['similarity'] >= threshold and not comparison['identical']:
                    self.similar_files.append({
                        'file1': file1,
                        'file2': file2,
                        'similarity': comparison['similarity'],
                        'differences_count': comparison['differences_count']
                    })

    def generate_report(self):
        """إنشاء تقرير مفصل"""
        report = {
            'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'project_path': str(self.project_path),
            'total_files_scanned': sum(len(files) for files in self.files_data.values()),
            'duplicate_groups': len(self.duplicates),
            'total_duplicates': sum(len(files) - 1 for files in self.duplicates.values()),
            'similar_files': len(self.similar_files),
            'duplicates': [],
            'similar': self.similar_files
        }

        # إضافة تفاصيل الملفات المكررة
        for file_hash, files_list in self.duplicates.items():
            duplicate_group = {
                'hash': file_hash,
                'files_count': len(files_list),
                'total_size': sum(f['size'] for f in files_list),
                'wasted_space': sum(f['size'] for f in files_list[1:]),
                'files': files_list
            }

            # مقارنة الميزات للملفات المكررة
            if all('features' in f for f in files_list):
                features_comparison = self.compare_features(files_list)
                duplicate_group['features_comparison'] = features_comparison

            report['duplicates'].append(duplicate_group)

        return report

    def compare_features(self, files_list):
        """مقارنة الميزات بين الملفات المكررة"""
        if len(files_list) < 2 or 'features' not in files_list[0]:
            return None

        comparison = {
            'identical_features': True,
            'differences': []
        }

        base_features = files_list[0]['features']

        for i, file_info in enumerate(files_list[1:], 1):
            features = file_info['features']

            for feature_type in base_features:
                if set(base_features[feature_type]) != set(features[feature_type]):
                    comparison['identical_features'] = False
                    comparison['differences'].append({
                        'file': file_info['path'],
                        'feature': feature_type,
                        'in_base_only': list(set(base_features[feature_type]) - set(features[feature_type])),
                        'in_file_only': list(set(features[feature_type]) - set(base_features[feature_type]))
                    })

        return comparison

    def save_report(self, output_file='duplicate_files_report.json'):
        """حفظ التقرير في ملف JSON"""
        report = self.generate_report()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\nتم حفظ التقرير في: {output_file}")
        return report

    def print_summary(self):
        """طباعة ملخص النتائج"""
        report = self.generate_report()

        print("\n" + "="*60)
        print("تقرير الملفات المكررة - AI Teddy Bear")
        print("="*60)
        print(f"تاريخ الفحص: {report['scan_date']}")
        print(f"مسار المشروع: {report['project_path']}")
        print(f"إجمالي الملفات المفحوصة: {report['total_files_scanned']}")
        print(f"مجموعات الملفات المكررة: {report['duplicate_groups']}")
        print(f"إجمالي الملفات المكررة: {report['total_duplicates']}")
        print(f"الملفات المتشابهة: {report['similar_files']}")

        if self.duplicates:
            print("\n" + "-"*40)
            print("الملفات المكررة:")
            print("-"*40)

            for i, duplicate_group in enumerate(report['duplicates'], 1):
                print(f"\nالمجموعة {i}:")
                print(f"  عدد الملفات: {duplicate_group['files_count']}")
                print(
                    f"  الحجم الإجمالي: {duplicate_group['total_size']:,} bytes")
                print(
                    f"  المساحة المهدورة: {duplicate_group['wasted_space']:,} bytes")
                print("  الملفات:")

                for file_info in duplicate_group['files']:
                    print(f"    - {file_info['path']}")
                    print(f"      الحجم: {file_info['size']:,} bytes")
                    print(f"      آخر تعديل: {file_info['modified']}")

                if 'features_comparison' in duplicate_group:
                    comp = duplicate_group['features_comparison']
                    if comp['identical_features']:
                        print("  ✓ جميع الميزات متطابقة")
                    else:
                        print("  ✗ توجد اختلافات في الميزات:")
                        for diff in comp['differences']:
                            print(
                                f"    - {diff['file']}: اختلاف في {diff['feature']}")

        if self.similar_files:
            print("\n" + "-"*40)
            print("الملفات المتشابهة (غير المتطابقة):")
            print("-"*40)

            for similar in self.similar_files:
                print(f"\n- {similar['file1']}")
                print(f"  مع: {similar['file2']}")
                print(f"  نسبة التشابه: {similar['similarity']:.1f}%")
                print(f"  عدد الاختلافات: {similar['differences_count']}")


def main():
    """الدالة الرئيسية"""
    import argparse

    parser = argparse.ArgumentParser(
        description='البحث عن الملفات المكررة في مشروع AI Teddy Bear')
    parser.add_argument('path', nargs='?', default='.',
                        help='مسار المشروع (افتراضي: المجلد الحالي)')
    parser.add_argument(
        '-o', '--output', default='duplicate_files_report.json', help='ملف التقرير')
    parser.add_argument('-t', '--threshold', type=int, default=80,
                        help='نسبة التشابه للملفات المتشابهة (افتراضي: 80%)')

    args = parser.parse_args()

    # إنشاء كائن الفاحص
    finder = DuplicateFileFinder(args.path)

    # فحص المشروع
    finder.scan_project()

    # البحث عن المكررات
    finder.find_duplicates()

    # البحث عن الملفات المتشابهة
    finder.find_similar_files(args.threshold)

    # طباعة الملخص
    finder.print_summary()

    # حفظ التقرير
    finder.save_report(args.output)

    print(f"\nللحصول على تفاصيل أكثر، افتح ملف: {args.output}")


if __name__ == "__main__":
    main()
