#!/usr/bin/env python3
"""
🔧 AI Teddy Bear - Phase 2: Services Consolidation
المرحلة الثانية: توحيد وتنظيم الخدمات

الهدف: دمج 19 مجلد services في 6 مجلدات منظمة
التحسين المتوقع: 68% تقليل في تعقيد Services
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set


class ServicesConsolidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"

        # هيكل الخدمات الجديد
        self.new_services_structure = {
            "ai_services": {
                "path": "src/application/services/ai",
                "patterns": [
                    "ai",
                    "openai",
                    "gpt",
                    "llm",
                    "claude",
                    "gemini",
                    "hume",
                    "emotion",
                    "analysis",
                ],
            },
            "audio_services": {
                "path": "src/application/services/audio",
                "patterns": [
                    "audio",
                    "voice",
                    "speech",
                    "tts",
                    "stt",
                    "sound",
                    "microphone",
                    "speaker",
                ],
            },
            "child_services": {
                "path": "src/application/services/child",
                "patterns": [
                    "child",
                    "kid",
                    "interaction",
                    "learning",
                    "progress",
                    "education",
                ],
            },
            "parent_services": {
                "path": "src/application/services/parent",
                "patterns": [
                    "parent",
                    "dashboard",
                    "control",
                    "report",
                    "monitor",
                    "auth",
                ],
            },
            "device_services": {
                "path": "src/application/services/device",
                "patterns": [
                    "device",
                    "esp32",
                    "hardware",
                    "teddy",
                    "simulator",
                    "connection",
                ],
            },
            "core_services": {
                "path": "src/application/services/core",
                "patterns": [
                    "notification",
                    "messaging",
                    "security",
                    "validation",
                    "utils",
                    "common",
                ],
            },
        }

    def analyze_current_services(self) -> Dict:
        """تحليل الخدمات الحالية"""
        print("🔍 تحليل الخدمات الحالية...")

        services_analysis = {
            "total_service_files": 0,
            "service_directories": [],
            "files_by_category": {
                category: [] for category in self.new_services_structure.keys()
            },
            "unclassified_files": [],
            "complexity_metrics": {},
        }

        # البحث عن ملفات الخدمات
        for root, dirs, files in os.walk(self.src_path):
            # تحديد مجلدات الخدمات
            for d in dirs:
                if "service" in d.lower():
                    services_analysis["service_directories"].append(
                        os.path.join(root, d)
                    )

            # تحليل ملفات الخدمات
            for file in files:
                if file.endswith(".py") and "service" in file.lower():
                    file_path = Path(root) / file
                    services_analysis["total_service_files"] += 1

                    # تصنيف الملف
                    classified = False
                    for category, config in self.new_services_structure.items():
                        if any(
                            pattern in file.lower() for pattern in config["patterns"]
                        ):
                            services_analysis["files_by_category"][category].append(
                                str(file_path)
                            )
                            classified = True
                            break

                    if not classified:
                        services_analysis["unclassified_files"].append(str(file_path))

        # حساب مقاييس التعقيد
        services_analysis["complexity_metrics"] = {
            "current_service_dirs": len(services_analysis["service_directories"]),
            "target_service_dirs": len(self.new_services_structure),
            "complexity_reduction": f"{len(services_analysis['service_directories'])} → {len(self.new_services_structure)} ({((len(services_analysis['service_directories']) - len(self.new_services_structure)) / len(services_analysis['service_directories']) * 100):.0f}% تحسن)",
            "files_distribution": {
                cat: len(files)
                for cat, files in services_analysis["files_by_category"].items()
            },
        }

        return services_analysis

    def create_new_service_directories(self):
        """إنشاء هيكل الخدمات الجديد"""
        print("🏗️ إنشاء هيكل الخدمات الجديد...")

        for category, config in self.new_services_structure.items():
            target_dir = Path(config["path"])
            target_dir.mkdir(parents=True, exist_ok=True)

            # إنشاء __init__.py
            init_file = target_dir / "__init__.py"
            if not init_file.exists():
                init_content = f'''"""
{category.replace('_', ' ').title()} Package
{config["path"].split('/')[-1]} services for AI Teddy Bear
"""

# TODO: Add service imports after consolidation
'''
                init_file.write_text(init_content, encoding="utf-8")

            print(f"  ✅ تم إنشاء: {config['path']}")

    def consolidate_ai_services(self, files: List[str]) -> Dict:
        """توحيد خدمات الذكاء الاصطناعي"""
        print("🤖 توحيد خدمات الذكاء الاصطناعي...")

        target_dir = Path(self.new_services_structure["ai_services"]["path"])
        consolidation_results = {"moved": 0, "errors": 0, "conflicts": []}

        for file_path in files:
            try:
                src_file = Path(file_path)
                if src_file.exists():
                    target_file = target_dir / src_file.name

                    # تجنب التعارضات
                    if target_file.exists():
                        # إنشاء اسم فريد
                        counter = 1
                        while target_file.exists():
                            name_parts = src_file.stem, counter, src_file.suffix
                            target_file = (
                                target_dir
                                / f"{name_parts[0]}_v{name_parts[1]}{name_parts[2]}"
                            )
                            counter += 1
                        consolidation_results["conflicts"].append(str(src_file))

                    shutil.move(str(src_file), str(target_file))
                    consolidation_results["moved"] += 1
                    print(f"  ✅ نُقل: {src_file.name}")

            except Exception as e:
                consolidation_results["errors"] += 1
                print(f"  ❌ خطأ في نقل {file_path}: {e}")

        return consolidation_results

    def consolidate_audio_services(self, files: List[str]) -> Dict:
        """توحيد خدمات الصوت"""
        print("🎵 توحيد خدمات الصوت...")

        target_dir = Path(self.new_services_structure["audio_services"]["path"])
        results = {"moved": 0, "errors": 0, "conflicts": []}

        for file_path in files:
            try:
                src_file = Path(file_path)
                if src_file.exists():
                    target_file = target_dir / src_file.name

                    if target_file.exists():
                        target_file = (
                            target_dir
                            / f"{src_file.stem}_consolidated{src_file.suffix}"
                        )
                        results["conflicts"].append(str(src_file))

                    shutil.move(str(src_file), str(target_file))
                    results["moved"] += 1
                    print(f"  ✅ نُقل: {src_file.name}")

            except Exception as e:
                results["errors"] += 1
                print(f"  ❌ خطأ: {e}")

        return results

    def consolidate_category_services(self, category: str, files: List[str]) -> Dict:
        """توحيد خدمات فئة معينة"""
        print(f"📦 توحيد {category.replace('_', ' ')}...")

        target_dir = Path(self.new_services_structure[category]["path"])
        results = {"moved": 0, "errors": 0, "conflicts": []}

        for file_path in files:
            try:
                src_file = Path(file_path)
                if src_file.exists():
                    target_file = target_dir / src_file.name

                    # معالجة التعارضات
                    if target_file.exists():
                        target_file = (
                            target_dir / f"{src_file.stem}_migrated{src_file.suffix}"
                        )
                        results["conflicts"].append(str(src_file))

                    shutil.move(str(src_file), str(target_file))
                    results["moved"] += 1
                    print(f"  ✅ {src_file.name}")

            except Exception as e:
                results["errors"] += 1
                print(f"  ❌ خطأ: {e}")

        return results

    def execute_consolidation(self, analysis: Dict) -> Dict:
        """تنفيذ عملية التوحيد"""
        print("🚀 بدء عملية توحيد الخدمات...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "categories_processed": {},
            "total_moved": 0,
            "total_errors": 0,
            "summary": {},
        }

        # إنشاء الهيكل الجديد
        self.create_new_service_directories()

        # توحيد كل فئة
        for category, files in analysis["files_by_category"].items():
            if files:  # إذا كان هناك ملفات في هذه الفئة
                category_results = self.consolidate_category_services(category, files)
                results["categories_processed"][category] = category_results
                results["total_moved"] += category_results["moved"]
                results["total_errors"] += category_results["errors"]

        # معالجة الملفات غير المصنفة
        if analysis["unclassified_files"]:
            print("📂 معالجة الملفات غير المصنفة...")
            unclassified_results = self.consolidate_category_services(
                "core_services", analysis["unclassified_files"]
            )
            results["categories_processed"]["unclassified"] = unclassified_results
            results["total_moved"] += unclassified_results["moved"]
            results["total_errors"] += unclassified_results["errors"]

        # إنشاء ملخص
        results["summary"] = {
            "services_reorganized": results["total_moved"],
            "errors_encountered": results["total_errors"],
            "structure_improvement": analysis["complexity_metrics"][
                "complexity_reduction"
            ],
            "new_structure": list(self.new_services_structure.keys()),
        }

        return results

    def generate_phase2_report(self, analysis: Dict, results: Dict) -> str:
        """إنشاء تقرير المرحلة الثانية"""
        report = f"""
