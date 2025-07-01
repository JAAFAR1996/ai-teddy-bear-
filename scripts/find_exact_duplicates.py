"""
أداة البحث عن الملفات المكررة الفعلية
يبحث عن الملفات المتطابقة تماماً في المحتوى
"""
import hashlib
import os
from collections import defaultdict
from pathlib import Path
import json
from datetime import datetime


class ExactDuplicateFinder:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.pytest_cache'}
        self.ignore_patterns = ['*.pyc', '*.log', '*.db', '*.sqlite']
        self.file_hashes = defaultdict(list)
        self.results = {
            'exact_duplicates': [],
            'total_files_scanned': 0,
            'duplicate_groups': 0,
            'space_wasted': 0
        }
    
    def calculate_file_hash(self, filepath):
        """حساب hash SHA256 للملف"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"خطأ في قراءة {filepath}: {e}")
            return None
    
    def should_ignore_file(self, filepath):
        """التحقق من أن الملف يجب تجاهله"""
        path = Path(filepath)
        # تجاهل الملفات الصغيرة جداً (أقل من 10 بايت)
        try:
            if path.stat().st_size < 10:
                return True
        except:
            return True
            
        # تجاهل أنماط معينة
        for pattern in self.ignore_patterns:
            if path.match(pattern):
                return True
        
        return False
    
    def scan_directory(self):
        """مسح المجلد بحثاً عن الملفات المكررة"""
        print("🔍 بدء البحث عن الملفات المكررة...")
        
        for root, dirs, files in os.walk(self.root_dir):
            # تجاهل المجلدات المحددة
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                filepath = Path(root) / file
                
                if self.should_ignore_file(filepath):
                    continue
                
                self.results['total_files_scanned'] += 1
                
                # حساب hash الملف
                file_hash = self.calculate_file_hash(filepath)
                if file_hash:
                    file_size = filepath.stat().st_size
                    self.file_hashes[file_hash].append({
                        'path': str(filepath),
                        'size': file_size
                    })
    
    def find_duplicates(self):
        """تحديد المجموعات المكررة"""
        print("📊 تحليل النتائج...")
        
        for file_hash, files in self.file_hashes.items():
            if len(files) > 1:
                # حساب المساحة المهدرة
                file_size = files[0]['size']
                wasted_space = file_size * (len(files) - 1)
                self.results['space_wasted'] += wasted_space
                
                # إضافة مجموعة مكررة
                duplicate_group = {
                    'hash': file_hash,
                    'files': [f['path'] for f in files],
                    'file_size': file_size,
                    'wasted_space': wasted_space,
                    'count': len(files)
                }
                
                # تحديد أفضل ملف للاحتفاظ به
                duplicate_group['recommended_keep'] = self.recommend_file_to_keep(files)
                
                self.results['exact_duplicates'].append(duplicate_group)
                self.results['duplicate_groups'] += 1
    
    def recommend_file_to_keep(self, files):
        """توصية بأي ملف يجب الاحتفاظ به"""
        # الأولوية للملفات في src/
        for f in files:
            if 'src\\' in f['path'] or 'src/' in f['path']:
                return f['path']
        
        # ثم الملفات في tests/
        for f in files:
            if 'tests\\' in f['path'] or 'tests/' in f['path']:
                return f['path']
        
        # تجنب الملفات في backup أو temp
        for f in files:
            path_lower = f['path'].lower()
            if 'backup' not in path_lower and 'temp' not in path_lower and 'old' not in path_lower:
                return f['path']
        
        # إذا لم نجد، نختار الأول
        return files[0]['path']
    
    def generate_report(self):
        """إنشاء تقرير مفصل"""
        # ترتيب حسب المساحة المهدرة
        self.results['exact_duplicates'].sort(key=lambda x: x['wasted_space'], reverse=True)
        
        # إنشاء تقرير JSON
        report_data = {
            'scan_date': datetime.now().isoformat(),
            'summary': {
                'total_files_scanned': self.results['total_files_scanned'],
                'duplicate_groups': self.results['duplicate_groups'],
                'total_duplicate_files': sum(d['count'] for d in self.results['exact_duplicates']),
                'space_wasted_bytes': self.results['space_wasted'],
                'space_wasted_mb': round(self.results['space_wasted'] / (1024 * 1024), 2)
            },
            'duplicates': self.results['exact_duplicates']
        }
        
        with open('exact_duplicates_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # إنشاء تقرير Markdown
        self.create_markdown_report(report_data)
        
        # إنشاء سكريبت للحذف الآمن
        self.create_cleanup_script(self.results['exact_duplicates'])
        
        return report_data
    
    def create_markdown_report(self, report_data):
        """إنشاء تقرير Markdown"""
        md = f"""# 🔍 تقرير الملفات المكررة الفعلية

