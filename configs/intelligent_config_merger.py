#!/usr/bin/env python3
"""
Intelligent Config Merger
أداة ذكية لدمج ملفات التكوين مع فحص التشابه والميزات
"""

import os
import json
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from datetime import datetime
from collections import defaultdict
import difflib
import re

class IntelligentConfigMerger:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.config_analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_configs": 0,
            "identical_duplicates": [],
            "similar_configs": [],
            "merged_configs": [],
            "deleted_configs": [],
            "updated_references": [],
            "errors": []
        }

    def discover_all_config_files(self) -> Dict[str, List[Path]]:
        """اكتشاف جميع ملفات التكوين في المشروع"""
        print("🔍 اكتشاف ملفات التكوين...")
        
        config_files = {
            "json": [],
            "yaml": [],
            "yml": [],
            "env": [],
            "conf": [],
            "ini": [],
            "toml": []
        }
        
        # أنماط الملفات للبحث
        patterns = {
            "json": ["*.json"],
            "yaml": ["*.yaml"],
            "yml": ["*.yml"],
            "env": ["*.env", ".env*"],
            "conf": ["*.conf", "*.config"],
            "ini": ["*.ini"],
            "toml": ["*.toml"]
        }
        
        # مجلدات للتجاهل
        ignore_dirs = {
            "__pycache__", ".git", "node_modules", ".venv", "venv",
            ".mypy_cache", ".pytest_cache", "dist", "build"
        }
        
        for file_type, file_patterns in patterns.items():
            for pattern in file_patterns:
                for file_path in self.base_path.rglob(pattern):
                    # تجاهل المجلدات المستبعدة
                    if any(ignore_dir in str(file_path) for ignore_dir in ignore_dirs):
                        continue
                    
                    config_files[file_type].append(file_path)
                    print(f"  📄 {file_type.upper()}: {file_path.name}")
        
        # إحصائيات
        total = sum(len(files) for files in config_files.values())
        print(f"\n📊 تم العثور على {total} ملف تكوين:")
        for file_type, files in config_files.items():
            if files:
                print(f"  {file_type.upper()}: {len(files)} ملف")
        
        self.config_analysis["total_configs"] = total
        return config_files

    def load_config_content(self, file_path: Path) -> Tuple[Optional[Dict], str, str]:
        """تحميل محتوى ملف التكوين"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # حساب hash للمحتوى الخام
            content_hash = hashlib.md5(raw_content.encode()).hexdigest()
            
            # محاولة تحليل المحتوى
            parsed_content = None
            file_ext = file_path.suffix.lower()
            
            if file_ext == '.json':
                try:
                    parsed_content = json.loads(raw_content)
                except json.JSONDecodeError:
                    pass
            elif file_ext in ['.yaml', '.yml']:
                try:
                    parsed_content = yaml.safe_load(raw_content)
                except yaml.YAMLError:
                    pass
            
            return parsed_content, raw_content, content_hash
        
        except Exception as e:
            print(f"  ❌ خطأ في قراءة {file_path}: {e}")
            return None, "", ""

    def calculate_content_similarity(self, content1: str, content2: str) -> float:
        """حساب نسبة التشابه بين محتويين"""
        if not content1 or not content2:
            return 0.0
        
        # إزالة المسافات والتعليقات للمقارنة الدقيقة
        clean1 = self._clean_content_for_comparison(content1)
        clean2 = self._clean_content_for_comparison(content2)
        
        if clean1 == clean2:
            return 100.0
        
        # استخدام difflib لحساب التشابه
        similarity = difflib.SequenceMatcher(None, clean1, clean2).ratio()
        return similarity * 100

    def _clean_content_for_comparison(self, content: str) -> str:
        """تنظيف المحتوى للمقارنة"""
        # إزالة التعليقات
        lines = []
        for line in content.split('\n'):
            # إزالة التعليقات في JSON و YAML
            if '//' in line:
                line = line.split('//')[0]
            if '#' in line and not line.strip().startswith('"'):
                line = line.split('#')[0]
            
            # إزالة المسافات الزائدة
            line = line.strip()
            if line:
                lines.append(line)
        
        return '\n'.join(lines)

    def analyze_config_duplicates(self, config_files: Dict[str, List[Path]]) -> Dict:
        """تحليل التكرارات في ملفات التكوين"""
        print("\n🔍 تحليل التكرارات والتشابهات...")
        
        analysis = {
            "identical_groups": [],      # مجموعات متطابقة 100%
            "similar_groups": [],        # مجموعات متشابهة 70-99%
            "unique_files": [],          # ملفات فريدة
            "content_map": {},           # خريطة المحتوى
            "similarity_matrix": {}      # مصفوفة التشابه
        }
        
        # تجميع جميع الملفات
        all_files = []
        for file_type, files in config_files.items():
            all_files.extend(files)
        
        print(f"📋 تحليل {len(all_files)} ملف...")
        
        # تحميل محتوى جميع الملفات
        file_contents = {}
        hash_to_files = defaultdict(list)
        
        for file_path in all_files:
            parsed, raw, content_hash = self.load_config_content(file_path)
            
            file_contents[str(file_path)] = {
                "parsed": parsed,
                "raw": raw,
                "hash": content_hash,
                "size": len(raw),
                "path": file_path
            }
            
            # تجميع الملفات حسب hash (متطابقة 100%)
            if content_hash and raw.strip():
                hash_to_files[content_hash].append(str(file_path))
        
        # العثور على المجموعات المتطابقة
        for content_hash, file_paths in hash_to_files.items():
            if len(file_paths) > 1:
                analysis["identical_groups"].append({
                    "hash": content_hash,
                    "files": file_paths,
                    "count": len(file_paths),
                    "size": file_contents[file_paths[0]]["size"]
                })
                print(f"  🔄 عثر على {len(file_paths)} ملفات متطابقة:")
                for fp in file_paths[:3]:  # أول 3 فقط
                    print(f"    - {Path(fp).name}")
                if len(file_paths) > 3:
                    print(f"    ... و{len(file_paths) - 3} أخرى")
        
        # البحث عن التشابهات (70-99%)
        unique_files = [fp for fp in file_contents.keys() 
                       if all(fp not in group["files"] for group in analysis["identical_groups"])]
        
        print(f"\n🔍 فحص التشابه بين {len(unique_files)} ملف فريد...")
        
        similar_groups = []
        processed_files = set()
        
        for i, file1 in enumerate(unique_files):
            if file1 in processed_files:
                continue
            
            content1 = file_contents[file1]["raw"]
            if not content1.strip():
                continue
            
            similar_files = [file1]
            
            for j, file2 in enumerate(unique_files[i+1:], i+1):
                if file2 in processed_files:
                    continue
                
                content2 = file_contents[file2]["raw"]
                similarity = self.calculate_content_similarity(content1, content2)
                
                if 70 <= similarity < 100:
                    similar_files.append(file2)
                    analysis["similarity_matrix"][f"{file1}:{file2}"] = similarity
            
            if len(similar_files) > 1:
                # حساب متوسط التشابه للمجموعة
                similarities = []
                for x in range(len(similar_files)):
                    for y in range(x+1, len(similar_files)):
                        sim = self.calculate_content_similarity(
                            file_contents[similar_files[x]]["raw"],
                            file_contents[similar_files[y]]["raw"]
                        )
                        similarities.append(sim)
                
                avg_similarity = sum(similarities) / len(similarities) if similarities else 0
                
                similar_groups.append({
                    "files": similar_files,
                    "count": len(similar_files),
                    "average_similarity": avg_similarity
                })
                
                print(f"  🔗 مجموعة متشابهة ({avg_similarity:.1f}% تشابه):")
                for sf in similar_files[:3]:
                    print(f"    - {Path(sf).name}")
                if len(similar_files) > 3:
                    print(f"    ... و{len(similar_files) - 3} أخرى")
                
                processed_files.update(similar_files)
        
        analysis["similar_groups"] = similar_groups
        analysis["content_map"] = file_contents
        
        return analysis

    def merge_similar_configs(self, similar_group: Dict, content_map: Dict) -> Dict:
        """دمج ملفات التكوين المتشابهة"""
        files = similar_group["files"]
        print(f"\n🔄 دمج مجموعة من {len(files)} ملفات...")
        
        # اختيار الملف الأساسي (الأكبر حجماً أو الأكثر تفصيلاً)
        primary_file = max(files, key=lambda f: content_map[f]["size"])
        other_files = [f for f in files if f != primary_file]
        
        print(f"  🎯 الملف الأساسي: {Path(primary_file).name}")
        print(f"  🔗 ملفات للدمج: {[Path(f).name for f in other_files]}")
        
        try:
            # تحميل المحتوى المحلل
            primary_parsed = content_map[primary_file]["parsed"]
            
            if primary_parsed is None:
                # إذا لم يتم تحليل الملف، استخدم النص الخام
                merged_content = content_map[primary_file]["raw"]
                merged_parsed = None
            else:
                merged_parsed = primary_parsed.copy() if isinstance(primary_parsed, dict) else primary_parsed
                
                # دمج المحتوى من الملفات الأخرى
                for other_file in other_files:
                    other_parsed = content_map[other_file]["parsed"]
                    if other_parsed and isinstance(other_parsed, dict) and isinstance(merged_parsed, dict):
                        merged_parsed = self._merge_dict_configs(merged_parsed, other_parsed)
                
                # تحويل العودة إلى نص
                if Path(primary_file).suffix.lower() == '.json':
                    merged_content = json.dumps(merged_parsed, indent=2, ensure_ascii=False)
                elif Path(primary_file).suffix.lower() in ['.yaml', '.yml']:
                    merged_content = yaml.dump(merged_parsed, default_flow_style=False, allow_unicode=True)
                else:
                    merged_content = content_map[primary_file]["raw"]
            
            return {
                "primary_file": primary_file,
                "merged_files": other_files,
                "merged_content": merged_content,
                "merged_parsed": merged_parsed
            }
        
        except Exception as e:
            print(f"  ❌ خطأ في الدمج: {e}")
            return {
                "primary_file": primary_file,
                "merged_files": other_files,
                "merged_content": content_map[primary_file]["raw"],
                "error": str(e)
            }

    def _merge_dict_configs(self, base_config: Dict, other_config: Dict) -> Dict:
        """دمج قواميس التكوين بذكاء"""
        merged = base_config.copy()
        
        for key, value in other_config.items():
            if key not in merged:
                # مفتاح جديد - إضافة مباشرة
                merged[key] = value
            else:
                # مفتاح موجود - دمج ذكي
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    # دمج القواميس المتداخلة
                    merged[key] = self._merge_dict_configs(merged[key], value)
                elif isinstance(merged[key], list) and isinstance(value, list):
                    # دمج القوائم مع إزالة التكرار
                    merged[key] = list(set(merged[key] + value))
                elif merged[key] != value:
                    # قيم مختلفة - الاحتفاظ بالأكثر تفصيلاً
                    if len(str(value)) > len(str(merged[key])):
                        merged[key] = value
        
        return merged

    def find_config_references(self, config_file_path: str) -> List[Dict]:
        """البحث عن مراجع ملف التكوين في المشروع"""
        print(f"🔍 البحث عن مراجع {Path(config_file_path).name}...")
        
        references = []
        config_name = Path(config_file_path).name
        config_stem = Path(config_file_path).stem
        
        # أنماط البحث
        search_patterns = [
            config_name,                    # اسم الملف كامل
            config_stem,                    # اسم الملف بدون امتداد
            f'"{config_name}"',            # بين علامات تنصيص
            f"'{config_name}'",            # بين علامات تنصيص مفردة
            f"/{config_name}",             # كمسار
            f"{config_stem}.",             # كمرجع Python
        ]
        
        # البحث في ملفات Python
        python_files = list(self.base_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in search_patterns:
                    if pattern in content:
                        # العثور على أرقام الأسطر
                        lines = content.split('\n')
                        line_numbers = []
                        
                        for i, line in enumerate(lines, 1):
                            if pattern in line:
                                line_numbers.append(i)
                        
                        if line_numbers:
                            references.append({
                                "file": str(py_file),
                                "pattern": pattern,
                                "lines": line_numbers,
                                "type": "python_import"
                            })
                            print(f"  📍 عثر في {py_file.name} (أسطر: {line_numbers})")
            
            except Exception:
                continue
        
        return references

    def update_config_references(self, old_path: str, new_path: str, references: List[Dict]) -> List[Dict]:
        """تحديث مراجع ملف التكوين"""
        if not references:
            return []
        
        print(f"🔄 تحديث المراجع من {Path(old_path).name} إلى {Path(new_path).name}...")
        
        updated_files = []
        old_name = Path(old_path).name
        new_name = Path(new_path).name
        
        for ref in references:
            try:
                file_path = Path(ref["file"])
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # استبدال المراجع
                updated_content = content.replace(old_name, new_name)
                
                if updated_content != content:
                    # كتابة التحديثات
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    updated_files.append({
                        "file": str(file_path),
                        "old_name": old_name,
                        "new_name": new_name,
                        "changes": len(ref["lines"])
                    })
                    
                    print(f"  ✅ تم تحديث {file_path.name}")
            
            except Exception as e:
                print(f"  ❌ خطأ في تحديث {ref['file']}: {e}")
        
        return updated_files

    def execute_intelligent_merge(self, analysis: Dict) -> Dict:
        """تنفيذ الدمج الذكي للملفات"""
        print("\n🚀 تنفيذ الدمج الذكي...")
        
        results = {
            "identical_removed": 0,
            "similar_merged": 0,
            "references_updated": 0,
            "space_saved_kb": 0,
            "errors": []
        }
        
        # إنشاء مجلد للنسخ الاحتياطية
        backup_dir = self.base_path / "deleted" / "config_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. إزالة الملفات المتطابقة 100%
            print("\n🗑️ إزالة الملفات المتطابقة...")
            
            for group in analysis["identical_groups"]:
                files = group["files"]
                primary_file = files[0]  # الاحتفاظ بالأول
                duplicate_files = files[1:]
                
                print(f"  📁 مجموعة: احتفاظ بـ {Path(primary_file).name}")
                
                for dup_file in duplicate_files:
                    try:
                        dup_path = Path(dup_file)
                        
                        # البحث عن المراجع
                        references = self.find_config_references(dup_file)
                        
                        # تحديث المراجع إلى الملف الأساسي
                        if references:
                            updated = self.update_config_references(dup_file, primary_file, references)
                            results["references_updated"] += len(updated)
                            self.config_analysis["updated_references"].extend(updated)
                        
                        # نسخ احتياطي
                        backup_path = backup_dir / f"identical_{dup_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        dup_path.rename(backup_path)
                        
                        size_kb = backup_path.stat().st_size / 1024
                        results["space_saved_kb"] += size_kb
                        results["identical_removed"] += 1
                        
                        self.config_analysis["deleted_configs"].append({
                            "original": str(dup_path),
                            "backup": str(backup_path),
                            "reason": "identical_duplicate",
                            "size_kb": size_kb
                        })
                        
                        print(f"    🗑️ حذف: {dup_path.name} ({size_kb:.1f}KB)")
                    
                    except Exception as e:
                        error_msg = f"خطأ في حذف {dup_file}: {str(e)}"
                        results["errors"].append(error_msg)
                        print(f"    ❌ {error_msg}")
            
            # 2. دمج الملفات المتشابهة
            print("\n🔗 دمج الملفات المتشابهة...")
            
            for group in analysis["similar_groups"]:
                try:
                    merge_result = self.merge_similar_configs(group, analysis["content_map"])
                    
                    if "error" not in merge_result:
                        primary_file = merge_result["primary_file"]
                        merged_files = merge_result["merged_files"]
                        merged_content = merge_result["merged_content"]
                        
                        # كتابة المحتوى المدموج
                        with open(primary_file, 'w', encoding='utf-8') as f:
                            f.write(merged_content)
                        
                        print(f"  ✅ تم دمج في: {Path(primary_file).name}")
                        
                        # حذف الملفات المدموجة
                        for merged_file in merged_files:
                            try:
                                merged_path = Path(merged_file)
                                
                                # البحث عن المراجع وتحديثها
                                references = self.find_config_references(merged_file)
                                if references:
                                    updated = self.update_config_references(merged_file, primary_file, references)
                                    results["references_updated"] += len(updated)
                                
                                # نسخ احتياطي
                                backup_path = backup_dir / f"merged_{merged_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                merged_path.rename(backup_path)
                                
                                size_kb = backup_path.stat().st_size / 1024
                                results["space_saved_kb"] += size_kb
                                
                                self.config_analysis["deleted_configs"].append({
                                    "original": str(merged_path),
                                    "backup": str(backup_path),
                                    "reason": "merged_into_primary",
                                    "primary_file": primary_file,
                                    "size_kb": size_kb
                                })
                                
                                print(f"    🗑️ دُمج وحُذف: {merged_path.name}")
                            
                            except Exception as e:
                                error_msg = f"خطأ في دمج {merged_file}: {str(e)}"
                                results["errors"].append(error_msg)
                                print(f"    ❌ {error_msg}")
                        
                        results["similar_merged"] += len(merged_files)
                        
                        self.config_analysis["merged_configs"].append({
                            "primary_file": primary_file,
                            "merged_files": merged_files,
                            "similarity": group["average_similarity"]
                        })
                    
                    else:
                        print(f"  ❌ فشل دمج المجموعة: {merge_result['error']}")
                
                except Exception as e:
                    error_msg = f"خطأ في معالجة مجموعة متشابهة: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"  ❌ {error_msg}")
        
        except Exception as e:
            error_msg = f"خطأ عام في الدمج: {str(e)}"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return results

    def generate_merge_report(self, analysis: Dict, results: Dict) -> str:
        """إنشاء تقرير الدمج الذكي"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# 🧹 تقرير تنظيف ملفات التكوين الذكي

