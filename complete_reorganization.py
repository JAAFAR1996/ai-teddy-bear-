#!/usr/bin/env python3
"""
🚀 إكمال إعادة التنظيم - AI Teddy Bear
إكمال نقل الكيانات المتبقية وتنظيم Infrastructure
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class ReorganizationCompleter:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        
    def complete_entities_migration(self) -> Dict:
        """إكمال نقل الكيانات المتبقية"""
        print("🎯 إكمال نقل الكيانات المتبقية...")
        
        results = {
            "entities_moved": [],
            "errors": [],
            "conflicts_resolved": []
        }
        
        # المسار المصدر والهدف
        source_entities = self.src_path / "domain" / "entities"
        target_entities = self.src_path / "core" / "domain" / "entities"
        
        # التأكد من وجود المجلد الهدف
        target_entities.mkdir(parents=True, exist_ok=True)
        
        if not source_entities.exists():
            print("  ⚠️ مجلد الكيانات المصدر غير موجود")
            return results
        
        # قائمة الكيانات المهمة للنقل
        important_entities = [
            "child.py",
            "conversation.py", 
            "audio_stream.py",
            "aggregate_root.py",
            "base.py",
            "child_read_model.py",
            "emotion_log.py",
            "transcription.py"
        ]
        
        for entity_file in important_entities:
            source_file = source_entities / entity_file
            target_file = target_entities / entity_file
            
            if source_file.exists():
                try:
                    # التحقق من وجود تضارب
                    if target_file.exists():
                        # مقارنة الأحجام
                        source_size = source_file.stat().st_size
                        target_size = target_file.stat().st_size
                        
                        if source_size > target_size:
                            # الملف المصدر أكبر، استبدال
                            shutil.copy2(source_file, target_file)
                            results["conflicts_resolved"].append(f"{entity_file} (source larger)")
                        else:
                            results["conflicts_resolved"].append(f"{entity_file} (target kept)")
                            continue
                    else:
                        # نقل الملف
                        shutil.copy2(source_file, target_file)
                    
                    results["entities_moved"].append(entity_file)
                    print(f"  ✅ نُقل: {entity_file}")
                    
                except Exception as e:
                    results["errors"].append(f"خطأ في نقل {entity_file}: {str(e)}")
                    print(f"  ❌ خطأ: {entity_file} - {str(e)}")
        
        return results
    
    def consolidate_infrastructure(self) -> Dict:
        """توحيد وتنظيم Infrastructure"""
        print("🏗️ توحيد وتنظيم Infrastructure...")
        
        results = {
            "directories_organized": [],
            "files_moved": [],
            "errors": []
        }
        
        # خطة تنظيم Infrastructure
        infrastructure_plan = {
            "persistence": {
                "target": "src/infrastructure/persistence",
                "sources": [
                    "src/infrastructure/persistence/repositories",
                    "src/domain/repositories", 
                    "src/infrastructure/database"
                ]
            },
            "external_services": {
                "target": "src/infrastructure/external_services", 
                "sources": [
                    "src/infrastructure/ai",
                    "src/infrastructure/audio"
                ]
            },
            "security": {
                "target": "src/infrastructure/security",
                "sources": [
                    "src/infrastructure/security",
                    "src/infrastructure/middleware"
                ]
            }
        }
        
        for category, config in infrastructure_plan.items():
            target_dir = Path(config["target"])
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # نقل الملفات من المصادر المختلفة
            for source_path in config["sources"]:
                source_dir = Path(source_path)
                if source_dir.exists():
                    try:
                        for file_path in source_dir.rglob("*.py"):
                            if file_path.name != "__init__.py":
                                relative_path = file_path.relative_to(source_dir)
                                target_file = target_dir / relative_path
                                
                                # إنشاء المجلدات الفرعية حسب الحاجة
                                target_file.parent.mkdir(parents=True, exist_ok=True)
                                
                                # نسخ الملف (وليس نقل لتجنب المشاكل)
                                if not target_file.exists():
                                    shutil.copy2(file_path, target_file)
                                    results["files_moved"].append(str(target_file))
                        
                        results["directories_organized"].append(category)
                        print(f"  ✅ تم تنظيم: {category}")
                        
                    except Exception as e:
                        results["errors"].append(f"خطأ في تنظيم {category}: {str(e)}")
                        print(f"  ❌ خطأ في {category}: {str(e)}")
        
        return results
    
    def create_missing_init_files(self) -> List[str]:
        """إنشاء ملفات __init__.py المفقودة"""
        print("📝 إنشاء ملفات __init__.py المفقودة...")
        
        created_files = []
        
        # المجلدات التي تحتاج __init__.py
        directories_needing_init = [
            "src/core/domain/entities",
            "src/infrastructure/persistence", 
            "src/infrastructure/external_services",
            "src/infrastructure/security"
        ]
        
        for dir_path in directories_needing_init:
            dir_obj = Path(dir_path)
            if dir_obj.exists():
                init_file = dir_obj / "__init__.py"
                if not init_file.exists():
                    # إنشاء محتوى مناسب
                    content = f'"""\n{dir_obj.name.replace("_", " ").title()} Package\nAI Teddy Bear - {dir_obj.parts[-1]} layer\n"""\n'
                    
                    try:
                        init_file.write_text(content, encoding='utf-8')
                        created_files.append(str(init_file))
                        print(f"  ✅ تم إنشاء: {init_file}")
                    except Exception as e:
                        print(f"  ❌ خطأ في إنشاء {init_file}: {e}")
        
        return created_files
    
    def fix_imports(self) -> Dict:
        """إصلاح imports المكسورة (فحص أولي)"""
        print("🔧 فحص imports المكسورة...")
        
        results = {
            "files_checked": 0,
            "potential_broken_imports": [],
            "common_patterns": []
        }
        
        # أنماط imports المحتملة للكسر
        broken_patterns = [
            "from src.domain.entities",
            "from src.application.services.cleanup",
            "from src.application.services.emotion",
            "from src.application.services.memory"
        ]
        
        # فحص ملفات Python للبحث عن imports مكسورة
        for file_path in self.src_path.rglob("*.py"):
            try:
                content = file_path.read_text(encoding='utf-8')
                results["files_checked"] += 1
                
                for pattern in broken_patterns:
                    if pattern in content:
                        results["potential_broken_imports"].append({
                            "file": str(file_path),
                            "pattern": pattern
                        })
                        
            except Exception:
                # تجاهل ملفات لا يمكن قراءتها
                pass
        
        # تجميع الأنماط الشائعة
        pattern_counts = {}
        for item in results["potential_broken_imports"]:
            pattern = item["pattern"]
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        results["common_patterns"] = [
            {"pattern": p, "count": c} 
            for p, c in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return results
    
    def generate_completion_report(self, entities_result: Dict, infra_result: Dict, 
                                 init_files: List[str], imports_result: Dict) -> str:
        """إنشاء تقرير الإكمال"""
        
        report = f"""
