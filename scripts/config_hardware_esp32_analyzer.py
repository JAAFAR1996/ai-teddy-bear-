#!/usr/bin/env python3
"""
أداة فحص وتحليل مجلدات config، hardware، و esp32
"""

import os
import hashlib
import difflib
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FileAnalysis:
    """تحليل تفصيلي للملف"""
    path: str
    size: int
    hash_sha256: str
    file_type: str
    category: str
    content_preview: str
    is_generated: bool = False

class ConfigHardwareESP32Analyzer:
    """محلل متقدم للمجلدات الثلاثة"""
    
    def __init__(self):
        self.target_dirs = ["config", "hardware", "esp32"]
        self.deleted_dir = Path("deleted/duplicates")
        self.reports_dir = Path("deleted/reports")
        
        self.file_registry: Dict[str, FileAnalysis] = {}
        self.duplicates: Dict[str, List[str]] = defaultdict(list)
        self.similar_files: List[Tuple[str, str, float]] = []
        self.cleanup_candidates: List[str] = []
        self.merged_files: List[Dict] = []
        
    def ensure_directories(self) -> None:
        """إنشاء المجلدات المطلوبة"""
        self.deleted_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"تم إنشاء المجلدات: {self.deleted_dir}, {self.reports_dir}")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """حساب هاش SHA256 للملف"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"خطأ في قراءة {file_path}: {e}")
            return ""
    
    def scan_all_directories(self) -> None:
        """مسح جميع المجلدات المحددة"""
        logger.info(f"بدء مسح المجلدات: {self.target_dirs}")
        
        for dir_name in self.target_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                logger.warning(f"المجلد غير موجود: {dir_name}")
                continue
                
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    try:
                        # تحديد الملفات المولدة للحذف (.pyc)
                        if file_path.suffix in ['.pyc', '.pyo'] or '__pycache__' in str(file_path):
                            self.cleanup_candidates.append(str(file_path))
                            continue
                        
                        file_hash = self.calculate_file_hash(file_path)
                        content_preview = self.get_content_preview(file_path)
                        stat = file_path.stat()
                        
                        analysis = FileAnalysis(
                            path=str(file_path),
                            size=stat.st_size,
                            hash_sha256=file_hash,
                            file_type=file_path.suffix.lower(),
                            category=dir_name,
                            content_preview=content_preview
                        )
                        
                        self.file_registry[str(file_path)] = analysis
                        
                    except Exception as e:
                        logger.error(f"خطأ في معالجة {file_path}: {e}")
        
        logger.info(f"تم مسح {len(self.file_registry)} ملف")
    
    def get_content_preview(self, file_path: Path, max_lines: int = 5) -> str:
        """استخراج معاينة من محتوى الملف"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:max_lines]
            return ''.join(lines).strip()
        except Exception:
            return ""
    
    def find_exact_duplicates(self) -> None:
        """البحث عن الملفات المتطابقة تماماً"""
        logger.info("البحث عن الملفات المتطابقة...")
        
        hash_groups = defaultdict(list)
        for file_path, analysis in self.file_registry.items():
            if analysis.hash_sha256:
                hash_groups[analysis.hash_sha256].append(file_path)
        
        duplicate_count = 0
        for hash_value, file_paths in hash_groups.items():
            if len(file_paths) > 1:
                self.duplicates[hash_value] = file_paths
                duplicate_count += len(file_paths) - 1
                logger.info(f"ملفات متطابقة: {file_paths}")
        
        logger.info(f"وُجدت {duplicate_count} ملف مكرر")
    
    def find_similar_files(self, similarity_threshold: float = 0.80) -> None:
        """البحث عن الملفات المشابهة"""
        logger.info("البحث عن الملفات المشابهة...")
        
        file_paths = list(self.file_registry.keys())
        similar_count = 0
        
        for i, path1 in enumerate(file_paths):
            for path2 in file_paths[i+1:]:
                if self._should_compare_files(path1, path2):
                    similarity = self._calculate_similarity(path1, path2)
                    if similarity >= similarity_threshold:
                        self.similar_files.append((path1, path2, similarity))
                        similar_count += 1
                        logger.info(f"ملفات مشابهة ({similarity:.1%}): {path1} <-> {path2}")
        
        logger.info(f"وُجدت {similar_count} زوج من الملفات المشابهة")
    
    def _should_compare_files(self, path1: str, path2: str) -> bool:
        """تحديد ما إذا كان يجب مقارنة الملفين"""
        analysis1 = self.file_registry[path1]
        analysis2 = self.file_registry[path2]
        
        # نفس نوع الملف
        if analysis1.file_type != analysis2.file_type:
            return False
        
        # تجاهل الملفات الصغيرة جداً
        if analysis1.size < 100 or analysis2.size < 100:
            return False
        
        return True
    
    def _calculate_similarity(self, path1: str, path2: str) -> float:
        """حساب نسبة التشابه بين ملفين"""
        try:
            with open(path1, 'r', encoding='utf-8', errors='ignore') as f1:
                content1 = f1.read()
            with open(path2, 'r', encoding='utf-8', errors='ignore') as f2:
                content2 = f2.read()
            
            return difflib.SequenceMatcher(None, content1, content2).ratio()
        except Exception as e:
            logger.warning(f"خطأ في مقارنة {path1} و {path2}: {e}")
            return 0.0
    
    def cleanup_generated_files(self) -> None:
        """حذف الملفات المولدة تلقائياً"""
        logger.info("حذف الملفات المولدة تلقائياً...")
        
        cleaned_count = 0
        for file_path in self.cleanup_candidates:
            try:
                path_obj = Path(file_path)
                if path_obj.exists():
                    if path_obj.is_file():
                        path_obj.unlink()
                    elif path_obj.is_dir():
                        shutil.rmtree(path_obj)
                    cleaned_count += 1
                    logger.info(f"تم حذف: {file_path}")
            except Exception as e:
                logger.error(f"خطأ في حذف {file_path}: {e}")
        
        logger.info(f"تم حذف {cleaned_count} ملف مولد")
    
    def move_exact_duplicates(self) -> None:
        """نقل الملفات المتطابقة إلى deleted/duplicates"""
        logger.info("نقل الملفات المتطابقة...")
        
        moved_count = 0
        for hash_value, file_paths in self.duplicates.items():
            if len(file_paths) > 1:
                # الاحتفاظ بأحدث ملف، نقل الباقي
                newest_file = max(file_paths, key=lambda p: Path(p).stat().st_mtime)
                
                for file_path in file_paths:
                    if file_path != newest_file:
                        try:
                            source_path = Path(file_path)
                            relative_path = source_path
                            dest_path = self.deleted_dir / relative_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            dest_path = dest_path.with_name(f"{dest_path.stem}_duplicate_{timestamp}{dest_path.suffix}")
                            
                            shutil.move(str(source_path), str(dest_path))
                            moved_count += 1
                            logger.info(f"تم نقل: {file_path} -> {dest_path}")
                            
                        except Exception as e:
                            logger.error(f"خطأ في نقل {file_path}: {e}")
        
        logger.info(f"تم نقل {moved_count} ملف متطابق")
    
    def merge_similar_files(self) -> None:
        """دمج الملفات المشابهة حسب النوع"""
        logger.info("دمج الملفات المشابهة...")
        
        for path1, path2, similarity in self.similar_files:
            try:
                analysis1 = self.file_registry[path1]
                merged_content = None
                
                # تحديد نوع الدمج حسب فئة الملف
                if analysis1.file_type == '.json':
                    merged_content = self._merge_json_files(path1, path2)
                elif analysis1.file_type in ['.py', '.cpp', '.ino', '.h']:
                    merged_content = self._merge_code_files(path1, path2)
                elif analysis1.file_type in ['.md', '.txt']:
                    merged_content = self._merge_doc_files(path1, path2)
                
                if merged_content:
                    # تحديد الملف الرئيسي (الأحدث)
                    primary_file = path1 if Path(path1).stat().st_mtime > Path(path2).stat().st_mtime else path2
                    secondary_file = path2 if primary_file == path1 else path1
                    
                    # كتابة المحتوى المدموج
                    with open(primary_file, 'w', encoding='utf-8') as f:
                        f.write(merged_content)
                    
                    # أرشفة الملف الثانوي
                    self._archive_merged_file(secondary_file)
                    
                    merge_info = {
                        'primary_file': primary_file,
                        'secondary_file': secondary_file,
                        'similarity': similarity,
                        'timestamp': datetime.now().isoformat(),
                        'type': analysis1.file_type
                    }
                    self.merged_files.append(merge_info)
                    
                    logger.info(f"تم دمج: {path1} + {path2} -> {primary_file}")
                
            except Exception as e:
                logger.error(f"خطأ في دمج {path1} و {path2}: {e}")
    
    def _merge_json_files(self, path1: str, path2: str) -> str:
        """دمج ملفات JSON"""
        try:
            with open(path1, 'r', encoding='utf-8') as f1:
                data1 = json.load(f1)
            with open(path2, 'r', encoding='utf-8') as f2:
                data2 = json.load(f2)
            
            # دمج القواميس
            if isinstance(data1, dict) and isinstance(data2, dict):
                merged_data = {**data1, **data2}
                merged_data['_merge_info'] = {
                    'merged_from': [path1, path2],
                    'merge_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                merged_data = {'file1': data1, 'file2': data2}
            
            return json.dumps(merged_data, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"خطأ في دمج JSON {path1}, {path2}: {e}")
            return ""
    
    def _merge_code_files(self, path1: str, path2: str) -> str:
        """دمج الملفات البرمجية"""
        try:
            with open(path1, 'r', encoding='utf-8') as f1:
                content1 = f1.read()
            with open(path2, 'r', encoding='utf-8') as f2:
                content2 = f2.read()
            
            merge_header = f"""
/*
 * MERGED FILE - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * Combined features from:
 * - {path1}
 * - {path2}
 */

"""
            
            merged_content = merge_header
            merged_content += f"// ========== Content from {path1} ==========\n"
            merged_content += content1 + "\n\n"
            merged_content += f"// ========== Content from {path2} ==========\n"
            merged_content += content2 + "\n"
            
            return merged_content
            
        except Exception as e:
            logger.error(f"خطأ في دمج الكود {path1}, {path2}: {e}")
            return ""
    
    def _merge_doc_files(self, path1: str, path2: str) -> str:
        """دمج ملفات التوثيق"""
        try:
            with open(path1, 'r', encoding='utf-8') as f1:
                content1 = f1.read()
            with open(path2, 'r', encoding='utf-8') as f2:
                content2 = f2.read()
            
            merged_content = f"""# Merged Documentation

> **Note**: Combined content from {Path(path1).name} and {Path(path2).name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content from {Path(path1).name}

{content1}

---

## Content from {Path(path2).name}

{content2}

---

*Merged automatically by config-hardware-esp32 analyzer*
"""
            
            return merged_content
            
        except Exception as e:
            logger.error(f"خطأ في دمج التوثيق {path1}, {path2}: {e}")
            return ""
    
    def _archive_merged_file(self, file_path: str) -> None:
        """أرشفة الملف المدموج في deleted"""
        try:
            source_path = Path(file_path)
            dest_path = self.deleted_dir / source_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = dest_path.with_name(f"{dest_path.stem}_merged_{timestamp}{dest_path.suffix}")
            
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"تم أرشفة: {file_path} -> {dest_path}")
            
        except Exception as e:
            logger.error(f"خطأ في أرشفة {file_path}: {e}")
    
    def generate_comprehensive_report(self) -> str:
        """إنشاء تقرير شامل"""
        report_path = self.reports_dir / f"config_hardware_esp32_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        total_duplicates = sum(len(files)-1 for files in self.duplicates.values())
        
        report_content = f"""# 📊 تقرير فحص مجلدات config، hardware، و esp32

## معلومات عامة
- **تاريخ التحليل**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **المجلدات المفحوصة**: {', '.join(self.target_dirs)}
- **عدد الملفات المفحوصة**: {len(self.file_registry)}
- **الملفات المكررة**: {total_duplicates}
- **الملفات المشابهة**: {len(self.similar_files)}
- **الملفات المدموجة**: {len(self.merged_files)}
- **الملفات المحذوفة**: {len(self.cleanup_candidates)}

## 🔍 الملفات المتطابقة تماماً

"""
        
        if self.duplicates:
            for hash_value, file_paths in self.duplicates.items():
                if len(file_paths) > 1:
                    report_content += f"### Hash: `{hash_value[:16]}...`\n"
                    for path in file_paths:
                        analysis = self.file_registry.get(path)
                        if analysis:
                            report_content += f"- `{path}` ({analysis.size} bytes, {analysis.category})\n"
                    report_content += "\n"
        else:
            report_content += "✅ لا توجد ملفات متطابقة تماماً\n\n"
        
        report_content += "## 📊 الملفات المشابهة والمدموجة\n\n"
        
        if self.merged_files:
            for merge_info in self.merged_files:
                report_content += f"### {merge_info['type']} - {merge_info['similarity']:.1%} تشابه\n"
                report_content += f"- **الملف الرئيسي**: `{merge_info['primary_file']}`\n"
                report_content += f"- **الملف المدموج**: `{merge_info['secondary_file']}`\n"
                report_content += f"- **التاريخ**: {merge_info['timestamp']}\n\n"
        else:
            report_content += "✅ لا توجد ملفات تحتاج دمج\n\n"
        
        report_content += """## 🎯 الخلاصة

✅ **تم الانتهاء من فحص وتنظيف المجلدات بنجاح**

- تم فحص جميع الملفات في المجلدات الثلاثة
- تم نقل الملفات المتطابقة إلى deleted/duplicates
- تم دمج الملفات المشابهة حسب النوع
- تم حذف الملفات المولدة تلقائياً

---

*تم إنشاء هذا التقرير بواسطة أداة تحليل المجلدات المتقدمة v1.0*
"""
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"تم إنشاء التقرير: {report_path}")
            return str(report_path)
        except Exception as e:
            logger.error(f"خطأ في إنشاء التقرير: {e}")
            return ""
    
    def run_complete_analysis(self) -> Dict[str, any]:
        """تشغيل التحليل الكامل"""
        logger.info("بدء التحليل الشامل للمجلدات...")
        
        self.ensure_directories()
        self.scan_all_directories()
        self.find_exact_duplicates()
        self.find_similar_files()
        
        # تنفيذ العمليات
        self.cleanup_generated_files()
        self.move_exact_duplicates()
        self.merge_similar_files()
        
        # إنشاء التقرير
        report_path = self.generate_comprehensive_report()
        
        results = {
            'files_scanned': len(self.file_registry),
            'duplicates_found': sum(len(files)-1 for files in self.duplicates.values()),
            'similar_files': len(self.similar_files),
            'files_merged': len(self.merged_files),
            'cleanup_files': len(self.cleanup_candidates),
            'report_path': report_path
        }
        
        logger.info(f"انتهى التحليل - النتائج: {results}")
        return results

def main():
    """الدالة الرئيسية"""
    try:
        analyzer = ConfigHardwareESP32Analyzer()
        results = analyzer.run_complete_analysis()
        
        print(f"\n{'='*60}")
        print("📊 تقرير فحص مجلدات config، hardware، و esp32")
        print(f"{'='*60}")
        print(f"📁 الملفات المفحوصة: {results['files_scanned']}")
        print(f"🔍 الملفات المكررة: {results['duplicates_found']}")
        print(f"📊 الملفات المشابهة: {results['similar_files']}")
        print(f"🔗 الملفات المدموجة: {results['files_merged']}")
        print(f"🧹 الملفات المحذوفة: {results['cleanup_files']}")
        print(f"📄 التقرير: {results['report_path']}")
        print(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"خطأ في التشغيل: {e}")

if __name__ == "__main__":
    main()
