#!/usr/bin/env python3
"""
AI Teddy Bear Project Enhanced Deep Cleaner & Fixer
==================================================
نسخة محسّنة مع تحسينات الأداء وأفضل الممارسات
- استخدام os.scandir() بدلاً من os.walk()
- خوارزميات تكرار محسّنة O(n log n)
- AST لتعديل الكود الآمن
- Logging مركزي مع RotatingFileHandler
- Progress tracking
- Unit tests ready
"""

import os
import ast
import sys
import shutil
import hashlib
import json
import datetime
import logging
import argparse
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Iterator, Any
from collections import defaultdict
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# === ENHANCED LOGGING CONFIGURATION ===
class EnhancedColoredFormatter(logging.Formatter):
    """محسّن للرسائل الملونة مع معلومات إضافية"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green  
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'PROGRESS': '\033[94m', # Blue
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # إضافة معلومات thread إذا كان متعدد الخيوط
        if hasattr(record, 'thread_name'):
            record.thread_info = f"[{record.thread_name}]"
        else:
            record.thread_info = ""
            
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_enhanced_logging(log_file: str = "project_cleanup_enhanced.log", 
                          max_size: int = 10 * 1024 * 1024,  # 10MB
                          backup_count: int = 5) -> logging.Logger:
    """إعداد نظام logging محسّن مع RotatingFileHandler"""
    
    # إنشاء logger مخصص
    logger = logging.getLogger('project_cleaner')
    logger.setLevel(logging.DEBUG)
    
    # تجنب إضافة handlers متعددة
    if logger.handlers:
        return logger
    
    # Console handler with enhanced colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = EnhancedColoredFormatter(
        '%(asctime)s %(thread_info)s- %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Rotating file handler لمنع كبر حجم السجل
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_size, 
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(threadName)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # إضافة handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # منع الانتشار للـ root logger
    logger.propagate = False
    
    return logger


# === SAFE AST CODE TRANSFORMER ===
class SafeCodeTransformer(ast.NodeTransformer):
    """محول آمن للكود باستخدام AST بدلاً من regex"""
    
    def __init__(self):
        self.changes_made = 0
        self.issues_found = []
        
    def visit_Call(self, node: ast.Call) -> Any:
        """زيارة استدعاءات الدوال"""
        # استبدال print بـ logger
        if (isinstance(node.func, ast.Name) and 
            node.func.id == 'print'):
            
            # إنشاء استدعاء logger.info
            logger_attr = ast.Attribute(
                value=ast.Name(id='logger', ctx=ast.Load()),
                attr='info',
                ctx=ast.Load()
            )
            
            new_call = ast.Call(
                func=logger_attr,
                args=node.args,
                keywords=node.keywords
            )
            
            self.changes_made += 1
            self.issues_found.append(f"استبدال print بـ logger في السطر {node.lineno}")
            return new_call
            
        # إزالة eval/exec - استبدال بـ ast.literal_eval أو تحذير
        elif (isinstance(node.func, ast.Name) and 
              node.func.id in ['eval', 'exec']):
            
            if node.func.id == 'eval':
                # استبدال eval بـ ast.literal_eval
                literal_eval = ast.Attribute(
                    value=ast.Name(id='ast', ctx=ast.Load()),
                    attr='literal_eval', 
                    ctx=ast.Load()
                )
                new_call = ast.Call(
                    func=literal_eval,
                    args=node.args,
                    keywords=node.keywords
                )
                self.changes_made += 1
                self.issues_found.append(f"استبدال eval بـ ast.literal_eval في السطر {node.lineno}")
                return new_call
            else:
                # إزالة exec وإضافة تحذير
                self.changes_made += 1
                self.issues_found.append(f"إزالة exec خطرة في السطر {node.lineno}")
                return ast.Constant(value=None)  # استبدال بـ None
                
        return self.generic_visit(node)
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> Any:
        """تحسين معالجة الأخطاء الضعيفة"""
        if node.type is None:  # except: بدون تحديد نوع
            # إضافة Exception as e
            node.type = ast.Name(id='Exception', ctx=ast.Load())
            node.name = 'e'
            self.changes_made += 1
            self.issues_found.append(f"تحسين معالجة أخطاء ضعيفة في السطر {node.lineno}")
            
        return self.generic_visit(node)


# === ENHANCED FILE SCANNER ===
class EnhancedFileScanner:
    """ماسح ملفات محسّن باستخدام os.scandir()"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.progress_count = 0
        self.progress_lock = threading.Lock()
        
    def iter_files(self, root: Path, 
                   extensions: Set[str] = None,
                   ignore_patterns: Set[str] = None) -> Iterator[Path]:
        """تكرار محسّن على الملفات باستخدام os.scandir()"""
        
        if ignore_patterns is None:
            ignore_patterns = {'.git', '__pycache__', 'venv', 'env', 
                             '.idea', '.vscode', 'node_modules'}
        
        try:
            with os.scandir(root) as entries:
                for entry in entries:
                    # تحديث التقدم
                    with self.progress_lock:
                        self.progress_count += 1
                        if self.progress_count % 1000 == 0:
                            self.logger.info(f"🔎 فحص {self.progress_count} عنصر حتى الآن...")
                    
                    if entry.is_dir(follow_symlinks=False):
                        # تجاهل المجلدات المحددة
                        if entry.name not in ignore_patterns:
                            yield from self.iter_files(
                                Path(entry.path), 
                                extensions, 
                                ignore_patterns
                            )
                    else:
                        # فلترة حسب الامتدادات
                        if extensions is None or Path(entry.path).suffix in extensions:
                            yield Path(entry.path)
                            
        except (OSError, PermissionError) as e:
            self.logger.warning(f"تعذر الوصول إلى {root}: {e}")


