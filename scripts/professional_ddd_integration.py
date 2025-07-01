#!/usr/bin/env python3
"""
🏗️ Professional DDD Integration Script
دمج ملفات DDD مع المشروع بشكل احترافي ونقل God Classes للـ legacy
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class ProfessionalDDDIntegrator:
    """أداة دمج DDD احترافية"""

    def __init__(self, src_path: str = "src"):
        self.src_path = Path(src_path)
        self.legacy_path = self.src_path / "legacy"
        self.report = {
            "moved_to_legacy": [],
            "integrated_domains": [],
            "updated_structure": [],
            "errors": [],
        }

    def integrate_ddd_professionally(self):
        """الدمج الاحترافي الشامل"""
        print("🚀 بدء الدمج الاحترافي لـ DDD...")
        print("=" * 60)

        try:
            # المرحلة 1: إنشاء مجلد legacy
            self._create_legacy_structure()

            # المرحلة 2: نقل God Classes إلى legacy
            self._move_god_classes_to_legacy()

            # المرحلة 3: دمج DDD domains في البنية الأساسية
            self._integrate_ddd_domains()

            # المرحلة 4: تنظيم البنية النهائية
            self._organize_final_structure()

            # المرحلة 5: تحديث المراجع والـ imports
            self._update_references()

            # المرحلة 6: إنشاء التقرير النهائي
            self._generate_integration_report()

            print("\n✅ تم الدمج الاحترافي بنجاح!")

        except Exception as e:
            print(f"❌ خطأ في الدمج: {e}")
            self.report["errors"].append(str(e))

    def _create_legacy_structure(self):
        """إنشاء هيكل legacy للملفات القديمة"""
        print("📁 إنشاء مجلد legacy...")

        legacy_structure = [
            "legacy",
            "legacy/god_classes",
            "legacy/deprecated_services",
            "legacy/old_implementations",
            "legacy/backup_files",
        ]

        for folder in legacy_structure:
            folder_path = self.src_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            (folder_path / "__init__.py").write_text(
                "# Legacy code - scheduled for removal\n"
            )

        # إنشاء README في legacy
        readme_content = """# 🗂️ Legacy Code Archive

## 📋 محتويات هذا المجلد:

### `god_classes/`
الملفات الضخمة القديمة (1000+ سطر) التي تم استبدالها بـ DDD architecture

### `deprecated_services/`  
الخدمات القديمة المهجورة

### `old_implementations/`
التنفيذات القديمة قبل إعادة الهيكلة

### `backup_files/`
نسخ احتياطية من الملفات المحدثة

## ⚠️ تحذير:
هذه الملفات مجدولة للحذف بعد التأكد من عمل النظام الجديد بشكل صحيح.

