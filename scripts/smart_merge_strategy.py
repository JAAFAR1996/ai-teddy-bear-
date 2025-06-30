#!/usr/bin/env python3
"""
Smart Merge Strategy
استراتيجية الدمج الذكي للملفات الفريدة
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

class SmartMergeStrategy:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.merge_plan = {
            "ai_services": {
                "target_file": "src/application/services/ai/unified_ai_service.py",
                "files_to_merge": [
                    "deprecated/services/ai_services/ai_service.py",
                    "deprecated/services/ai_services/llm_service.py", 
                    "deprecated/services/ai_services/llm_service_factory.py",
                    "deprecated/services/ai_services/main_service.py"
                ],
                "special_files": {
                    "deprecated/services/ai_services/edge_ai_integration_service.py": "src/adapters/edge/",
                    "deprecated/services/ai_services/child_domain_service.py": "src/domain/services/",
                    "deprecated/services/ai_services/email_service.py": "src/application/services/communication/",
                    "deprecated/services/ai_services/test_ai_service_integration.py": "tests/integration/"
                }
            },
            "audio_services": {
                "target_file": "src/application/services/core/unified_audio_service.py",
                "files_to_merge": [
                    "deprecated/services/audio_services/voice_service.py",
                    "deprecated/services/audio_services/voice_interaction_service.py",
                    "deprecated/services/audio_services/synthesis_service.py",
                    "deprecated/services/audio_services/transcription_service.py"
                ],
                "special_files": {
                    "deprecated/services/audio_services/azure_speech_to_text_service.py": "src/infrastructure/services/external/",
                    "deprecated/services/audio_services/speech_to_text_service.py": "src/infrastructure/services/external/",
                    "deprecated/services/audio_services/audio_service.py": "src/presentation/services/",
                    "deprecated/services/audio_services/test_voice_service.py": "tests/unit/"
                }
            },
            "cache_services": {
                "target_file": "src/infrastructure/services/data/unified_cache_service.py",
                "files_to_merge": [
                    "deprecated/services/cache_services/cache_service.py",
                    "deprecated/services/cache_services/simple_cache_service.py"
                ]
            },
            "monitoring_services": {
                "target_file": "src/infrastructure/services/monitoring/unified_monitoring_service.py",
                "files_to_merge": [
                    "deprecated/services/monitoring_services/issue_tracker_service.py",
                    "deprecated/services/monitoring_services/rate_monitor_service.py",
                    "deprecated/services/monitoring_services/simple_health_service.py"
                ]
            }
        }

    def analyze_file_content(self, file_path: Path) -> Dict:
        """تحليل محتوى الملف لاستخراج الوظائف والكلاسات"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # استخراج الكلاسات والدوال الرئيسية
            classes = []
            functions = []
            imports = []
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('class '):
                    classes.append(line)
                elif line.startswith('def '):
                    functions.append(line)
                elif line.startswith('from ') or line.startswith('import '):
                    imports.append(line)
            
            return {
                "file_path": str(file_path),
                "content": content,
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "size": len(content)
            }
        
        except Exception as e:
            print(f"خطأ في تحليل {file_path}: {e}")
            return {}

    def create_unified_service(self, service_group: str) -> str:
        """إنشاء خدمة موحدة من عدة ملفات"""
        group_config = self.merge_plan[service_group]
        files_to_merge = group_config["files_to_merge"]
        target_file = group_config["target_file"]
        
        print(f"🔄 إنشاء خدمة موحدة: {target_file}")
        
        # تحليل جميع الملفات
        analyzed_files = []
        for file_path_str in files_to_merge:
            file_path = self.base_path / file_path_str
            if file_path.exists():
                analysis = self.analyze_file_content(file_path)
                if analysis:
                    analyzed_files.append(analysis)
        
        if not analyzed_files:
            return ""
        
        # إنشاء محتوى الملف الموحد
        unified_content = self._generate_unified_content(service_group, analyzed_files)
        
        # إنشاء الملف الموحد
        target_path = self.base_path / target_file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(unified_content)
        
        print(f"  ✅ تم إنشاء: {target_file}")
        return unified_content

    def _generate_unified_content(self, service_group: str, analyzed_files: List[Dict]) -> str:
        """إنشاء محتوى موحد من عدة ملفات"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # جمع جميع الاستيرادات وإزالة التكرار
        all_imports = set()
        all_classes = []
        all_functions = []
        
        for file_data in analyzed_files:
            all_imports.update(file_data.get("imports", []))
            all_classes.extend(file_data.get("classes", []))
            all_functions.extend(file_data.get("functions", []))
        
        # إنشاء اسم الكلاس الموحد
        service_name = service_group.replace('_', ' ').title().replace(' ', '')
        unified_class_name = f"Unified{service_name.replace('Services', 'Service')}"
        
        content = f'''#!/usr/bin/env python3
"""
{unified_class_name}
خدمة موحدة تم دمجها من عدة ملفات منفصلة
تم الإنشاء: {timestamp}
"""

{chr(10).join(sorted(all_imports))}
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class {unified_class_name}:
    """
    خدمة موحدة تجمع وظائف متعددة من:
    {chr(10).join(f"    - {file_data['file_path']}" for file_data in analyzed_files)}
    """
    
    def __init__(self):
        """تهيئة الخدمة الموحدة"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize_components()
    
    def _initialize_components(self):
        """تهيئة المكونات الفرعية"""
        # TODO: تهيئة المكونات من الملفات المدموجة
        pass