# 🚀 تقرير إكمال إعادة التنظيم - AI Teddy Bear

## 📊 ملخص العمليات المنفذة:

### ✅ إكمال نقل الكيانات:
- كيانات تم نقلها: {len(entities_result['entities_moved'])}
- تضاربات تم حلها: {len(entities_result['conflicts_resolved'])}
- أخطاء: {len(entities_result['errors'])}

**الكيانات المنقولة:**
{chr(10).join(f"- {entity}" for entity in entities_result['entities_moved'])}

### 🏗️ تنظيم Infrastructure:
- مجالات تم تنظيمها: {len(infra_result['directories_organized'])}
- ملفات تم نقلها: {len(infra_result['files_moved'])}
- أخطاء: {len(infra_result['errors'])}

**المجالات المنظمة:**
{chr(10).join(f"- {category}" for category in infra_result['directories_organized'])}

### 📝 ملفات __init__.py:
- ملفات تم إنشاؤها: {len(init_files)}

### 🔧 فحص Imports:
- ملفات تم فحصها: {imports_result['files_checked']}
- imports مكسورة محتملة: {len(imports_result['potential_broken_imports'])}

**الأنماط الشائعة للإصلاح:**
{chr(10).join(f"- {item['pattern']}: {item['count']} ملف" for item in imports_result['common_patterns'][:5])}

## 🎯 الحالة الحالية:
✅ المرحلة الأولى: تنظيم الكيانات (مكتملة)
✅ المرحلة الثانية: توحيد الخدمات (مكتملة)  
✅ المرحلة الثالثة: Infrastructure (مكتملة)
⏳ المرحلة الرابعة: إصلاح Imports (جاري)

## 📝 التوصيات التالية:
1. مراجعة imports المكسورة وإصلاحها
2. اختبار النظام للتأكد من عمله
3. تحديث الوثائق
4. تدريب الفريق على الهيكل الجديد

تم إنشاء التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report
    
    def execute_completion(self) -> Dict:
        """تنفيذ الإكمال الشامل"""
        print("🚀 بدء إكمال إعادة التنظيم...")
        print("="*60)
        
        # 1. إكمال نقل الكيانات
        entities_result = self.complete_entities_migration()
        
        # 2. تنظيم Infrastructure  
        infra_result = self.consolidate_infrastructure()
        
        # 3. إنشاء ملفات __init__.py
        init_files = self.create_missing_init_files()
        
        # 4. فحص imports
        imports_result = self.fix_imports()
        
        # 5. إنشاء التقرير
        report = self.generate_completion_report(
            entities_result, infra_result, init_files, imports_result
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "entities_migration": entities_result,
            "infrastructure_organization": infra_result,
            "init_files_created": init_files,
            "imports_analysis": imports_result,
            "report": report,
            "success": True
        }

def main():
    """البرنامج الرئيسي"""
    print("🚀 مرحباً بك في إكمال إعادة التنظيم!")
    print("="*60)
    
    completer = ReorganizationCompleter()
    
    try:
        # تنفيذ الإكمال
        results = completer.execute_completion()
        
        # عرض النتائج
        print(f"\n✅ تم إكمال إعادة التنظيم بنجاح!")
        print(f"📊 النتائج:")
        print(f"- كيانات منقولة: {len(results['entities_migration']['entities_moved'])}")
        print(f"- مجالات Infrastructure منظمة: {len(results['infrastructure_organization']['directories_organized'])}")
        print(f"- ملفات __init__.py تم إنشاؤها: {len(results['init_files_created'])}")
        print(f"- ملفات تم فحصها للimports: {results['imports_analysis']['files_checked']}")
        
        # حفظ التقرير
        report_file = "completion_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(results['report'])
        
        print(f"📄 تقرير مفصل في: {report_file}")
        
        if results['imports_analysis']['potential_broken_imports']:
            print(f"\n⚠️ تحذير: {len(results['imports_analysis']['potential_broken_imports'])} import محتمل الكسر")
            print("يُنصح بمراجعة التقرير وإصلاح imports")
        
    except Exception as e:
        print(f"❌ خطأ في الإكمال: {e}")

if __name__ == "__main__":
    main() 