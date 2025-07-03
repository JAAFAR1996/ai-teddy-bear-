#!/usr/bin/env python3
"""
🧹 Cleanup and Migration Tool - AI Teddy Bear Project
أداة تنظيف الملفات المكررة وتحديث المراجع للبنية الجديدة
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Set

class CleanupMigrator:
    def __init__(self):
        self.duplicate_files = []
        self.updated_imports = []
        self.migration_report = []
        
    def run_cleanup(self):
        """تشغيل عملية التنظيف الشاملة"""
        print("🧹 بدء عملية التنظيف والتحويل...")
        
        # 1. تحديد الملفات المكررة
        self.identify_duplicate_files()
        
        # 2. تحديث المراجع
        self.update_imports()
        
        # 3. حذف الملفات المكررة
        self.remove_duplicate_files()
        
        # 4. تنظيف الملفات الفارغة
        self.cleanup_empty_files()
        
        # 5. تقرير النتائج
        self.generate_report()
        
        print("✅ تم الانتهاء من التنظيف!")
    
    def identify_duplicate_files(self):
        """تحديد الملفات المكررة للحذف"""
        print("🔍 تحديد الملفات المكررة...")
        
        # AI service files to remove (keeping the new unified structure)
        ai_files_to_remove = [
            "src/application/services/ai/ai_service.py",
            "src/application/services/ai/modern_ai_service.py", 
            "src/application/services/ai/refactored_ai_service.py",
            "src/application/services/ai/ai_service_factory.py",
            "src/application/services/ai/llm_service.py",
            "src/application/services/ai/openai_service.py",
            "src/application/services/ai/interfaces/ai_service_interface.py"
        ]
        
        for file_path in ai_files_to_remove:
            if os.path.exists(file_path):
                self.duplicate_files.append(file_path)
                print(f"  📄 مخطط للحذف: {file_path}")
    
    def update_imports(self):
        """تحديث المراجع لاستخدام البنية الجديدة"""
        print("🔄 تحديث المراجع...")
        
        # Import mapping from old to new
        import_mapping = {
            "from src.application.services.ai.ai_service import": "from src.application.services.ai.core import",
            "from src.application.services.ai.modern_ai_service import": "from src.application.services.ai.core import",
            "from src.application.services.ai.refactored_ai_service import": "from src.application.services.ai.core import",
            "from src.application.services.ai.openai_service import": "from src.application.services.ai.providers.openai_provider import OpenAIProvider",
            "from src.application.services.ai.llm_service import": "from src.application.services.ai.core import",
            "from src.application.services.ai.ai_service_factory import": "from src.application.services.ai.core import IAIServiceFactory",
            "from src.application.services.ai.interfaces.ai_service_interface import": "from src.application.services.ai.core import"
        }
        
        # Class name mapping
        class_mapping = {
            "AIService": "IAIService",
            "ModernAIService": "IAIService", 
            "RefactoredAIService": "IAIService",
            "OpenAIService": "OpenAIProvider",
            "LLMService": "IAIService",
            "AIServiceFactory": "IAIServiceFactory",
            "IAIServiceInterface": "IAIService"
        }
        
        # Search for Python files to update
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self.update_file_imports(file_path, import_mapping, class_mapping)
    
    def update_file_imports(self, file_path: str, import_mapping: Dict, class_mapping: Dict):
        """تحديث المراجع في ملف واحد"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update imports
            for old_import, new_import in import_mapping.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    print(f"  📝 تحديث import في {file_path}")
            
            # Update class names
            for old_class, new_class in class_mapping.items():
                pattern = rf'\\b{old_class}\\b'
                if re.search(pattern, content):
                    content = re.sub(pattern, new_class, content)
                    print(f"  🔄 تحديث class {old_class} -> {new_class} في {file_path}")
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.updated_imports.append(file_path)
                
        except Exception as e:
            print(f"❌ خطأ في تحديث {file_path}: {e}")
    
    def remove_duplicate_files(self):
        """حذف الملفات المكررة"""
        print("🗑️ حذف الملفات المكررة...")
        
        for file_path in self.duplicate_files:
            try:
                if os.path.exists(file_path):
                    # Create backup before deletion
                    backup_path = f"{file_path}.backup"
                    shutil.copy2(file_path, backup_path)
                    
                    # Delete the duplicate
                    os.remove(file_path)
                    print(f"  ✅ تم حذف: {file_path}")
                    print(f"  💾 نسخة احتياطية: {backup_path}")
                    
                    self.migration_report.append({
                        "action": "deleted",
                        "file": file_path,
                        "backup": backup_path
                    })
                else:
                    print(f"  ⚠️ الملف غير موجود: {file_path}")
                    
            except Exception as e:
                print(f"❌ خطأ في حذف {file_path}: {e}")
    
    def cleanup_empty_files(self):
        """تنظيف الملفات الفارغة"""
        print("🧹 تنظيف الملفات الفارغة...")
        
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        
                        # Check if file is effectively empty
                        if not content or content == '""' or content == "''":
                            print(f"  🗑️ حذف ملف فارغ: {file_path}")
                            os.remove(file_path)
                            
                    except Exception as e:
                        print(f"❌ خطأ في فحص {file_path}: {e}")
    
    def generate_report(self):
        """إنشاء تقرير التنظيف"""
        print("📊 إنشاء تقرير التنظيف...")
        
        import datetime
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# 🧹 تقرير التنظيف والتحويل
## تاريخ: {current_time}

## الملفات المحذوفة:
"""
        
        for file_path in self.duplicate_files:
            report += f"- ✅ {file_path}\\n"
        
        report += f"""
## الملفات المحدثة:
"""
        
        for file_path in self.updated_imports:
            report += f"- 🔄 {file_path}\\n"
        
        report += f"""
## الإحصائيات:
- الملفات المحذوفة: {len(self.duplicate_files)}
- الملفات المحدثة: {len(self.updated_imports)}
- إجمالي العمليات: {len(self.duplicate_files) + len(self.updated_imports)}

## البنية الجديدة:
```
src/application/services/ai/
├── core/
│   ├── __init__.py          # واردات موحدة
│   ├── interfaces.py        # جميع الواجهات
│   ├── models.py           # جميع النماذج
│   └── enums.py            # جميع الثوابت
├── providers/
│   ├── base_provider.py    # الفئة الأساسية
│   └── openai_provider.py  # مزود OpenAI
```

## الفوائد:
1. ✅ إزالة التكرار الوظيفي
2. ✅ توحيد الواجهات
3. ✅ تنظيم منطقي واضح
4. ✅ الحفاظ على جميع المميزات
5. ✅ سهولة الصيانة والتطوير
"""
        
        with open("cleanup_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("📄 تم إنشاء تقرير التنظيف: cleanup_report.md")


if __name__ == "__main__":
    migrator = CleanupMigrator()
    migrator.run_cleanup() 