#!/usr/bin/env python3
"""
Quick Duplicate Finder for AI Teddy Bear Project
محلل سريع للملفات المكررة
"""

import os
import ast
import hashlib
from pathlib import Path
from collections import defaultdict
import json

class QuickDuplicateFinder:
    def __init__(self):
        self.files_info = {}
        self.duplicates = []
        self.service_duplicates = {}
        
    def scan_project(self):
        print('🔍 مسح المشروع...')
        for file_path in Path('.').rglob('*.py'):
            if any(skip in str(file_path) for skip in ['.git', '__pycache__', 'venv', '.venv']):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if len(content.strip()) > 0:
                    self.files_info[str(file_path)] = {
                        'content': content,
                        'hash': hashlib.md5(content.encode()).hexdigest(),
                        'size': len(content),
                        'lines': len(content.splitlines()),
                        'classes': self.extract_classes(content),
                        'functions': self.extract_functions(content)
                    }
            except:
                pass
        print(f'✅ تم مسح {len(self.files_info)} ملف')
        
    def extract_classes(self, content):
        """استخراج أسماء الكلاسات"""
        try:
            tree = ast.parse(content)
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            return classes
        except:
            return []
    
    def extract_functions(self, content):
        """استخراج أسماء الدوال"""
        try:
            tree = ast.parse(content)
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
            return functions
        except:
            return []
        
    def find_exact_duplicates(self):
        print('🔍 البحث عن الملفات المطابقة تماماً...')
        hash_groups = defaultdict(list)
        
        for file_path, info in self.files_info.items():
            hash_groups[info['hash']].append((file_path, info))
        
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                self.duplicates.append(files)
        
        print(f'✅ تم العثور على {len(self.duplicates)} مجموعة مكررة')
        
    def find_service_duplicates(self):
        print('🔍 البحث عن الخدمات المتشابهة...')
        service_patterns = {
            'ai_service': [],
            'audio_service': [],
            'emotion_service': [],
            'transcription_service': [],
            'cache_service': [],
            'moderation_service': [],
            'synthesis_service': [],
            'streaming_service': [],
            'memory_service': [],
            'database_service': []
        }
        
        for file_path in self.files_info.keys():
            filename = Path(file_path).name.lower()
            for pattern in service_patterns.keys():
                pattern_words = pattern.split('_')
                if any(word in filename for word in pattern_words):
                    service_patterns[pattern].append(file_path)
        
        self.service_duplicates = {k: v for k, v in service_patterns.items() if len(v) > 1}
        
        if self.service_duplicates:
            print('🛠️ الخدمات المكررة:')
            for service_type, files in self.service_duplicates.items():
                print(f'  - {service_type}: {len(files)} ملف')
                for file_path in files:
                    print(f'    • {file_path}')
        else:
            print('✅ لم يتم العثور على خدمات مكررة')
    
    def find_similar_classes(self):
        print('🔍 البحث عن الكلاسات المتشابهة...')
        class_groups = defaultdict(list)
        
        for file_path, info in self.files_info.items():
            for class_name in info['classes']:
                class_groups[class_name].append(file_path)
        
        duplicate_classes = {k: v for k, v in class_groups.items() if len(v) > 1}
        
        if duplicate_classes:
            print('🏗️ الكلاسات المكررة:')
            for class_name, files in duplicate_classes.items():
                print(f'  - {class_name}: {len(files)} ملف')
                for file_path in files:
                    print(f'    • {file_path}')
        else:
            print('✅ لم يتم العثور على كلاسات مكررة')
            
        return duplicate_classes
    
    def find_config_duplicates(self):
        print('🔍 البحث عن ملفات التكوين المكررة...')
        config_files = []
        
        for file_path in self.files_info.keys():
            if 'config' in Path(file_path).name.lower():
                config_files.append(file_path)
        
        if len(config_files) > 3:  # أكثر من 3 ملفات تكوين
            print(f'⚠️ يوجد {len(config_files)} ملف تكوين:')
            for file_path in config_files:
                print(f'  • {file_path}')
        else:
            print('✅ عدد ملفات التكوين طبيعي')
        
        return config_files
        
    def generate_report(self):
        print('📊 إنشاء التقرير...')
        
        total_wasted_space = 0
        
        print('=' * 80)
        print('🔍 تقرير الملفات المكررة الشامل')
        print('=' * 80)
        print(f'📁 إجمالي الملفات: {len(self.files_info)}')
        print(f'🔄 مجموعات مكررة: {len(self.duplicates)}')
        print(f'🛠️ أنواع خدمات مكررة: {len(self.service_duplicates)}')
        
        if self.duplicates:
            print('\n🔄 الملفات المطابقة تماماً:')
            for i, group in enumerate(self.duplicates, 1):
                print(f'\n{i}. مجموعة مكررة ({len(group)} ملفات):')
                
                # حساب المساحة المهدرة
                file_size = group[0][1]['size']
                wasted_space = file_size * (len(group) - 1)
                total_wasted_space += wasted_space
                
                print(f'   المساحة المهدرة: {wasted_space} بايت')
                
                for file_path, info in group:
                    print(f'   • {file_path} ({info["lines"]} سطر)')
        
        if self.service_duplicates:
            print('\n🛠️ الخدمات المكررة:')
            for service_type, files in self.service_duplicates.items():
                print(f'\n{service_type.upper()}:')
                for file_path in files:
                    print(f'  • {file_path}')
        
        print(f'\n💾 إجمالي المساحة المهدرة: {total_wasted_space} بايت')
        print('=' * 80)
        
        # حفظ التقرير في ملف JSON
        report_data = {
            'total_files': len(self.files_info),
            'exact_duplicates': len(self.duplicates),
            'service_duplicates': len(self.service_duplicates),
            'wasted_space': total_wasted_space,
            'duplicate_groups': [
                {
                    'files': [f[0] for f in group],
                    'size': group[0][1]['size'],
                    'lines': group[0][1]['lines']
                }
                for group in self.duplicates
            ],
            'service_duplicates_detail': self.service_duplicates
        }
        
        with open('duplicate_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print('✅ تم حفظ التقرير في: duplicate_report.json')
        
    def create_cleanup_suggestions(self):
        print('💡 إنشاء اقتراحات التنظيف...')
        
        suggestions = []
        
        # اقتراحات للملفات المطابقة تماماً
        for group in self.duplicates:
            files = [f[0] for f in group]
            # اختر الملف الأفضل (في src عادة)
            best_file = None
            for file_path in files:
                if 'src/' in file_path and 'test' not in file_path:
                    best_file = file_path
                    break
            
            if not best_file:
                best_file = files[0]  # اختر الأول إذا لم نجد أفضل
            
            files_to_delete = [f for f in files if f != best_file]
            
            suggestions.append({
                'type': 'exact_duplicate',
                'keep': best_file,
                'delete': files_to_delete,
                'reason': 'ملفات متطابقة تماماً'
            })
        
        # اقتراحات للخدمات المكررة
        for service_type, files in self.service_duplicates.items():
            if len(files) > 2:  # أكثر من ملفين
                suggestions.append({
                    'type': 'service_consolidation',
                    'service': service_type,
                    'files': files,
                    'reason': f'دمج خدمات {service_type}'
                })
        
        # حفظ الاقتراحات
        with open('cleanup_suggestions.json', 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, indent=2, ensure_ascii=False)
        
        print('✅ تم حفظ اقتراحات التنظيف في: cleanup_suggestions.json')
        
        return suggestions
        
    def run(self):
        self.scan_project()
        self.find_exact_duplicates()
        self.find_service_duplicates()
        duplicate_classes = self.find_similar_classes()
        config_files = self.find_config_duplicates()
        self.generate_report()
        suggestions = self.create_cleanup_suggestions()
        
        print('\n🎯 ملخص النتائج:')
        print(f'  - ملفات مطابقة تماماً: {len(self.duplicates)}')
        print(f'  - خدمات مكررة: {len(self.service_duplicates)}')
        print(f'  - كلاسات مكررة: {len(duplicate_classes)}')
        print(f'  - ملفات تكوين: {len(config_files)}')
        print(f'  - اقتراحات تنظيف: {len(suggestions)}')

if __name__ == "__main__":
    finder = QuickDuplicateFinder()
    finder.run() 