#!/usr/bin/env python3
"""
🧹 Immediate Cleanup Script - AI Teddy Bear Project
التنظيف الفوري للملفات المهجورة والمؤقتة

Lead Architect: جعفر أديب (Jaafar Adeeb)
"""

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path


class ImmediateCleanup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.cleaned_size = 0
        self.cleaned_files = 0

    def get_dir_size(self, path):
        """حساب حجم المجلد"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
        except Exception:
            pass
        return total_size

    def safe_remove_dir(self, dir_path):
        """حذف آمن للمجلد مع تسجيل الحجم"""
        if not os.path.exists(dir_path):
            return 0, 0

        size = self.get_dir_size(dir_path)
        file_count = sum([len(files) for r, d, files in os.walk(dir_path)])

        try:
            shutil.rmtree(dir_path)
            print(f"✅ تم حذف {dir_path} ({size/1024/1024:.1f}MB, {file_count} ملف)")
            return size, file_count
        except Exception as e:
            print(f"❌ خطأ في حذف {dir_path}: {e}")
            return 0, 0

    def remove_cache_files(self):
        """حذف ملفات cache"""
        print("🔄 حذف ملفات cache...")

        patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.pyd",
            "**/*~",
            "**/.pytest_cache",
            "**/.mypy_cache",
            "**/node_modules/.cache",
        ]

        for pattern in patterns:
            for path in glob.glob(pattern, recursive=True):
                if os.path.isfile(path):
                    try:
                        size = os.path.getsize(path)
                        os.remove(path)
                        self.cleaned_size += size
                        self.cleaned_files += 1
                    except Exception:
                        pass
                elif os.path.isdir(path):
                    size, files = self.safe_remove_dir(path)
                    self.cleaned_size += size
                    self.cleaned_files += files

    def remove_deprecated_dirs(self):
        """حذف المجلدات المهجورة"""
        print("🗑️ حذف المجلدات المهجورة...")

        deprecated_dirs = [
            "deprecated",
            "deleted",
            "unused_services",
            "legacy_core",
            "duplicates",
            "tests_config_duplicates",
        ]

        for dir_name in deprecated_dirs:
            for dir_path in glob.glob(f"**/{dir_name}", recursive=True):
                size, files = self.safe_remove_dir(dir_path)
                self.cleaned_size += size
                self.cleaned_files += files

    def remove_duplicate_files(self):
        """حذف الملفات المكررة"""
        print("🔄 حذف الملفات المكررة...")

        duplicate_patterns = [
            "**/*_1.py",
            "**/*_copy.py",
            "**/*_backup.py",
            "**/*_old.py",
            "**/*_duplicate.py",
        ]

        for pattern in duplicate_patterns:
            for file_path in glob.glob(pattern, recursive=True):
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    self.cleaned_size += size
                    self.cleaned_files += 1
                    print(f"🗑️ حُذف ملف مكرر: {file_path}")
                except Exception:
                    pass

    def clean_log_files(self):
        """تنظيف ملفات السجلات القديمة"""
        print("📝 تنظيف ملفات السجلات...")

        log_patterns = ["**/*.log", "**/logs/**/*", "**/.logs/**/*"]

        for pattern in log_patterns:
            for file_path in glob.glob(pattern, recursive=True):
                if os.path.isfile(file_path):
                    try:
                        # حذف ملفات السجلات الأكبر من 10MB
                        size = os.path.getsize(file_path)
                        if size > 10 * 1024 * 1024:  # 10MB
                            os.remove(file_path)
                            self.cleaned_size += size
                            self.cleaned_files += 1
                            print(f"📝 حُذف سجل كبير: {file_path}")
                    except Exception:
                        pass

    def create_gitignore_updates(self):
        """تحديث .gitignore لتجنب المشاكل المستقبلية"""
        print("📝 تحديث .gitignore...")

        gitignore_additions = """
# Python cache files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Development files
*_backup.py
*_old.py
*_copy.py
*_duplicate.py
*_test.py
*_temp.py

# Log files
*.log
logs/
.logs/

# Cache directories
.mypy_cache/
.pytest_cache/
.coverage
htmlcov/

# Deprecated code
deprecated/
deleted/
unused_services/
legacy_core/
duplicates/
"""

        gitignore_path = self.project_root / ".gitignore"
        try:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                f.write(gitignore_additions)
            print("✅ تم تحديث .gitignore")
        except Exception as e:
            print(f"⚠️ تعذر تحديث .gitignore: {e}")

    def run_cleanup(self):
        """تشغيل عملية التنظيف الكاملة"""
        print("🧹 بدء التنظيف الفوري لمشروع AI Teddy Bear")
        print("=" * 50)

        # 1. حذف المجلدات المهجورة
        self.remove_deprecated_dirs()

        # 2. حذف ملفات cache
        self.remove_cache_files()

        # 3. حذف الملفات المكررة
        self.remove_duplicate_files()

        # 4. تنظيف ملفات السجلات
        self.clean_log_files()

        # 5. تحديث gitignore
        self.create_gitignore_updates()

        # تقرير النتائج
        print("\n" + "=" * 50)
        print("📊 نتائج التنظيف:")
        print(f"🗑️ ملفات محذوفة: {self.cleaned_files:,}")
        print(f"💾 مساحة محررة: {self.cleaned_size/1024/1024:.1f} MB")
        print("✅ انتهى التنظيف الفوري بنجاح!")

        return self.cleaned_files, self.cleaned_size


def main():
    """الدالة الرئيسية"""
    try:
        cleaner = ImmediateCleanup()
        files_cleaned, size_freed = cleaner.run_cleanup()

        print(f"\n🎯 خلاصة سريعة:")
        print(f"   📁 {files_cleaned:,} ملف تم حذفه")
        print(f"   💾 {size_freed/1024/1024:.1f} MB تم توفيرها")
        print(f"   🚀 المشروع أصبح أنظف وأسرع!")

        return 0

    except KeyboardInterrupt:
        print("\n⚠️ تم إيقاف العملية بواسطة المستخدم")
        return 1
    except Exception as e:
        print(f"\n❌ خطأ في التنظيف: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
