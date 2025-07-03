"""
أداة فحص وتحليل متقدمة للمجلدات: tests، observability، chaos، argocd، deployments
"""

import difflib
import hashlib
import json
import logging
import shutil
import warnings
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

warnings.filterwarnings("ignore", category=UserWarning)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
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
    is_test_file: bool = False
    is_config_file: bool = False


class AdvancedDirectoriesAnalyzer:
    """محلل متقدم للمجلدات المتخصصة"""

    def __init__(self):
        self.target_dirs = ["tests", "observability", "chaos", "argocd", "deployments"]
        self.deleted_dir = Path("deleted/duplicates")
        self.reports_dir = Path("deleted/reports")
        self.file_registry: Dict[str, FileAnalysis] = {}
        self.duplicates: Dict[str, List[str]] = defaultdict(list)
        self.similar_files: List[Tuple[str, str, float]] = []
        self.merged_files: List[Dict] = []
        self.cleanup_candidates: List[str] = []

    def ensure_directories(self) -> None:
        """إنشاء المجلدات المطلوبة"""
        self.deleted_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"تم إنشاء المجلدات: {self.deleted_dir}, {self.reports_dir}")

    def calculate_file_hash(self, file_path: Path) -> str:
        """حساب هاش SHA256 للملف"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"خطأ في قراءة {file_path}: {e}")
            return ""

    def classify_file(self, file_path: Path) -> Tuple[str, bool, bool, bool]:
        """تصنيف الملف وتحديد نوعه"""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()
        path_str = str(file_path).lower()
        if suffix in [".pyc", ".pyo"] or "__pycache__" in path_str:
            return "generated", False, False, True
        is_test = (
            "test" in path_str
            or name.startswith("test_")
            or name.startswith("conftest")
            or "_test" in name
        )
        is_config = (
            suffix in [".json", ".yaml", ".yml", ".ini", ".cfg"] or "config" in path_str
        )
        if is_test:
            category = "test"
        elif is_config:
            category = "config"
        else:
            category = "other"
        return category, is_test, is_config, False

    def get_content_preview(self, file_path: Path, max_lines: int = 5) -> str:
        """استخراج معاينة من محتوى الملف"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[:max_lines]
            return "".join(lines).strip()
        # FIXME: replace with specific exception
