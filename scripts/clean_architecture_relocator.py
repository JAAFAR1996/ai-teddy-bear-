#!/usr/bin/env python3
"""
Clean Architecture Relocator
أداة نقل الخدمات المهمة لمواقعها الصحيحة حسب Clean Architecture
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class CleanArchitectureRelocator:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.relocation_plan = self._create_relocation_plan()
        self.moved_services = []
        self.errors = []

    def _create_relocation_plan(self) -> Dict[str, Dict]:
        """إنشاء خطة إعادة التوزيع حسب Clean Architecture"""
        return {
            # خدمات الذكاء الاصطناعي - Application Layer
            "ai_services": {
                "target_dir": "src/application/services/ai",
                "services": [
                    "llm_service.py",
                    "main_service.py",
                    "llm_service_factory.py",
                ],
            },
            # خدمات الصوت - Application Layer
            "audio_services": {
                "target_dir": "src/application/services/audio",
                "services": [
                    "transcription_service.py",
                    "voice_interaction_service.py",
                    "synthesis_service.py",
                ],
            },
            # خدمات التخزين المؤقت - Infrastructure Layer
            "cache_services": {
                "target_dir": "src/infrastructure/services/data",
                "services": ["simple_cache_service.py"],
            },
            # خدمات المراقبة - Infrastructure Layer
            "monitoring_services": {
                "target_dir": "src/infrastructure/services/monitoring",
                "services": ["issue_tracker_service.py", "simple_health_service.py"],
            },
        }

    def validate_source_files(self) -> Dict[str, List[str]]:
        """التحقق من وجود الملفات المصدر"""
        print("🔍 التحقق من وجود الملفات المصدر...")

        validation_results = {
            "found": [],
            "missing": [],
            "total_found": 0,
            "total_missing": 0,
        }

        deprecated_base = self.base_path / "deprecated" / "services"

        for group_name, group_info in self.relocation_plan.items():
            group_dir = deprecated_base / group_name

            if not group_dir.exists():
                print(f"  ❌ مجلد غير موجود: {group_dir}")
                for service in group_info["services"]:
                    validation_results["missing"].append(f"{group_name}/{service}")
                continue

            for service_file in group_info["services"]:
                source_path = group_dir / service_file
                if source_path.exists():
                    validation_results["found"].append(str(source_path))
                    print(f"  ✅ موجود: {service_file} في {group_name}")
                else:
                    validation_results["missing"].append(f"{group_name}/{service_file}")
                    print(f"  ❌ مفقود: {service_file} في {group_name}")

        validation_results["total_found"] = len(validation_results["found"])
        validation_results["total_missing"] = len(validation_results["missing"])

        print(f"\n📊 نتائج التحقق:")
        print(f"  ✅ ملفات موجودة: {validation_results['total_found']}")
        print(f"  ❌ ملفات مفقودة: {validation_results['total_missing']}")

        return validation_results

    def create_target_directories(self) -> Dict[str, bool]:
        """إنشاء المجلدات المستهدفة"""
        print("\n📁 إنشاء المجلدات المستهدفة...")

        creation_results = {}

        for group_name, group_info in self.relocation_plan.items():
            target_dir = self.base_path / group_info["target_dir"]

            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                creation_results[group_name] = True
                print(f"  ✅ تم إنشاء: {target_dir}")
            except Exception as e:
                creation_results[group_name] = False
                error_msg = f"خطأ في إنشاء {target_dir}: {str(e)}"
                self.errors.append(error_msg)
                print(f"  ❌ {error_msg}")

        return creation_results

    def relocate_services(self) -> Dict[str, any]:
        """تنفيذ عملية النقل"""
        print("\n🚀 بدء عملية النقل...")

        relocation_results = {
            "successful_moves": [],
            "failed_moves": [],
            "total_moved": 0,
            "total_failed": 0,
        }

        deprecated_base = self.base_path / "deprecated" / "services"

        for group_name, group_info in self.relocation_plan.items():
            print(f"\n📋 معالجة مجموعة: {group_name}")

            source_dir = deprecated_base / group_name
            target_dir = self.base_path / group_info["target_dir"]

            for service_file in group_info["services"]:
                source_path = source_dir / service_file
                target_path = target_dir / service_file

                try:
                    if source_path.exists():
                        # نسخ الملف مع الاحتفاظ بالنسخة الأصلية
                        shutil.copy2(source_path, target_path)

                        move_info = {
                            "service": service_file,
                            "group": group_name,
                            "source": str(source_path),
                            "target": str(target_path),
                            "size": source_path.stat().st_size,
                        }

                        relocation_results["successful_moves"].append(move_info)
                        self.moved_services.append(move_info)

                        print(f"  ✅ نُقل: {service_file} → {group_info['target_dir']}")

                        # حذف الملف الأصلي بعد النسخ الناجح
                        source_path.unlink()
                        print(f"    🗑️  حُذف الأصل: {source_path}")

                    else:
                        error_info = {
                            "service": service_file,
                            "group": group_name,
                            "error": "الملف غير موجود",
                        }
                        relocation_results["failed_moves"].append(error_info)
                        print(f"  ❌ فشل: {service_file} (غير موجود)")

                except Exception as e:
                    error_info = {
                        "service": service_file,
                        "group": group_name,
                        "error": str(e),
                    }
                    relocation_results["failed_moves"].append(error_info)
                    self.errors.append(f"خطأ في نقل {service_file}: {str(e)}")
                    print(f"  ❌ فشل: {service_file} - {str(e)}")

        relocation_results["total_moved"] = len(relocation_results["successful_moves"])
        relocation_results["total_failed"] = len(relocation_results["failed_moves"])

        return relocation_results

    def cleanup_empty_directories(self) -> Dict[str, bool]:
        """تنظيف المجلدات الفارغة"""
        print("\n🧹 تنظيف المجلدات الفارغة...")

        cleanup_results = {}
        deprecated_base = self.base_path / "deprecated" / "services"

        for group_name in self.relocation_plan.keys():
            group_dir = deprecated_base / group_name

            try:
                if group_dir.exists() and not any(group_dir.iterdir()):
                    group_dir.rmdir()
                    cleanup_results[group_name] = True
                    print(f"  🗑️  حُذف المجلد الفارغ: {group_dir}")
                else:
                    cleanup_results[group_name] = False
                    if group_dir.exists():
                        remaining_files = list(group_dir.iterdir())
                        print(
                            f"  📁 المجلد ليس فارغاً: {group_dir} ({len(remaining_files)} ملفات)"
                        )
                    else:
                        print(f"  ❓ المجلد غير موجود: {group_dir}")

            except Exception as e:
                cleanup_results[group_name] = False
                error_msg = f"خطأ في حذف {group_dir}: {str(e)}"
                self.errors.append(error_msg)
                print(f"  ❌ {error_msg}")

        return cleanup_results

    def create_updated_imports_guide(self) -> str:
        """إنشاء دليل تحديث الاستيرادات"""
        print("\n📝 إنشاء دليل تحديث الاستيرادات...")

        guide_content = f"""
