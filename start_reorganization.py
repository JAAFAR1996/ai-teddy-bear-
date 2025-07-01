#!/usr/bin/env python3
"""
🏗️ AI Teddy Bear - Smart Reorganization Script
سكريبت إعادة التنظيم الذكي للمشروع

المشكلة الحالية:
- 261 مجلد في src/
- 19 مجلد services مختلف
- 16 مجلد persistence مختلف
- تعقيد مدمر للإنتاجية

الحل: إعادة تنظيم تدريجي وذكي
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Set
import json
from datetime import datetime

class SmartReorganizer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        
        # خريطة التنظيم الجديد
        self.new_structure = {
            "core/domain/entities": [],
            "core/domain/value_objects": [],
            "core/domain/services": [],
            "application/services": [],
            "application/use_cases": [],
            "infrastructure/persistence": [],
            "infrastructure/external_services": [],
            "presentation/api": [],
            "adapters/inbound": [],
            "adapters/outbound": []
        }
        
        # نسخ احتياطي
        self.backup_dir = self.project_root / "backup_before_reorganization"
        
    def analyze_current_structure(self) -> Dict:
        """تحليل الهيكل الحالي"""
        print("🔍 تحليل الهيكل الحالي...")
        
        analysis = {
            "total_directories": 0,
            "services_dirs": [],
            "models_dirs": [],
            "persistence_dirs": [],
            "entities_files": [],
            "duplicate_names": {},
            "complexity_score": 0
        }
        
        for root, dirs, files in os.walk(self.src_path):
            analysis["total_directories"] += len(dirs)
            
            for d in dirs:
                full_path = os.path.join(root, d)
                if 'service' in d.lower():
                    analysis["services_dirs"].append(full_path)
                if 'model' in d.lower():
                    analysis["models_dirs"].append(full_path)
                if 'persistence' in d.lower():
                    analysis["persistence_dirs"].append(full_path)
            
            # البحث عن ملفات الكيانات
            for f in files:
                if f.endswith('.py') and any(entity in f.lower() for entity in 
                    ['child', 'parent', 'conversation', 'device', 'session', 'user']):
                    analysis["entities_files"].append(os.path.join(root, f))
        
        # حساب درجة التعقيد
        analysis["complexity_score"] = (
            analysis["total_directories"] + 
            len(analysis["services_dirs"]) * 2 + 
            len(analysis["persistence_dirs"]) * 2
        )
        
        return analysis
    
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        print("💾 إنشاء نسخة احتياطية...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        shutil.copytree(self.src_path, self.backup_dir / "src")
        
        backup_info = {
            "timestamp": datetime.now().isoformat(),
            "original_structure": str(self.src_path),
            "backup_location": str(self.backup_dir)
        }
        
        with open(self.backup_dir / "backup_info.json", 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        print(f"✅ تم إنشاء النسخة الاحتياطية في: {self.backup_dir}")
    
    def identify_core_entities(self) -> List[Path]:
        """تحديد الكيانات الأساسية"""
        print("🎯 تحديد الكيانات الأساسية...")
        
        entity_files = []
        entity_patterns = [
            'child', 'parent', 'conversation', 'device', 'session', 
            'user', 'teddy', 'voice', 'audio', 'message'
        ]
        
        for root, dirs, files in os.walk(self.src_path):
            for file in files:
                if file.endswith('.py'):
                    file_lower = file.lower()
                    if any(pattern in file_lower for pattern in entity_patterns):
                        # تجنب test files
                        if 'test' not in file_lower:
                            entity_files.append(Path(root) / file)
        
        return entity_files
    
    def consolidate_services(self) -> Dict[str, List[Path]]:
        """توحيد الخدمات"""
        print("🔧 توحيد الخدمات...")
        
        services_map = {
            "ai_services": [],
            "audio_services": [],
            "child_services": [],
            "parent_services": [],
            "device_services": [],
            "notification_services": []
        }
        
        for root, dirs, files in os.walk(self.src_path):
            for file in files:
                if file.endswith('.py') and 'service' in file.lower():
                    file_path = Path(root) / file
                    file_lower = file.lower()
                    
                    if any(ai_term in file_lower for ai_term in ['ai', 'openai', 'gpt', 'llm']):
                        services_map["ai_services"].append(file_path)
                    elif any(audio_term in file_lower for audio_term in ['audio', 'voice', 'speech', 'tts', 'stt']):
                        services_map["audio_services"].append(file_path)
                    elif 'child' in file_lower:
                        services_map["child_services"].append(file_path)
                    elif 'parent' in file_lower:
                        services_map["parent_services"].append(file_path)
                    elif any(device_term in file_lower for device_term in ['device', 'esp32', 'hardware']):
                        services_map["device_services"].append(file_path)
                    elif any(notif_term in file_lower for notif_term in ['notification', 'alert', 'message']):
                        services_map["notification_services"].append(file_path)
        
        return services_map
    
    def generate_reorganization_plan(self) -> Dict:
        """إنشاء خطة إعادة التنظيم"""
        print("📋 إنشاء خطة إعادة التنظيم...")
        
        analysis = self.analyze_current_structure()
        entities = self.identify_core_entities()
        services = self.consolidate_services()
        
        plan = {
            "current_state": analysis,
            "phase_1_entities": {
                "target_dir": "src/core/domain/entities/",
                "files_to_move": [str(f) for f in entities[:10]]  # أول 10 ملفات
            },
            "phase_2_services": {
                "target_dirs": {
                    "src/application/services/ai/": [str(f) for f in services["ai_services"]],
                    "src/application/services/audio/": [str(f) for f in services["audio_services"]],
                    "src/application/services/child/": [str(f) for f in services["child_services"]]
                }
            },
            "phase_3_infrastructure": {
                "target_dir": "src/infrastructure/persistence/",
                "files_to_consolidate": analysis["persistence_dirs"]
            },
            "estimated_improvement": {
                "directories_reduction": f"{analysis['total_directories']} → ~40 (-{((analysis['total_directories'] - 40) / analysis['total_directories'] * 100):.0f}%)",
                "services_consolidation": f"{len(analysis['services_dirs'])} → 6 مجلدات",
                "maintenance_improvement": "60% تحسن في سهولة الصيانة"
            }
        }
        
        return plan
    
    def execute_phase_1_entities(self, plan: Dict):
        """تنفيذ المرحلة الأولى - نقل الكيانات"""
        print("🚀 تنفيذ المرحلة الأولى - نقل الكيانات...")
        
        target_dir = Path(plan["phase_1_entities"]["target_dir"])
        target_dir.mkdir(parents=True, exist_ok=True)
        
        moved_count = 0
        for file_path in plan["phase_1_entities"]["files_to_move"]:
            src_file = Path(file_path)
            if src_file.exists():
                target_file = target_dir / src_file.name
                
                # تجنب الكتابة فوق ملف موجود
                if target_file.exists():
                    target_file = target_dir / f"{src_file.stem}_migrated{src_file.suffix}"
                
                shutil.move(str(src_file), str(target_file))
                moved_count += 1
                print(f"  ✅ نُقل: {src_file.name}")
        
        print(f"🎯 تم نقل {moved_count} ملف كيان إلى: {target_dir}")
    
    def generate_summary_report(self, plan: Dict) -> str:
        """إنشاء تقرير ملخص"""
        report = f"""