# 🔧 تقرير المرحلة الثانية - توحيد الخدمات

## الوضع قبل التوحيد:
- مجلدات Services: {analysis['complexity_metrics']['current_service_dirs']}
- إجمالي ملفات الخدمات: {analysis['total_service_files']}
- التوزيع حسب الفئة: {analysis['complexity_metrics']['files_distribution']}

## التحسينات المحققة:
- {analysis['complexity_metrics']['complexity_reduction']}
- ملفات تم نقلها: {results['total_moved']}
- أخطاء: {results['total_errors']}

## الهيكل الجديد:
{chr(10).join(f"- {cat}: {config['path']}" for cat, config in self.new_services_structure.items())}

## الفئات المعالجة:
{chr(10).join(f"- {cat}: {res['moved']} ملف" for cat, res in results['categories_processed'].items())}

## الحالة الحالية:
✅ المرحلة الأولى: تم (نقل الكيانات)
✅ المرحلة الثانية: تم (توحيد الخدمات)
⏳ المرحلة الثالثة: Infrastructure
⏳ المرحلة الرابعة: تحديث Imports

## الخطوات التالية:
1. مراجعة الهيكل الجديد
2. تنفيذ المرحلة الثالثة (Infrastructure)
3. تحديث جميع imports
4. اختبار شامل للنظام