# === OPTIMIZED DUPLICATE DETECTOR ===
class OptimizedDuplicateDetector:
    """كاشف تكرارات محسّن بتعقيد O(n log n)"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.size_groups: Dict[int, List[Path]] = defaultdict(list)
        self.hash_cache: Dict[Path, str] = {}
        
    def find_duplicates(self, files: List[Path]) -> List[Dict]:
        """العثور على التكرارات بكفاءة عالية"""
        
        self.logger.info("🔍 تجميع الملفات حسب الحجم...")
        
        # المرحلة 1: تجميع حسب الحجم
        for file_path in files:
            try:
                size = file_path.stat().st_size
                self.size_groups[size].append(file_path)
            except (OSError, FileNotFoundError):
                continue
        
        self.logger.info(f"📊 وُجد {len(self.size_groups)} مجموعة حجم مختلفة")
        
        duplicates = []
        potential_groups = [(size, files) for size, files in self.size_groups.items() 
                           if len(files) > 1]
        
        self.logger.info(f"🔎 فحص {len(potential_groups)} مجموعة محتملة للتكرار...")
        
        # المرحلة 2: فحص hash فقط للملفات ذات نفس الحجم
        for size, size_group in potential_groups:
            hash_groups = self._group_by_hash(size_group)
            
            for file_hash, hash_group in hash_groups.items():
                if len(hash_group) > 1:
                    # ترتيب الملفات لتحديد أيها نحتفظ به
                    sorted_files = self._sort_files_by_priority(hash_group)
                    keep_file = sorted_files[0]
                    
                    for duplicate_file in sorted_files[1:]:
                        duplicates.append({
                            'file1': str(keep_file),
                            'file2': str(duplicate_file),
                            'keep': str(keep_file),
                            'remove': str(duplicate_file),
                            'size': size,
                            'hash': file_hash
                        })
        
        self.logger.info(f"✅ اكتشف {len(duplicates)} ملف مكرر")
        return duplicates
    
    def _group_by_hash(self, files: List[Path]) -> Dict[str, List[Path]]:
        """تجميع الملفات حسب hash"""
        hash_groups = defaultdict(list)
        
        for file_path in files:
            try:
                file_hash = self._get_file_hash(file_path)
                hash_groups[file_hash].append(file_path)
            except Exception as e:
                self.logger.debug(f"خطأ في حساب hash لـ {file_path}: {e}")
                continue
                
        return hash_groups
    
    def _get_file_hash(self, file_path: Path) -> str:
        """حساب hash الملف مع cache"""
        if file_path in self.hash_cache:
            return self.hash_cache[file_path]
            
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                # قراءة الملف على أجزاء لتوفير الذاكرة
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            
            file_hash = hasher.hexdigest()
            self.hash_cache[file_path] = file_hash
            return file_hash
            
        except Exception as e:
            raise Exception(f"فشل في حساب hash: {e}")
    
    def _sort_files_by_priority(self, files: List[Path]) -> List[Path]:
        """ترتيب الملفات حسب الأولوية (أيها نحتفظ به)"""
        def priority_key(file_path: Path) -> Tuple[int, int, str]:
            # 1. تجنب backup folders
            backup_penalty = 0 if 'backup' in str(file_path).lower() else 1
            
            # 2. تفضيل src/ folder  
            src_bonus = 1 if 'src/' in str(file_path) else 0
            
            # 3. تفضيل الملف الأقدم (الأصلي)
            try:
                mtime = -file_path.stat().st_mtime  # سالب للترتيب العكسي
            except:
                mtime = 0
                
            return (backup_penalty, src_bonus, mtime)
        
        return sorted(files, key=priority_key, reverse=True)


# === MAIN ENHANCED CLEANER CLASS ===
class EnhancedProjectCleaner:
    """منظف مشروع محسّن مع أفضل الممارسات"""
    
    def __init__(self, project_root: str, dry_run: bool = True, 
                 max_workers: int = 4):
        self.project_root = Path(project_root).resolve()
        self.dry_run = dry_run
        self.max_workers = max_workers
        
        # إعداد logging
        self.logger = setup_enhanced_logging()
        
        # إعداد المكونات المحسّنة
        self.file_scanner = EnhancedFileScanner(self.logger)
        self.duplicate_detector = OptimizedDuplicateDetector(self.logger)
        self.ast_transformer = SafeCodeTransformer()
        
        # نسخة احتياطية
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = self.project_root / f"enhanced_backup_{timestamp}"
        
        # إحصائيات محسّنة
        self.stats = {
            'files_scanned': 0,
            'directories_scanned': 0,
            'issues_found': 0,
            'issues_fixed': 0,
            'duplicates_removed': 0,
            'security_fixes': 0,
            'ast_transformations': 0,
            'encoding_fixes': 0,
            'performance_optimizations': 0
        }
        
        # تجميع المشاكل
        self.issues = {
            'duplicates': [],
            'security_issues': [],
            'code_quality': [],
            'encoding_problems': [],
            'large_files': [],
            'empty_files': [],
            'misplaced_files': []
        }
    
    def create_safe_backup(self) -> bool:
        """إنشاء نسخة احتياطية آمنة"""
        if self.dry_run:
            self.logger.info("🔍 وضع المعاينة - تخطي النسخة الاحتياطية")
            return True
            
        try:
            self.logger.info(f"💾 إنشاء نسخة احتياطية آمنة في: {self.backup_dir}")
            
            def ignore_func(dir_path, filenames):
                """تجاهل الملفات غير الضرورية في النسخة الاحتياطية"""
                ignore = set()
                for filename in filenames:
                    if (filename.endswith(('.pyc', '.pyo')) or
                        filename in {'__pycache__', '.git', 'venv', 'env', 
                                   'node_modules', '.idea', '.vscode'}):
                        ignore.add(filename)
                return ignore
            
            shutil.copytree(self.project_root, self.backup_dir, ignore=ignore_func)
            self.logger.info("✅ تم إنشاء النسخة الاحتياطية بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ فشل في إنشاء النسخة الاحتياطية: {e}")
            return False 