# 📊 تقرير إعادة التنظيم - AI Teddy Bear

## الوضع قبل التنظيم:
- إجمالي المجلدات: {plan['current_state']['total_directories']}
- مجلدات Services: {len(plan['current_state']['services_dirs'])}
- مجلدات Persistence: {len(plan['current_state']['persistence_dirs'])}
- درجة التعقيد: {plan['current_state']['complexity_score']}

## التحسينات المتوقعة:
{plan['estimated_improvement']['directories_reduction']}
- {plan['estimated_improvement']['services_consolidation']}
- {plan['estimated_improvement']['maintenance_improvement']}

## الخطوات المنفذة:
✅ تم إنشاء نسخة احتياطية
✅ تم تحليل الهيكل الحالي
✅ تم نقل الكيانات الأساسية
⏳ باقي المراحل: Services، Infrastructure، Presentation

## التوصيات التالية:
1. تنفيذ المرحلة الثانية (Services)
2. تنظيف Infrastructure
3. تحديث جميع imports
4. اختبار النظام

تم إنشاء التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report

def main():
    """البرنامج الرئيسي"""
    print("🏗️ مرحباً بك في إعادة التنظيم الذكي لـ AI Teddy Bear!")
    print("="*60)
    
    reorganizer = SmartReorganizer()
    
    try:
        # إنشاء نسخة احتياطية
        reorganizer.create_backup()
        
        # إنشاء خطة التنظيم
        plan = reorganizer.generate_reorganization_plan()
        
        # عرض الخطة
        print("\n📋 خطة إعادة التنظيم:")
        print(f"- الكيانات للنقل: {len(plan['phase_1_entities']['files_to_move'])} ملف")
        print(f"- تقليل المجلدات: {plan['estimated_improvement']['directories_reduction']}")
        
        # تأكيد من المستخدم
        response = input("\n🚀 هل تريد بدء التنفيذ؟ (y/n): ")
        
        if response.lower() == 'y':
            # تنفيذ المرحلة الأولى
            reorganizer.execute_phase_1_entities(plan)
            
            # إنشاء التقرير
            report = reorganizer.generate_summary_report(plan)
            
            # حفظ التقرير
            report_file = "reorganization_report.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\n✅ تم إنهاء المرحلة الأولى بنجاح!")
            print(f"📄 تقرير مفصل في: {report_file}")
            print("\n🎯 الخطوات التالية:")
            print("1. مراجعة النتائج")
            print("2. تشغيل المرحلة الثانية (Services)")
            print("3. تحديث imports")
            
        else:
            print("❌ تم إلغاء العملية")
            
    except Exception as e:
        print(f"❌ خطأ في التنفيذ: {e}")
        print("💾 النسخة الاحتياطية متوفرة في: backup_before_reorganization/")

if __name__ == "__main__":
    main() 