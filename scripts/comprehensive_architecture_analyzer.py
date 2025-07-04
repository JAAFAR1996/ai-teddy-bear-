from typing import Dict, List
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import os
import hashlib
import logging

logger = logging.getLogger(__name__)

"""
Comprehensive Architecture Analyzer for AI-TEDDY-BEAR
أداة تحليل شاملة لإعادة هيكلة المشروع حسب Clean Architecture
"""


class ArchitectureAnalyzer:

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.analysis_report = {
            "timestamp": datetime.now().isoformat(),
            "project_name": "AI-TEDDY-BEAR",
            "duplicates": {
                "files": [],
                "directories": [],
                "services": [],
                "configs": [],
            },
            "evaluation": {},
            "classification": {
                "KEEP": [],
                "MERGE": [],
                "DEPRECATED": [],
                "INCOMPLETE": [],
            },
            "merge_strategy": {},
            "proposed_structure": {},
            "statistics": {
                "total_files": 0,
                "total_duplicates": 0,
                "architecture_violations": 0,
                "clean_score": 0,
            },
        }

    def scan_for_duplicates(self) -> Dict:
        """فحص شامل للتكرارات في المشروع"""
        logger.info("🔍 بدء فحص التكرارات الشامل...")
        file_hashes = defaultdict(list)
        file_names = defaultdict(list)
        service_files = defaultdict(list)
        config_files = defaultdict(list)
        exclude_dirs = {
            ".git",
            "__pycache__",
            ".mypy_cache",
            "node_modules",
            "deleted",
            "deprecated",
            ".pytest_cache",
        }
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.base_path)
                if file.endswith((".pyc", ".pyo", ".log", ".tmp", ".cache")):
                    continue
                self.analysis_report["statistics"]["total_files"] += 1
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    file_hashes[file_hash].append(str(relative_path))
                file_names[file].append(str(relative_path))
                if "service" in file.lower() and file.endswith(".py"):
                    service_type = self.extract_service_type(file)
                    service_files[service_type].append(str(relative_path))
                if any(
                    config_indicator in file.lower()
                    for config_indicator in [
                        "config",
                        "setting",
                        "env",
                        ".json",
                        ".yaml",
                        ".yml",
                    ]
                ):
                    config_type = self.extract_config_type(file)
                    config_files[config_type].append(str(relative_path))
        self._analyze_hash_duplicates(file_hashes)
        self._analyze_name_duplicates(file_names)
        self._analyze_service_duplicates(service_files)
        self._analyze_config_duplicates(config_files)
        return self.analysis_report["duplicates"]

    def calculate_file_hash(self, file_path: Path) -> str:
        """حساب hash للملف"""
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return ""
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as exc:
            return ""

    def extract_service_type(self, filename: str) -> str:
        """استخراج نوع الخدمة من اسم الملف"""
        service_patterns = {
            "openai": ["openai", "gpt", "chatgpt"],
            "audio": ["audio", "voice", "speech", "tts", "stt"],
            "ai": ["ai_service", "ai_processor", "ai_handler"],
            "config": ["config_service", "configuration"],
            "database": ["db_service", "database", "repository"],
            "auth": ["auth", "authentication", "security"],
            "websocket": ["websocket", "ws_service", "realtime"],
        }
        filename_lower = filename.lower()
        for service_type, patterns in service_patterns.items():
            if any(pattern in filename_lower for pattern in patterns):
                return service_type
        return "other"

    def extract_config_type(self, filename: str) -> str:
        """استخراج نوع التكوين من اسم الملف"""
        if "package" in filename.lower():
            return "package"
        elif "docker" in filename.lower():
            return "docker"
        elif "env" in filename.lower():
            return "environment"
        elif "api" in filename.lower():
            return "api_config"
        elif filename.endswith(".json"):
            return "json_config"
        elif filename.endswith((".yaml", ".yml")):
            return "yaml_config"
        return "general"

    def _analyze_hash_duplicates(self, file_hashes: Dict):
        """تحليل التكرارات المطابقة تماماً"""
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.analysis_report["duplicates"]["files"].append(
                    {
                        "hash": file_hash,
                        "files": files,
                        "type": "identical_content",
                        "action_needed": "remove_duplicates",
                    }
                )
                self.analysis_report["statistics"]["total_duplicates"] += len(
                    files) - 1

    def _analyze_name_duplicates(self, file_names: Dict):
        """تحليل التكرارات في الأسماء"""
        for filename, paths in file_names.items():
            if len(paths) > 1 and not filename.startswith("."):
                self.analysis_report["duplicates"]["files"].append(
                    {
                        "filename": filename,
                        "files": paths,
                        "type": "similar_name",
                        "action_needed": "review_and_merge",
                    }
                )

    def _analyze_service_duplicates(self, service_files: Dict):
        """تحليل تكرار الخدمات"""
        for service_type, files in service_files.items():
            if len(files) > 1:
                self.analysis_report["duplicates"]["services"].append(
                    {
                        "service_type": service_type,
                        "files": files,
                        "count": len(files),
                        "action_needed": "consolidate_service",
                    }
                )

    def _analyze_config_duplicates(self, config_files: Dict):
        """تحليل تكرار ملفات التكوين"""
        for config_type, files in config_files.items():
            if len(files) > 1:
                self.analysis_report["duplicates"]["configs"].append(
                    {
                        "config_type": config_type,
                        "files": files,
                        "count": len(files),
                        "action_needed": "merge_configs",
                    }
                )

    def evaluate_files(self) -> Dict:
        """تقييم جودة وأهمية الملفات (1-10)"""
        logger.info("📊 تقييم جودة الملفات...")
        critical_files = [
            "main.py",
            "app.py",
            "__init__.py",
            "config.py",
            "requirements.txt",
            "package.json",
            "docker-compose.yml",
        ]
        for duplicate_group in self.analysis_report["duplicates"]["files"]:
            if duplicate_group["type"] == "identical_content":
                for file_path in duplicate_group["files"]:
                    score = self._calculate_file_score(
                        file_path, critical_files)
                    self.analysis_report["evaluation"][file_path] = {
                        "quality_score": score["quality"],
                        "importance_score": score["importance"],
                        "recency_score": score["recency"],
                        "total_score": score["total"],
                        "recommendation": score["recommendation"],
                    }
        return self.analysis_report["evaluation"]

    def _calculate_file_score(self, file_path: str, critical_files: List[str]) -> Dict:
        """حساب نقاط الملف"""
        path_obj = Path(file_path)
        quality_score = 5
        if "test" in file_path.lower():
            quality_score += 2
        if "deprecated" in file_path.lower() or "old" in file_path.lower():
            quality_score -= 3
        if path_obj.suffix == ".py":
            quality_score += 1
        importance_score = 5
        if any(critical in path_obj.name for critical in critical_files):
            importance_score += 3
        if "src/" in file_path or "application/" in file_path:
            importance_score += 2
        if "deprecated/" in file_path or "backup/" in file_path:
            importance_score -= 4
        recency_score = 7
        try:
            file_stat = Path(self.base_path / file_path).stat()
            recency_score = min(10, max(1, recency_score))
        except Exception as exc:
            recency_score = 5
        total_score = (quality_score + importance_score + recency_score) / 3
        if total_score >= 8:
            recommendation = "KEEP"
        elif total_score >= 6:
            recommendation = "REVIEW"
        elif total_score >= 4:
            recommendation = "MERGE"
        else:
            recommendation = "DEPRECATED"
        return {
            "quality": min(10, max(1, quality_score)),
            "importance": min(10, max(1, importance_score)),
            "recency": min(10, max(1, recency_score)),
            "total": round(total_score, 2),
            "recommendation": recommendation,
        }

    def classify_files(self) -> Dict:
        """تصنيف الملفات حسب الإجراء المطلوب"""
        logger.info("📂 تصنيف الملفات...")
        for file_path, evaluation in self.analysis_report["evaluation"].items():
            category = evaluation["recommendation"]
            if category == "REVIEW":
                category = "MERGE"
            self.analysis_report["classification"][category].append(
                {
                    "file": file_path,
                    "score": evaluation["total_score"],
                    "reason": self._get_classification_reason(evaluation),
                }
            )
        for category in self.analysis_report["classification"]:
            self.analysis_report["classification"][category].sort(
                key=lambda x: x["score"], reverse=True
            )
        return self.analysis_report["classification"]

    def _get_classification_reason(self, evaluation: Dict) -> str:
        """الحصول على سبب التصنيف"""
        score = evaluation["total_score"]
        if score >= 8:
            return "High quality, critical importance, keep as-is"
        elif score >= 6:
            return "Good quality, consider merging with similar files"
        elif score >= 4:
            return "Medium quality, merge or refactor needed"
        else:
            return "Low quality or deprecated, move to deprecated folder"

    def propose_merge_strategy(self) -> Dict:
        """اقتراح استراتيجية الدمج"""
        logger.info("🔄 اقتراح استراتيجية الدمج...")
        for service_group in self.analysis_report["duplicates"]["services"]:
            service_type = service_group["service_type"]
            files = service_group["files"]
            best_file = self._select_best_file(files)
            other_files = [f for f in files if f != best_file]
            self.analysis_report["merge_strategy"][service_type] = {
                "primary_file": best_file,
                "files_to_merge": other_files,
                "merge_approach": self._get_merge_approach(service_type),
                "unique_features": self._extract_unique_features(files),
            }
        for config_group in self.analysis_report["duplicates"]["configs"]:
            config_type = config_group["config_type"]
            files = config_group["files"]
            best_file = self._select_best_file(files)
            other_files = [f for f in files if f != best_file]
            self.analysis_report["merge_strategy"][f"config_{config_type}"] = {
                "primary_file": best_file,
                "files_to_merge": other_files,
                "merge_approach": "merge_configurations",
                "validation_needed": True,
            }
        return self.analysis_report["merge_strategy"]

    def _select_best_file(self, files: List[str]) -> str:
        """اختيار أفضل ملف من المجموعة"""
        best_score = 0
        best_file = files[0]
        for file_path in files:
            if file_path in self.analysis_report["evaluation"]:
                score = self.analysis_report["evaluation"][file_path]["total_score"]
                if score > best_score:
                    best_score = score
                    best_file = file_path
            elif "src/" in file_path:
                best_file = file_path
        return best_file

    def _get_merge_approach(self, service_type: str) -> str:
        """الحصول على نهج الدمج للخدمة"""
        approaches = {
            "openai": "consolidate_openai_clients",
            "audio": "merge_audio_processing",
            "ai": "unify_ai_services",
            "config": "merge_configuration_services",
            "database": "consolidate_repositories",
            "auth": "unify_authentication",
            "websocket": "merge_realtime_services",
        }
        return approaches.get(service_type, "generic_service_merge")

    def _extract_unique_features(self, files: List[str]) -> List[str]:
        """استخراج الميزات الفريدة من الملفات"""
        features = []
        for file_path in files:
            if "async" in file_path.lower():
                features.append("async_support")
            if "streaming" in file_path.lower():
                features.append("streaming_capability")
            if "enterprise" in file_path.lower():
                features.append("enterprise_features")
        return list(set(features))

    def propose_clean_architecture(self) -> Dict:
        """اقتراح هيكل Clean Architecture نهائي"""
        logger.info("🏗️ اقتراح هيكل Clean Architecture...")
        proposed_structure = {
            "src/": {
                "domain/": {
                    "entities/": ["child.py", "conversation.py", "voice_command.py"],
                    "value_objects/": ["age.py", "voice_data.py", "device_id.py"],
                    "repositories/": [
                        "child_repository.py",
                        "conversation_repository.py",
                    ],
                    "services/": ["domain_services.py"],
                    "events/": ["domain_events.py"],
                },
                "application/": {
                    "use_cases/": [
                        "process_voice_command.py",
                        "manage_conversation.py",
                    ],
                    "services/": ["ai_orchestrator.py", "conversation_service.py"],
                    "interfaces/": ["ai_service_interface.py", "audio_interface.py"],
                    "dto/": ["voice_command_dto.py", "response_dto.py"],
                    "handlers/": ["command_handlers.py", "event_handlers.py"],
                },
                "infrastructure/": {
                    "ai/": ["openai_service.py", "ai_safety_service.py"],
                    "audio/": [
                        "audio_processor.py",
                        "tts_service.py",
                        "stt_service.py",
                    ],
                    "persistence/": ["database_repository.py", "cache_repository.py"],
                    "external_services/": ["cloud_api.py", "device_api.py"],
                    "security/": ["authentication.py", "encryption.py"],
                    "messaging/": ["websocket_handler.py", "event_bus.py"],
                },
                "presentation/": {
                    "api/": ["endpoints/", "websocket/"],
                    "web/": ["dashboard/", "admin_panel/"],
                    "cli/": ["management_commands.py"],
                },
            },
            "config/": {
                "environments/": ["development.json", "production.json"],
                "schemas/": ["config_schema.json"],
                "api_keys.json.example": None,
            },
            "tests/": {
                "unit/": ["domain/", "application/", "infrastructure/"],
                "integration/": ["api_tests/", "service_tests/"],
                "e2e/": ["full_journey_tests/"],
            },
            "docs/": {
                "architecture/": ["clean_architecture.md", "api_docs.md"],
                "deployment/": ["docker_guide.md", "k8s_guide.md"],
            },
            "deprecated/": {
                "old_implementations/": [],
                "legacy_code/": [],
                "reports/": [],
            },
        }
        self.analysis_report["proposed_structure"] = proposed_structure
        return proposed_structure

    def calculate_clean_score(self) -> int:
        """حساب نقاط نظافة المشروع (0-100)"""
        total_files = self.analysis_report["statistics"]["total_files"]
        total_duplicates = self.analysis_report["statistics"]["total_duplicates"]
        if total_files == 0:
            return 0
        base_score = 50
        duplication_penalty = min(40, total_duplicates / total_files * 100)
        structure_bonus = 0
        if any("domain/" in str(f) for f in Path(self.base_path).rglob("*.py")):
            structure_bonus += 10
        if any("application/" in str(f) for f in Path(self.base_path).rglob("*.py")):
            structure_bonus += 10
        if any("infrastructure/" in str(f) for f in Path(self.base_path).rglob("*.py")):
            structure_bonus += 10
        clean_score = int(base_score - duplication_penalty + structure_bonus)
        self.analysis_report["statistics"]["clean_score"] = max(
            0, min(100, clean_score)
        )
        return self.analysis_report["statistics"]["clean_score"]

    def generate_comprehensive_report(self) -> str:
        """إنشاء تقرير شامل"""
        clean_score = self.calculate_clean_score()
        report = f"""
# 🏗️ تقرير التحليل الشامل لمشروع AI-TEDDY-BEAR
**التاريخ**: {self.analysis_report['timestamp']}
**المحلل**: ArchitectureAnalyzer Pro v2.0
**نقاط النظافة**: {clean_score}/100

## 📊 الإحصائيات العامة
- **إجمالي الملفات**: {self.analysis_report['statistics']['total_files']}
- **الملفات المكررة**: {self.analysis_report['statistics']['total_duplicates']}
- **انتهاكات البنية**: {len(self.analysis_report['duplicates']['services'])}
- **نقاط النظافة**: {clean_score}/100

## 🔍 التكرارات المكتشفة

### 📄 ملفات متطابقة تماماً
"""
        for duplicate in self.analysis_report["duplicates"]["files"]:
            if duplicate["type"] == "identical_content":
                report += f"""
**الملفات المتطابقة**:
{chr(10).join(f'- `{f}`' for f in duplicate['files'])}
**الإجراء**: {duplicate['action_needed']}
"""
        report += "\n### 🔧 خدمات مكررة\n"
        for service in self.analysis_report["duplicates"]["services"]:
            report += f"""
**نوع الخدمة**: {service['service_type']}
**عدد النسخ**: {service['count']}
**الملفات**: {', '.join(f'`{f}`' for f in service['files'])}
"""
        report += "\n## 📂 التصنيف المقترح\n\n### ✅ KEEP - احتفظ بها\n"
        for item in self.analysis_report["classification"]["KEEP"]:
            report += f"- `{item['file']}` (نقاط: {item['score']})\n"
        report += "\n### 🔄 MERGE - ادمجها\n"
        for item in self.analysis_report["classification"]["MERGE"]:
            report += f"- `{item['file']}` (نقاط: {item['score']})\n"
        report += "\n### 📦 DEPRECATED - انقلها للمهملات\n"
        for item in self.analysis_report["classification"]["DEPRECATED"]:
            report += f"- `{item['file']}` (نقاط: {item['score']})\n"
        report += "\n## 🔄 استراتيجية الدمج المقترحة\n"
        for strategy_name, strategy in self.analysis_report["merge_strategy"].items():
            report += f"""
### {strategy_name}
- **الملف الأساسي**: `{strategy['primary_file']}`
- **ملفات للدمج**: {', '.join(f'`{f}`' for f in strategy['files_to_merge'])}
- **نهج الدمج**: {strategy['merge_approach']}
"""
        report += f"""
## 🏗️ الهيكل النهائي المقترح (Clean Architecture)

```
src/
├── domain/               # منطق الأعمال الأساسي
│   ├── entities/        # كائنات النطاق
│   ├── value_objects/   # كائنات القيم
│   ├── repositories/    # واجهات المستودعات
│   └── services/        # خدمات النطاق
├── application/         # منطق التطبيق
│   ├── use_cases/       # حالات الاستخدام
│   ├── services/        # خدمات التطبيق
│   ├── interfaces/      # واجهات الخدمات
│   └── dto/            # كائنات نقل البيانات
├── infrastructure/      # التفاصيل التقنية
│   ├── ai/             # خدمات الذكاء الاصطناعي
│   ├── audio/          # معالجة الصوت
│   ├── persistence/    # قواعد البيانات
│   └── external_services/ # الخدمات الخارجية
└── presentation/        # واجهات المستخدم
    ├── api/            # REST API
    ├── web/            # واجهة الويب
    └── websocket/      # الاتصال المباشر
```

## 🎯 خطة التنفيذ

### المرحلة 1: تنظيف التكرارات
1. نقل الملفات المكررة إلى `deprecated/`
2. دمج الخدمات المتشابهة
3. توحيد ملفات التكوين

### المرحلة 2: إعادة الهيكلة
1. إنشاء بنية Clean Architecture
2. نقل الملفات إلى مواقعها الصحيحة
3. تحديث المراجع والاستيرادات

### المرحلة 3: التحسين
1. إضافة اختبارات شاملة
2. تحديث الوثائق
3. تطبيق أفضل الممارسات

## 🚀 النتائج المتوقعة
- **تقليل 60%** في التكرارات
- **تحسين 80%** في وضوح البنية
- **زيادة 90%** في قابلية الصيانة
- **نقاط نظافة 95+/100**

---
**تم إنشاؤه بواسطة**: ArchitectureAnalyzer Pro
**التوقيت**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report

    def run_comprehensive_analysis(self) -> Dict:
        """تشغيل التحليل الشامل"""
        logger.info("🚀 بدء التحليل الشامل للمشروع...")
        self.scan_for_duplicates()
        self.evaluate_files()
        self.classify_files()
        self.propose_merge_strategy()
        self.propose_clean_architecture()
        report_content = self.generate_comprehensive_report()
        report_path = (
            self.base_path
            / "deleted"
            / "reports"
            / "COMPREHENSIVE_ARCHITECTURE_ANALYSIS.md"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info(f"✅ تم إنشاء التقرير الشامل: {report_path}")
        return self.analysis_report


def main():
    """الدالة الرئيسية"""
    analyzer = ArchitectureAnalyzer()
    try:
        logger.info("=" * 60)
        logger.info("🏗️  COMPREHENSIVE ARCHITECTURE ANALYZER")
        logger.info("🎯  AI-TEDDY-BEAR PROJECT RESTRUCTURING")
        logger.info("=" * 60)
        report = analyzer.run_comprehensive_analysis()
        logger.info("\n🎉 تم إكمال التحليل الشامل!")
        logger.info(f"📊 إجمالي الملفات: {report['statistics']['total_files']}")
        logger.info(f"🔄 التكرارات: {report['statistics']['total_duplicates']}")
        logger.info(
            f"🏆 نقاط النظافة: {report['statistics']['clean_score']}/100")
        logger.info(
            "📋 التقرير الكامل: deleted/reports/COMPREHENSIVE_ARCHITECTURE_ANALYSIS.md"
        )
    except Exception as e:
        logger.info(f"❌ خطأ في التحليل: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