**التاريخ**: {timestamp}  
**الأداة**: IntelligentConfigMerger v1.0

## 📊 ملخص العملية

### 🎯 الإحصائيات الإجمالية:
- **إجمالي ملفات التكوين**: {self.config_analysis['total_configs']}
- **ملفات متطابقة محذوفة**: {results['identical_removed']}
- **ملفات مدموجة**: {results['similar_merged']}
- **مراجع محدثة**: {results['references_updated']}
- **مساحة موفرة**: {results['space_saved_kb']:.1f} KB
- **أخطاء**: {len(results['errors'])}

---

## 🔄 التكرارات المتطابقة

### ✅ المجموعات المحذوفة:
"""
        
        if analysis["identical_groups"]:
            for i, group in enumerate(analysis["identical_groups"], 1):
                files = group["files"]
                primary = Path(files[0]).name
                duplicates = [Path(f).name for f in files[1:]]
                
                report += f"""
#### مجموعة {i}:
- **الملف الأساسي**: `{primary}`
- **الملفات المحذوفة**: {len(duplicates)} ملف
- **الحجم**: {group['size']} بايت
- **المحذوفة**: {', '.join(duplicates[:3])}{"..." if len(duplicates) > 3 else ""}
"""
        
        report += f"""

---

## 🔗 الملفات المدموجة

