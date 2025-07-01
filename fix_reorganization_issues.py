#!/usr/bin/env python3
"""
🔧 إصلاح مشاكل إعادة التنظيم
حل المشاكل المكتشفة في مراجعة النتائج وإكمال التنظيم
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class ReorganizationFixer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        
        # المجلدات القديمة التي يجب حذفها
        self.old_service_dirs = [
            "cleanup", "communication", "conversation", "emotion", 
            "enhanced_componentshume_componentsintegration", "esp32", 
            "memory", "moderation", "parent_componentsdashboard", 
            "parentdashboard", "reporting", "streaming"
        ]
        
        # المجلدات الجديدة المنظمة (يجب الاحتفاظ بها)
        self.new_service_dirs = [
            "ai", "audio", "child", "parent", "device", "core"
        ]
    
    def analyze_current_issues(self) -> Dict:
        """تحليل المشاكل الحالية"""
        print("🔍 تحليل المشاكل الحالية...")
        
        issues = {
            "old_directories_remaining": [],
            "migrated_files": [],
            "empty_directories": [],
            "missing_entities": [],
            "total_directories": 0
        }
        
        services_path = self.src_path / "application" / "services"
        
        # فحص المجلدات القديمة المتبقية
        for old_dir in self.old_service_dirs:
            old_path = services_path / old_dir
            if old_path.exists():
                issues["old_directories_remaining"].append(str(old_path))
        
        # البحث عن ملفات migrated
        for root, dirs, files in os.walk(self.src_path):
            for file in files:
                if "_migrated.py" in file:
                    issues["migrated_files"].append(os.path.join(root, file))
        
        # حساب إجمالي المجلدات
        for root, dirs, files in os.walk(self.src_path):
            issues["total_directories"] += len(dirs)
        
        # فحص مجلد الكيانات
        entities_path = self.src_path / "core" / "domain" / "entities"
        if entities_path.exists():
            entity_files = list(entities_path.glob("*.py"))
            if len(entity_files) < 10:
                issues["missing_entities"] = 10 - len(entity_files)
        
        return issues
    
    def cleanup_old_service_directories(self) -> Dict:
        """تنظيف المجلدات القديمة"""
        print("🧹 تنظيف المجلدات القديمة...")
        
        cleanup_results = {
            "directories_removed": [],
            "files_relocated": [],
            "errors": []
        }
        
        services_path = self.src_path / "application" / "services"
        
        for old_dir in self.old_service_dirs:
            old_path = services_path / old_dir
            
            if old_path.exists():
                try:
                    # فحص محتويات المجلد
                    files_in_dir = list(old_path.rglob("*.py"))
                    
                    if files_in_dir:
                        # نقل الملفات المهمة إلى core
                        core_path = services_path / "core"
                        core_path.mkdir(exist_ok=True)
                        
                        for file_path in files_in_dir:
                            if file_path.name != "__init__.py":
                                target_file = core_path / file_path.name
                                
                                # تجنب الكتابة فوق ملف موجود
                                counter = 1
                                while target_file.exists():
                                    stem = file_path.stem
                                    suffix = file_path.suffix
                                    target_file = core_path / f"{stem}_legacy_{counter}{suffix}"
                                    counter += 1
                                
                                shutil.move(str(file_path), str(target_file))
                                cleanup_results["files_relocated"].append(str(target_file))
                    
                    # حذف المجلد القديم
                    shutil.rmtree(old_path)
                    cleanup_results["directories_removed"].append(str(old_path))
                    print(f"  ✅ تم حذف: {old_dir}")
                    
                except Exception as e:
                    cleanup_results["errors"].append(f"خطأ في حذف {old_dir}: {str(e)}")
                    print(f"  ❌ خطأ: {old_dir} - {str(e)}")
        
        return cleanup_results
    
    def consolidate_migrated_files(self) -> Dict:
        """دمج الملفات المكررة (*_migrated.py)"""
        print("🔄 دمج الملفات المكررة...")
        
        consolidation_results = {
            "files_consolidated": [],
            "conflicts_resolved": [],
            "errors": []
        }
        
        # البحث عن ملفات migrated
        for root, dirs, files in os.walk(self.src_path):
            for file in files:
                if "_migrated.py" in file:
                    migrated_file = Path(root) / file
                    original_name = file.replace("_migrated", "")
                    original_file = Path(root) / original_name
                    
                    try:
                        if original_file.exists():
                            # مقارنة الحجم واختيار الأحدث
                            migrated_size = migrated_file.stat().st_size
                            original_size = original_file.stat().st_size
                            
                            if migrated_size > original_size:
                                # الملف المنقول أكبر، استبدال الأصلي
                                original_file.unlink()
                                migrated_file.rename(original_file)
                                consolidation_results["files_consolidated"].append(str(original_file))
                            else:
                                # الملف الأصلي أكبر، حذف المنقول
                                migrated_file.unlink()
                                consolidation_results["conflicts_resolved"].append(str(original_file))
                        else:
                            # لا يوجد أصلي، إعادة تسمية
                            migrated_file.rename(original_file)
                            consolidation_results["files_consolidated"].append(str(original_file))
                        
                        print(f"  ✅ دُمج: {original_name}")
                        
                    except Exception as e:
                        consolidation_results["errors"].append(f"خطأ في دمج {file}: {str(e)}")
                        print(f"  ❌ خطأ: {file} - {str(e)}")
        
        return consolidation_results
    
    def remove_empty_directories(self) -> List[str]:
        """حذف المجلدات الفارغة"""
        print("🗑️ حذف المجلدات الفارغة...")
        
        removed_dirs = []
        
        # البحث عن المجلدات الفارغة من الأسفل للأعلى
        for root, dirs, files in os.walk(self.src_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                
                try:
                    # فحص إذا كان المجلد فارغ (لا يحتوي على ملفات .py)
                    py_files = list(dir_path.glob("*.py"))
                    subdirs = [d for d in dir_path.iterdir() if d.is_dir()]
                    
                    if not py_files and not subdirs:
                        dir_path.rmdir()
                        removed_dirs.append(str(dir_path))
                        print(f"  ✅ حُذف مجلد فارغ: {dir_name}")
                        
                except OSError:
                    # المجلد غير فارغ أو لا يمكن حذفه
                    pass
        
        return removed_dirs
    
    def generate_final_statistics(self) -> Dict:
        """إنشاء إحصائيات نهائية"""
        print("📊 حساب الإحصائيات النهائية...")
        
        stats = {
            "total_directories": 0,
            "service_directories": 0,
            "organized_files": 0,
            "ai_files": 0,
            "improvement_achieved": {}
        }
        
        # حساب إجمالي المجلدات
        for root, dirs, files in os.walk(self.src_path):
            stats["total_directories"] += len(dirs)
        
        # حساب مجلدات الخدمات
        services_path = self.src_path / "application" / "services"
        if services_path.exists():
            service_dirs = [d for d in services_path.iterdir() if d.is_dir()]
            stats["service_directories"] = len(service_dirs)
        
        # حساب ملفات AI المنظمة
        ai_path = services_path / "ai"
        if ai_path.exists():
            ai_files = list(ai_path.glob("*.py"))
            stats["ai_files"] = len(ai_files)
        
        # حساب التحسن
        original_dirs = 261  # العدد الأصلي
        current_dirs = stats["total_directories"]
        improvement = ((original_dirs - current_dirs) / original_dirs) * 100
        
        stats["improvement_achieved"] = {
            "original_directories": original_dirs,
            "current_directories": current_dirs,
            "reduction_percentage": f"{improvement:.1f}%",
            "target_achieved": improvement > 50
        }
        
        return stats
    
    def execute_complete_fix(self) -> Dict:
        """تنفيذ الإصلاح الكامل"""
        print("🚀 بدء الإصلاح الكامل...")
        
        # تحليل المشاكل
        issues = self.analyze_current_issues()
        
        # تنظيف المجلدات القديمة
        cleanup_results = self.cleanup_old_service_directories()
        
        # دمج الملفات المكررة
        consolidation_results = self.consolidate_migrated_files()
        
        # حذف المجلدات الفارغة
        removed_dirs = self.remove_empty_directories()
        
        # الإحصائيات النهائية
        final_stats = self.generate_final_statistics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "issues_found": issues,
            "cleanup_results": cleanup_results,
            "consolidation_results": consolidation_results,
            "removed_empty_dirs": removed_dirs,
            "final_statistics": final_stats,
            "success": True
        }

def main():
    """البرنامج الرئيسي"""
    print("🔧 مرحباً بك في برنامج إصلاح إعادة التنظيم!")
    print("="*60)
    
    fixer = ReorganizationFixer()
    
    try:
        # تحليل المشاكل أولاً
        issues = fixer.analyze_current_issues()
        
        print("\n📋 المشاكل المكتشفة:")
        print(f"- مجلدات قديمة متبقية: {len(issues['old_directories_remaining'])}")
        print(f"- ملفات مكررة (migrated): {len(issues['migrated_files'])}")
        print(f"- إجمالي المجلدات: {issues['total_directories']}")
        
        if issues['missing_entities']:
            print(f"- كيانات مفقودة: {issues['missing_entities']}")
        
        # تأكيد من المستخدم
        response = input("\n🚀 هل تريد إصلاح هذه المشاكل؟ (y/n): ")
        
        if response.lower() == 'y':
            # تنفيذ الإصلاح
            results = fixer.execute_complete_fix()
            
            # عرض النتائج
            print(f"\n✅ تم الإصلاح بنجاح!")
            print(f"📊 النتائج النهائية:")
            print(f"- مجلدات محذوفة: {len(results['cleanup_results']['directories_removed'])}")
            print(f"- ملفات دُمجت: {len(results['consolidation_results']['files_consolidated'])}")
            print(f"- مجلدات فارغة حُذفت: {len(results['removed_empty_dirs'])}")
            
            stats = results['final_statistics']
            print(f"- إجمالي المجلدات الآن: {stats['total_directories']}")
            print(f"- تحسن محقق: {stats['improvement_achieved']['reduction_percentage']}")
            
            # حفظ التقرير
            report_file = "reorganization_fix_report.json"
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"📄 تقرير مفصل في: {report_file}")
            
        else:
            print("❌ تم إلغاء عملية الإصلاح")
            
    except Exception as e:
        print(f"❌ خطأ في الإصلاح: {e}")

if __name__ == "__main__":
    main() 