## 📅 تاريخ النقل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        (self.legacy_path / "README.md").write_text(readme_content)
        print("✅ تم إنشاء هيكل legacy")

    def _move_god_classes_to_legacy(self):
        """نقل God Classes إلى legacy"""
        print("🔄 نقل God Classes إلى legacy...")

        # قائمة God Classes المحددة للنقل
        god_classes = [
            "data_cleanup_service.py",
            "parent_dashboard_service.py",
            "parent_report_service.py",
            "memory_service.py",
            "moderation_service.py",
            "enhanced_hume_integration.py",
            "accessibility_service.py",
            "ar_vr_service.py",
            "streaming_service.py",
            "notification_service.py",
        ]

        services_path = self.src_path / "application" / "services"
        legacy_god_classes = self.legacy_path / "god_classes"

        for god_class in god_classes:
            source_file = services_path / god_class
            if source_file.exists():
                try:
                    # نسخ إلى legacy مع timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"{god_class.replace('.py', '')}_{timestamp}.py"
                    destination = legacy_god_classes / backup_name

                    shutil.copy2(source_file, destination)

                    # حذف الملف الأصلي
                    source_file.unlink()

                    self.report["moved_to_legacy"].append(
                        {
                            "original": str(source_file),
                            "legacy_location": str(destination),
                            "size_lines": self._count_lines(destination),
                        }
                    )

                    print(f"✅ تم نقل {god_class} إلى legacy")

                except Exception as e:
                    print(f"❌ خطأ في نقل {god_class}: {e}")
                    self.report["errors"].append(f"Failed to move {god_class}: {e}")
            else:
                print(f"⚠️ {god_class} غير موجود")

    def _integrate_ddd_domains(self):
        """دمج DDD domains في البنية الأساسية"""
        print("🏗️ دمج DDD domains...")

        services_path = self.src_path / "application" / "services"

        # البحث عن مجلدات DDD
        ddd_folders = [
            folder
            for folder in services_path.iterdir()
            if folder.is_dir() and folder.name.endswith("_ddd")
        ]

        for ddd_folder in ddd_folders:
            # استخراج اسم الدومين
            domain_name = ddd_folder.name.replace("_ddd", "")

            try:
                # إنشاء هيكل الدومين الجديد
                self._create_domain_structure(domain_name, ddd_folder)

                # نقل محتويات DDD إلى البنية الجديدة
                self._move_ddd_content(ddd_folder, domain_name)

                # حذف مجلد DDD القديم
                shutil.rmtree(ddd_folder)

                self.report["integrated_domains"].append(
                    {
                        "domain": domain_name,
                        "old_path": str(ddd_folder),
                        "new_structure": f"Integrated into main architecture",
                    }
                )

                print(f"✅ تم دمج domain: {domain_name}")

            except Exception as e:
                print(f"❌ خطأ في دمج {domain_name}: {e}")
                self.report["errors"].append(f"Failed to integrate {domain_name}: {e}")

    def _create_domain_structure(self, domain_name: str, ddd_folder: Path):
        """إنشاء هيكل الدومين في البنية الأساسية"""

        # إنشاء مجلد الدومين في domain layer
        domain_path = self.src_path / "domain" / domain_name
        domain_path.mkdir(parents=True, exist_ok=True)

        # إنشاء مجلد التطبيق في application layer
        app_path = self.src_path / "application" / domain_name
        app_path.mkdir(parents=True, exist_ok=True)

        # إنشاء مجلد البنية التحتية في infrastructure layer
        infra_path = self.src_path / "infrastructure" / domain_name
        infra_path.mkdir(parents=True, exist_ok=True)

        # إنشاء __init__.py files
        for path in [domain_path, app_path, infra_path]:
            (path / "__init__.py").write_text(f"# {domain_name.title()} Domain\n")

        return domain_path, app_path, infra_path

    def _move_ddd_content(self, ddd_folder: Path, domain_name: str):
        """نقل محتويات DDD إلى البنية الجديدة"""

        domain_path = self.src_path / "domain" / domain_name
        app_path = self.src_path / "application" / domain_name
        infra_path = self.src_path / "infrastructure" / domain_name

        # نقل domain content
        ddd_domain = ddd_folder / "domain"
        if ddd_domain.exists():
            for item in ddd_domain.iterdir():
                if item.is_dir():
                    shutil.copytree(item, domain_path / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, domain_path / item.name)

        # نقل application content
        ddd_app = ddd_folder / "application"
        if ddd_app.exists():
            for item in ddd_app.iterdir():
                if item.is_dir():
                    shutil.copytree(item, app_path / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, app_path / item.name)

        # نقل infrastructure content
        ddd_infra = ddd_folder / "infrastructure"
        if ddd_infra.exists():
            for item in ddd_infra.iterdir():
                if item.is_dir():
                    shutil.copytree(item, infra_path / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, infra_path / item.name)

    def _organize_final_structure(self):
        """تنظيم البنية النهائية"""
        print("🎯 تنظيم البنية النهائية...")

        # إنشاء هيكل احترافي للمشروع
        structure = {
            # Domain Layer
            "domain": [
                "shared",  # Domain مشترك
                "contracts",  # Interfaces and contracts
                "events",  # Domain events
                "exceptions",  # Domain exceptions
            ],
            # Application Layer
            "application": [
                "shared",  # Application مشترك
                "pipelines",  # Processing pipelines
                "orchestrators",  # Complex operations
                "coordinators",  # Service coordination
            ],
            # Infrastructure Layer
            "infrastructure": [
                "shared",  # Infrastructure مشترك
                "adapters",  # External service adapters
                "gateways",  # API gateways
                "repositories",  # Data repositories
            ],
        }

        for layer, folders in structure.items():
            layer_path = self.src_path / layer
            for folder in folders:
                folder_path = layer_path / folder
                folder_path.mkdir(parents=True, exist_ok=True)
                (folder_path / "__init__.py").write_text(
                    f"# {folder.title()} {layer}\n"
                )

        self.report["updated_structure"].append("Created professional layer structure")
        print("✅ تم تنظيم البنية النهائية")

    def _update_references(self):
        """تحديث المراجع والـ imports"""
        print("🔗 تحديث المراجع والـ imports...")

        # البحث عن ملفات Python التي تحتاج تحديث imports
        python_files = list(self.src_path.rglob("*.py"))

        # mapping للمسارات الجديدة
        import_mappings = {
            # من DDD إلى البنية الجديدة
            "cleanup_ddd": "domain.cleanup",
            "memory_ddd": "domain.memory",
            "emotion_ddd": "domain.emotion",
            "parentdashboard_ddd": "domain.parentdashboard",
            "parentreport_ddd": "domain.parentreport",
        }

        updated_files = 0
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding="utf-8")
                original_content = content

                # تحديث imports
                for old_import, new_import in import_mappings.items():
                    content = content.replace(old_import, new_import)

                # حفظ إذا تم التحديث
                if content != original_content:
                    py_file.write_text(content, encoding="utf-8")
                    updated_files += 1

            except Exception as e:
                print(f"⚠️ خطأ في تحديث {py_file}: {e}")

        print(f"✅ تم تحديث {updated_files} ملف")
        self.report["updated_structure"].append(
            f"Updated imports in {updated_files} files"
        )

    def _count_lines(self, file_path: Path) -> int:
        """حساب عدد أسطر الملف"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return len(f.readlines())
        except:
            return 0

    def _generate_integration_report(self):
        """إنشاء التقرير النهائي"""
        report_content = f"""# 🏆 تقرير الدمج الاحترافي لـ DDD