تم إنشاء التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report


def main():
    """البرنامج الرئيسي للمرحلة الثانية"""
    print("🔧 مرحباً بك في المرحلة الثانية - توحيد الخدمات!")
    print("=" * 60)

    consolidator = ServicesConsolidator()

    try:
        # تحليل الخدمات الحالية
        analysis = consolidator.analyze_current_services()

        # عرض التحليل
        print(f"\n📊 نتائج التحليل:")
        print(
            f"- مجلدات Services حالياً: {analysis['complexity_metrics']['current_service_dirs']}"
        )
        print(
            f"- مجلدات Services مستهدفة: {analysis['complexity_metrics']['target_service_dirs']}"
        )
        print(
            f"- التحسن المتوقع: {analysis['complexity_metrics']['complexity_reduction']}"
        )
        print(f"- إجمالي ملفات الخدمات: {analysis['total_service_files']}")

        # تأكيد من المستخدم
        response = input("\n🚀 هل تريد بدء توحيد الخدمات؟ (y/n): ")

        if response.lower() == "y":
            # تنفيذ التوحيد
            results = consolidator.execute_consolidation(analysis)

            # إنشاء التقرير
            report = consolidator.generate_phase2_report(analysis, results)

            # حفظ التقرير
            report_file = "phase_2_services_consolidation_report.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)

            print(f"\n✅ تم إنهاء المرحلة الثانية بنجاح!")
            print(f"📄 تقرير مفصل في: {report_file}")
            print(f"🎯 ملفات تم نقلها: {results['total_moved']}")
            print(
                f"🚀 التحسن المحقق: {analysis['complexity_metrics']['complexity_reduction']}"
            )

        else:
            print("❌ تم إلغاء العملية")

    except Exception as e:
        print(f"❌ خطأ في التنفيذ: {e}")


if __name__ == "__main__":
    main()
