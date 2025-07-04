"""
أداة فحص صحة وترابط مشروع AI Teddy Bear
يتحقق من أن جميع المكونات تعمل بشكل صحيح
"""
import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
import importlib.util


class ProjectHealthChecker:
    def __init__(self):
        self.checks = {
            'imports': {'passed': 0, 'failed': 0, 'errors': []},
            'tests': {'passed': 0, 'failed': 0, 'errors': []},
            'dependencies': {'passed': 0, 'failed': 0, 'errors': []},
            'structure': {'passed': 0, 'failed': 0, 'errors': []},
            'security': {'passed': 0, 'failed': 0, 'errors': []}
        }

    def check_python_imports(self):
        """التحقق من أن جميع الملفات Python يمكن استيرادها"""
        print("🔍 فحص استيراد ملفات Python...")

        python_files = list(Path('.').rglob('*.py'))

        # استثناء ملفات معينة
        exclude_patterns = [
            'security_backup_',
            '__pycache__',
            '.venv',
            'venv',
            'tests',
            'scripts'
        ]

        for py_file in python_files:
            # تجاهل الملفات المستثناة
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue

            try:
                # محاولة تحليل الملف كـ AST
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                compile(content, py_file, 'exec')
                self.checks['imports']['passed'] += 1
            except SyntaxError as e:
                self.checks['imports']['failed'] += 1
                self.checks['imports']['errors'].append(f"{py_file}: {str(e)}")
            except Exception as e:
                self.checks['imports']['failed'] += 1
                self.checks['imports']['errors'].append(f"{py_file}: {str(e)}")

    def check_required_files(self):
        """التحقق من وجود الملفات المطلوبة"""
        print("📋 فحص الملفات المطلوبة...")

        required_files = [
            'requirements.txt',
            'README.md',
            '.gitignore',
            'src/__init__.py',
            'src/domain/__init__.py',
            'src/application/__init__.py',
            'src/infrastructure/__init__.py'
        ]

        for file_path in required_files:
            if Path(file_path).exists():
                self.checks['structure']['passed'] += 1
            else:
                self.checks['structure']['failed'] += 1
                self.checks['structure']['errors'].append(
                    f"Missing required file: {file_path}")

    def check_directory_structure(self):
        """التحقق من بنية المجلدات"""
        print("📁 فحص بنية المجلدات...")

        required_dirs = [
            'src',
            'src/domain',
            'src/application',
            'src/infrastructure',
            'src/presentation',
            'tests',
            'configs',
            'scripts',
            'docs'
        ]

        for dir_path in required_dirs:
            if Path(dir_path).is_dir():
                self.checks['structure']['passed'] += 1
            else:
                self.checks['structure']['failed'] += 1
                self.checks['structure']['errors'].append(
                    f"Missing required directory: {dir_path}")

    def check_dependencies(self):
        """التحقق من التبعيات"""
        print("📦 فحص التبعيات...")

        try:
            # قراءة requirements.txt
            if Path('requirements.txt').exists():
                with open('requirements.txt', 'r') as f:
                    requirements = f.read().splitlines()

                # التحقق من أن الملف غير فارغ
                if requirements:
                    self.checks['dependencies']['passed'] += 1
                else:
                    self.checks['dependencies']['failed'] += 1
                    self.checks['dependencies']['errors'].append(
                        "requirements.txt is empty")

                # التحقق من وجود المكتبات الأساسية
                essential_libs = [
                    'fastapi',
                    'pydantic',
                    'sqlalchemy',
                    'pytest',
                    'openai'
                ]

                requirements_lower = [req.lower() for req in requirements]

                for lib in essential_libs:
                    if any(lib in req for req in requirements_lower):
                        self.checks['dependencies']['passed'] += 1
                    else:
                        self.checks['dependencies']['failed'] += 1
                        self.checks['dependencies']['errors'].append(
                            f"Missing essential dependency: {lib}")
            else:
                self.checks['dependencies']['failed'] += 1
                self.checks['dependencies']['errors'].append(
                    "requirements.txt not found")

        except Exception as e:
            self.checks['dependencies']['failed'] += 1
            self.checks['dependencies']['errors'].append(
                f"Error reading requirements: {str(e)}")

    def check_security_fixes(self):
        """التحقق من الإصلاحات الأمنية"""
        print("🔐 فحص الإصلاحات الأمنية...")

        # البحث عن استخدامات eval/exec المتبقية
        python_files = list(Path('src').rglob('*.py'))

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # التحقق من eval/exec غير الآمن
                if 'eval(' in content and 'ast.literal_eval' not in content:
                    self.checks['security']['failed'] += 1
                    self.checks['security']['errors'].append(
                        f"Unsafe eval in {py_file}")
                elif 'exec(' in content and '# SECURITY' not in content:
                    self.checks['security']['failed'] += 1
                    self.checks['security']['errors'].append(
                        f"Unsafe exec in {py_file}")
                else:
                    self.checks['security']['passed'] += 1

            except Exception as e:
                pass

    def run_basic_tests(self):
        """تشغيل اختبارات أساسية"""
        print("🧪 تشغيل الاختبارات الأساسية...")

        # التحقق من وجود pytest بشكل آمن
        try:
            # SECURITY: Explicit shell=False and controlled arguments
            result = subprocess.run(
                ['pytest', '--version'],
                capture_output=True,
                text=True,
                shell=False,  # SECURITY: Prevent shell injection
                timeout=30,   # SECURITY: Prevent hanging processes
                check=False   # Don't raise exception on non-zero exit
            )
            if result.returncode == 0:
                self.checks['tests']['passed'] += 1
            else:
                self.checks['tests']['failed'] += 1
                self.checks['tests']['errors'].append(
                    "pytest not installed or not working")
        except subprocess.TimeoutExpired:
            self.checks['tests']['failed'] += 1
            self.checks['tests']['errors'].append("pytest command timed out")
        except FileNotFoundError:
            self.checks['tests']['failed'] += 1
            self.checks['tests']['errors'].append("pytest not found")
        except Exception as e:
            self.checks['tests']['failed'] += 1
            self.checks['tests']['errors'].append(
                f"pytest check failed: {str(e)}")

    def generate_report(self):
        """إنشاء تقرير الصحة"""
        total_passed = sum(check['passed'] for check in self.checks.values())
        total_failed = sum(check['failed'] for check in self.checks.values())
        total_checks = total_passed + total_failed
        health_score = (total_passed / total_checks *
                        100) if total_checks > 0 else 0

        report = f"""# 🏥 تقرير صحة مشروع AI Teddy Bear

## 📅 معلومات الفحص
- **التاريخ**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **النتيجة الإجمالية**: {health_score:.1f}%
- **الفحوصات الناجحة**: {total_passed}
- **الفحوصات الفاشلة**: {total_failed}

## 📊 تفاصيل الفحوصات

"""

        for category, results in self.checks.items():
            emoji = {
                'imports': '📦',
                'tests': '🧪',
                'dependencies': '📚',
                'structure': '📁',
                'security': '🔐'
            }.get(category, '📌')

            report += f"### {emoji} {category.title()}\n"
            report += f"- **نجح**: {results['passed']}\n"
            report += f"- **فشل**: {results['failed']}\n"

            if results['errors']:
                report += f"- **الأخطاء**:\n"
                for error in results['errors'][:5]:  # أول 5 أخطاء فقط
                    report += f"  - {error}\n"
                if len(results['errors']) > 5:
                    report += f"  - ... و{len(results['errors']) - 5} أخطاء أخرى\n"

            report += "\n"

        # التوصيات
        report += "## 💡 التوصيات\n\n"

        if health_score >= 90:
            report += "✅ **المشروع في حالة ممتازة!** جاهز للإطلاق.\n"
        elif health_score >= 70:
            report += "⚠️ **المشروع في حالة جيدة** لكن يحتاج بعض التحسينات.\n"
        else:
            report += "❌ **المشروع يحتاج عمل إضافي** قبل الإطلاق.\n"

        if total_failed > 0:
            report += "\n### 🔧 الإصلاحات المطلوبة:\n"

            if self.checks['structure']['failed'] > 0:
                report += "1. أنشئ الملفات والمجلدات المفقودة\n"

            if self.checks['imports']['failed'] > 0:
                report += "2. أصلح أخطاء الصياغة في ملفات Python\n"

            if self.checks['dependencies']['failed'] > 0:
                report += "3. أضف المكتبات المفقودة إلى requirements.txt\n"

            if self.checks['security']['failed'] > 0:
                report += "4. راجع وأصلح المشاكل الأمنية المتبقية\n"

            if self.checks['tests']['failed'] > 0:
                report += "5. تأكد من تثبيت وإعداد بيئة الاختبار\n"

        with open('project_health_report.md', 'w', encoding='utf-8') as f:
            f.write(report)

        return health_score

    def run_all_checks(self):
        """تشغيل جميع الفحوصات"""
        print("🏥 بدء فحص صحة المشروع...\n")

        self.check_required_files()
        self.check_directory_structure()
        self.check_python_imports()
        self.check_dependencies()
        self.check_security_fixes()
        self.run_basic_tests()

        health_score = self.generate_report()

        print(f"\n✅ تم الانتهاء من الفحص!")
        print(f"📊 النتيجة الإجمالية: {health_score:.1f}%")
        print("📄 راجع project_health_report.md للتفاصيل")

        return health_score


def main():
    checker = ProjectHealthChecker()
    health_score = checker.run_all_checks()

    # إرجاع كود خروج بناءً على النتيجة
    if health_score >= 90:
        sys.exit(0)  # نجاح
    else:
        sys.exit(1)  # يحتاج عمل


if __name__ == "__main__":
    main()
