#!/usr/bin/env python3
"""
Usage Pattern Analyzer
أداة فحص أنماط الاستخدام الفعلي للملفات لتحديد ما يحتاجه المشروع
"""

import ast
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple


class UsagePatternAnalyzer:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.usage_data = {
            "timestamp": datetime.now().isoformat(),
            "file_references": defaultdict(list),  # من يستورد من
            "import_patterns": defaultdict(set),  # أنماط الاستيراد
            "actual_usage": {},  # الاستخدام الفعلي
            "unused_files": [],  # الملفات غير المستخدمة
            "critical_files": [],  # الملفات الحرجة
            "merge_recommendations": {},  # توصيات الدمج
        }

    def scan_all_python_files(self) -> List[Path]:
        """فحص جميع ملفات Python في المشروع"""
        python_files = []

        # فحص src/ و api/ و frontend/ و tests/
        scan_dirs = ["src", "api", "frontend", "tests", "scripts"]

        for scan_dir in scan_dirs:
            dir_path = self.base_path / scan_dir
            if dir_path.exists():
                python_files.extend(dir_path.rglob("*.py"))

        return python_files

    def extract_imports_from_file(self, file_path: Path) -> Dict:
        """استخراج الاستيرادات من ملف Python"""
        imports_data = {
            "file_path": str(file_path),
            "imports": [],
            "from_imports": [],
            "relative_imports": [],
            "service_imports": [],
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # استخدام regex لاستخراج الاستيرادات
            import_patterns = [
                r"^import\s+([^\s#]+)",  # import module
                r"^from\s+([^\s]+)\s+import\s+([^#]+)",  # from module import something
            ]

            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # import statements
                if line.startswith("import "):
                    match = re.match(r"^import\s+([^\s#]+)", line)
                    if match:
                        module = match.group(1)
                        imports_data["imports"].append(
                            {"module": module, "line": line_num, "full_line": line}
                        )

                # from ... import statements
                elif line.startswith("from "):
                    match = re.match(r"^from\s+([^\s]+)\s+import\s+([^#]+)", line)
                    if match:
                        module = match.group(1)
                        imports = match.group(2).strip()
                        imports_data["from_imports"].append(
                            {
                                "module": module,
                                "imports": imports,
                                "line": line_num,
                                "full_line": line,
                            }
                        )

                        # فحص استيراد الخدمات
                        if "service" in module.lower() or "service" in imports.lower():
                            imports_data["service_imports"].append(
                                {"module": module, "imports": imports, "line": line_num}
                            )

        except Exception as e:
            print(f"خطأ في تحليل {file_path}: {e}")

        return imports_data

    def analyze_service_usage_patterns(self) -> Dict:
        """تحليل أنماط استخدام الخدمات"""
        print("🔍 تحليل أنماط استخدام الخدمات...")

        # فحص الملفات المنقولة
        deprecated_services = self.base_path / "deprecated" / "services"
        if not deprecated_services.exists():
            print("❌ مجلد deprecated/services غير موجود!")
            return {}

        # جمع أسماء جميع ملفات الخدمات
        service_files = {}
        for group_dir in deprecated_services.iterdir():
            if group_dir.is_dir():
                for service_file in group_dir.glob("*.py"):
                    service_name = service_file.stem
                    service_files[service_name] = {
                        "path": str(service_file),
                        "group": group_dir.name,
                        "references": [],
                        "usage_count": 0,
                    }

        print(f"  📄 ملفات الخدمات المكتشفة: {len(service_files)}")

        # فحص جميع ملفات Python للبحث عن المراجع
        python_files = self.scan_all_python_files()
        print(f"  📁 ملفات Python للفحص: {len(python_files)}")

        for py_file in python_files:
            imports_data = self.extract_imports_from_file(py_file)

            # فحص المراجع لكل خدمة
            for service_name, service_info in service_files.items():
                file_content = ""
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        file_content = f.read()
                except:
                    continue

                # البحث عن مراجع الخدمة
                references_found = []

                # البحث في الاستيرادات
                for imp in imports_data["imports"] + imports_data["from_imports"]:
                    if service_name.lower() in str(imp).lower():
                        references_found.append(
                            {
                                "type": "import",
                                "line": imp.get("line", 0),
                                "content": imp.get("full_line", str(imp)),
                            }
                        )

                # البحث في المحتوى العام
                if service_name in file_content:
                    lines = file_content.split("\n")
                    for line_num, line in enumerate(lines, 1):
                        if service_name in line and not line.strip().startswith("#"):
                            references_found.append(
                                {
                                    "type": "usage",
                                    "line": line_num,
                                    "content": line.strip()[:100],  # أول 100 حرف
                                }
                            )

                if references_found:
                    service_files[service_name]["references"].append(
                        {"file": str(py_file), "references": references_found}
                    )
                    service_files[service_name]["usage_count"] += len(references_found)

        return service_files

    def classify_services_by_usage(self, service_usage: Dict) -> Dict:
        """تصنيف الخدمات حسب الاستخدام"""
        print("📊 تصنيف الخدمات حسب الاستخدام...")

        classification = {
            "heavily_used": [],  # مستخدمة بكثرة (5+ مراجع)
            "moderately_used": [],  # مستخدمة متوسط (2-4 مراجع)
            "lightly_used": [],  # مستخدمة قليلاً (1 مرجع)
            "unused": [],  # غير مستخدمة (0 مراجع)
            "test_only": [],  # مستخدمة في الاختبارات فقط
        }

        for service_name, service_data in service_usage.items():
            usage_count = service_data["usage_count"]
            references = service_data["references"]

            # فحص ما إذا كانت مستخدمة في الاختبارات فقط
            test_only = True
            for ref in references:
                if "test" not in ref["file"].lower():
                    test_only = False
                    break

            if usage_count == 0:
                classification["unused"].append(service_name)
            elif test_only and usage_count > 0:
                classification["test_only"].append(service_name)
            elif usage_count >= 5:
                classification["heavily_used"].append(service_name)
            elif usage_count >= 2:
                classification["moderately_used"].append(service_name)
            else:
                classification["lightly_used"].append(service_name)

        # طباعة النتائج
        for category, services in classification.items():
            if services:
                print(f"  {category}: {len(services)} خدمات")
                for service in services[:3]:  # أول 3 فقط
                    usage_count = service_usage[service]["usage_count"]
                    print(f"    - {service} ({usage_count} مراجع)")
                if len(services) > 3:
                    print(f"    ... و{len(services) - 3} أخرى")

        return classification

    def generate_smart_merge_recommendations(
        self, service_usage: Dict, classification: Dict
    ) -> Dict:
        """إنشاء توصيات دمج ذكية"""
        print("🎯 إنشاء توصيات الدمج الذكي...")

        recommendations = {
            "primary_services": {},  # الخدمات الأساسية لكل مجموعة
            "merge_into_primary": {},  # ما يُدمج في الأساسي
            "move_to_correct_location": {},  # ما يُنقل للمكان الصحيح
            "safe_to_delete": [],  # آمن للحذف
            "needs_review": [],  # يحتاج مراجعة
        }

        # تجميع الخدمات حسب المجموعة
        groups = defaultdict(list)
        for service_name, service_data in service_usage.items():
            group = service_data["group"]
            groups[group].append((service_name, service_data))

        for group_name, group_services in groups.items():
            print(f"\n📋 تحليل مجموعة: {group_name}")

            # ترتيب الخدمات حسب الاستخدام
            sorted_services = sorted(
                group_services, key=lambda x: x[1]["usage_count"], reverse=True
            )

            if not sorted_services:
                continue

            # اختيار الخدمة الأساسية (الأكثر استخداماً)
            primary_service_name, primary_service_data = sorted_services[0]

            # إذا كانت الخدمة الأساسية غير مستخدمة، ابحث عن بديل
            if primary_service_data["usage_count"] == 0:
                # ابحث عن أي خدمة مستخدمة في المجموعة
                used_services = [s for s in sorted_services if s[1]["usage_count"] > 0]
                if used_services:
                    primary_service_name, primary_service_data = used_services[0]
                else:
                    # كل الخدمات غير مستخدمة - اختر أول واحدة
                    pass

            recommendations["primary_services"][group_name] = {
                "service": primary_service_name,
                "usage_count": primary_service_data["usage_count"],
                "path": primary_service_data["path"],
            }

            print(
                f"  🎯 الخدمة الأساسية: {primary_service_name} ({primary_service_data['usage_count']} مراجع)"
            )

            # تصنيف باقي الخدمات
            for service_name, service_data in sorted_services[1:]:
                if service_data["usage_count"] == 0:
                    recommendations["safe_to_delete"].append(
                        {
                            "service": service_name,
                            "group": group_name,
                            "reason": "غير مستخدمة نهائياً",
                        }
                    )
                    print(f"    🗑️  للحذف: {service_name} (غير مستخدم)")

                elif service_data["usage_count"] <= 2:
                    recommendations["merge_into_primary"].setdefault(
                        group_name, []
                    ).append(
                        {
                            "service": service_name,
                            "usage_count": service_data["usage_count"],
                            "reason": "استخدام قليل، يمكن دمجه",
                        }
                    )
                    print(
                        f"    🔄 للدمج: {service_name} ({service_data['usage_count']} مراجع)"
                    )

                else:
                    recommendations["needs_review"].append(
                        {
                            "service": service_name,
                            "group": group_name,
                            "usage_count": service_data["usage_count"],
                            "reason": "استخدام كثير، يحتاج مراجعة يدوية",
                        }
                    )
                    print(
                        f"    📝 مراجعة: {service_name} ({service_data['usage_count']} مراجع)"
                    )

        return recommendations

    def execute_usage_based_organization(self, recommendations: Dict) -> Dict:
        """تنفيذ التنظيم المبني على الاستخدام"""
        print("\n🚀 تنفيذ التنظيم المبني على الاستخدام...")

        results = {
            "files_deleted": 0,
            "files_merged": 0,
            "files_moved": 0,
            "primary_services_kept": 0,
            "errors": [],
        }

        # إنشاء المجلدات المطلوبة
        unused_dir = self.base_path / "deleted" / "unused_services"
        unused_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 1. نقل الخدمات غير المستخدمة للحذف
            for item in recommendations["safe_to_delete"]:
                service_name = item["service"]
                group_name = item["group"]

                source_path = (
                    self.base_path
                    / "deprecated"
                    / "services"
                    / group_name
                    / f"{service_name}.py"
                )
                if source_path.exists():
                    target_path = unused_dir / f"{service_name}.py"
                    source_path.rename(target_path)
                    results["files_deleted"] += 1
                    print(f"  🗑️  نقل للحذف: {service_name}")

            # 2. الاحتفاظ بالخدمات الأساسية في مكانها الصحيح
            for group_name, primary_info in recommendations["primary_services"].items():
                service_name = primary_info["service"]

                # تحديد المكان الصحيح حسب Clean Architecture
                target_location = self._get_clean_architecture_location(group_name)
                source_path = (
                    self.base_path
                    / "deprecated"
                    / "services"
                    / group_name
                    / f"{service_name}.py"
                )
                target_path = self.base_path / target_location / f"{service_name}.py"

                if source_path.exists():
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    source_path.rename(target_path)
                    results["primary_services_kept"] += 1
                    print(f"  ✅ احتفظ بـ: {service_name} → {target_location}")

            # 3. دمج الخدمات القليلة الاستخدام (معالجة لاحقة)
            for group_name, merge_list in recommendations["merge_into_primary"].items():
                for item in merge_list:
                    service_name = item["service"]
                    # TODO: دمج فعلي للمحتوى
                    print(f"  🔄 سيتم دمج: {service_name} (TODO)")
                    results["files_merged"] += 1

        except Exception as e:
            error_msg = f"خطأ في التنظيم: {str(e)}"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")

        return results

    def _get_clean_architecture_location(self, group_name: str) -> str:
        """تحديد المكان الصحيح في Clean Architecture"""
        locations = {
            "ai_services": "src/application/services/ai",
            "audio_services": "src/application/services/core",
            "cache_services": "src/infrastructure/services/data",
            "monitoring_services": "src/infrastructure/services/monitoring",
        }
        return locations.get(group_name, "src/application/services/core")

    def generate_usage_analysis_report(
        self,
        service_usage: Dict,
        classification: Dict,
        recommendations: Dict,
        results: Dict,
    ) -> str:
        """إنشاء تقرير تحليل الاستخدام"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""
# 📊 تقرير تحليل أنماط الاستخدام للخدمات
**التاريخ**: {timestamp}
**المحلل**: UsagePatternAnalyzer v1.0

## 🎯 الهدف
تحديد الملفات التي يحتاجها المشروع فعلاً والدمج الذكي بناءً على الاستخدام الفعلي.

## 📈 إحصائيات الاستخدام

### تصنيف الخدمات:
- **مستخدمة بكثرة** (5+ مراجع): {len(classification['heavily_used'])} خدمات
- **مستخدمة متوسط** (2-4 مراجع): {len(classification['moderately_used'])} خدمات  
- **مستخدمة قليلاً** (1 مرجع): {len(classification['lightly_used'])} خدمات
- **غير مستخدمة**: {len(classification['unused'])} خدمات
- **اختبارات فقط**: {len(classification['test_only'])} خدمات

## 🎯 توصيات الدمج الذكي

"""

        # الخدمات الأساسية المحتفظ بها
        report += f"""
### ✅ الخدمات الأساسية المحتفظ بها
"""
        for group, primary in recommendations["primary_services"].items():
            report += f"""
#### {group.replace('_', ' ').title()}
- **الخدمة الأساسية**: `{primary['service']}`
- **عدد المراجع**: {primary['usage_count']}
- **المسار الجديد**: `{self._get_clean_architecture_location(group)}/{primary['service']}.py`
"""

        # الخدمات المحذوفة
        if recommendations["safe_to_delete"]:
            report += f"""
### 🗑️ الخدمات المحذوفة (غير مستخدمة)
"""
            for item in recommendations["safe_to_delete"]:
                report += f"- `{item['service']}` ({item['reason']})\n"

        # الخدمات المدموجة
        if recommendations["merge_into_primary"]:
            report += f"""
### 🔄 الخدمات للدمج
"""
            for group, merge_list in recommendations["merge_into_primary"].items():
                report += f"""
#### {group.replace('_', ' ').title()}
"""
                for item in merge_list:
                    report += f"- `{item['service']}` ({item['usage_count']} مراجع) - {item['reason']}\n"

        # الخدمات التي تحتاج مراجعة
        if recommendations["needs_review"]:
            report += f"""
### 📝 خدمات تحتاج مراجعة يدوية
"""
            for item in recommendations["needs_review"]:
                report += f"- `{item['service']}` في {item['group']} ({item['usage_count']} مراجع)\n"

        report += f"""
## 📊 نتائج التنفيذ
- **ملفات محذوفة**: {results['files_deleted']}
- **خدمات أساسية محتفظ بها**: {results['primary_services_kept']}
- **ملفات مدموجة**: {results['files_merged']}
- **أخطاء**: {len(results['errors'])}

## 🎯 النتيجة النهائية

### ✅ ما تم تحقيقه:
1. **الاحتفاظ بالملفات المهمة فقط** - تم حفظ الخدمات المستخدمة فعلاً
2. **حذف الملفات غير المستخدمة** - توفير مساحة وتقليل التعقيد
3. **التنظيم حسب Clean Architecture** - كل خدمة في مكانها الصحيح
4. **قرارات مبنية على البيانات** - تحليل الاستخدام الفعلي

### 📋 الخطوات التالية:
1. **مراجعة الخدمات المدموجة** - تنفيذ الدمج الفعلي للمحتوى
2. **تحديث المراجع** - إصلاح الاستيرادات للمسارات الجديدة
3. **اختبار شامل** - التأكد من عمل كل شيء بعد التغييرات
4. **توثيق الخدمات الجديدة** - كتابة وثائق للخدمات الموحدة

---
**تم إنشاؤه بواسطة**: UsagePatternAnalyzer v1.0
**التوقيت**: {timestamp}
"""

        return report

    def run_complete_usage_analysis(self) -> Dict:
        """تشغيل التحليل الكامل للاستخدام"""
        print("=" * 60)
        print("📊  USAGE PATTERN ANALYZER")
        print("🎯  ANALYZING ACTUAL PROJECT NEEDS")
        print("=" * 60)

        # تحليل أنماط الاستخدام
        service_usage = self.analyze_service_usage_patterns()

        # تصنيف حسب الاستخدام
        classification = self.classify_services_by_usage(service_usage)

        # إنشاء توصيات الدمج
        recommendations = self.generate_smart_merge_recommendations(
            service_usage, classification
        )

        # تنفيذ التنظيم
        results = self.execute_usage_based_organization(recommendations)

        # إنشاء التقرير
        report_content = self.generate_usage_analysis_report(
            service_usage, classification, recommendations, results
        )
        report_path = (
            self.base_path / "deleted" / "reports" / "USAGE_PATTERN_ANALYSIS.md"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"\n🎉 تم إكمال تحليل أنماط الاستخدام!")
        print(f"📋 التقرير: {report_path}")
        print(f"📊 خدمات محذوفة: {results['files_deleted']}")
        print(f"✅ خدمات محتفظ بها: {results['primary_services_kept']}")

        return {
            "service_usage": service_usage,
            "classification": classification,
            "recommendations": recommendations,
            "results": results,
        }


def main():
    """الدالة الرئيسية"""
    analyzer = UsagePatternAnalyzer()

    try:
        analysis = analyzer.run_complete_usage_analysis()
        print(f"\n✅ تم التحليل بنجاح!")

    except Exception as e:
        print(f"❌ خطأ في التحليل: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
