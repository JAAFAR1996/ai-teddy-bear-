#!/usr/bin/env python3
"""
أداة فحص وتحليل الملفات المكررة والمشابهة في مجلد src
تتبع المعايير المؤسسية لعام 2025 وأفضل الممارسات الأمنية
"""

import difflib
import filecmp
import hashlib
import json
import logging
import os
import shutil
import sys
# تجنب مشاكل الترميز في Windows PowerShell
import warnings
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

warnings.filterwarnings("ignore", category=UserWarning)

# إعداد نظام السجلات المتقدم
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("src_deduplication.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """معلومات تفصيلية عن الملف"""

    path: str
    size: int
    hash_md5: str
    hash_sha256: str
    content_preview: str
    created_time: float
    modified_time: float
    file_type: str


class AdvancedFileComparator:
    """مقارن ملفات متطور مع خوارزميات متعددة"""

    def __init__(self, src_directory: str = "src"):
        self.src_dir = Path(src_directory)
        self.deleted_dir = Path("deleted/duplicates")
        self.reports_dir = Path("deleted/reports")
        self.file_registry: Dict[str, FileInfo] = {}
        self.duplicates: Dict[str, List[str]] = defaultdict(list)
        self.similar_files: List[Tuple[str, str, float]] = []

    def ensure_directories(self) -> None:
        """إنشاء المجلدات المطلوبة إذا لم تكن موجودة"""
        self.deleted_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"[SUCCESS] تم إنشاء المجلدات: {self.deleted_dir}, {self.reports_dir}"
        )

    def calculate_file_hashes(self, file_path: Path) -> Tuple[str, str]:
        """حساب هاش MD5 و SHA256 للملف"""
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)
        except Exception as e:
            logger.error(f"[ERROR] خطأ في قراءة الملف {file_path}: {e}")
            return "", ""

        return md5_hash.hexdigest(), sha256_hash.hexdigest()

    def get_content_preview(self, file_path: Path, max_lines: int = 10) -> str:
        """استخراج معاينة من محتوى الملف"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[:max_lines]
            return "".join(lines).strip()
        except Exception as e:
            logger.warning(f"[WARNING] لا يمكن قراءة محتوى {file_path}: {e}")
            return ""

    def scan_all_files(self) -> None:
        """مسح جميع الملفات في مجلد src وتسجيل معلوماتها"""
        logger.info(f"[SCANNING] بدء مسح الملفات في {self.src_dir}")

        for file_path in self.src_dir.rglob("*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                try:
                    md5_hash, sha256_hash = self.calculate_file_hashes(file_path)
                    content_preview = self.get_content_preview(file_path)
                    stat = file_path.stat()

                    file_info = FileInfo(
                        path=str(file_path),
                        size=stat.st_size,
                        hash_md5=md5_hash,
                        hash_sha256=sha256_hash,
                        content_preview=content_preview,
                        created_time=stat.st_ctime,
                        modified_time=stat.st_mtime,
                        file_type=file_path.suffix.lower(),
                    )

                    self.file_registry[str(file_path)] = file_info

                except Exception as e:
                    logger.error(f"[ERROR] خطأ في معالجة الملف {file_path}: {e}")

        logger.info(f"[SUCCESS] تم مسح {len(self.file_registry)} ملف")

    def _should_ignore_file(self, file_path: Path) -> bool:
        """تحديد الملفات التي يجب تجاهلها"""
        ignore_patterns = {
            ".pyc",
            ".pyo",
            ".pyd",
            "__pycache__",
            ".git",
            ".DS_Store",
            ".log",
            ".tmp",
        }

        return any(pattern in str(file_path) for pattern in ignore_patterns)

    def find_exact_duplicates(self) -> None:
        """البحث عن الملفات المتطابقة تماماً"""
        hash_groups = defaultdict(list)

        for file_path, file_info in self.file_registry.items():
            if file_info.hash_sha256:  # تجاهل الملفات التي فشل في قراءتها
                hash_groups[file_info.hash_sha256].append(file_path)

        # تسجيل المكررات
        for hash_value, file_paths in hash_groups.items():
            if len(file_paths) > 1:
                self.duplicates[hash_value] = file_paths
                logger.info(f"[DUPLICATE] وُجدت ملفات مكررة: {file_paths}")

    def find_similar_files(self, similarity_threshold: float = 0.85) -> None:
        """البحث عن الملفات المشابهة باستخدام نسبة التشابه"""
        file_paths = list(self.file_registry.keys())

        for i, path1 in enumerate(file_paths):
            for path2 in file_paths[i + 1 :]:
                if self._files_compatible_for_comparison(path1, path2):
                    similarity = self._calculate_similarity(path1, path2)
                    if similarity >= similarity_threshold:
                        self.similar_files.append((path1, path2, similarity))
                        logger.info(
                            f"[SIMILAR] ملفات مشابهة: {path1} <-> {path2} ({similarity:.2%})"
                        )

    def _files_compatible_for_comparison(self, path1: str, path2: str) -> bool:
        """تحديد ما إذا كان الملفان قابلان للمقارنة"""
        info1 = self.file_registry[path1]
        info2 = self.file_registry[path2]

        # نفس نوع الملف
        return info1.file_type == info2.file_type

    def _calculate_similarity(self, path1: str, path2: str) -> float:
        """حساب نسبة التشابه بين ملفين"""
        try:
            with open(path1, "r", encoding="utf-8", errors="ignore") as f1:
                content1 = f1.read()
            with open(path2, "r", encoding="utf-8", errors="ignore") as f2:
                content2 = f2.read()

            # استخدام SequenceMatcher للمقارنة
            similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
            return similarity

        except Exception as e:
            logger.warning(f"[WARNING] خطأ في مقارنة {path1} و {path2}: {e}")
            return 0.0

    def move_exact_duplicates(self) -> None:
        """نقل الملفات المتطابقة إلى مجلد deleted/duplicates"""
        moved_count = 0

        for hash_value, file_paths in self.duplicates.items():
            if len(file_paths) > 1:
                # الاحتفاظ بأحدث ملف، نقل الباقي
                newest_file = max(
                    file_paths, key=lambda p: self.file_registry[p].modified_time
                )

                for file_path in file_paths:
                    if file_path != newest_file:
                        try:
                            source_path = Path(file_path)
                            # إنشاء مسار فريد في مجلد deleted
                            relative_path = source_path.relative_to(self.src_dir)
                            dest_path = self.deleted_dir / relative_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)

                            # إضافة timestamp لتجنب التضارب
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            dest_path = dest_path.with_name(
                                f"{dest_path.stem}_{timestamp}{dest_path.suffix}"
                            )

                            shutil.move(str(source_path), str(dest_path))
                            moved_count += 1
                            logger.info(
                                f"[MOVED] تم نقل الملف المكرر: {file_path} -> {dest_path}"
                            )

                        except Exception as e:
                            logger.error(f"[ERROR] خطأ في نقل الملف {file_path}: {e}")

        logger.info(f"[RESULT] تم نقل {moved_count} ملف مكرر")

    def generate_detailed_report(self) -> str:
        """إنشاء تقرير مفصل عن عملية التنظيف"""
        report_path = (
            self.reports_dir
            / f"src_deduplication_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        report_content = f"""# تقرير تنظيف وإزالة التكرار - مجلد src

## معلومات عامة
- **تاريخ التحليل**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **عدد الملفات المفحوصة**: {len(self.file_registry)}
- **عدد الملفات المكررة**: {sum(len(files)-1 for files in self.duplicates.values())}
- **عدد الملفات المشابهة**: {len(self.similar_files)}

## الملفات المكررة (متطابقة 100%)

"""

        for hash_value, file_paths in self.duplicates.items():
            if len(file_paths) > 1:
                report_content += f"### Hash: `{hash_value[:16]}...`\n"
                for path in file_paths:
                    info = self.file_registry[path]
                    report_content += f"- `{path}` ({info.size} bytes)\n"
                report_content += "\n"

        report_content += "## الملفات المشابهة\n\n"

        for path1, path2, similarity in self.similar_files:
            report_content += f"### {similarity:.1%} تشابه\n"
            report_content += f"- `{path1}`\n"
            report_content += f"- `{path2}`\n\n"

        report_content += """## التوصيات

### للملفات المكررة:
- تم نقل الملفات المكررة تلقائياً إلى `deleted/duplicates/`
- تم الاحتفاظ بأحدث نسخة من كل ملف

### للملفات المشابهة:
- يُنصح بمراجعة الملفات المشابهة يدوياً
- دمج الوظائف المفيدة من الملفات المختلفة
- إزالة التكرار في المنطق البرمجي

## التحقق من السلامة
- [ ] تشغيل اختبارات النظام
- [ ] فحص التبعيات المكسورة
- [ ] التأكد من عمل جميع الوحدات

---
*تم إنشاء هذا التقرير بواسطة أداة تحليل الملفات المتقدمة v1.0*
"""

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"[REPORT] تم إنشاء التقرير: {report_path}")
            return str(report_path)
        except Exception as e:
            logger.error(f"[ERROR] خطأ في إنشاء التقرير: {e}")
            return ""

    def run_full_analysis(self) -> str:
        """تشغيل التحليل الكامل"""
        logger.info("[START] بدء التحليل الشامل لمجلد src")

        self.ensure_directories()
        self.scan_all_files()
        self.find_exact_duplicates()
        self.find_similar_files()
        self.move_exact_duplicates()
        report_path = self.generate_detailed_report()

        logger.info("[COMPLETE] تم الانتهاء من التحليل بنجاح")
        return report_path


def main():
    """الدالة الرئيسية"""
    try:
        analyzer = AdvancedFileComparator()
        report_path = analyzer.run_full_analysis()

        print(f"\n{'='*60}")
        print("تم الانتهاء من تحليل وتنظيف مجلد src")
        print(f"التقرير المفصل: {report_path}")
        print(f"الملفات المحذوفة: deleted/duplicates/")
        print(f"{'='*60}")

    except Exception as e:
        logger.error(f"[ERROR] خطأ في التشغيل: {e}")
        raise


if __name__ == "__main__":
    main()
