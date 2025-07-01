import logging

logger = logging.getLogger(__name__)

"""
Verify DDD Structure Script
===========================
Check if DDD integration is correct and find issues
"""
import os
from pathlib import Path


def check_file_completeness():
    """فحص اكتمال الملفات"""
    logger.info("🔍 فحص اكتمال الملفات...")
    services_dir = Path("src/application/services")
    god_classes = [
        "accessibility_service.py",
        "memory_service.py",
        "moderation_service.py",
        "parent_dashboard_service.py",
        "parent_report_service.py",
    ]
    for filename in god_classes:
        file_path = services_dir / filename
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                lines = len(f.readlines())
            logger.info(f"📄 {filename}: {lines} lines (God Class)")
        else:
            logger.info(f"❌ {filename}: Missing")
    logger.info("\n🔍 فحص الملفات المدمجة...")
    domains = ["accessibility", "memory", "moderation"]
    for domain in domains:
        domain_dir = Path(f"src/domain/{domain}")
        app_dir = Path(f"src/application/{domain}")
        if domain_dir.exists():
            files_count = len(list(domain_dir.rglob("*.py")))
            logger.info(f"📁 {domain} domain: {files_count} files")
        else:
            logger.info(f"❌ {domain} domain: Missing")
        if app_dir.exists():
            files_count = len(list(app_dir.rglob("*.py")))
            logger.info(f"📁 {domain} application: {files_count} files")
        else:
            logger.info(f"❌ {domain} application: Missing")


def check_imports():
    """فحص الاستدعاءات"""
    logger.info("\n🔗 فحص الاستدعاءات...")
    broken_imports = []
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if "_ddd" in content:
                        broken_imports.append(str(file_path))
                    if "from src.domain." in content:
                        lines = content.split("\n")
                        for line in lines:
                            if "from src.domain." in line and "import" in line:
                                logger.info(
                                    f"📝 Found import: {line.strip()} in {file_path.name}"
                                )
                except Exception as e:
                    logger.info(f"⚠️ Error reading {file_path}: {e}")
    if broken_imports:
        logger.info(f"\n❌ Found {len(broken_imports)} files with broken imports:")
        for imp in broken_imports:
            logger.info(f"   - {imp}")
    else:
        logger.info("✅ No broken imports found")


def check_file_sizes():
    """فحص أحجام الملفات"""
    logger.info("\n📏 فحص أحجام الملفات...")
    large_files = []
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = len(f.readlines())
                    if lines > 300:
                        large_files.append((str(file_path), lines))
                except Exception:
                    continue
    if large_files:
        logger.info(f"⚠️ Found {len(large_files)} large files (>300 lines):")
        for file_path, lines in sorted(large_files, key=lambda x: x[1], reverse=True):
            logger.info(f"   - {file_path}: {lines} lines")
    else:
        logger.info("✅ All files are appropriately sized")


def generate_fix_report():
    """إنشاء تقرير الإصلاح"""
    report = """# تقرير فحص بنية DDD
===================

## المشاكل المكتشفة:

### 1. الملفات الأصلية الكبيرة (God Classes)
- accessibility_service.py (788 lines) - يحتاج تقسيم
- memory_service.py (1421 lines) - يحتاج تقسيم  
- moderation_service.py (1146 lines) - يحتاج تقسيم
- parent_dashboard_service.py (1295 lines) - يحتاج تقسيم
- parent_report_service.py (1297 lines) - يحتاج تقسيم

### 2. الملفات المدمجة ناقصة
- src/domain/accessibility/ - ملفات صغيرة وناقصة
- src/application/accessibility/ - لا تحتوي على المنطق الكامل

### 3. الحلول المطلوبة:
1. إنشاء تقسيم صحيح للملفات الكبيرة
2. نسخ المنطق الكامل إلى البنية الجديدة
3. تحديث الاستدعاءات
4. اختبار البنية الجديدة

## التوصيات:
1. تشغيل سكريبت إصلاح متخصص
2. التحقق من عمل جميع الاستدعاءات
3. نقل الملفات الكبيرة إلى legacy بعد التقسيم
"""
    with open("DDD_STRUCTURE_VERIFICATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    logger.info("\n📄 تم إنشاء تقرير الفحص: DDD_STRUCTURE_VERIFICATION_REPORT.md")


def main():
    logger.info("=" * 60)
    logger.info("🔍 فحص بنية DDD...")
    logger.info("=" * 60)
    check_file_completeness()
    check_imports()
    check_file_sizes()
    generate_fix_report()
    logger.info("\n" + "=" * 60)
    logger.info("✅ انتهى الفحص!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