# 📝 دليل تحديث الاستيرادات بعد إعادة التوزيع

**التاريخ**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 الملفات المنقولة والاستيرادات الجديدة

"""

        for move_info in self.moved_services:
            service_name = move_info["service"].replace(".py", "")
            old_path = f"deprecated.services.{move_info['group']}.{service_name}"
            new_path = (
                move_info["target"]
                .replace(str(self.base_path), "")
                .replace("\\", ".")
                .replace("/", ".")
                .strip(".")
            )
            new_path = new_path.replace(".py", "")

            guide_content += f"""
### {service_name}
**من**: `{old_path}`  
**إلى**: `{new_path}`

```python
# بدلاً من:
# from deprecated.services.{move_info['group']}.{service_name} import {service_name.title().replace('_', '')}

# استخدم:
from {new_path} import {service_name.title().replace('_', '')}
```
"""

        guide_content += f"""

## 🔍 البحث والاستبدال السريع

يمكنك استخدام هذه الأوامر للبحث والاستبدال:

```bash
# البحث عن الاستيرادات القديمة
grep -r "from deprecated.services" src/
grep -r "import.*deprecated.services" src/

# استبدال سريع (مثال)
find src/ -name "*.py" -exec sed -i 's/from deprecated.services/from src.application.services/g' {{}} +
```

## 📋 الخطوات التالية:
1. **فحص جميع ملفات Python** للاستيرادات القديمة
2. **تحديث الاستيرادات** حسب الجدول أعلاه  
3. **اختبار المشروع** للتأكد من عمل كل شيء
4. **حذف مجلد deprecated/services** بعد التأكد

---
**تم إنشاؤه بواسطة**: CleanArchitectureRelocator v1.0
"""

        return guide_content

    def generate_relocation_report(
        self, validation_results: Dict, relocation_results: Dict, cleanup_results: Dict
    ) -> str:
        """إنشاء تقرير شامل لعملية إعادة التوزيع"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""
# 🎯 تقرير إعادة توزيع الخدمات حسب Clean Architecture

**التاريخ**: {timestamp}  
**الأداة**: CleanArchitectureRelocator v1.0

## 📊 ملخص العملية

### ✅ النتائج الإجمالية:
- **ملفات تم نقلها**: {relocation_results['total_moved']}
- **ملفات فشل نقلها**: {relocation_results['total_failed']}
- **مجلدات فارغة تم حذفها**: {sum(1 for v in cleanup_results.values() if v)}
- **أخطاء**: {len(self.errors)}

## 🗺️ خريطة إعادة التوزيع

### الخدمات المنقولة بنجاح:
"""

        # تجميع الخدمات حسب المجموعة
        by_group = {}
        for move in relocation_results["successful_moves"]:
            group = move["group"]
            if group not in by_group:
                by_group[group] = []
            by_group[group].append(move)

        for group_name, moves in by_group.items():
            target_dir = self.relocation_plan[group_name]["target_dir"]
            report += f"""