## 📅 تاريخ التنفيذ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 الإحصائيات:
- ملفات منقولة إلى legacy: {len(self.report['moved_to_legacy'])}
- Domains مدموجة: {len(self.report['integrated_domains'])}
- تحديثات البنية: {len(self.report['updated_structure'])}
- أخطاء: {len(self.report['errors'])}

## 🗂️ الملفات المنقولة إلى Legacy:
"""

        for moved_file in self.report["moved_to_legacy"]:
            report_content += f"- {Path(moved_file['original']).name} ({moved_file['size_lines']} سطر)\n"

        report_content += "\n## 🏗️ Domains المدموجة:\n"
        for domain in self.report["integrated_domains"]:
            report_content += f"- {domain['domain']}: تم الدمج في البنية الأساسية\n"

        report_content += "\n## 🎯 البنية النهائية:\n"
        report_content += """
```
src/
├── domain/                    # Domain Layer
│   ├── cleanup/              # Data cleanup domain
│   ├── memory/               # Memory management domain  
│   ├── emotion/              # Emotion analysis domain
│   ├── parentdashboard/      # Parent dashboard domain
│   ├── parentreport/         # Parent reporting domain
│   └── shared/               # Shared domain logic
├── application/              # Application Layer
│   ├── cleanup/              # Cleanup use cases
│   ├── memory/               # Memory use cases
│   ├── emotion/              # Emotion use cases
│   └── orchestrators/        # Complex operations
├── infrastructure/           # Infrastructure Layer
│   ├── cleanup/              # Cleanup infrastructure
│   ├── memory/               # Memory infrastructure
│   ├── emotion/              # Emotion infrastructure
│   └── shared/               # Shared infrastructure
└── legacy/                   # Legacy code (for removal)
    ├── god_classes/          # Old large files
    ├── deprecated_services/  # Old services
    └── backup_files/         # Backup files
```
"""

        if self.report["errors"]:
            report_content += "\n## ❌ أخطاء حدثت:\n"
            for error in self.report["errors"]:
                report_content += f"- {error}\n"

        report_content += "\n## ✅ النتيجة النهائية:\n"
        report_content += "تم دمج DDD بنجاح في البنية الأساسية للمشروع مع نقل الملفات القديمة إلى legacy.\n"
        report_content += (
            "المشروع الآن يتبع معايير Domain-Driven Design بشكل احترافي.\n"
        )

        # حفظ التقرير
        report_file = self.src_path.parent / "DDD_INTEGRATION_REPORT.md"
        report_file.write_text(report_content, encoding="utf-8")

        print(f"📋 تم إنشاء التقرير: {report_file}")


def main():
    """تشغيل الدمج الاحترافي"""
    integrator = ProfessionalDDDIntegrator()
    integrator.integrate_ddd_professionally()


if __name__ == "__main__":
    main()