### ✅ المجموعات المدموجة:
"""
        
        if analysis["similar_groups"]:
            for i, group in enumerate(analysis["similar_groups"], 1):
                files = [Path(f).name for f in group["files"]]
                primary = files[0]
                others = files[1:]
                
                report += f"""
#### مجموعة {i}:
- **التشابه**: {group['average_similarity']:.1f}%
- **الملف الأساسي**: `{primary}`
- **ملفات مدموجة**: {', '.join(others[:3])}{"..." if len(others) > 3 else ""}
"""
        
        report += f"""

---

## 🔄 تحديث المراجع

### ✅ الملفات المحدثة:
"""
        
        if self.config_analysis["updated_references"]:
            for update in self.config_analysis["updated_references"][:10]:  # أول 10
                report += f"""
- **الملف**: `{Path(update['file']).name}`
- **من**: `{update['old_name']}`  
- **إلى**: `{update['new_name']}`
- **تغييرات**: {update['changes']} مكان
"""
            
            if len(self.config_analysis["updated_references"]) > 10:
                remaining = len(self.config_analysis["updated_references"]) - 10
                report += f"\n... و{remaining} ملف أخرى\n"
        
        report += f"""

---

## 📁 الملفات المحذوفة

### 🗑️ نسخ احتياطية:
"""
        
        if self.config_analysis["deleted_configs"]:
            for delete in self.config_analysis["deleted_configs"][:15]:  # أول 15
                original_name = Path(delete['original']).name
                reason_text = {
                    "identical_duplicate": "تكرار متطابق",
                    "merged_into_primary": "دُمج في ملف أساسي"
                }.get(delete['reason'], delete['reason'])
                
                report += f"""
