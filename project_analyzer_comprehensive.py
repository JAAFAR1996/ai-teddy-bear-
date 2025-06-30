import os
import hashlib
import ast
import re
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime
import glob

class ComprehensiveProjectAnalyzer:
    def __init__(self, project_root='.'):
        self.project_root = Path(project_root)
        self.analysis = {
            "total_files": 0,
            "file_types": defaultdict(int),
            "duplicate_candidates": [],
            "large_files": [],
            "empty_files": [],
            "test_files": [],
            "config_files": [],
            "detailed_analysis": [],
            "hash_to_files": defaultdict(list),
            "function_signatures": defaultdict(list),
            "import_graph": defaultdict(set),
            "unused_files": [],
            "misplaced_files": []
        }
        
    def analyze_project(self):
        """تحليل شامل لكل ملف في المشروع"""
        print("🔍 بدء تحليل المشروع...")
        
        # مسح كل الملفات
        for root, dirs, files in os.walk(self.project_root):
            # تجاهل المجلدات غير المهمة
            dirs[:] = [d for d in dirs if d not in [
                '.git', '__pycache__', 'node_modules', '.venv', 
                'venv', '.pytest_cache', '.idea', '.vscode', 
                '__pycache__', 'build', 'dist', '*.egg-info'
            ]]
            
            for file in files:
                if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.yml', '.yaml')):
                    file_path = Path(root) / file
                    self.analyze_file(file_path)
                    
        # تحليل العلاقات والتبعيات
        self._analyze_dependencies()
        self._find_duplicates()
        self._identify_unused_files()
        
        return self.generate_report()
    
    def analyze_file(self, file_path):
        """تحليل ملف واحد"""
        try:
            self.analysis["total_files"] += 1
            
            # قراءة المحتوى
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            # حساب hash
            file_hash = hashlib.md5(content.encode()).hexdigest()
            self.analysis["hash_to_files"][file_hash].append(str(file_path))
            
            # تحديد نوع الملف
            file_ext = file_path.suffix
            self.analysis["file_types"][file_ext] += 1
            
            # تحليل حسب نوع الملف
            if file_ext == '.py':
                file_info = self._analyze_python_file(file_path, content, lines)
            elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                file_info = self._analyze_javascript_file(file_path, content, lines)
            else:
                file_info = self._analyze_generic_file(file_path, content, lines)
                
            # إضافة معلومات إضافية
            file_info.update({
                "path": str(file_path),
                "relative_path": str(file_path.relative_to(self.project_root)),
                "hash": file_hash,
                "size_bytes": file_path.stat().st_size,
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
            
            self.analysis["detailed_analysis"].append(file_info)
            
            # تحديد الملفات الخاصة
            if len(lines) == 0 or len(content.strip()) == 0:
                self.analysis["empty_files"].append(str(file_path))
            elif len(lines) > 500:
                self.analysis["large_files"].append({
                    "path": str(file_path),
                    "lines": len(lines)
                })
            elif 'test' in str(file_path).lower():
                self.analysis["test_files"].append(str(file_path))
            elif file_ext in ['.json', '.yml', '.yaml'] or 'config' in str(file_path).lower():
                self.analysis["config_files"].append(str(file_path))
                
        except Exception as e:
            print(f"❌ خطأ في تحليل {file_path}: {e}")
            
    def _analyze_python_file(self, file_path, content, lines):
        """تحليل ملف Python"""
        info = {
            "type": "python",
            "stats": {
                "lines": len(lines),
                "classes": 0,
                "functions": 0,
                "imports": 0,
                "docstrings": 0,
                "comments": 0
            },
            "issues": [],
            "imports": [],
            "exports": []
        }
        
        try:
            # تحليل AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    info["stats"]["classes"] += 1
                    info["exports"].append(f"class:{node.name}")
                elif isinstance(node, ast.FunctionDef):
                    info["stats"]["functions"] += 1
                    info["exports"].append(f"func:{node.name}")
                    # حفظ توقيع الدالة
                    args = [arg.arg for arg in node.args.args]
                    signature = f"{node.name}({','.join(args)})"
                    self.analysis["function_signatures"][signature].append(str(file_path))
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    info["stats"]["imports"] += 1
                    if isinstance(node, ast.ImportFrom) and node.module:
                        info["imports"].append(node.module)
                        self.analysis["import_graph"][str(file_path)].add(node.module)
                        
            # حساب التعليقات والdocstrings
            info["stats"]["comments"] = content.count('#')
            info["stats"]["docstrings"] = content.count('"""') + content.count("'''")
            
        except:
            info["issues"].append("Failed to parse AST")
            
        # تحديد نوع الملف Python
        info["python_type"] = self._determine_python_file_type(file_path, content, info)
        info["importance"] = self._determine_importance(file_path, content, info)
        info["issues"].extend(self._find_python_issues(content, str(file_path)))
        info["suggested_location"] = self._suggest_location(file_path, info["python_type"])
        
        return info
        
    def _analyze_javascript_file(self, file_path, content, lines):
        """تحليل ملف JavaScript/TypeScript"""
        info = {
            "type": "javascript",
            "stats": {
                "lines": len(lines),
                "components": 0,
                "functions": 0,
                "imports": 0,
                "exports": 0
            },
            "issues": []
        }
        
        # تحليل بسيط للـ JavaScript
        info["stats"]["imports"] = content.count('import ')
        info["stats"]["exports"] = content.count('export ')
        info["stats"]["functions"] = content.count('function ') + content.count('=>')
        info["stats"]["components"] = len(re.findall(r'(function|const|class)\s+[A-Z]\w+', content))
        
        info["importance"] = self._determine_importance(file_path, content, info)
        
        return info
        
    def _analyze_generic_file(self, file_path, content, lines):
        """تحليل ملف عام"""
        return {
            "type": "generic",
            "stats": {
                "lines": len(lines)
            },
            "importance": "medium" if len(content) > 100 else "low",
            "issues": []
        }
        
    def _determine_python_file_type(self, file_path, content, info):
        """تحديد نوع ملف Python"""
        path_str = str(file_path).lower()
        
        if 'test_' in path_str or '_test.py' in path_str:
            return 'test'
        elif 'main.py' in path_str or 'app.py' in path_str or '__main__.py' in path_str:
            return 'entry_point'
        elif 'model' in path_str or 'entity' in path_str or 'entities' in path_str:
            return 'model'
        elif 'service' in path_str or 'services' in path_str:
            return 'service'
        elif 'repository' in path_str or 'repo' in path_str:
            return 'repository'
        elif 'controller' in path_str or 'endpoint' in path_str or 'route' in path_str or 'api' in path_str:
            return 'controller'
        elif 'util' in path_str or 'helper' in path_str or 'utils' in path_str:
            return 'utility'
        elif 'config' in path_str:
            return 'config'
        elif 'exception' in path_str or 'error' in path_str:
            return 'exception'
        elif 'middleware' in path_str:
            return 'middleware'
        elif '__init__.py' in path_str:
            return 'init'
        elif info["stats"]["classes"] > 0:
            return 'class_file'
        elif info["stats"]["functions"] > 0:
            return 'module'
        else:
            return 'other'
            
    def _determine_importance(self, file_path, content, info):
        """تحديد أهمية الملف"""
        path_str = str(file_path).lower()
        
        # Critical files
        critical_patterns = [
            'main.py', 'app.py', 'wsgi.py', '__main__.py',
            'security', 'auth', 'child_safety',
            'database', 'models', 'entities',
            'api/endpoints'
        ]
        
        if any(pattern in path_str for pattern in critical_patterns):
            return 'critical'
            
        # Trash files
        trash_patterns = [
            '_old', '_backup', '_temp', '_copy', '_test_old',
            'deprecated', 'unused', 'draft', 'example'
        ]
        
        if any(pattern in path_str for pattern in trash_patterns):
            return 'trash'
            
        if len(content.strip()) == 0:
            return 'trash'
            
        # High importance
        if info.get("stats", {}).get("classes", 0) > 2 or info.get("stats", {}).get("functions", 0) > 5:
            return 'high'
            
        if any(x in path_str for x in ['service', 'repository', 'controller', 'handler']):
            return 'high'
            
        # Low importance
        if info.get("stats", {}).get("classes", 0) == 0 and info.get("stats", {}).get("functions", 0) == 0:
            return 'low'
            
        return 'medium'
        
    def _find_python_issues(self, content, file_path):
        """إيجاد المشاكل في ملف Python"""
        issues = []
        
        # فحص المشاكل الشائعة
        if 'except:' in content or 'except Exception:' in content:
            issues.append("Generic exception handling")
        if re.search(r'print\s*\(', content) and 'test' not in file_path.lower():
            issues.append("Print statements in production code")
        if 'TODO' in content or 'FIXME' in content:
            issues.append("Contains TODO/FIXME")
        if 'eval(' in content or 'exec(' in content:
            issues.append("Uses eval/exec (security risk)")
        if len(content.splitlines()) > 500:
            issues.append("File too large (>500 lines)")
        if 'import *' in content:
            issues.append("Uses wildcard imports")
        if 'global ' in content:
            issues.append("Uses global variables")
        if content.count('def ') > 20:
            issues.append("Too many functions (>20)")
            
        return issues
        
    def _suggest_location(self, current_path, file_type):
        """اقتراح موقع أفضل للملف"""
        type_to_location = {
            'model': 'src/core/domain/entities/',
            'service': 'src/core/services/',
            'repository': 'src/infrastructure/persistence/repositories/',
            'controller': 'src/api/endpoints/',
            'test': 'tests/',
            'config': 'configs/',
            'utility': 'src/shared/utils/',
            'exception': 'src/core/domain/exceptions/',
            'middleware': 'src/api/middleware/',
            'entry_point': 'src/'
        }
        
        suggested = type_to_location.get(file_type, 'src/')
        current_str = str(current_path)
        
        # تحقق إذا كان الملف في المكان الصحيح
        if suggested in current_str:
            return None
            
        # إذا كان الملف في مكان خاطئ
        self.analysis["misplaced_files"].append({
            "current": current_str,
            "suggested": suggested,
            "type": file_type
        })
        
        return suggested
        
    def _analyze_dependencies(self):
        """تحليل التبعيات بين الملفات"""
        # سيتم تنفيذه لاحقاً لتحديد الملفات غير المستخدمة
        pass
        
    def _find_duplicates(self):
        """إيجاد الملفات المكررة"""
        # التكرارات الكاملة (نفس الhash)
        for file_hash, files in self.analysis["hash_to_files"].items():
            if len(files) > 1:
                self.analysis["duplicate_candidates"].append({
                    "type": "exact",
                    "hash": file_hash,
                    "files": files
                })
                
        # التكرارات الوظيفية (نفس توقيعات الدوال)
        for signature, files in self.analysis["function_signatures"].items():
            if len(files) > 1:
                self.analysis["duplicate_candidates"].append({
                    "type": "functional",
                    "signature": signature,
                    "files": files
                })
                
    def _identify_unused_files(self):
        """تحديد الملفات غير المستخدمة"""
        # سيتم تنفيذه بناءً على import graph
        pass
        
    def generate_report(self):
        """إنشاء تقرير شامل"""
        report = {
            "summary": {
                "total_files": self.analysis["total_files"],
                "by_type": dict(self.analysis["file_types"]),
                "empty_files": len(self.analysis["empty_files"]),
                "large_files": len(self.analysis["large_files"]),
                "duplicate_files": len(self.analysis["duplicate_candidates"]),
                "misplaced_files": len(self.analysis["misplaced_files"])
            },
            "critical_issues": {
                "empty_files": self.analysis["empty_files"][:10],  # أول 10 فقط
                "duplicates": self.analysis["duplicate_candidates"][:10],
                "misplaced": self.analysis["misplaced_files"][:10]
            },
            "recommendations": self._generate_recommendations(),
            "detailed_analysis": self.analysis["detailed_analysis"]
        }
        
        return report
        
    def _generate_recommendations(self):
        """توليد توصيات للتنظيف"""
        recommendations = []
        
        if len(self.analysis["empty_files"]) > 0:
            recommendations.append({
                "priority": "high",
                "action": "delete_empty_files",
                "count": len(self.analysis["empty_files"]),
                "description": "حذف الملفات الفارغة"
            })
            
        if len(self.analysis["duplicate_candidates"]) > 0:
            recommendations.append({
                "priority": "high", 
                "action": "merge_duplicates",
                "count": len(self.analysis["duplicate_candidates"]),
                "description": "دمج الملفات المكررة"
            })
            
        if len(self.analysis["misplaced_files"]) > 0:
            recommendations.append({
                "priority": "medium",
                "action": "reorganize_structure", 
                "count": len(self.analysis["misplaced_files"]),
                "description": "نقل الملفات للأماكن الصحيحة"
            })
            
        return recommendations
        
    def save_report(self, filename="project_analysis_report.json"):
        """حفظ التقرير"""
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        # إنشاء تقرير markdown أيضاً
        self._save_markdown_report(report)
        
        return filename
        
    def _save_markdown_report(self, report):
        """حفظ تقرير بصيغة Markdown"""
        md_content = f"""# 📊 تقرير تحليل مشروع AI Teddy Bear

## 📈 ملخص عام

- **إجمالي الملفات**: {report['summary']['total_files']}
- **الملفات الفارغة**: {report['summary']['empty_files']}
- **الملفات الكبيرة**: {report['summary']['large_files']} 
- **الملفات المكررة**: {report['summary']['duplicate_files']}
- **الملفات في أماكن خاطئة**: {report['summary']['misplaced_files']}

## 📊 توزيع الملفات حسب النوع

| النوع | العدد |
|-------|--------|
"""
        
        for ext, count in report['summary']['by_type'].items():
            md_content += f"| {ext} | {count} |\n"
            
        md_content += "\n## 🚨 المشاكل الحرجة\n\n"
        
        if report['critical_issues']['empty_files']:
            md_content += "### 🗑️ ملفات فارغة (يجب حذفها)\n"
            for file in report['critical_issues']['empty_files']:
                md_content += f"- `{file}`\n"
                
        if report['critical_issues']['duplicates']:
            md_content += "\n### 🔄 ملفات مكررة (يجب دمجها)\n"
            for dup in report['critical_issues']['duplicates']:
                md_content += f"\n**{dup['type']} duplicate:**\n"
                for file in dup['files']:
                    md_content += f"- `{file}`\n"
                    
        md_content += "\n## 💡 التوصيات\n\n"
        
        for rec in report['recommendations']:
            emoji = "🔴" if rec['priority'] == 'high' else "🟡"
            md_content += f"{emoji} **{rec['description']}** ({rec['count']} ملف)\n"
            
        with open("project_analysis_report.md", 'w', encoding='utf-8') as f:
            f.write(md_content)

# تشغيل التحليل
if __name__ == "__main__":
    print("🚀 بدء تحليل المشروع الشامل...")
    analyzer = ComprehensiveProjectAnalyzer()
    report = analyzer.analyze_project()
    
    filename = analyzer.save_report()
    print(f"\n✅ تم حفظ التقرير في: {filename}")
    print(f"✅ تم حفظ التقرير المفصل في: project_analysis_report.md")
    
    # طباعة ملخص سريع
    print("\n📊 ملخص سريع:")
    print(f"- إجمالي الملفات: {report['summary']['total_files']}")
    print(f"- ملفات فارغة: {report['summary']['empty_files']}")
    print(f"- ملفات مكررة: {report['summary']['duplicate_files']}")
    print(f"- ملفات في أماكن خاطئة: {report['summary']['misplaced_files']}") 