'''
        
        # إضافة الوظائف المدموجة
        content += f'''
    # ==========================================
    # الوظائف المدموجة من الملفات المختلفة
    # ==========================================
'''
        
        for i, file_data in enumerate(analyzed_files):
            file_name = Path(file_data['file_path']).name
            content += f'''
    # ----- من {file_name} -----
    
'''
            # إضافة الدوال (مع تعديل بسيط للتوافق)
            for func in file_data.get("functions", []):
                if not func.startswith("def __"):  # تجنب الدوال الخاصة
                    content += f"    {func}\n"
                    content += f"        \"\"\"دالة مدموجة من {file_name}\"\"\"\n"
                    content += f"        # TODO: تنفيذ الدالة من {file_name}\n"
                    content += f"        pass\n\n"
        
        content += f'''
    # ==========================================
    # دوال مساعدة إضافية
    # ==========================================
    
    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة الخدمة الموحدة"""
        return {{
            "service_name": "{unified_class_name}",
            "status": "active",
            "components": self._get_active_components(),
            "merged_from": [
                {chr(10).join(f'                "{Path(file_data["file_path"]).name}",' for file_data in analyzed_files)}
            ]
        }}
    
    def _get_active_components(self) -> List[str]:
        """الحصول على المكونات النشطة"""
        # TODO: تنفيذ منطق فحص المكونات
        return []

# ==========================================
# Factory Pattern للإنشاء
# ==========================================

class {unified_class_name}Factory:
    """مصنع لإنشاء خدمة {unified_class_name}"""
    
    @staticmethod
    def create() -> {unified_class_name}:
        """إنشاء مثيل من الخدمة الموحدة"""
        return {unified_class_name}()
    
    @staticmethod
    def create_with_config(config: Dict[str, Any]) -> {unified_class_name}:
        """إنشاء مثيل مع تكوين مخصص"""
        service = {unified_class_name}()
        # TODO: تطبيق التكوين
        return service

# ==========================================
# Singleton Pattern (اختياري)
# ==========================================

_instance = None

def get_{service_group}_instance() -> {unified_class_name}:
    """الحصول على مثيل وحيد من الخدمة"""
    global _instance
    if _instance is None:
        _instance = {unified_class_name}Factory.create()
    return _instance
'''
        
        return content

    def handle_special_files(self, service_group: str) -> Dict:
        """معالجة الملفات الخاصة (غير المدموجة)"""
        group_config = self.merge_plan[service_group]
        special_files = group_config.get("special_files", {})
        
        results = {"moved_files": 0, "errors": []}
        
        for source_file, target_dir in special_files.items():
            try:
                source_path = self.base_path / source_file
                target_path = self.base_path / target_dir
                
                if source_path.exists():
                    target_path.mkdir(parents=True, exist_ok=True)
                    target_file = target_path / source_path.name
                    
                    shutil.move(str(source_path), str(target_file))
                    results["moved_files"] += 1
                    print(f"  📁 نقل: {source_path.name} → {target_dir}")
            
            except Exception as e:
                error_msg = f"خطأ في نقل {source_file}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"  ❌ {error_msg}")
        
        return results

    def generate_merge_report(self, results: Dict) -> str:
        """إنشاء تقرير الدمج"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# 🔄 تقرير الدمج الذكي للخدمات
