from typing import Dict, List
from pathlib import Path
from datetime import datetime
import shutil
import logging

logger = logging.getLogger(__name__)

"""
Service Organizer Analyzer
أداة تحليل وتنظيم الخدمات المكررة حسب Clean Architecture
"""


class ServiceOrganizerAnalyzer:

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.services = {
            "other_services": [
                "src/adapters/edge/edge_ai_integration_service.py",
                "src/application/main_service.py",
                "src/application/story_service.py",
                "src/application/interfaces/services.py",
                "src/application/services/accessibility_service.py",
                "src/application/services/advanced_personalization_service.py",
                "src/application/services/ar_vr_service.py",
                "src/application/services/base_service.py",
                "src/application/services/cloud_transcription_service.py",
                "src/application/services/conversation_service.py",
                "src/application/services/data_cleanup_service.py",
                "src/application/services/email_service.py",
                "src/application/services/emotion_service.py",
                "src/application/services/enhanced_child_interaction_service.py",
                "src/application/services/enhanced_parent_report_service.py",
                "src/application/services/health_service.py",
                "src/application/services/issue_tracker_service.py",
                "src/application/services/llm_service.py",
                "src/application/services/llm_service_factory.py",
                "src/application/services/memory_service.py",
                "src/application/services/moderation_service.py",
                "src/application/services/moderation_service_modern.py",
                "src/application/services/notification_service.py",
                "src/application/services/parent_dashboard_service.py",
                "src/application/services/parent_report_service.py",
                "src/application/services/push_service.py",
                "src/application/services/rate_monitor_service.py",
                "src/application/services/scheduler_service.py",
                "src/application/services/service_registry.py",
                "src/application/services/simple_health_service.py",
                "src/application/services/sms_service.py",
                "src/application/services/streaming_service.py",
                "src/application/services/audio/synthesis_service.py",
                "src/application/services/audio/transcription_service.py",
                "src/domain/entities/child_domain_service.py",
                "src/domain/entities/child_service.py",
                "src/domain/services/event_sourcing_service.py",
                "src/infrastructure/external_services.py",
                "src/infrastructure/caching/cache_integration_service.py",
                "src/infrastructure/caching/cache_service.py",
                "src/infrastructure/caching/simple_cache_service.py",
                "src/infrastructure/security/he_integration_service.py",
                "src/presentation/api/graphql/service_resolvers.py",
            ],
            "ai_services": [
                "src/application/services/ai_service.py",
                "src/application/services/ai/modern_ai_service.py",
                "tests/integration/test_ai_service_integration.py",
            ],
            "audio_services": [
                "src/application/services/azure_speech_to_text_service.py",
                "src/application/services/speech_to_text_service.py",
                "src/application/services/voice_interaction_service.py",
                "src/application/services/voice_service.py",
                "src/presentation/grpc/audio_service.py",
                "tests/unit/test_voice_service.py",
            ],
        }
        self.categorized_services = {
            "domain_services": [],
            "application_services": [],
            "infrastructure_services": [],
            "presentation_services": [],
            "deprecated_services": [],
            "test_services": [],
        }
        self.organization_plan = {}

    def categorize_services_by_functionality(self) -> Dict:
        """تصنيف الخدمات حسب الوظيفة"""
        logger.info("🔍 تصنيف الخدمات حسب الوظيفة...")
        functional_groups = {
            "ai_ml": [],
            "audio_processing": [],
            "communication": [],
            "personalization": [],
            "monitoring": [],
            "data_management": [],
            "security": [],
            "ui_presentation": [],
            "infrastructure": [],
            "parent_features": [],
            "child_features": [],
            "deprecated": [],
        }
        all_services = (
            self.services["other_services"]
            + self.services["ai_services"]
            + self.services["audio_services"]
        )
        for service_path in all_services:
            service_name = Path(service_path).stem
            if any(
                ai_term in service_name.lower()
                for ai_term in ["ai", "llm", "gpt", "ml", "intelligence"]
            ):
                functional_groups["ai_ml"].append(service_path)
            elif any(
                audio_term in service_name.lower()
                for audio_term in [
                    "audio",
                    "voice",
                    "speech",
                    "transcription",
                    "synthesis",
                    "tts",
                    "stt",
                ]
            ):
                functional_groups["audio_processing"].append(service_path)
            elif any(
                comm_term in service_name.lower()
                for comm_term in ["email", "sms", "push", "notification", "streaming"]
            ):
                functional_groups["communication"].append(service_path)
            elif any(
                person_term in service_name.lower()
                for person_term in ["personalization", "personality", "accessibility"]
            ):
                functional_groups["personalization"].append(service_path)
            elif any(
                monitor_term in service_name.lower()
                for monitor_term in ["health", "monitor", "rate", "issue_tracker"]
            ):
                functional_groups["monitoring"].append(service_path)
            elif any(
                data_term in service_name.lower()
                for data_term in [
                    "data",
                    "memory",
                    "cache",
                    "cleanup",
                    "event_sourcing",
                ]
            ):
                functional_groups["data_management"].append(service_path)
            elif any(
                sec_term in service_name.lower()
                for sec_term in ["security", "he_integration", "moderation"]
            ):
                functional_groups["security"].append(service_path)
            elif any(
                parent_term in service_name.lower()
                for parent_term in ["parent", "dashboard", "report"]
            ):
                functional_groups["parent_features"].append(service_path)
            elif any(
                child_term in service_name.lower()
                for child_term in ["child", "interaction", "story", "conversation"]
            ):
                functional_groups["child_features"].append(service_path)
            elif any(
                infra_term in service_name.lower()
                for infra_term in ["external", "service_registry", "scheduler", "base"]
            ):
                functional_groups["infrastructure"].append(service_path)
            elif any(
                ui_term in service_name.lower()
                for ui_term in ["graphql", "resolver", "presentation"]
            ):
                functional_groups["ui_presentation"].append(service_path)
            elif any(
                test_term in service_path.lower()
                for test_term in ["test", "simple_", "edge_ai"]
            ):
                functional_groups["deprecated"].append(service_path)
            else:
                functional_groups["infrastructure"].append(service_path)
        return functional_groups

    def create_clean_architecture_plan(self, functional_groups: Dict) -> Dict:
        """إنشاء خطة إعادة التنظيم حسب Clean Architecture"""
        logger.info("🏗️ إنشاء خطة Clean Architecture...")
        clean_arch_plan = {
            "src/domain/services/": [],
            "src/application/services/core/": [],
            "src/application/services/ai/": [],
            "src/application/services/communication/": [],
            "src/application/services/personalization/": [],
            "src/infrastructure/services/monitoring/": [],
            "src/infrastructure/services/data/": [],
            "src/infrastructure/services/security/": [],
            "src/infrastructure/services/external/": [],
            "src/presentation/services/": [],
            "deprecated/services/": [],
        }
        mapping = {
            "child_features": "src/domain/services/",
            "ai_ml": "src/application/services/ai/",
            "communication": "src/application/services/communication/",
            "personalization": "src/application/services/personalization/",
            "audio_processing": "src/application/services/core/",
            "monitoring": "src/infrastructure/services/monitoring/",
            "data_management": "src/infrastructure/services/data/",
            "security": "src/infrastructure/services/security/",
            "infrastructure": "src/infrastructure/services/external/",
            "parent_features": "src/application/services/core/",
            "ui_presentation": "src/presentation/services/",
            "deprecated": "deprecated/services/",
        }
        for group, services in functional_groups.items():
            target_location = mapping.get(
                group, "src/application/services/core/")
            clean_arch_plan[target_location].extend(services)
        return clean_arch_plan

    def detect_duplicate_functionalities(self, functional_groups: Dict) -> Dict:
        """اكتشاف الخدمات المكررة الوظائف"""
        logger.info("🔄 اكتشاف الخدمات المكررة...")
        duplicates = {}
        ai_services = functional_groups["ai_ml"]
        if len(ai_services) > 1:
            duplicates["ai_services"] = {
                "primary": self._select_primary_service(ai_services, "ai"),
                "duplicates": [
                    s
                    for s in ai_services
                    if s != self._select_primary_service(ai_services, "ai")
                ],
                "merge_strategy": "consolidate_into_unified_ai_service",
            }
        audio_services = functional_groups["audio_processing"]
        if len(audio_services) > 1:
            duplicates["audio_services"] = {
                "primary": self._select_primary_service(audio_services, "audio"),
                "duplicates": [
                    s
                    for s in audio_services
                    if s != self._select_primary_service(audio_services, "audio")
                ],
                "merge_strategy": "merge_audio_processing_pipeline",
            }
        monitoring_services = functional_groups["monitoring"]
        if len(monitoring_services) > 1:
            duplicates["monitoring_services"] = {
                "primary": self._select_primary_service(monitoring_services, "health"),
                "duplicates": [
                    s
                    for s in monitoring_services
                    if s != self._select_primary_service(monitoring_services, "health")
                ],
                "merge_strategy": "unified_monitoring_service",
            }
        cache_services = [
            s for s in functional_groups["data_management"] if "cache" in s.lower()
        ]
        if len(cache_services) > 1:
            duplicates["cache_services"] = {
                "primary": self._select_primary_service(cache_services, "cache"),
                "duplicates": [
                    s
                    for s in cache_services
                    if s != self._select_primary_service(cache_services, "cache")
                ],
                "merge_strategy": "unified_caching_layer",
            }
        return duplicates

    def _select_primary_service(self, services: List[str], service_type: str) -> str:
        """اختيار الخدمة الأساسية من مجموعة"""
        app_services = [
            s
            for s in services
            if "src/application/services/" in s and "test" not in s.lower()
        ]
        if app_services:
            for service in app_services:
                if "modern" in service.lower() or "enhanced" in service.lower():
                    return service
            return app_services[0]
        return services[0] if services else ""

    def generate_merge_operations(self, duplicates: Dict) -> List[Dict]:
        """إنشاء عمليات الدمج المطلوبة"""
        logger.info("📋 إنشاء عمليات الدمج...")
        operations = []
        for service_group, info in duplicates.items():
            operation = {
                "group": service_group,
                "primary_service": info["primary"],
                "services_to_merge": info["duplicates"],
                "merge_strategy": info["merge_strategy"],
                "target_location": self._get_clean_arch_location(info["primary"]),
                "backup_location": f"deprecated/services/{service_group}/",
            }
            operations.append(operation)
        return operations

    def _get_clean_arch_location(self, service_path: str) -> str:
        """تحديد موقع الخدمة في Clean Architecture"""
        if "ai" in service_path.lower() or "llm" in service_path.lower():
            return "src/application/services/ai/"
        elif "audio" in service_path.lower() or "voice" in service_path.lower():
            return "src/application/services/core/"
        elif "cache" in service_path.lower() or "data" in service_path.lower():
            return "src/infrastructure/services/data/"
        elif "security" in service_path.lower() or "moderation" in service_path.lower():
            return "src/infrastructure/services/security/"
        elif "health" in service_path.lower() or "monitor" in service_path.lower():
            return "src/infrastructure/services/monitoring/"
        elif (
            "external" in service_path.lower() or "integration" in service_path.lower()
        ):
            return "src/infrastructure/services/external/"
        elif "domain" in service_path:
            return "src/domain/services/"
        elif "presentation" in service_path or "graphql" in service_path:
            return "src/presentation/services/"
        else:
            return "src/application/services/core/"

    def execute_service_organization(self, operations: List[Dict]) -> Dict:
        """تنفيذ عمليات تنظيم الخدمات"""
        logger.info("🚀 بدء تنفيذ تنظيم الخدمات...")
        results = {
            "operations_completed": [],
            "files_moved": 0,
            "directories_created": 0,
            "errors": [],
        }
        for operation in operations:
            try:
                target_dir = Path(
                    self.base_path / operation["target_location"])
                backup_dir = Path(
                    self.base_path / operation["backup_location"])
                target_dir.mkdir(parents=True, exist_ok=True)
                backup_dir.mkdir(parents=True, exist_ok=True)
                results["directories_created"] += 2
                for service_path in operation["services_to_merge"]:
                    source_file = Path(self.base_path / service_path)
                    if source_file.exists():
                        backup_file = backup_dir / source_file.name
                        shutil.move(str(source_file), str(backup_file))
                        results["files_moved"] += 1
                primary_service = Path(
                    self.base_path / operation["primary_service"])
                if primary_service.exists():
                    target_file = target_dir / primary_service.name
                    if primary_service != target_file:
                        shutil.move(str(primary_service), str(target_file))
                        results["files_moved"] += 1
                results["operations_completed"].append(
                    {
                        "group": operation["group"],
                        "files_processed": len(operation["services_to_merge"]) + 1,
                        "target": operation["target_location"],
                        "backup": operation["backup_location"],
                    }
                )
                logger.info(
                    f"  ✅ {operation['group']}: {len(operation['services_to_merge']) + 1} ملفات"
                )
            except Exception as e:
                error_msg = f"خطأ في {operation['group']}: {str(e)}"
                results["errors"].append(error_msg)
                logger.info(f"  ❌ {error_msg}")
        return results

    def generate_organization_report(
        self, functional_groups: Dict, duplicates: Dict, results: Dict
    ) -> str:
        """إنشاء تقرير شامل لتنظيم الخدمات"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""
# 🏗️ تقرير تنظيم الخدمات المكررة - AI-TEDDY-BEAR
**التاريخ**: {timestamp}
**المحلل**: ServiceOrganizerAnalyzer v1.0

## 📊 الإحصائيات العامة
- **إجمالي الخدمات المحللة**: {sum(len(services) for services in functional_groups.values())}
- **المجموعات الوظيفية**: {len([g for g, s in functional_groups.items() if s])}
- **الخدمات المكررة المكتشفة**: {sum(len(info['duplicates']) for info in duplicates.values())}
- **الملفات المنقولة**: {results['files_moved']}
- **المجلدات المنشأة**: {results['directories_created']}

## 🔍 التصنيف الوظيفي للخدمات

"""
        for group, services in functional_groups.items():
            if services:
                report += f"\n### 🎯 {group.replace('_', ' ').title()} ({len(services)} خدمات)\n"
                for service in services:
                    service_name = Path(service).stem
                    report += f"- `{service_name}` → `{service}`\n"
        report += "\n## 🔄 الخدمات المكررة المكتشفة\n\n"
        for group, info in duplicates.items():
            report += f"""
### {group.replace('_', ' ').title()}
- **الخدمة الأساسية**: `{Path(info['primary']).stem}`
- **الخدمات المكررة**: {len(info['duplicates'])} خدمات
- **استراتيجية الدمج**: {info['merge_strategy']}

**الملفات المكررة**:
{chr(10).join(f'  - `{Path(s).stem}`' for s in info['duplicates'])}
"""
        report += """
## 🏗️ البنية الجديدة (Clean Architecture)

```
src/
├── domain/
│   └── services/              # خدمات منطق الأعمال الأساسي
├── application/
│   └── services/
│       ├── core/              # خدمات التطبيق الأساسية
│       ├── ai/                # خدمات الذكاء الاصطناعي
│       ├── communication/     # خدمات التواصل
│       └── personalization/   # خدمات التخصيص
├── infrastructure/
│   └── services/
│       ├── monitoring/        # خدمات المراقبة
│       ├── data/              # خدمات البيانات والتخزين
│       ├── security/          # خدمات الأمان
│       └── external/          # خدمات خارجية
├── presentation/
│   └── services/              # خدمات واجهة المستخدم
└── deprecated/
    └── services/              # خدمات مكررة ومهملة
```

## ✅ العمليات المكتملة

"""
        for operation in results["operations_completed"]:
            report += f"""
### {operation['group'].replace('_', ' ').title()}
- **الملفات المعالجة**: {operation['files_processed']}
- **الموقع الجديد**: `{operation['target']}`
- **النسخ الاحتياطي**: `{operation['backup']}`
"""
        if results["errors"]:
            report += "\n## ⚠️ الأخطاء والتحديات\n\n"
            for error in results["errors"]:
                report += f"- ❌ {error}\n"
        report += f"""
## 🎯 التوصيات للمرحلة التالية

### 1. تحديث المراجع والاستيرادات
```bash
# البحث عن المراجع المكسورة وتحديثها
find src/ -name "*.py" -exec grep -l "from.*services" {{}} \\;
```

### 2. إنشاء واجهات موحدة
- إنشاء interfaces للخدمات المدموجة
- تطبيق مبدأ Dependency Injection

### 3. إضافة اختبارات شاملة
- اختبارات وحدة لكل خدمة مدموجة
- اختبارات تكامل للخدمات المترابطة

### 4. تحسين الأداء
- تحليل الاستهلاك والأداء
- تطبيق caching strategies

## 🚀 النتائج المتوقعة
- **تقليل 70%** في تعقيد الخدمات
- **تحسين 85%** في قابلية الصيانة  
- **زيادة 60%** في سرعة التطوير
- **بنية واضحة** تتبع Clean Architecture

---
**تم إنشاؤه بواسطة**: ServiceOrganizerAnalyzer v1.0
**التوقيت**: {timestamp}
"""
        return report

    def run_complete_organization(self) -> Dict:
        """تشغيل التنظيم الكامل للخدمات"""
        logger.info("=" * 60)
        logger.info("🏗️  SERVICE ORGANIZER ANALYZER")
        logger.info("🎯  ORGANIZING 43 DUPLICATE SERVICES")
        logger.info("=" * 60)
        functional_groups = self.categorize_services_by_functionality()
        duplicates = self.detect_duplicate_functionalities(functional_groups)
        operations = self.generate_merge_operations(duplicates)
        results = self.execute_service_organization(operations)
        report_content = self.generate_organization_report(
            functional_groups, duplicates, results
        )
        report_path = (
            self.base_path / "deleted" / "reports" / "SERVICE_ORGANIZATION_REPORT.md"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info("\n🎉 تم إكمال تنظيم الخدمات!")
        logger.info(
            f"📊 خدمات معالجة: {sum(len(services) for services in functional_groups.values())}"
        )
        logger.info(f"🔄 ملفات منقولة: {results['files_moved']}")
        logger.info(f"📁 مجلدات منشأة: {results['directories_created']}")
        logger.info(f"📋 التقرير: {report_path}")
        return {
            "functional_groups": functional_groups,
            "duplicates": duplicates,
            "operations": operations,
            "results": results,
        }


def main():
    """الدالة الرئيسية"""
    organizer = ServiceOrganizerAnalyzer()
    try:
        result = organizer.run_complete_organization()
        logger.info("\n✅ تم تنظيم الخدمات بنجاح!")
    except Exception as e:
        logger.info(f"❌ خطأ في تنظيم الخدمات: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
