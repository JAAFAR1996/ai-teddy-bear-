#!/usr/bin/env python3
"""
AI Teddy Bear Project Deep Cleaner & Fixer
==========================================
يقوم بإصلاح جميع المشاكل في المشروع مع الحفاظ على قيمته وميزاته
"""

import os
import shutil
import hashlib
import json
import re
import ast
import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import logging
import argparse
import yaml

# إعداد نظام التسجيل
class ColoredFormatter(logging.Formatter):
    """ملون للرسائل في console"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

# إعداد logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler with colors
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# File handler
file_handler = logging.FileHandler('project_cleanup.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

class ProjectDeepCleaner:
    """منظف ومصلح عميق للمشروع"""
    
    def __init__(self, project_root: str, dry_run: bool = True):
        self.project_root = Path(project_root).resolve()
        self.dry_run = dry_run
        self.backup_dir = self.project_root / f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # إحصائيات
        self.stats = {
            'files_analyzed': 0,
            'issues_found': 0,
            'issues_fixed': 0,
            'files_moved': 0,
            'duplicates_removed': 0,
            'security_issues_fixed': 0,
            'code_quality_fixes': 0,
            'encoding_fixes': 0
        }
        
        # قوائم المشاكل
        self.issues = {
            'misplaced_files': [],
            'duplicate_files': [],
            'security_issues': [],
            'code_quality_issues': [],
            'encoding_issues': [],
            'empty_files': [],
            'large_files': [],
            'unused_imports': [],
            'todo_fixme': []
        }
        
        # الهيكل الصحيح للمشروع
        self.correct_structure = {
            'src': {
                'api': ['endpoints', 'middleware', 'routes'],
                'application': ['services', 'use_cases', 'dto'],
                'domain': ['entities', 'repositories', 'value_objects'],
                'infrastructure': ['database', 'external_services', 'memory'],
                'presentation': ['ui', 'cli', 'web'],
                'compliance': ['checkers', 'managers', 'reports', 'alerts'],
                'monitoring': ['performance', 'logging', 'metrics'],
                'security': ['auth', 'encryption', 'validation']
            },
            'tests': {
                'unit': ['api', 'domain', 'services'],
                'integration': ['api', 'database', 'external'],
                'e2e': ['scenarios', 'fixtures']
            },
            'scripts': ['deployment', 'maintenance', 'analysis'],
            'docs': ['api', 'architecture', 'guides'],
            'config': ['development', 'production', 'testing'],
            'docker': ['services', 'volumes'],
            'kubernetes': ['deployments', 'services', 'configmaps']
        }
        
        # ملفات يجب الحفاظ عليها
        self.protected_files = {
            'README.md', 'LICENSE', '.gitignore', 'requirements.txt',
            'setup.py', 'pyproject.toml', 'Dockerfile', 'docker-compose.yml',
            '.env.example', 'Makefile'
        }
        
        # أنماط الملفات الحساسة
        self.sensitive_patterns = [
            r'api[_-]?key\s*=\s*["\'][\w-]+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI keys
            r'hume_[a-zA-Z0-9]+',   # Hume keys
        ]

    def create_backup(self):
        """إنشاء نسخة احتياطية كاملة قبل البدء"""
        if not self.dry_run:
            logger.info(f"إنشاء نسخة احتياطية في: {self.backup_dir}")
            shutil.copytree(self.project_root, self.backup_dir, 
                          ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.git', 'venv', 'env'))
            logger.info("✅ تم إنشاء النسخة الاحتياطية بنجاح")

    def analyze_project(self):
        """تحليل المشروع بالكامل"""
        logger.info("🔍 بدء التحليل العميق للمشروع...")
        
        for root, dirs, files in os.walk(self.project_root):
            # تجاهل المجلدات غير المرغوبة
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', 'env', '.idea', '.vscode'}]
            
            for file in files:
                if file.endswith('.pyc'):
                    continue
                    
                file_path = Path(root) / file
                self.stats['files_analyzed'] += 1
                
                # فحص موقع الملف
                self._check_file_location(file_path)
                
                # فحص التكرار
                self._check_duplicates(file_path)
                
                # فحص المشاكل الأمنية
                if file_path.suffix in ['.py', '.yml', '.yaml', '.json', '.env']:
                    self._check_security_issues(file_path)
                
                # فحص جودة الكود
                if file_path.suffix == '.py':
                    self._check_code_quality(file_path)
                
                # فحص ترميز الملف
                self._check_encoding(file_path)
                
                # فحص الملفات الفارغة والكبيرة
                self._check_file_size(file_path)

    def _check_file_location(self, file_path: Path):
        """فحص ما إذا كان الملف في المكان الصحيح"""
        relative_path = file_path.relative_to(self.project_root)
        parts = relative_path.parts
        
        # قواعد تحديد الموقع الصحيح
        correct_locations = {
            'cleanup_analyzer.py': 'scripts/maintenance/',
            'find_more_duplicates.py': 'scripts/analysis/',
            'project_cleanup_analyzer.py': 'scripts/maintenance/',
            'imports_checker.py': 'scripts/analysis/',
            'compatibility_test.py': 'tests/integration/',
            'demo_runner.py': 'scripts/demo/'
        }
        
        # فحص الملفات في المستوى الرئيسي
        if len(parts) == 1 and file_path.name.endswith('.py'):
            if file_path.name not in self.protected_files:
                if file_path.name in correct_locations:
                    self.issues['misplaced_files'].append({
                        'file': str(file_path),
                        'current_location': '.',
                        'correct_location': correct_locations[file_path.name]
                    })
                elif any(keyword in file_path.name.lower() for keyword in ['test', 'spec']):
                    self.issues['misplaced_files'].append({
                        'file': str(file_path),
                        'current_location': '.',
                        'correct_location': 'tests/'
                    })
                elif any(keyword in file_path.name.lower() for keyword in ['script', 'tool', 'util']):
                    self.issues['misplaced_files'].append({
                        'file': str(file_path),
                        'current_location': '.',
                        'correct_location': 'scripts/'
                    })
        
        # فحص الملفات في مجلدات backup
        if 'backup' in str(file_path).lower() or 'final_backup' in str(file_path):
            self.issues['misplaced_files'].append({
                'file': str(file_path),
                'current_location': str(file_path.parent),
                'correct_location': 'DELETE_BACKUP'
            })

    def _check_duplicates(self, file_path: Path):
        """فحص الملفات المكررة"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.md5(content).hexdigest()
                
            # البحث عن ملفات أخرى بنفس المحتوى
            for root, _, files in os.walk(self.project_root):
                for other_file in files:
                    other_path = Path(root) / other_file
                    if other_path != file_path and other_path.exists():
                        try:
                            with open(other_path, 'rb') as f:
                                other_content = f.read()
                                other_hash = hashlib.md5(other_content).hexdigest()
                                
                            if file_hash == other_hash:
                                # تحديد أي ملف يجب الاحتفاظ به
                                keep_file = self._determine_file_to_keep(file_path, other_path)
                                remove_file = other_path if keep_file == file_path else file_path
                                
                                duplicate_entry = {
                                    'file1': str(file_path),
                                    'file2': str(other_path),
                                    'keep': str(keep_file),
                                    'remove': str(remove_file),
                                    'size': len(content)
                                }
                                
                                # تجنب إضافة التكرارات المعكوسة
                                if not any(d['file1'] == str(other_path) and d['file2'] == str(file_path) 
                                         for d in self.issues['duplicate_files']):
                                    self.issues['duplicate_files'].append(duplicate_entry)
                                    
                        except Exception:
                            pass
                            
        except Exception as e:
            logger.debug(f"خطأ في فحص التكرار للملف {file_path}: {e}")

    def _determine_file_to_keep(self, file1: Path, file2: Path) -> Path:
        """تحديد أي ملف يجب الاحتفاظ به من الملفات المكررة"""
        # الأولوية للملفات خارج مجلدات backup
        if 'backup' in str(file1).lower():
            return file2
        if 'backup' in str(file2).lower():
            return file1
            
        # الأولوية للملفات في src/
        if str(file1).startswith(str(self.project_root / 'src')):
            return file1
        if str(file2).startswith(str(self.project_root / 'src')):
            return file2
            
        # الأولوية للملف الأقدم (الأصلي على الأرجح)
        if file1.stat().st_mtime < file2.stat().st_mtime:
            return file1
        return file2

    def _check_security_issues(self, file_path: Path):
        """فحص المشاكل الأمنية"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            issues_found = []
            
            # فحص hardcoded secrets
            for pattern in self.sensitive_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    issues_found.append({
                        'type': 'hardcoded_secret',
                        'pattern': pattern,
                        'matches': matches[:3]  # أول 3 نتائج فقط
                    })
            
            # فحص eval/exec في Python
            if file_path.suffix == '.py':
                if 'eval(' in content or 'exec(' in content:
                    issues_found.append({
                        'type': 'dangerous_function',
                        'functions': []
                    })
                    if 'eval(' in content:
                        issues_found[-1]['functions'].append('eval')
                    if 'exec(' in content:
                        issues_found[-1]['functions'].append('exec')
                
                # فحص broad exception handling
                broad_except_pattern = r'except\s*:|except\s+Exception\s*:'
                if re.search(broad_except_pattern, content):
                    issues_found.append({
                        'type': 'broad_exception',
                        'count': len(re.findall(broad_except_pattern, content))
                    })
            
            if issues_found:
                self.issues['security_issues'].append({
                    'file': str(file_path),
                    'issues': issues_found
                })
                
        except Exception as e:
            logger.debug(f"خطأ في فحص الأمان للملف {file_path}: {e}")

    def _check_code_quality(self, file_path: Path):
        """فحص جودة الكود"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                content = ''.join(lines)
            
            issues_found = []
            
            # فحص print statements
            print_count = len(re.findall(r'\bprint\s*\(', content))
            if print_count > 0 and 'test' not in str(file_path).lower():
                issues_found.append({
                    'type': 'print_statements',
                    'count': print_count
                })
            
            # فحص حجم الملف
            if len(lines) > 500:
                issues_found.append({
                    'type': 'large_file',
                    'lines': len(lines)
                })
            
            # فحص TODO/FIXME
            todos = re.findall(r'#\s*(TODO|FIXME).*', content)
            if todos:
                issues_found.append({
                    'type': 'todo_fixme',
                    'items': todos[:5]  # أول 5 فقط
                })
            
            # فحص missing docstrings
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            issues_found.append({
                                'type': 'missing_docstring',
                                'name': node.name,
                                'line': node.lineno
                            })
            except:
                pass
            
            # فحص unused imports
            import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(.+)$'
            imports = re.findall(import_pattern, content, re.MULTILINE)
            used_names = set(re.findall(r'\b(\w+)\b', content))
            
            unused = []
            for from_module, import_names in imports:
                names = [n.strip().split(' as ')[-1] for n in import_names.split(',')]
                for name in names:
                    if name not in used_names:
                        unused.append(name)
            
            if unused:
                issues_found.append({
                    'type': 'unused_imports',
                    'imports': unused[:5]  # أول 5 فقط
                })
            
            if issues_found:
                self.issues['code_quality_issues'].append({
                    'file': str(file_path),
                    'issues': issues_found
                })
                
        except Exception as e:
            logger.debug(f"خطأ في فحص جودة الكود للملف {file_path}: {e}")

    def _check_encoding(self, file_path: Path):
        """فحص مشاكل الترميز"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError:
            self.issues['encoding_issues'].append(str(file_path))
        except Exception:
            pass

    def _check_file_size(self, file_path: Path):
        """فحص حجم الملف"""
        try:
            size = file_path.stat().st_size
            if size == 0:
                self.issues['empty_files'].append(str(file_path))
            elif size > 100 * 1024:  # أكبر من 100KB
                self.issues['large_files'].append({
                    'file': str(file_path),
                    'size': size
                })
        except Exception:
            pass

    def fix_issues(self):
        """إصلاح جميع المشاكل المكتشفة"""
        if self.dry_run:
            logger.info("🔍 وضع المعاينة - لن يتم إجراء أي تغييرات")
            return
            
        logger.info("🔧 بدء إصلاح المشاكل...")
        
        # 1. إصلاح مواقع الملفات
        self._fix_misplaced_files()
        
        # 2. حذف الملفات المكررة
        self._fix_duplicate_files()
        
        # 3. إصلاح المشاكل الأمنية
        self._fix_security_issues()
        
        # 4. إصلاح جودة الكود
        self._fix_code_quality()
        
        # 5. إصلاح مشاكل الترميز
        self._fix_encoding_issues()
        
        # 6. حذف الملفات الفارغة
        self._fix_empty_files()

    def _fix_misplaced_files(self):
        """نقل الملفات إلى أماكنها الصحيحة"""
        logger.info("📁 إصلاح مواقع الملفات...")
        
        for issue in self.issues['misplaced_files']:
            source = Path(issue['file'])
            
            if issue['correct_location'] == 'DELETE_BACKUP':
                # حذف مجلدات backup
                if source.exists():
                    if source.is_dir():
                        shutil.rmtree(source)
                    else:
                        source.unlink()
                    self.stats['files_moved'] += 1
                    logger.info(f"✅ حذف backup: {source}")
            else:
                # نقل الملف للمكان الصحيح
                target_dir = self.project_root / issue['correct_location']
                target_dir.mkdir(parents=True, exist_ok=True)
                
                target = target_dir / source.name
                if source.exists() and not target.exists():
                    shutil.move(str(source), str(target))
                    self.stats['files_moved'] += 1
                    logger.info(f"✅ نقل: {source} -> {target}")

    def _fix_duplicate_files(self):
        """حذف الملفات المكررة"""
        logger.info("🔄 حذف الملفات المكررة...")
        
        removed = set()
        for issue in self.issues['duplicate_files']:
            remove_file = Path(issue['remove'])
            if remove_file.exists() and str(remove_file) not in removed:
                remove_file.unlink()
                removed.add(str(remove_file))
                self.stats['duplicates_removed'] += 1
                logger.info(f"✅ حذف مكرر: {remove_file}")

    def _fix_security_issues(self):
        """إصلاح المشاكل الأمنية"""
        logger.info("🔐 إصلاح المشاكل الأمنية...")
        
        for issue in self.issues['security_issues']:
            file_path = Path(issue['file'])
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                # استبدال hardcoded secrets
                for sec_issue in issue['issues']:
                    if sec_issue['type'] == 'hardcoded_secret':
                        for match in sec_issue['matches']:
                            # استبدال بمتغير بيئة
                            env_var = self._extract_env_var_name(match)
                            replacement = f'os.getenv("{env_var}")'
                            content = content.replace(match, replacement)
                    
                    elif sec_issue['type'] == 'dangerous_function':
                        # استبدال eval/exec بحلول آمنة
                        if 'eval' in sec_issue['functions']:
                            content = re.sub(r'\beval\s*\(', 'ast.literal_eval(', content)
                        if 'exec' in sec_issue['functions']:
                            # إضافة تحذير بدلاً من exec
                            content = re.sub(r'\bexec\s*\(([^)]+)\)', 
                                          r'# SECURITY WARNING: exec removed\n# Original: exec(\1)', 
                                          content)
                    
                    elif sec_issue['type'] == 'broad_exception':
                        # استبدال broad exceptions
                        content = re.sub(r'except\s*:', 'except Exception as e:', content)
                        content = re.sub(r'except\s+Exception\s*:', 'except Exception as e:', content)
                
                # إضافة imports إذا لزم الأمر
                if 'os.getenv' in content and 'import os' not in content:
                    content = 'import os\n' + content
                if 'ast.literal_eval' in content and 'import ast' not in content:
                    content = 'import ast\n' + content
                
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.stats['security_issues_fixed'] += 1
                    logger.info(f"✅ إصلاح أمني: {file_path}")
                    
            except Exception as e:
                logger.error(f"❌ خطأ في إصلاح {file_path}: {e}")

    def _extract_env_var_name(self, secret_string: str) -> str:
        """استخراج اسم متغير البيئة من السلسلة"""
        if 'api_key' in secret_string.lower():
            return 'API_KEY'
        elif 'password' in secret_string.lower():
            return 'PASSWORD'
        elif 'secret' in secret_string.lower():
            return 'SECRET_KEY'
        elif 'token' in secret_string.lower():
            return 'AUTH_TOKEN'
        elif 'sk-' in secret_string:
            return 'OPENAI_API_KEY'
        elif 'hume_' in secret_string:
            return 'HUME_API_KEY'
        else:
            return 'SECRET_VALUE'

    def _fix_code_quality(self):
        """إصلاح مشاكل جودة الكود"""
        logger.info("📝 إصلاح جودة الكود...")
        
        for issue in self.issues['code_quality_issues']:
            file_path = Path(issue['file'])
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                for quality_issue in issue['issues']:
                    if quality_issue['type'] == 'print_statements':
                        # استبدال print بـ logging
                        content = self._replace_print_with_logging(content)
                    
                    elif quality_issue['type'] == 'unused_imports':
                        # حذف imports غير المستخدمة
                        for unused in quality_issue['imports']:
                            # حذف import كامل إذا كان غير مستخدم
                            content = re.sub(f'\\bimport\\s+{unused}\\b.*\\n', '', content)
                            content = re.sub(f'\\bfrom\\s+\\S+\\s+import\\s+.*{unused}.*\\n', '', content)
                
                if content != original_content:
                    # إضافة import logging إذا لزم الأمر
                    if 'logger.' in content and 'import logging' not in content:
                        content = 'import logging\n\nlogger = logging.getLogger(__name__)\n' + content
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.stats['code_quality_fixes'] += 1
                    logger.info(f"✅ تحسين جودة: {file_path}")
                    
            except Exception as e:
                logger.error(f"❌ خطأ في تحسين {file_path}: {e}")

    def _replace_print_with_logging(self, content: str) -> str:
        """استبدال print statements بـ logging"""
        # استبدال print() بـ logger.info()
        content = re.sub(r'\bprint\s*\(\s*f["\']([^"\']+)["\']\s*\)', r'logger.info("\1")', content)
        content = re.sub(r'\bprint\s*\(\s*["\']([^"\']+)["\']\s*\)', r'logger.info("\1")', content)
        content = re.sub(r'\bprint\s*\(([^)]+)\)', r'logger.info(\1)', content)
        
        return content

    def _fix_encoding_issues(self):
        """إصلاح مشاكل الترميز"""
        logger.info("🔤 إصلاح مشاكل الترميز...")
        
        for file_path in self.issues['encoding_issues']:
            file_path = Path(file_path)
            if not file_path.exists():
                continue
                
            try:
                # محاولة قراءة بترميزات مختلفة
                content = None
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content:
                    # إعادة الكتابة بترميز UTF-8
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.stats['encoding_fixes'] += 1
                    logger.info(f"✅ إصلاح ترميز: {file_path}")
                    
            except Exception as e:
                logger.error(f"❌ خطأ في إصلاح ترميز {file_path}: {e}")

    def _fix_empty_files(self):
        """حذف الملفات الفارغة غير الضرورية"""
        logger.info("🗑️ حذف الملفات الفارغة...")
        
        for file_path in self.issues['empty_files']:
            file_path = Path(file_path)
            if not file_path.exists():
                continue
                
            # الحفاظ على __init__.py الضرورية
            if file_path.name == '__init__.py':
                # التحقق من وجود ملفات Python أخرى في نفس المجلد
                parent_dir = file_path.parent
                other_py_files = list(parent_dir.glob('*.py'))
                if len(other_py_files) > 1:  # يوجد ملفات أخرى
                    continue  # الحفاظ على __init__.py
            
            # حذف الملف الفارغ
            file_path.unlink()
            self.stats['issues_fixed'] += 1
            logger.info(f"✅ حذف ملف فارغ: {file_path}")

    def generate_report(self) -> str:
        """توليد تقرير شامل بتنسيق Markdown"""
        report = []
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report.append("# 📊 تقرير تنظيف وإصلاح مشروع AI Teddy Bear")
        report.append(f"\n**التاريخ والوقت**: {timestamp}")
        report.append(f"\n**الوضع**: {'معاينة فقط' if self.dry_run else 'تنفيذ فعلي'}")
        
        # الإحصائيات العامة
        report.append("\n## 📈 الإحصائيات العامة")
        report.append(f"- **الملفات المفحوصة**: {self.stats['files_analyzed']:,}")
        report.append(f"- **المشاكل المكتشفة**: {self._count_total_issues():,}")
        report.append(f"- **المشاكل المُصلحة**: {self.stats['issues_fixed']:,}")
        
        # تفاصيل الإصلاحات
        if not self.dry_run:
            report.append("\n## ✅ الإصلاحات المنفذة")
            report.append(f"- **الملفات المنقولة**: {self.stats['files_moved']}")
            report.append(f"- **الملفات المكررة المحذوفة**: {self.stats['duplicates_removed']}")
            report.append(f"- **المشاكل الأمنية المُصلحة**: {self.stats['security_issues_fixed']}")
            report.append(f"- **تحسينات جودة الكود**: {self.stats['code_quality_fixes']}")
            report.append(f"- **مشاكل الترميز المُصلحة**: {self.stats['encoding_fixes']}")
        
        # تفاصيل المشاكل
        report.append("\n## 🔍 تفاصيل المشاكل المكتشفة")
        
        # 1. الملفات في أماكن خاطئة
        if self.issues['misplaced_files']:
            report.append(f"\n### 📁 الملفات في أماكن خاطئة ({len(self.issues['misplaced_files'])})")
            report.append("\n| الملف | الموقع الحالي | الموقع الصحيح | الحالة |")
            report.append("|-------|---------------|---------------|--------|")
            
            for issue in self.issues['misplaced_files'][:20]:  # أول 20 فقط
                status = "✅ تم النقل" if not self.dry_run else "⏳ في الانتظار"
                current = issue['current_location']
                correct = issue['correct_location']
                if correct == 'DELETE_BACKUP':
                    correct = "🗑️ حذف (backup)"
                report.append(f"| {Path(issue['file']).name} | {current} | {correct} | {status} |")
            
            if len(self.issues['misplaced_files']) > 20:
                report.append(f"\n*... و {len(self.issues['misplaced_files']) - 20} ملف آخر*")
        
        # 2. الملفات المكررة
        if self.issues['duplicate_files']:
            report.append(f"\n### 🔄 الملفات المكررة ({len(self.issues['duplicate_files'])})")
            report.append("\n| الملف الأصلي | الملف المكرر | الحجم | الحالة |")
            report.append("|---------------|--------------|--------|--------|")
            
            for issue in self.issues['duplicate_files'][:15]:
                status = "✅ تم الحذف" if not self.dry_run else "⏳ في الانتظار"
                size = self._format_size(issue['size'])
                keep_name = Path(issue['keep']).name
                remove_name = Path(issue['remove']).name
                report.append(f"| {keep_name} | {remove_name} | {size} | {status} |")
            
            if len(self.issues['duplicate_files']) > 15:
                report.append(f"\n*... و {len(self.issues['duplicate_files']) - 15} ملف مكرر آخر*")
        
        # 3. المشاكل الأمنية
        if self.issues['security_issues']:
            report.append(f"\n### 🔐 المشاكل الأمنية ({len(self.issues['security_issues'])})")
            
            security_summary = defaultdict(int)
            for issue in self.issues['security_issues']:
                for sec_issue in issue['issues']:
                    security_summary[sec_issue['type']] += 1
            
            report.append("\n| نوع المشكلة | العدد | الحالة |")
            report.append("|-------------|-------|--------|")
            
            type_names = {
                'hardcoded_secret': '🔑 مفاتيح مكشوفة',
                'dangerous_function': '⚠️ دوال خطرة (eval/exec)',
                'broad_exception': '🕳️ معالجة أخطاء ضعيفة'
            }
            
            for issue_type, count in security_summary.items():
                status = "✅ تم الإصلاح" if not self.dry_run else "⏳ في الانتظار"
                report.append(f"| {type_names.get(issue_type, issue_type)} | {count} | {status} |")
            
            # أمثلة على الملفات المتأثرة
            report.append("\n**أمثلة على الملفات المتأثرة:**")
            for issue in self.issues['security_issues'][:5]:
                report.append(f"- `{Path(issue['file']).name}`")
        
        # 4. مشاكل جودة الكود
        if self.issues['code_quality_issues']:
            report.append(f"\n### 📝 مشاكل جودة الكود ({len(self.issues['code_quality_issues'])})")
            
            quality_summary = defaultdict(int)
            for issue in self.issues['code_quality_issues']:
                for q_issue in issue['issues']:
                    quality_summary[q_issue['type']] += 1
            
            report.append("\n| نوع المشكلة | العدد | الحالة |")
            report.append("|-------------|-------|--------|")
            
            type_names = {
                'print_statements': '🖨️ استخدام print',
                'large_file': '📏 ملفات كبيرة جداً',
                'todo_fixme': '📌 TODO/FIXME',
                'missing_docstring': '📄 نقص التوثيق',
                'unused_imports': '📦 imports غير مستخدمة'
            }
            
            for issue_type, count in quality_summary.items():
                status = "✅ تم الإصلاح" if not self.dry_run and issue_type in ['print_statements', 'unused_imports'] else "⏳ يحتاج مراجعة"
                report.append(f"| {type_names.get(issue_type, issue_type)} | {count} | {status} |")
        
        # 5. مشاكل الترميز
        if self.issues['encoding_issues']:
            report.append(f"\n### 🔤 مشاكل الترميز ({len(self.issues['encoding_issues'])})")
            report.append("\n**الملفات المتأثرة:**")
            for file_path in self.issues['encoding_issues'][:10]:
                status = "✅" if not self.dry_run else "⏳"
                report.append(f"- {status} `{Path(file_path).name}`")
            
            if len(self.issues['encoding_issues']) > 10:
                report.append(f"\n*... و {len(self.issues['encoding_issues']) - 10} ملف آخر*")
        
        # 6. الملفات الفارغة
        if self.issues['empty_files']:
            report.append(f"\n### 🗑️ الملفات الفارغة ({len(self.issues['empty_files'])})")
            empty_by_type = defaultdict(list)
            for file_path in self.issues['empty_files']:
                ext = Path(file_path).suffix or 'no_extension'
                empty_by_type[ext].append(file_path)
            
            for ext, files in empty_by_type.items():
                report.append(f"\n**{ext} ({len(files)} ملف):**")
                for file_path in files[:5]:
                    status = "✅ محذوف" if not self.dry_run else "⏳"
                    report.append(f"- {status} `{Path(file_path).name}`")
                if len(files) > 5:
                    report.append(f"  *... و {len(files) - 5} ملف آخر*")
        
        # 7. الملفات الكبيرة
        if self.issues['large_files']:
            report.append(f"\n### 📏 الملفات الكبيرة جداً ({len(self.issues['large_files'])})")
            report.append("\n| الملف | الحجم | السطور | التوصية |")
            report.append("|-------|--------|---------|----------|")
            
            sorted_large = sorted(self.issues['large_files'], key=lambda x: x['size'], reverse=True)
            for issue in sorted_large[:10]:
                file_name = Path(issue['file']).name
                size = self._format_size(issue['size'])
                lines = "N/A"
                if Path(issue['file']).suffix == '.py':
                    try:
                        with open(issue['file'], 'r', encoding='utf-8', errors='ignore') as f:
                            lines = str(len(f.readlines()))
                    except:
                        pass
                report.append(f"| {file_name} | {size} | {lines} | يحتاج تقسيم |")
        
        # التوصيات
        report.append("\n## 💡 التوصيات")
        report.append("\n### للحفاظ على نظافة المشروع:")
        report.append("1. **استخدام pre-commit hooks** لفحص الكود قبل الـ commit")
        report.append("2. **تطبيق معايير كتابة كود واضحة** (PEP 8 for Python)")
        report.append("3. **مراجعة الكود الإلزامية** لكل Pull Request")
        report.append("4. **استخدام أدوات تحليل تلقائية** (pylint, flake8, black)")
        report.append("5. **توثيق واضح** لهيكل المشروع والمعايير المتبعة")
        
        report.append("\n### للأمان:")
        report.append("1. **استخدام متغيرات البيئة** لجميع المفاتيح والأسرار")
        report.append("2. **تجنب eval/exec** نهائياً")
        report.append("3. **معالجة أخطاء محددة** بدلاً من catch-all")
        report.append("4. **مراجعة أمنية دورية** للكود والتبعيات")
        
        # الخطوات التالية
        if self.dry_run:
            report.append("\n## 🚀 الخطوات التالية")
            report.append("\n**لتنفيذ الإصلاحات، شغل الأمر التالي:**")
            report.append("```bash")
            report.append("python project_deep_cleaner.py --execute")
            report.append("```")
            report.append("\n⚠️ **تحذير**: تأكد من وجود نسخة احتياطية قبل التنفيذ!")
        else:
            report.append("\n## ✅ تم الانتهاء")
            report.append(f"\n**النسخة الاحتياطية محفوظة في**: `{self.backup_dir}`")
            report.append("\n**يُنصح بـ**:")
            report.append("1. مراجعة التغييرات في git: `git diff`")
            report.append("2. تشغيل الاختبارات: `pytest`")
            report.append("3. التحقق من عمل التطبيق")
        
        return '\n'.join(report)

    def _count_total_issues(self) -> int:
        """حساب إجمالي المشاكل المكتشفة"""
        total = 0
        total += len(self.issues['misplaced_files'])
        total += len(self.issues['duplicate_files'])
        total += len(self.issues['security_issues'])
        total += len(self.issues['code_quality_issues'])
        total += len(self.issues['encoding_issues'])
        total += len(self.issues['empty_files'])
        total += len(self.issues['large_files'])
        return total

    def _format_size(self, size_bytes: int) -> str:
        """تنسيق حجم الملف"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def save_report(self, report: str):
        """حفظ التقرير في ملف"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.project_root / f"cleanup_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 تم حفظ التقرير في: {report_file}")

    def run(self):
        """تشغيل عملية التنظيف والإصلاح الكاملة"""
        logger.info("🚀 بدء عملية التنظيف والإصلاح...")
        logger.info(f"📁 مجلد المشروع: {self.project_root}")
        
        # إنشاء نسخة احتياطية
        if not self.dry_run:
            self.create_backup()
        
        # تحليل المشروع
        self.analyze_project()
        
        # إصلاح المشاكل
        self.fix_issues()
        
        # توليد التقرير
        report = self.generate_report()
        
        # عرض التقرير
        print("\n" + "="*80)
        print(report)
        print("="*80 + "\n")
        
        # حفظ التقرير
        self.save_report(report)
        
        logger.info("✅ انتهت عملية التنظيف والإصلاح!")


def main():
    """نقطة الدخول الرئيسية"""
    parser = argparse.ArgumentParser(
        description='منظف ومصلح عميق لمشروع AI Teddy Bear',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة الاستخدام:
  python project_deep_cleaner.py --dry-run     # معاينة فقط (افتراضي)
  python project_deep_cleaner.py --execute     # تنفيذ الإصلاحات
  python project_deep_cleaner.py --path /path/to/project --execute
        """
    )
    
    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='مسار مجلد المشروع (افتراضي: المجلد الحالي)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='معاينة فقط بدون إجراء تغييرات (افتراضي)'
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='تنفيذ الإصلاحات فعلياً'
    )
    
    args = parser.parse_args()
    
    # تحديد وضع التشغيل
    dry_run = not args.execute
    
    # إنشاء وتشغيل المنظف
    cleaner = ProjectDeepCleaner(args.path, dry_run=dry_run)
    cleaner.run()


if __name__ == "__main__":
    main()