except Exception as exc:return ""

    def scan_all_directories(self) -> None:
        """مسح جميع المجلدات المحددة"""
        logger.info(f"بدء مسح المجلدات: {self.target_dirs}")
        for dir_name in self.target_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                logger.warning(f"المجلد غير موجود: {dir_name}")
                continue
            logger.info(f"مسح مجلد: {dir_name}")
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    try:
                        category, is_test, is_config, is_generated = self.classify_file(
                            file_path
                        )
                        if is_generated:
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
                            category=category,
                            content_preview=content_preview,
                            is_test_file=is_test,
                            is_config_file=is_config,
                        )
                        self.file_registry[str(file_path)] = analysis
                    except Exception as e:
                        logger.error(f"خطأ في معالجة {file_path}: {e}")
        logger.info(f"تم مسح {len(self.file_registry)} ملف")
        logger.info(f"تم تحديد {len(self.cleanup_candidates)} ملف للحذف")

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

    def find_similar_files(self, similarity_threshold: float = 0.8) -> None:
        """البحث عن الملفات المشابهة"""
        logger.info("البحث عن الملفات المشابهة...")
        file_paths = list(self.file_registry.keys())
        similar_count = 0
        for i, path1 in enumerate(file_paths):
            for path2 in file_paths[i + 1 :]:
                if self._should_compare_files(path1, path2):
                    similarity = self._calculate_similarity(path1, path2)
                    if similarity >= similarity_threshold:
                        self.similar_files.append((path1, path2, similarity))
                        similar_count += 1
                        logger.info(
                            f"ملفات مشابهة ({similarity:.1%}): {path1} <-> {path2}"
                        )
        logger.info(f"وُجدت {similar_count} زوج من الملفات المشابهة")

    def _should_compare_files(self, path1: str, path2: str) -> bool:
        """تحديد ما إذا كان يجب مقارنة الملفين"""
        analysis1 = self.file_registry[path1]
        analysis2 = self.file_registry[path2]
        if analysis1.file_type != analysis2.file_type:
            return False
        if analysis1.category != analysis2.category:
            return False
        if analysis1.size < 100 or analysis2.size < 100:
            return False
        return True

    def _calculate_similarity(self, path1: str, path2: str) -> float:
        """حساب نسبة التشابه بين ملفين"""
        try:
            with open(path1, "r", encoding="utf-8", errors="ignore") as f1:
                content1 = f1.read()
            with open(path2, "r", encoding="utf-8", errors="ignore") as f2:
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
                primary_file = self._choose_primary_file(file_paths)
                for file_path in file_paths:
                    if file_path != primary_file:
                        try:
                            source_path = Path(file_path)
                            relative_path = source_path
                            dest_path = self.deleted_dir / relative_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            dest_path = dest_path.with_name(
                                f"{dest_path.stem}_duplicate_{timestamp}{dest_path.suffix}"
                            )
                            shutil.move(str(source_path), str(dest_path))
                            moved_count += 1
                            logger.info(f"تم نقل: {file_path} -> {dest_path}")
                        except Exception as e:
                            logger.error(f"خطأ في نقل {file_path}: {e}")
        logger.info(f"تم نقل {moved_count} ملف متطابق")

    def _choose_primary_file(self, file_paths: List[str]) -> str:
        """اختيار الملف الرئيسي للاحتفاظ به"""
        priority_order = ["tests", "observability", "chaos", "argocd", "deployments"]
        for priority_dir in priority_order:
            for file_path in file_paths:
                if file_path.startswith(priority_dir + "/") or file_path.startswith(
                    priority_dir + "\\"
                ):
                    return file_path
        return max(file_paths, key=lambda p: Path(p).stat().st_mtime)

    def merge_similar_files(self) -> None:
        """دمج الملفات المشابهة حسب النوع"""
        logger.info("دمج الملفات المشابهة...")
        for path1, path2, similarity in self.similar_files:
            try:
                analysis1 = self.file_registry[path1]
                merged_content = None
                if analysis1.is_test_file:
                    merged_content = self._merge_test_files(path1, path2)
                elif analysis1.is_config_file:
                    merged_content = self._merge_config_files(path1, path2)
                else:
                    merged_content = self._merge_generic_files(path1, path2)
                if merged_content:
                    primary_file = self._choose_primary_file([path1, path2])
                    secondary_file = path2 if primary_file == path1 else path1
                    with open(primary_file, "w", encoding="utf-8") as f:
                        f.write(merged_content)
                    self._archive_merged_file(secondary_file)
                    merge_info = {
                        "primary_file": primary_file,
                        "secondary_file": secondary_file,
                        "similarity": similarity,
                        "timestamp": datetime.now().isoformat(),
                        "type": analysis1.category,
                    }
                    self.merged_files.append(merge_info)
                    logger.info(f"تم دمج: {path1} + {path2} -> {primary_file}")
            except Exception as e:
                logger.error(f"خطأ في دمج {path1} و {path2}: {e}")

    def _merge_test_files(self, path1: str, path2: str) -> str:
        """دمج ملفات الاختبارات"""
        try:
            with open(path1, "r", encoding="utf-8") as f1:
                content1 = f1.read()
            with open(path2, "r", encoding="utf-8") as f2:
                content2 = f2.read()
            merge_header = f"""# MERGED TEST FILE - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Combined test cases from: {path1} + {path2}

"""
            merged_content = merge_header
            merged_content += f"# ========== Tests from {Path(path1).name} ==========\n"
            merged_content += content1 + "\n\n"
            merged_content += f"# ========== Tests from {Path(path2).name} ==========\n"
            merged_content += content2 + "\n"
            return merged_content
        except Exception as e:
            logger.error(f"خطأ في دمج ملفات الاختبارات {path1}, {path2}: {e}")
            return ""

    def _merge_config_files(self, path1: str, path2: str) -> str:
        """دمج ملفات التكوين"""
        try:
            if path1.endswith(".json"):
                return self._merge_json_configs(path1, path2)
            else:
                return self._merge_generic_files(path1, path2)
        except Exception as e:
            logger.error(f"خطأ في دمج ملفات التكوين {path1}, {path2}: {e}")
            return ""

    def _merge_json_configs(self, path1: str, path2: str) -> str:
        """دمج ملفات JSON"""
        try:
            with open(path1, "r", encoding="utf-8") as f1:
                data1 = json.load(f1)
            with open(path2, "r", encoding="utf-8") as f2:
                data2 = json.load(f2)
            if isinstance(data1, dict) and isinstance(data2, dict):
                merged_data = {**data1, **data2}
                merged_data["_merge_info"] = {
                    "merged_from": [path1, path2],
                    "merge_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            else:
                merged_data = {"config1": data1, "config2": data2}
            return json.dumps(merged_data, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"خطأ في دمج JSON {path1}, {path2}: {e}")
            return ""

    def _merge_generic_files(self, path1: str, path2: str) -> str:
        """دمج الملفات العامة"""
        try:
            with open(path1, "r", encoding="utf-8") as f1:
                content1 = f1.read()
            with open(path2, "r", encoding="utf-8") as f2:
                content2 = f2.read()
            merge_header = f"""# MERGED FILE - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Combined from: {path1} + {path2}

"""
            merged_content = merge_header
            merged_content += (
                f"# ========== Content from {Path(path1).name} ==========\n"
            )
            merged_content += content1 + "\n\n"
            merged_content += (
                f"# ========== Content from {Path(path2).name} ==========\n"
            )
            merged_content += content2 + "\n"
            return merged_content
        except Exception as e:
            logger.error(f"خطأ في دمج الملفات {path1}, {path2}: {e}")
            return ""

    def _archive_merged_file(self, file_path: str) -> None:
        """أرشفة الملف المدموج في deleted"""
        try:
            source_path = Path(file_path)
            dest_path = self.deleted_dir / source_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = dest_path.with_name(
                f"{dest_path.stem}_merged_{timestamp}{dest_path.suffix}"
            )
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"تم أرشفة: {file_path} -> {dest_path}")
        except Exception as e:
            logger.error(f"خطأ في أرشفة {file_path}: {e}")

    def generate_comprehensive_report(self) -> str:
        """إنشاء تقرير شامل"""
        report_path = (
            self.reports_dir
            / f"advanced_directories_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        total_duplicates = sum(len(files) - 1 for files in self.duplicates.values())
        report_content = f"""# 📊 تقرير فحص المجلدات المتقدمة

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
                            report_content += f"""- `{path}` ({analysis.size} bytes, {analysis.category})
"""
                    report_content += "\n"
        else:
            report_content += "✅ لا توجد ملفات متطابقة تماماً\n\n"
        if self.merged_files:
            report_content += "## 🔗 الملفات المدموجة\n\n"
            for merge_info in self.merged_files:
                report_content += f"""### {merge_info['type']} - {merge_info['similarity']:.1%} تشابه
"""
                report_content += (
                    f"- **الملف الرئيسي**: `{merge_info['primary_file']}`\n"
                )
                report_content += (
                    f"- **الملف المدموج**: `{merge_info['secondary_file']}`\n"
                )
                report_content += f"- **التاريخ**: {merge_info['timestamp']}\n\n"
        report_content += """## 🎯 الخلاصة

✅ **تم الانتهاء من فحص وتنظيف المجلدات المتقدمة بنجاح**

---

*تم إنشاء هذا التقرير بواسطة أداة تحليل المجلدات المتقدمة v1.0*
"""
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"تم إنشاء التقرير: {report_path}")
            return str(report_path)
        except Exception as e:
            logger.error(f"خطأ في إنشاء التقرير: {e}")
            return ""

    def run_complete_analysis(self) -> Dict[str, any]:
        """تشغيل التحليل الكامل"""
        logger.info("بدء التحليل الشامل للمجلدات المتقدمة...")
        self.ensure_directories()
        self.scan_all_directories()
        self.find_exact_duplicates()
        self.find_similar_files()
        self.cleanup_generated_files()
        self.move_exact_duplicates()
        self.merge_similar_files()
        report_path = self.generate_comprehensive_report()
        results = {
            "files_scanned": len(self.file_registry),
            "duplicates_found": sum(
                len(files) - 1 for files in self.duplicates.values()
            ),
            "similar_files": len(self.similar_files),
            "files_merged": len(self.merged_files),
            "cleanup_files": len(self.cleanup_candidates),
            "report_path": report_path,
        }
        logger.info(f"انتهى التحليل - النتائج: {results}")
        return results


def main():
    """الدالة الرئيسية"""
    try:
        analyzer = AdvancedDirectoriesAnalyzer()
        results = analyzer.run_complete_analysis()
        logger.info(f"\n{'=' * 70}")
        logger.info("📊 تقرير فحص المجلدات المتقدمة")
        logger.info(f"{'=' * 70}")
        logger.info(f"📁 الملفات المفحوصة: {results['files_scanned']}")
        logger.info(f"🔍 الملفات المكررة: {results['duplicates_found']}")
        logger.info(f"📊 الملفات المشابهة: {results['similar_files']}")
        logger.info(f"🔗 الملفات المدموجة: {results['files_merged']}")
        logger.info(f"🧹 الملفات المحذوفة: {results['cleanup_files']}")
        logger.info(f"📄 التقرير: {results['report_path']}")
        logger.info(f"{'=' * 70}")
    except Exception as e:
        logger.error(f"خطأ في التشغيل: {e}")


if __name__ == "__main__":
    main()
