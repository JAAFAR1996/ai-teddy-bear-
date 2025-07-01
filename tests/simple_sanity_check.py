"""
اختبار بسيط للتحقق من سلامة المشروع بعد التنظيف
"""
import os
import sys
from pathlib import Path

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent.parent))

def test_project_structure():
    """التحقق من وجود الهيكل الأساسي للمشروع"""
    print("🔍 فحص هيكل المشروع...")
    
    # المجلدات الأساسية المطلوبة
    required_dirs = [
        'src',
        'src/core',
        'src/core/domain',
        'src/core/services',
        'src/infrastructure',
        'src/application',
        'src/api',
        'tests',
        'scripts',
        'configs',
        'docs'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - مفقود!")
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0

def test_important_files():
    """التحقق من وجود الملفات المهمة"""
    print("\n📄 فحص الملفات المهمة...")
    
    important_files = [
        'requirements.txt',
        'README.md',
        'src/__init__.py',
        'src/main.py'
    ]
    
    missing_files = []
    for file_path in important_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - مفقود!")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_no_backup_folder():
    """التحقق من حذف مجلد النسخ الاحتياطي القديم"""
    print("\n🗑️ التحقق من حذف المجلدات القديمة...")
    
    if not Path('backup_before_reorganization').exists():
        print("  ✅ تم حذف backup_before_reorganization")
        return True
    else:
        print("  ❌ لا يزال backup_before_reorganization موجوداً!")
        return False

def test_imports():
    """التحقق من إمكانية استيراد الوحدات الأساسية"""
    print("\n📦 فحص الاستيرادات الأساسية...")
    
    imports_ok = True
    
    # اختبار استيراد الوحدات الأساسية
    test_imports = [
        ('src', 'الوحدة الأساسية'),
        ('src.core', 'النواة'),
        ('src.infrastructure', 'البنية التحتية'),
        ('src.application', 'طبقة التطبيق')
    ]
    
    for module_name, description in test_imports:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name} - {description}")
        except ImportError as e:
            print(f"  ❌ {module_name} - {description}: {e}")
            imports_ok = False
    
    return imports_ok

def test_file_count():
    """عد الملفات للتحقق من التنظيف"""
    print("\n📊 إحصائيات الملفات...")
    
    py_files = list(Path('src').rglob('*.py'))
    test_files = list(Path('tests').rglob('*.py'))
    script_files = list(Path('scripts').rglob('*.py'))
    
    print(f"  • ملفات Python في src: {len(py_files)}")
    print(f"  • ملفات الاختبار: {len(test_files)}")
    print(f"  • السكريبتات: {len(script_files)}")
    print(f"  • الإجمالي: {len(py_files) + len(test_files) + len(script_files)}")
    
    return True

def main():
    """تشغيل جميع الفحوصات"""
    print("=" * 60)
    print("🧪 فحص سلامة المشروع بعد التنظيف")
    print("=" * 60)
    
    all_tests_passed = True
    
    # تشغيل الاختبارات
    all_tests_passed &= test_project_structure()
    all_tests_passed &= test_important_files()
    all_tests_passed &= test_no_backup_folder()
    all_tests_passed &= test_imports()
    all_tests_passed &= test_file_count()
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("✅ جميع الفحوصات نجحت! المشروع في حالة جيدة.")
    else:
        print("⚠️ بعض الفحوصات فشلت. يرجى مراجعة المشاكل أعلاه.")
    print("=" * 60)
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 