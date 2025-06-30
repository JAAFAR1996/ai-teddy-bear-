#!/usr/bin/env python3
"""
Content Similarity Analyzer
أداة فحص التشابه الفعلي في محتوى الملفات للتحقق من التطابق 100%
"""

import os
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import difflib
import ast

class ContentSimilarityAnalyzer:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "identical_files": [],
            "similar_files": [],
            "unique_files": [],
            "merge_candidates": [],
            "delete_candidates": [],
            "actions_taken": []
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """حساب hash للملف"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"خطأ في حساب hash للملف {file_path}: {e}")
            return ""

    def get_file_content_normalized(self, file_path: Path) -> str:
        """الحصول على محتوى الملف مع تطبيع للمقارنة"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # إزالة التعليقات والمسافات الزائدة للمقارنة الدقيقة
            lines = []
            for line in content.split('\n'):
                # إزالة المسافات الزائدة
                line = line.strip()
                # تجاهل التعليقات والسطور الفارغة
                if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                    lines.append(line)
            
            return '\n'.join(lines)
        except Exception as e:
            print(f"خطأ في قراءة الملف {file_path}: {e}")
            return ""

    def calculate_similarity_percentage(self, content1: str, content2: str) -> float:
        """حساب نسبة التشابه بين محتويين"""
        if not content1 or not content2:
            return 0.0
        
        # استخدام difflib لحساب التشابه
        similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
        return similarity * 100

    def analyze_service_group(self, group_name: str) -> Dict:
        """تحليل مجموعة خدمات محددة"""
        print(f"🔍 تحليل مجموعة: {group_name}")
        
        deprecated_dir = self.base_path / "deprecated" / "services" / group_name
        if not deprecated_dir.exists():
            print(f"  ⚠️ المجلد غير موجود: {deprecated_dir}")
            return {"identical": [], "similar": [], "unique": []}
        
        files = list(deprecated_dir.glob("*.py"))
        if len(files) < 2:
            print(f"  ⚠️ عدد الملفات قليل جداً: {len(files)}")
            return {"identical": [], "similar": [], "unique": list(files)}
        
        results = {
            "identical": [],
            "similar": [], 
            "unique": []
        }
        
        # حساب hash وmحتوى كل ملف
        file_data = {}
        for file_path in files:
            content = self.get_file_content_normalized(file_path)
            file_hash = hashlib.md5(content.encode()).hexdigest()
            file_data[file_path] = {
                "hash": file_hash,
                "content": content,
                "size": len(content)
            }
        
        # مقارنة الملفات
        compared_pairs = set()
        
        for file1 in files:
            for file2 in files:
                if file1 == file2:
                    continue
                
                # تجنب المقارنة المكررة
                pair = tuple(sorted([str(file1), str(file2)]))
                if pair in compared_pairs:
                    continue
                compared_pairs.add(pair)
                
                data1 = file_data[file1]
                data2 = file_data[file2]
                
                # فحص التطابق الكامل (hash)
                if data1["hash"] == data2["hash"]:
                    results["identical"].append({
                        "file1": str(file1),
                        "file2": str(file2),
                        "similarity": 100.0,
                        "action": "delete_duplicate"
                    })
                    print(f"  ✅ متطابق 100%: {file1.name} ↔ {file2.name}")
                
                else:
                    # فحص التشابه
                    similarity = self.calculate_similarity_percentage(data1["content"], data2["content"])
                    
                    if similarity >= 90.0:
                        results["similar"].append({
                            "file1": str(file1),
                            "file2": str(file2),
                            "similarity": similarity,
                            "action": "merge_files"
                        })
                        print(f"  🔄 متشابه {similarity:.1f}%: {file1.name} ↔ {file2.name}")
                    
                    elif similarity >= 70.0:
                        results["similar"].append({
                            "file1": str(file1),
                            "file2": str(file2),
                            "similarity": similarity,
                            "action": "review_merge"
                        })
                        print(f"  📝 مراجعة {similarity:.1f}%: {file1.name} ↔ {file2.name}")
        
        # الملفات الفريدة (لم تجد مطابقة)
        identified_files = set()
        for group in [results["identical"], results["similar"]]:
            for item in group:
                identified_files.add(item["file1"])
                identified_files.add(item["file2"])
        
        for file_path in files:
            if str(file_path) not in identified_files:
                results["unique"].append(str(file_path))
                print(f"  🆕 فريد: {file_path.name}")
        
        return results

    def execute_cleanup_actions(self, group_name: str, analysis: Dict) -> Dict:
        """تنفيذ إجراءات التنظيف"""
        print(f"🚀 تنفيذ إجراءات التنظيف لمجموعة: {group_name}")
        
        actions_taken = {
            "deleted_duplicates": 0,
            "merged_files": 0,
            "files_moved_to_delete": 0,
            "errors": []
        }
        
        # إنشاء مجلد للحذف النهائي
        final_delete_dir = self.base_path / "deleted" / "duplicates" / "final_cleanup" / group_name
        final_delete_dir.mkdir(parents=True, exist_ok=True)
        
        # إنشاء مجلد للدمج
        merge_dir = self.base_path / "deleted" / "duplicates" / "merge_needed" / group_name
        merge_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # معالجة الملفات المتطابقة 100% - نقل للحذف النهائي
            processed_files = set()
            for identical in analysis["identical"]:
                file1_path = Path(identical["file1"])
                file2_path = Path(identical["file2"])
                
                # احتفظ بأحد الملفين، احذف الآخر
                if str(file1_path) not in processed_files and str(file2_path) not in processed_files:
                    # احتفظ بالملف الأول، انقل الثاني للحذف
                    if file2_path.exists():
                        target_file = final_delete_dir / file2_path.name
                        shutil.move(str(file2_path), str(target_file))
                        actions_taken["files_moved_to_delete"] += 1
                        processed_files.add(str(file2_path))
                        print(f"  ✅ نقل للحذف: {file2_path.name}")
                
                elif str(file2_path) not in processed_files:
                    # الملف الأول معالج، انقل الثاني
                    if file2_path.exists():
                        target_file = final_delete_dir / file2_path.name
                        shutil.move(str(file2_path), str(target_file))
                        actions_taken["files_moved_to_delete"] += 1
                        processed_files.add(str(file2_path))
                        print(f"  ✅ نقل للحذف: {file2_path.name}")
            
            # معالجة الملفات المتشابهة - نقل للدمج
            for similar in analysis["similar"]:
                file1_path = Path(similar["file1"])
                file2_path = Path(similar["file2"])
                
                # نقل الملفات المتشابهة لمجلد الدمج للمراجعة اليدوية
                if file1_path.exists() and str(file1_path) not in processed_files:
                    target_file = merge_dir / file1_path.name
                    if not target_file.exists():
                        shutil.copy2(str(file1_path), str(target_file))
                        print(f"  🔄 نسخ للدمج: {file1_path.name}")
                
                if file2_path.exists() and str(file2_path) not in processed_files:
                    target_file = merge_dir / file2_path.name
                    if not target_file.exists():
                        shutil.copy2(str(file2_path), str(target_file))
                        print(f"  🔄 نسخ للدمج: {file2_path.name}")
        
        except Exception as e:
            error_msg = f"خطأ في معالجة {group_name}: {str(e)}"
            actions_taken["errors"].append(error_msg)
            print(f"  ❌ {error_msg}")
        
        return actions_taken

    def generate_detailed_analysis_report(self, all_results: Dict) -> str:
        """إنشاء تقرير تحليل مفصل"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# 🔍 تقرير التحليل التفصيلي للتشابه في المحتوى
**التاريخ**: {timestamp}
**المحلل**: ContentSimilarityAnalyzer v1.0

## 📊 ملخص التحليل الشامل
"""
        
        total_identical = 0
        total_similar = 0
        total_unique = 0
        total_deleted = 0
        total_merged = 0
        
        for group_name, results in all_results.items():
            if 'analysis' in results:
                analysis = results['analysis']
                actions = results.get('actions', {})
                
                total_identical += len(analysis['identical'])
                total_similar += len(analysis['similar'])
                total_unique += len(analysis['unique'])
                total_deleted += actions.get('files_moved_to_delete', 0)
                total_merged += actions.get('merged_files', 0)
        
        report += f"""
- **إجمالي الملفات المتطابقة 100%**: {total_identical} زوج
- **إجمالي الملفات المتشابهة**: {total_similar} زوج  
- **إجمالي الملفات الفريدة**: {total_unique} ملف
- **الملفات المنقولة للحذف النهائي**: {total_deleted} ملف
- **الملفات المعدة للدمج**: {total_merged} ملف

## 🔍 تحليل تفصيلي لكل مجموعة

"""
        
        for group_name, results in all_results.items():
            if 'analysis' not in results:
                continue
                
            analysis = results['analysis']
            actions = results.get('actions', {})
            
            report += f"""
### 📁 مجموعة: {group_name.replace('_', ' ').title()}

#### ✅ الملفات المتطابقة 100% ({len(analysis['identical'])} أزواج)
"""
            for identical in analysis['identical']:
                file1_name = Path(identical['file1']).name
                file2_name = Path(identical['file2']).name
                report += f"- `{file1_name}` ↔ `{file2_name}` (تطابق: {identical['similarity']:.1f}%)\n"
            
            report += f"""
#### 🔄 الملفات المتشابهة ({len(analysis['similar'])} أزواج)
"""
            for similar in analysis['similar']:
                file1_name = Path(similar['file1']).name
                file2_name = Path(similar['file2']).name
                action_text = "دمج مطلوب" if similar['action'] == 'merge_files' else "مراجعة مطلوبة"
                report += f"- `{file1_name}` ↔ `{file2_name}` (تشابه: {similar['similarity']:.1f}%) - {action_text}\n"
            
            report += f"""
#### 🆕 الملفات الفريدة ({len(analysis['unique'])} ملفات)
"""
            for unique in analysis['unique']:
                unique_name = Path(unique).name
                report += f"- `{unique_name}`\n"
            
            report += f"""
#### 🎯 الإجراءات المتخذة
- **ملفات منقولة للحذف النهائي**: {actions.get('files_moved_to_delete', 0)}
- **ملفات مُعدة للدمج**: {actions.get('merged_files', 0)}
- **أخطاء**: {len(actions.get('errors', []))}
"""
            
            if actions.get('errors'):
                report += f"""
##### ⚠️ الأخطاء:
"""
                for error in actions['errors']:
                    report += f"- ❌ {error}\n"
        
        report += f"""
## 📂 المجلدات المنشأة

### 🗑️ للحذف النهائي
```
deleted/duplicates/final_cleanup/
├── ai_services/           # ملفات AI متطابقة 100%
├── audio_services/        # ملفات صوت متطابقة 100% 
├── cache_services/        # ملفات cache متطابقة 100%
└── monitoring_services/   # ملفات مراقبة متطابقة 100%
```

### 🔄 للدمج (مراجعة يدوية مطلوبة)
```
deleted/duplicates/merge_needed/
├── ai_services/           # ملفات AI تحتاج دمج
├── audio_services/        # ملفات صوت تحتاج دمج
├── cache_services/        # ملفات cache تحتاج دمج
└── monitoring_services/   # ملفات مراقبة تحتاج دمج
```

## 🎯 التوصيات النهائية

### ✅ آمن للحذف النهائي
- جميع الملفات في `deleted/duplicates/final_cleanup/` متطابقة 100%
- يمكن حذفها نهائياً بأمان

### 🔄 يحتاج مراجعة ودمج
- جميع الملفات في `deleted/duplicates/merge_needed/` تحتاج مراجعة يدوية
- دمج الميزات الفريدة من كل ملف
- حذف التكرار مع الاحتفاظ بالوظائف المهمة

### 📋 الخطوات التالية
1. **مراجعة ملفات الدمج** - فحص الاختلافات يدوياً
2. **دمج الميزات الفريدة** - نقل الوظائف المهمة
3. **تحديث المراجع** - إصلاح الاستيرادات المكسورة
4. **اختبار شامل** - التأكد من عمل كل شيء

---
**تم إنشاؤه بواسطة**: ContentSimilarityAnalyzer v1.0  
**التوقيت**: {timestamp}
"""
        
        return report

    def run_complete_similarity_analysis(self) -> Dict:
        """تشغيل التحليل الكامل للتشابه"""
        print("=" * 60)
        print("🔍  CONTENT SIMILARITY ANALYZER")
        print("🎯  CHECKING 100% IDENTICAL vs MERGE NEEDED")
        print("=" * 60)
        
        deprecated_services = self.base_path / "deprecated" / "services"
        if not deprecated_services.exists():
            print("❌ مجلد deprecated/services غير موجود!")
            return {}
        
        service_groups = [d.name for d in deprecated_services.iterdir() if d.is_dir()]
        print(f"📁 المجموعات المكتشفة: {service_groups}")
        
        all_results = {}
        
        for group_name in service_groups:
            print(f"\n{'='*40}")
            print(f"📋 معالجة مجموعة: {group_name}")
            print(f"{'='*40}")
            
            # تحليل المحتوى
            analysis = self.analyze_service_group(group_name)
            
            # تنفيذ الإجراءات
            actions = self.execute_cleanup_actions(group_name, analysis)
            
            all_results[group_name] = {
                "analysis": analysis,
                "actions": actions
            }
        
        # إنشاء التقرير
        report_content = self.generate_detailed_analysis_report(all_results)
        report_path = self.base_path / "deleted" / "reports" / "CONTENT_SIMILARITY_ANALYSIS.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n🎉 تم إكمال التحليل التفصيلي!")
        print(f"📋 التقرير: {report_path}")
        
        return all_results

def main():
    """الدالة الرئيسية"""
    analyzer = ContentSimilarityAnalyzer()
    
    try:
        results = analyzer.run_complete_similarity_analysis()
        print(f"\n✅ تم التحليل بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ في التحليل: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()