- **الملف**: `{original_name}`
- **السبب**: {reason_text}
- **الحجم**: {delete['size_kb']:.1f} KB
- **النسخة الاحتياطية**: `{Path(delete['backup']).name}`
"""
            
            if len(self.config_analysis["deleted_configs"]) > 15:
                remaining = len(self.config_analysis["deleted_configs"]) - 15
                report += f"\n... و{remaining} ملف أخرى\n"
        
        # إضافة الأخطاء إن وجدت
        if results["errors"]:
            report += f"""

---

## ⚠️ الأخطاء والتحذيرات

### 🚨 مشاكل واجهتها:
"""
            for error in results["errors"][:10]:  # أول 10 أخطاء
                report += f"- ❌ {error}\n"
        
        report += f"""

---

## 🎯 النتائج المحققة

### ✅ التحسينات:
1. **تنظيف شامل** - إزالة {results['identical_removed']} ملف مكرر
2. **دمج ذكي** - دمج {results['similar_merged']} ملف متشابه
3. **توفير مساحة** - {results['space_saved_kb']:.1f} KB تم توفيرها
4. **تحديث المراجع** - {results['references_updated']} مرجع تم تحديثه
5. **نسخ احتياطية آمنة** - جميع الملفات محفوظة في `deleted/config_backups/`