## 📅 معلومات الفحص
- **التاريخ**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **الملفات المفحوصة**: {report_data['summary']['total_files_scanned']}
- **مجموعات مكررة**: {report_data['summary']['duplicate_groups']}
- **إجمالي الملفات المكررة**: {report_data['summary']['total_duplicate_files']}
- **المساحة المهدرة**: {report_data['summary']['space_wasted_mb']} MB

## 📊 الملفات المكررة
"""
        
        for i, dup in enumerate(report_data['duplicates'][:20], 1):
            md += f"\n### {i}. مجموعة مكررة ({dup['count']} ملفات)\n"
            md += f"- **الحجم**: {dup['file_size']:,} بايت\n"
            md += f"- **المساحة المهدرة**: {dup['wasted_space']:,} بايت\n"
            md += f"- **يُنصح بالاحتفاظ بـ**: `{dup['recommended_keep']}`\n"
            md += "- **الملفات**:\n"
            
            for file in dup['files']:
                if file == dup['recommended_keep']:
                    md += f"  - ✅ `{file}` (احتفظ بهذا)\n"
                else:
                    md += f"  - ❌ `{file}` (يمكن حذفه)\n"
        
        with open('exact_duplicates_report.md', 'w', encoding='utf-8') as f:
            f.write(md)
    
    def create_cleanup_script(self, duplicates):
        """إنشاء سكريبت PowerShell للحذف الآمن"""
        ps_script = """# PowerShell Script للحذف الآمن للملفات المكررة
# تم إنشاؤه بواسطة ExactDuplicateFinder

$deletedCount = 0
$freedSpace = 0

Write-Host "🧹 بدء حذف الملفات المكررة..." -ForegroundColor Yellow

"""
        
        for dup in duplicates:
            ps_script += f"\n# مجموعة مكررة - الاحتفاظ بـ: {dup['recommended_keep']}\n"
            
            for file in dup['files']:
                if file != dup['recommended_keep']:
                    ps_script += f"""
if (Test-Path "{file}") {{
    Remove-Item "{file}" -Force
    Write-Host "✅ حذف: {file}" -ForegroundColor Green
    $deletedCount++
    $freedSpace += {dup['file_size']}
}}
"""
        
        ps_script += """
Write-Host ""
Write-Host "✅ تم الانتهاء!" -ForegroundColor Green
Write-Host "📊 الملفات المحذوفة: $deletedCount" -ForegroundColor Cyan
Write-Host "💾 المساحة المحررة: $([math]::Round($freedSpace/1MB, 2)) MB" -ForegroundColor Cyan
"""
        
        with open('cleanup_exact_duplicates.ps1', 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        print("✅ تم إنشاء سكريبت الحذف: cleanup_exact_duplicates.ps1")


def main():
    finder = ExactDuplicateFinder()
    finder.scan_directory()
    finder.find_duplicates()
    report = finder.generate_report()
    
    print("\n✅ تم الانتهاء من البحث!")
    print(f"📊 عدد المجموعات المكررة: {report['summary']['duplicate_groups']}")
    print(f"💾 المساحة المهدرة: {report['summary']['space_wasted_mb']} MB")
    print("\n📄 التقارير المُنشأة:")
    print("   - exact_duplicates_report.json")
    print("   - exact_duplicates_report.md")
    print("   - cleanup_exact_duplicates.ps1")


if __name__ == "__main__":
    main() 