**التاريخ**: {timestamp}
**الأداة**: SmartMergeStrategy v1.0

## 📊 ملخص العمليات
- **الخدمات المدموجة**: {len([k for k, v in results.items() if v.get('unified_created')])}
- **الملفات المنقولة**: {sum(v.get('moved_files', 0) for v in results.values())}
- **إجمالي الأخطاء**: {sum(len(v.get('errors', [])) for v in results.values())}

## 🏗️ الخدمات الموحدة المنشأة

"""
        
        for service_group, result in results.items():
            if result.get('unified_created'):
                report += f"""
### {service_group.replace('_', ' ').title()}
- **الملف الموحد**: `{self.merge_plan[service_group]['target_file']}`
- **الملفات المدموجة**: {len(self.merge_plan[service_group]['files_to_merge'])}
- **الملفات المنقولة**: {result.get('moved_files', 0)}
"""
        
        report += f"""
## 🎯 التوصيات للخطوات التالية

### 1. مراجعة الملفات الموحدة
- فحص كل ملف موحد وتنفيذ الدوال المؤقتة
- دمج المنطق الفعلي من الملفات الأصلية
- إزالة التكرار والتنظيف

### 2. تحديث المراجع
```bash
# البحث عن الاستيرادات المكسورة
find src/ -name "*.py" -exec grep -l "from.*services" {{}} \\;
```

### 3. إضافة الاختبارات
- إنشاء اختبارات شاملة للخدمات الموحدة
- اختبار التكامل بين المكونات المدموجة

### 4. التحسين والتنظيف
- إزالة الكود المكرر
- تحسين الأداء
- توثيق الوظائف الجديدة

---
**تم إنشاؤه بواسطة**: SmartMergeStrategy v1.0
**التوقيت**: {timestamp}
"""
        
        return report

    def execute_smart_merge(self) -> Dict:
        """تنفيذ الدمج الذكي الكامل"""
        print("=" * 60)
        print("🔄  SMART MERGE STRATEGY")
        print("🎯  MERGING UNIQUE FILES INTELLIGENTLY")
        print("=" * 60)
        
        results = {}
        
        for service_group in self.merge_plan.keys():
            print(f"\n📋 معالجة: {service_group}")
            print("-" * 40)
            
            # إنشاء الخدمة الموحدة
            unified_content = self.create_unified_service(service_group)
            
            # معالجة الملفات الخاصة
            special_results = self.handle_special_files(service_group)
            
            results[service_group] = {
                "unified_created": bool(unified_content),
                "unified_size": len(unified_content),
                "moved_files": special_results["moved_files"],
                "errors": special_results["errors"]
            }
        
        # إنشاء التقرير
        report_content = self.generate_merge_report(results)
        report_path = self.base_path / "deleted" / "reports" / "SMART_MERGE_REPORT.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n🎉 تم إكمال الدمج الذكي!")
        print(f"📋 التقرير: {report_path}")
        
        return results

def main():
    """الدالة الرئيسية"""
    merger = SmartMergeStrategy()
    
    try:
        results = merger.execute_smart_merge()
        print(f"\n✅ تم الدمج الذكي بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ في الدمج: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 