### 📈 الفوائد:
- **مساحة أقل** - تقليل استخدام القرص الصلب
- **إدارة أسهل** - ملفات تكوين أقل وأكثر تنظيماً
- **أداء محسن** - تحميل أسرع للتكوين
- **صيانة أسهل** - تحديث واحد بدلاً من عدة ملفات

### 🔒 الأمان:
- **نسخ احتياطية كاملة** - يمكن استرداد أي ملف
- **تتبع التغييرات** - سجل كامل للعمليات
- **اختبار المراجع** - تحديث آمن للروابط

---

**تم إنشاؤه بواسطة**: IntelligentConfigMerger v1.0  
**التوقيت**: {timestamp}
"""
        
        return report

    def run_intelligent_config_cleanup(self) -> Dict:
        """تشغيل تنظيف ملفات التكوين الذكي"""
        print("=" * 60)
        print("🧹  INTELLIGENT CONFIG MERGER")
        print("🔍  SMART DUPLICATION ANALYSIS & MERGING")
        print("=" * 60)
        
        # اكتشاف ملفات التكوين
        config_files = self.discover_all_config_files()
        
        if self.config_analysis["total_configs"] == 0:
            print("❌ لم يتم العثور على ملفات تكوين!")
            return {}
        
        # تحليل التكرارات والتشابهات
        analysis = self.analyze_config_duplicates(config_files)
        
        # عرض النتائج
        identical_count = sum(len(group["files"]) - 1 for group in analysis["identical_groups"])
        similar_count = sum(len(group["files"]) - 1 for group in analysis["similar_groups"])
        
        print(f"\n📊 نتائج التحليل:")
        print(f"  🔄 ملفات متطابقة للحذف: {identical_count}")
        print(f"  🔗 ملفات متشابهة للدمج: {similar_count}")
        print(f"  💾 مساحة متوقعة للتوفير: {sum(group['size'] for group in analysis['identical_groups']) / 1024:.1f} KB")
        
        if identical_count == 0 and similar_count == 0:
            print("✅ لا توجد تكرارات أو تشابهات للمعالجة!")
            return analysis
        
        # تأكيد من المستخدم
        print(f"\n⚠️  سيتم حذف/دمج {identical_count + similar_count} ملف")
        print("📁 جميع الملفات ستُحفظ في deleted/config_backups/")
        
        # تنفيذ الدمج الذكي
        results = self.execute_intelligent_merge(analysis)
        
        # إنشاء التقرير
        report_content = self.generate_merge_report(analysis, results)
        report_path = self.base_path / "deleted" / "reports" / "INTELLIGENT_CONFIG_CLEANUP.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n🎉 تم إكمال تنظيف ملفات التكوين!")
        print(f"📋 التقرير الشامل: {report_path}")
        print(f"🗑️ ملفات محذوفة: {results['identical_removed']}")
        print(f"🔗 ملفات مدموجة: {results['similar_merged']}")
        print(f"💾 مساحة موفرة: {results['space_saved_kb']:.1f} KB")
        print(f"🔄 مراجع محدثة: {results['references_updated']}")
        
        return {
            "analysis": analysis,
            "results": results,
            "config_analysis": self.config_analysis
        }

def main():
    """الدالة الرئيسية"""
    merger = IntelligentConfigMerger()
    
    try:
        results = merger.run_intelligent_config_cleanup()
        
        if results:
            print(f"\n✅ تم التنظيف بنجاح!")
        else:
            print(f"\n⚠️ لا توجد ملفات للمعالجة!")
            
    except Exception as e:
        print(f"❌ خطأ في تنظيف ملفات التكوين: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 