from pathlib import Path
import sys
import subprocess
import os
import structlog
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

#
#!/usr/bin/env python3
"""
سكريبت إعداد وتشغيل مشروع AI Teddy Bear
"""

logger = structlog.get_logger(__name__)


def create_directories() -> Any:
    """إنشاء المجلدات المطلوبة"""
    directories = [
        "data",
        "uploads/audio",
        "uploads/temp",
        "outputs/stories",
        "outputs/responses",
        "outputs/processed",
        "static/css",
        "static/js",
        "static/images",
        "logs"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ تم إنشاء مجلد: {directory}")


def install_requirements() -> Any:
    """تثبيت المتطلبات"""
    logger.info("📦 تثبيت المتطلبات...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("✓ تم تثبيت جميع المتطلبات بنجاح")
    except Exception as e:
        logger.error(f"❌ فشل في تثبيت المتطلبات: {e}")
        return False
    return True


def create_env_file() -> Any:
    """إنشاء ملف البيئة"""
    env_content =

    if not Path(".env").exists():
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        logger.info("✓ تم إنشاء ملف .env")
        logger.warning("⚠️  يرجى تعبئة مفاتيح API في ملف .env")
    else:
        logger.info("✓ ملف .env موجود بالفعل")


def initialize_database() -> Any:
    """تهيئة قاعدة البيانات"""
    logger.info("🗄️  تهيئة قاعدة البيانات...")
    try:
        from src.data.database import Database
        db = Database()
        logger.info("✓ تم تهيئة قاعدة البيانات بنجاح")
    except Exception as e:
        logger.error(f"❌ فشل في تهيئة قاعدة البيانات: {e}")


def run_tests() -> Any:
    """تشغيل الاختبارات"""
    logger.info("🧪 تشغيل الاختبارات...")
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v"])
        logger.info("✓ جميع الاختبارات نجحت")
    except subprocess.CalledProcessError as e:
        logger.error(f"⚠️  بعض الاختبارات فشلت: {e}")
    except Exception as e:
        logger.error(f"ℹ️  خطأ غير متوقع أثناء تشغيل الاختبارات: {e}")


def main() -> Any:
    """الدالة الرئيسية للإعداد"""
    logger.info("🚀 بدء إعداد مشروع AI Teddy Bear")
    logger.info("=" * 50)

    # إنشاء المجلدات
    create_directories()

    # تثبيت المتطلبات
    if not install_requirements():
        return

    # إنشاء ملف البيئة
    create_env_file()

    # تهيئة قاعدة البيانات
    initialize_database()

    # تشغيل الاختبارات
    run_tests()

    logger.info("\n" + "=" * 50)
    logger.info("✅ تم إعداد المشروع بنجاح!")
    logger.info("\n📋 خطوات التشغيل:")
    logger.info("1. تعبئة مفاتيح API في ملف .env")
    logger.info("2. تشغيل الأمر: python main.py")
    logger.info("3. فتح المتصفح على: http://localhost:8000")
    logger.info("\n🔧 للمساعدة:")
    logger.info("- لوحة الأهل: http://localhost:8000")
    logger.info("- API التفاعل: http://localhost:8000/interact")
    logger.info("- WebSocket: ws://localhost:8000/ws/{child_id}")


if __name__ == "__main__":
    main()
