#!/usr/bin/env python3
"""
Quick Config Analyzer
أداة سريعة لتحليل ملفات التكوين واكتشاف التكرارات
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

class QuickConfigAnalyzer:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        
    def discover_config_files(self) -> List[Path]:
        """اكتشاف جميع ملفات التكوين"""
        print("🔍 اكتشاف ملفات التكوين...")
        
        config_files = []
        extensions = ['.json', '.yaml', '.yml', '.env', '.conf', '.ini', '.toml']
        
        # مجلدات للتجاهل
        ignore_dirs = {'__pycache__', '.git', 'node_modules', '.venv', 'venv', '.mypy_cache'}
        
        for ext in extensions:
            files = list(self.base_path.rglob(f'*{ext}'))
            # تصفية الملفات في المجلدات المستبعدة
            filtered_files = []
            for f in files:
                if not any(ignore_dir in str(f) for ignore_dir in ignore_dirs):
                    filtered_files.append(f)
            
            config_files.extend(filtered_files)
            if filtered_files:
                print(f"  📄 {ext}: {len(filtered_files)} ملف")
        
        print(f"📊 إجمالي: {len(config_files)} ملف تكوين")
        return config_files
    
    def analyze_exact_duplicates(self, files: List[Path]) -> Dict[str, List[Path]]:
        """تحليل التكرارات المتطابقة 100%"""
        print("\n🔍 تحليل التكرارات المتطابقة...")
        
        file_hashes = {}
        duplicates = {}
        
        for file_path in files:
            try:
                # محاولة قراءة الملف بتشفيرات مختلفة
                content = self._read_file_safe(file_path)
                
                if not content:  # تجاهل الملفات الفارغة
                    continue
                    
                # حساب hash للمحتوى
                content_hash = hashlib.md5(content.encode()).hexdigest()
                
                if content_hash in file_hashes:
                    # عثر على تكرار
                    if content_hash not in duplicates:
                        duplicates[content_hash] = [file_hashes[content_hash]]
                    duplicates[content_hash].append(file_path)
                else:
                    file_hashes[content_hash] = file_path
                    
            except Exception as e:
                print(f"❌ خطأ في قراءة {file_path}: {e}")
        
        return duplicates
    
    def _read_file_safe(self, file_path: Path) -> str:
        """قراءة الملف بأمان مع تجربة تشفيرات مختلفة"""
        encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-32', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read().strip()
                    return content
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception:
                break
        
        # إذا فشلت جميع التشفيرات، اقرأ كـ binary وحول
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                # محاولة تحويل البيانات الخام
                for encoding in ['utf-8', 'latin-1']:
                    try:
                        return raw_data.decode(encoding, errors='ignore').strip()
                    except:
                        continue
        except Exception:
            pass
        
        print(f"⚠️ تم تجاهل ملف غير قابل للقراءة: {file_path.name}")
        return ""
    
    def calculate_similarity(self, content1: str, content2: str) -> float:
        """حساب نسبة التشابه بين محتويين"""
        if not content1 or not content2:
            return 0.0
        
        # تنظيف المحتوى للمقارنة
        clean1 = self._clean_content(content1)
        clean2 = self._clean_content(content2)
        
        if clean1 == clean2:
            return 100.0
        
        # حساب التشابه باستخدام Longest Common Subsequence
        return self._lcs_similarity(clean1, clean2)
    
    def _clean_content(self, content: str) -> str:
        """تنظيف المحتوى للمقارنة"""
        lines = []
        for line in content.split('\n'):
            # إزالة التعليقات
            if '//' in line:
                line = line.split('//')[0]
            if '#' in line and not line.strip().startswith('"'):
                line = line.split('#')[0]
            
            # إزالة المسافات الزائدة
            line = line.strip()
            if line:
                lines.append(line)
        
        return '\n'.join(lines)
    
    def _lcs_similarity(self, text1: str, text2: str) -> float:
        """حساب التشابه باستخدام Longest Common Subsequence"""
        len1, len2 = len(text1), len(text2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # مصفوفة ديناميكية للـ LCS
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        lcs_length = dp[len1][len2]
        similarity = (2.0 * lcs_length) / (len1 + len2) * 100
        return similarity
    
    def find_similar_configs(self, files: List[Path], threshold: float = 70.0) -> List[Dict]:
        """البحث عن ملفات التكوين المتشابهة"""
        print(f"\n🔍 البحث عن التشابهات (>{threshold}%)...")
        
        similar_groups = []
        processed_files = set()
        
        for i, file1 in enumerate(files):
            if file1 in processed_files:
                continue
            
            try:
                content1 = self._read_file_safe(file1)
                
                if not content1:
                    continue
                
                similar_files = [file1]
                
                for j, file2 in enumerate(files[i+1:], i+1):
                    if file2 in processed_files:
                        continue
                    
                    try:
                        content2 = self._read_file_safe(file2)
                        
                        similarity = self.calculate_similarity(content1, content2)
                        
                        if threshold <= similarity < 100:
                            similar_files.append(file2)
                    
                    except Exception:
                        continue
                
                if len(similar_files) > 1:
                    # حساب متوسط التشابه للمجموعة
                    similarities = []
                    for x in range(len(similar_files)):
                        for y in range(x+1, len(similar_files)):
                            try:
                                content_x = self._read_file_safe(similar_files[x])
                                content_y = self._read_file_safe(similar_files[y])
                                sim = self.calculate_similarity(content_x, content_y)
                                similarities.append(sim)
                            except Exception:
                                continue
                    
                    avg_similarity = sum(similarities) / len(similarities) if similarities else 0
                    
                    similar_groups.append({
                        "files": similar_files,
                        "average_similarity": avg_similarity,
                        "count": len(similar_files)
                    })
                    
                    processed_files.update(similar_files)
            
            except Exception as e:
                print(f"❌ خطأ في معالجة {file1}: {e}")
        
        return similar_groups
    
    def analyze_config_sizes(self, files: List[Path]) -> Dict:
        """تحليل أحجام ملفات التكوين"""
        print("\n📊 تحليل أحجام الملفات...")
        
        sizes = []
        large_files = []
        empty_files = []
        
        for file_path in files:
            try:
                size = file_path.stat().st_size
                sizes.append(size)
                
                if size == 0:
                    empty_files.append(file_path)
                elif size > 50 * 1024:  # أكبر من 50KB
                    large_files.append((file_path, size))
            
            except Exception:
                continue
        
        if sizes:
            avg_size = sum(sizes) / len(sizes)
            total_size = sum(sizes)
            
            print(f"  📁 متوسط الحجم: {avg_size/1024:.1f} KB")
            print(f"  📦 الحجم الإجمالي: {total_size/1024:.1f} KB")
            print(f"  📄 ملفات فارغة: {len(empty_files)}")
            print(f"  📈 ملفات كبيرة (>50KB): {len(large_files)}")
        
        return {
            "average_size": avg_size if sizes else 0,
            "total_size": sum(sizes),
            "empty_files": empty_files,
            "large_files": large_files
        }
    
    def run_comprehensive_analysis(self) -> Dict:
        """تشغيل التحليل الشامل"""
        print("=" * 60)
        print("🧹  QUICK CONFIG ANALYZER")
        print("🔍  SMART DUPLICATION DETECTION")
        print("=" * 60)
        
        # اكتشاف ملفات التكوين
        config_files = self.discover_config_files()
        
        if not config_files:
            print("❌ لم يتم العثور على ملفات تكوين!")
            return {}
        
        # تحليل الأحجام
        size_analysis = self.analyze_config_sizes(config_files)
        
        # تحليل التكرارات المتطابقة
        exact_duplicates = self.analyze_exact_duplicates(config_files)
        
        # تحليل التشابهات
        similar_groups = self.find_similar_configs(config_files, threshold=70.0)
        
        # عرض النتائج
        print("\n" + "="*50)
        print("📊  ANALYSIS RESULTS")
        print("="*50)
        
        # إحصائيات التكرارات
        total_exact_duplicates = sum(len(group) - 1 for group in exact_duplicates.values())
        total_similar_files = sum(group["count"] - 1 for group in similar_groups)
        
        print(f"\n🔄 التكرارات المتطابقة:")
        print(f"  📁 مجموعات: {len(exact_duplicates)}")
        print(f"  🗑️ ملفات للحذف: {total_exact_duplicates}")
        
        if exact_duplicates:
            print(f"\n  📋 تفاصيل المجموعات:")
            for i, (hash_val, file_list) in enumerate(exact_duplicates.items(), 1):
                primary = file_list[0]
                dups = file_list[1:]
                
                print(f"    {i}. احتفاظ: {primary.name}")
                print(f"       حذف ({len(dups)}): {[f.name for f in dups[:3]]}")
                if len(dups) > 3:
                    print(f"       ... و{len(dups) - 3} أخرى")
        
        print(f"\n🔗 التشابهات (70%+):")
        print(f"  📁 مجموعات: {len(similar_groups)}")
        print(f"  🔄 ملفات للدمج: {total_similar_files}")
        
        if similar_groups:
            print(f"\n  📋 تفاصيل المجموعات:")
            for i, group in enumerate(similar_groups, 1):
                files = [f.name for f in group["files"]]
                similarity = group["average_similarity"]
                
                print(f"    {i}. تشابه: {similarity:.1f}%")
                print(f"       ملفات ({len(files)}): {files[:3]}")
                if len(files) > 3:
                    print(f"       ... و{len(files) - 3} أخرى")
        
        # إحصائيات المساحة
        total_space_saved = 0
        for group in exact_duplicates.values():
            if len(group) > 1:
                try:
                    file_size = group[0].stat().st_size
                    total_space_saved += file_size * (len(group) - 1)
                except Exception:
                    continue
        
        print(f"\n💾 توفير المساحة:")
        print(f"  📊 مساحة متوقعة: {total_space_saved/1024:.1f} KB")
        print(f"  📈 نسبة التوفير: {(total_space_saved/size_analysis['total_size']*100):.1f}%")
        
        # ملفات فارغة أو كبيرة
        if size_analysis["empty_files"]:
            print(f"\n📄 ملفات فارغة للمراجعة:")
            for empty_file in size_analysis["empty_files"][:5]:
                print(f"    - {empty_file.name}")
            if len(size_analysis["empty_files"]) > 5:
                print(f"    ... و{len(size_analysis['empty_files']) - 5} أخرى")
        
        if size_analysis["large_files"]:
            print(f"\n📈 ملفات كبيرة للمراجعة:")
            for large_file, size in size_analysis["large_files"][:5]:
                print(f"    - {large_file.name} ({size/1024:.1f} KB)")
        
        print(f"\n🎯 التوصيات:")
        if total_exact_duplicates > 0:
            print(f"  1. حذف {total_exact_duplicates} ملف مكرر متطابق")
        if total_similar_files > 0:
            print(f"  2. دمج {total_similar_files} ملف متشابه")
        if size_analysis["empty_files"]:
            print(f"  3. مراجعة {len(size_analysis['empty_files'])} ملف فارغ")
        
        print(f"\n⚠️ للتنفيذ الآمن:")
        print(f"  - استخدم الأداة الكاملة IntelligentConfigMerger")
        print(f"  - ستتم معالجة المراجع تلقائياً")
        print(f"  - نسخ احتياطية آمنة لجميع الملفات")
        
        return {
            "config_files_count": len(config_files),
            "exact_duplicates": exact_duplicates,
            "similar_groups": similar_groups,
            "size_analysis": size_analysis,
            "total_exact_duplicates": total_exact_duplicates,
            "total_similar_files": total_similar_files,
            "space_saved_kb": total_space_saved / 1024
        }

def main():
    """الدالة الرئيسية"""
    analyzer = QuickConfigAnalyzer()
    
    try:
        results = analyzer.run_comprehensive_analysis()
        
        if results and (results.get("total_exact_duplicates", 0) > 0 or results.get("total_similar_files", 0) > 0):
            print(f"\n✅ تم اكتشاف تكرارات وتشابهات!")
            print(f"🚀 لتنفيذ التنظيف، شغل: python scripts/intelligent_config_merger.py")
        else:
            print(f"\n✅ لا توجد تكرارات أو تشابهات كبيرة!")
            
    except Exception as e:
        print(f"❌ خطأ في التحليل: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 