#### {group_name.replace('_', ' ').title()}
**المجلد الجديد**: `{target_dir}`

"""
            for move in moves:
                size_kb = round(move["size"] / 1024, 1)
                report += f"- ✅ `{move['service']}` ({size_kb} KB)\n"

        # الخدمات التي فشل نقلها
        if relocation_results["failed_moves"]:
            report += f"""
### ❌ الخدمات التي فشل نقلها:
"""
            for failed in relocation_results["failed_moves"]:
                report += f"- ❌ `{failed['service']}` في {failed['group']} - {failed['error']}\n"

        # الأخطاء
        if self.errors:
            report += f"""
### 🚨 الأخطاء المسجلة:
"""
            for error in self.errors:
                report += f"- ⚠️ {error}\n"

        report += f"""

## 🏗️ البنية الجديدة حسب Clean Architecture

```
src/
├── application/
│   └── services/
│       ├── ai/                 # خدمات الذكاء الاصطناعي
│       │   ├── ai_service.py
│       │   ├── llm_service.py
│       │   ├── main_service.py
│       │   └── llm_service_factory.py
│       ├── audio/              # خدمات الصوت
│       │   ├── transcription_service.py
│       │   ├── voice_interaction_service.py
│       │   └── synthesis_service.py
│       └── core/               # الخدمات الأساسية
│           └── voice_service.py
└── infrastructure/
    └── services/
        ├── data/               # خدمات البيانات
        │   ├── cache_service.py
        │   └── simple_cache_service.py
        └── monitoring/         # خدمات المراقبة
            ├── rate_monitor_service.py
            ├── issue_tracker_service.py
            └── simple_health_service.py
```

## 🎯 الفوائد المحققة

### ✅ التحسينات:
1. **تنظيم حسب Clean Architecture** - كل خدمة في طبقتها الصحيحة
2. **سهولة الصيانة** - الخدمات مجمعة حسب الوظيفة
3. **وضوح المسؤوليات** - فصل واضح بين الطبقات
4. **تحسين الاستيرادات** - مسارات منطقية ومنظمة

### 📋 الخطوات التالية:
1. **تحديث الاستيرادات** في جميع الملفات
2. **اختبار شامل** للتأكد من عمل النظام
3. **حذف deprecated/services** بعد التأكد
4. **توثيق الهيكل الجديد**

---
**تم إنشاؤه بواسطة**: CleanArchitectureRelocator v1.0  
**التوقيت**: {timestamp}
"""

        return report

    def run_complete_relocation(self) -> Dict:
        """تشغيل عملية إعادة التوزيع الكاملة"""
        print("=" * 60)
        print("🎯  CLEAN ARCHITECTURE RELOCATOR")
        print("🏗️  MOVING SERVICES TO CORRECT LOCATIONS")
        print("=" * 60)

        # التحقق من الملفات المصدر
        validation_results = self.validate_source_files()

        if validation_results["total_missing"] > 0:
            print(f"\n⚠️  تحذير: {validation_results['total_missing']} ملفات مفقودة!")
            print("  💡 سيتم تخطي الملفات المفقودة والمتابعة مع الموجودة")

        # إنشاء المجلدات المستهدفة
        creation_results = self.create_target_directories()

        # تنفيذ النقل
        relocation_results = self.relocate_services()

        # تنظيف المجلدات الفارغة
        cleanup_results = self.cleanup_empty_directories()

        # إنشاء دليل الاستيرادات
        imports_guide = self.create_updated_imports_guide()
        imports_guide_path = (
            self.base_path / "deleted" / "reports" / "IMPORTS_UPDATE_GUIDE.md"
        )
        imports_guide_path.parent.mkdir(parents=True, exist_ok=True)

        with open(imports_guide_path, "w", encoding="utf-8") as f:
            f.write(imports_guide)

        # إنشاء التقرير الشامل
        report_content = self.generate_relocation_report(
            validation_results, relocation_results, cleanup_results
        )
        report_path = (
            self.base_path / "deleted" / "reports" / "CLEAN_ARCHITECTURE_RELOCATION.md"
        )

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"\n🎉 تم إكمال إعادة التوزيع!")
        print(f"📋 التقرير الشامل: {report_path}")
        print(f"📝 دليل الاستيرادات: {imports_guide_path}")
        print(f"✅ خدمات منقولة: {relocation_results['total_moved']}")
        print(f"❌ خدمات فشلت: {relocation_results['total_failed']}")

        return {
            "validation": validation_results,
            "relocation": relocation_results,
            "cleanup": cleanup_results,
            "errors": self.errors,
        }


def main():
    """الدالة الرئيسية"""
    relocator = CleanArchitectureRelocator()

    try:
        results = relocator.run_complete_relocation()

        if results["relocation"]["total_moved"] > 0:
            print(f"\n✅ تم النقل بنجاح!")
            print(f"🎯 البنية الجديدة جاهزة حسب Clean Architecture")
        else:
            print(f"\n⚠️  لم يتم نقل أي ملفات!")

    except Exception as e:
        print(f"❌ خطأ في عملية إعادة التوزيع: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
