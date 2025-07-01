import json
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import ast

class DeepAnalyzer:
    """محلل عميق لمشروع AI Teddy Bear"""
    
    def __init__(self, analysis_file: str = "project_analysis.json"):
        # إذا كنا في مجلد scripts، استخدم الملف المحلي
        if not os.path.exists(analysis_file) and os.path.exists(f"scripts/{analysis_file}"):
            analysis_file = f"scripts/{analysis_file}"
        elif os.path.exists(f"../{analysis_file}"):
            analysis_file = f"../{analysis_file}"
            
        with open(analysis_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def analyze_all(self):
        """تشغيل جميع التحليلات"""
        print("🔍 تحليل عميق لمشروع AI Teddy Bear\n")
        
        print("="*60)
        self.analyze_duplicates()
        
        print("\n" + "="*60)
        self.analyze_large_files()
        
        print("\n" + "="*60)
        self.analyze_issues()
        
        print("\n" + "="*60)
        self.analyze_structure_problems()
        
        print("\n" + "="*60)
        self.analyze_dependencies()
        
        print("\n" + "="*60)
        self.generate_cleanup_recommendations()
    
    def analyze_duplicates(self):
        """تحليل الملفات المكررة"""
        print("🔄 تحليل الملفات المكررة")
        print("-"*40)
        
        duplicates = self.data.get('duplicate_candidates', [])
        
        if not duplicates:
            print("✅ لا توجد ملفات مكررة!")
            return
        
        # تصنيف التكرارات
        exact_duplicates = [d for d in duplicates if d['type'] == 'exact']
        functional_duplicates = [d for d in duplicates if d['type'] == 'functional']
        
        print(f"\n📊 إحصائيات التكرار:")
        print(f"  • تكرارات كاملة: {len(exact_duplicates)} مجموعة")
        print(f"  • تكرارات وظيفية: {len(functional_duplicates)} مجموعة")
        
        # عرض التكرارات الكاملة
        if exact_duplicates:
            print(f"\n🔴 التكرارات الكاملة (نفس المحتوى تماماً):")
            for i, dup in enumerate(exact_duplicates[:10], 1):
                print(f"\n  {i}. مجموعة (Hash: {dup['hash'][:8]}...):")
                for file in dup['files']:
                    print(f"     - {file}")
                    
                # اقتراح أي ملف نحتفظ به
                best_file = self._suggest_best_duplicate(dup['files'])
                print(f"     ✨ اقتراح: احتفظ بـ {best_file}")
        
        # عرض التكرارات الوظيفية
        if functional_duplicates:
            print(f"\n🟡 التكرارات الوظيفية (نفس الدوال):")
            for i, dup in enumerate(functional_duplicates[:5], 1):
                print(f"\n  {i}. الدالة: {dup['signature']}")
                for file in dup['files']:
                    print(f"     - {file}")
    
    def analyze_large_files(self):
        """تحليل الملفات الكبيرة"""
        print("📦 تحليل الملفات الكبيرة")
        print("-"*40)
        
        large_files = self.data.get('large_files', [])
        
        if not large_files:
            print("✅ لا توجد ملفات كبيرة جداً!")
            return
        
        # ترتيب حسب الحجم
        large_files.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n🔴 الملفات الكبيرة ({len(large_files)} ملف):")
        
        for file_path, lines in large_files[:10]:
            # إيجاد معلومات الملف من التحليل المفصل
            file_info = next((f for f in self.data['detailed_analysis'] 
                            if f['path'] == file_path), None)
            
            if file_info:
                print(f"\n  📄 {file_path}")
                print(f"     • الأسطر: {lines}")
                print(f"     • النوع: {file_info['type']}")
                print(f"     • الأهمية: {file_info['importance']}")
                print(f"     • الكلاسات: {file_info['stats']['classes']}")
                print(f"     • الدوال: {file_info['stats']['functions']}")
                
                # اقتراحات للتقسيم
                if lines > 500:
                    print(f"     ⚠️  اقتراح: قسّم هذا الملف إلى ملفات أصغر")
    
    def analyze_issues(self):
        """تحليل المشاكل في الكود"""
        print("⚠️  تحليل المشاكل المكتشفة")
        print("-"*40)
        
        # جمع جميع المشاكل
        issue_counts = defaultdict(int)
        files_with_issues = defaultdict(list)
        
        for file_info in self.data['detailed_analysis']:
            for issue in file_info.get('issues', []):
                issue_counts[issue] += 1
                files_with_issues[issue].append(file_info['path'])
        
        if not issue_counts:
            print("✅ لا توجد مشاكل مكتشفة!")
            return
        
        # ترتيب المشاكل حسب التكرار
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n📊 المشاكل الأكثر شيوعاً:")
        for issue, count in sorted_issues[:10]:
            print(f"\n  🔸 {issue}: {count} ملف")
            # عرض بعض الأمثلة
            for file in files_with_issues[issue][:3]:
                print(f"     - {file}")
            if len(files_with_issues[issue]) > 3:
                print(f"     ... و {len(files_with_issues[issue]) - 3} ملف آخر")
    
    def analyze_structure_problems(self):
        """تحليل مشاكل الهيكل"""
        print("🏗️ تحليل مشاكل هيكل المشروع")
        print("-"*40)
        
        misplaced_files = []
        
        for file_info in self.data['detailed_analysis']:
            if file_info.get('suggested_location'):
                misplaced_files.append(file_info)
        
        if not misplaced_files:
            print("✅ جميع الملفات في أماكنها الصحيحة!")
            return
        
        # تصنيف الملفات حسب النوع
        by_type = defaultdict(list)
        for file in misplaced_files:
            by_type[file['type']].append(file)
        
        print(f"\n🔴 الملفات في أماكن خاطئة ({len(misplaced_files)} ملف):")
        
        for file_type, files in by_type.items():
            print(f"\n  📁 {file_type} ({len(files)} ملف):")
            for file in files[:5]:
                current = file['path']
                suggested = file['suggested_location']
                print(f"     • {current}")
                print(f"       ➡️  {suggested}")
    
    def analyze_dependencies(self):
        """تحليل التبعيات"""
        print("🔗 تحليل التبعيات")
        print("-"*40)
        
        # جمع جميع التبعيات
        all_deps = defaultdict(int)
        external_deps = set()
        internal_deps = set()
        
        for file_info in self.data['detailed_analysis']:
            for dep in file_info.get('dependencies', []):
                all_deps[dep] += 1
                
                # تصنيف التبعيات
                if dep.startswith(('src', 'app', 'domain', 'infrastructure')):
                    internal_deps.add(dep)
                else:
                    external_deps.add(dep)
        
        print(f"\n📊 إحصائيات التبعيات:")
        print(f"  • التبعيات الخارجية: {len(external_deps)}")
        print(f"  • التبعيات الداخلية: {len(internal_deps)}")
        
        # أكثر التبعيات استخداماً
        sorted_deps = sorted(all_deps.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n🔸 أكثر التبعيات استخداماً:")
        for dep, count in sorted_deps[:10]:
            print(f"  • {dep}: {count} ملف")
    
    def generate_cleanup_recommendations(self):
        """توليد توصيات التنظيف"""
        print("💡 توصيات التنظيف")
        print("-"*40)
        
        recommendations = []
        
        # توصيات بناءً على التحليل
        duplicates = self.data.get('duplicate_candidates', [])
        large_files = self.data.get('large_files', [])
        empty_files = self.data.get('empty_files', [])
        
        # حساب التوفير المحتمل
        duplicate_files = sum(len(d['files']) - 1 for d in duplicates if d['type'] == 'exact')
        
        if duplicate_files > 0:
            recommendations.append({
                'priority': 'HIGH',
                'action': f'حذف {duplicate_files} ملف مكرر',
                'impact': 'توفير مساحة وتقليل التعقيد'
            })
        
        if len(large_files) > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': f'تقسيم {len(large_files)} ملف كبير',
                'impact': 'تحسين قابلية الصيانة'
            })
        
        if len(empty_files) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'action': f'حذف {len(empty_files)} ملف فارغ',
                'impact': 'تنظيف المشروع'
            })
        
        # حساب الملفات في أماكن خاطئة
        misplaced = sum(1 for f in self.data['detailed_analysis'] 
                       if f.get('suggested_location'))
        
        if misplaced > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': f'نقل {misplaced} ملف إلى أماكنها الصحيحة',
                'impact': 'تحسين تنظيم المشروع'
            })
        
        # عرض التوصيات
        print("\n📋 خطة العمل المقترحة:")
        
        # ترتيب حسب الأولوية
        high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
        medium_priority = [r for r in recommendations if r['priority'] == 'MEDIUM']
        
        if high_priority:
            print("\n🔴 أولوية عالية:")
            for i, rec in enumerate(high_priority, 1):
                print(f"  {i}. {rec['action']}")
                print(f"     التأثير: {rec['impact']}")
        
        if medium_priority:
            print("\n🟡 أولوية متوسطة:")
            for i, rec in enumerate(medium_priority, 1):
                print(f"  {i}. {rec['action']}")
                print(f"     التأثير: {rec['impact']}")
        
        # ملخص التوفير المتوقع
        print("\n💰 التوفير المتوقع:")
        print(f"  • حذف {duplicate_files + len(empty_files)} ملف")
        print(f"  • تحسين تنظيم {misplaced} ملف")
        print(f"  • تقليل التعقيد بنسبة ~{((duplicate_files + len(empty_files)) / self.data['total_python_files'] * 100):.1f}%")
    
    def _suggest_best_duplicate(self, files: List[str]) -> str:
        """اقتراح أفضل ملف من المكررات"""
        scores = {}
        
        for file in files:
            score = 0
            
            # تفضيل الملفات في src
            if 'src/' in file:
                score += 10
            
            # تفضيل الملفات الأساسية
            if any(x in file for x in ['core', 'domain', 'service']):
                score += 5
            
            # تجنب الملفات القديمة
            if any(x in file for x in ['old', 'backup', 'temp']):
                score -= 20
            
            # تفضيل الملفات في المجلدات المنظمة
            depth = len(Path(file).parts)
            if 3 <= depth <= 5:  # عمق مثالي
                score += 3
            
            scores[file] = score
        
        return max(scores.items(), key=lambda x: x[1])[0]


def main():
    """تشغيل التحليل العميق"""
    analyzer = DeepAnalyzer()
    analyzer.analyze_all()
    
    print("\n" + "="*60)
    print("✅ اكتمل التحليل العميق!")
    print("\n💡 الخطوة التالية: شغّل project_cleaner.py --dry-run للمعاينة")


if __name__ == "__main__":
    main() 