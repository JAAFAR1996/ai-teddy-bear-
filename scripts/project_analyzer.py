import os
import hashlib
import ast
import re
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class ProjectAnalyzer:
    """محلل شامل لمشروع AI Teddy Bear"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_result = {
            "total_files": 0,
            "total_python_files": 0,
            "file_types": defaultdict(int),
            "duplicate_candidates": [],
            "large_files": [],
            "empty_files": [],
            "test_files": [],
            "config_files": [],
            "detailed_analysis": [],
            "file_hashes": defaultdict(list),
            "function_signatures": defaultdict(list),
            "import_dependencies": defaultdict(set)
        }
        
    def analyze_project(self) -> Dict:
        """تحليل شامل لكل ملف في المشروع"""
        print("🔍 بدء تحليل المشروع...")
        
        # مسح كل الملفات
        for root, dirs, files in os.walk(self.project_root):
            # تجاهل المجلدات غير المهمة
            dirs[:] = [d for d in dirs if d not in [
                '.git', '__pycache__', 'node_modules', '.venv', 'venv',
                '.pytest_cache', '.mypy_cache', 'dist', 'build', '.idea'
            ]]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.analyze_python_file(file_path)
                elif file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    self.analysis_result["file_types"]["javascript"] += 1
                elif file.endswith(('.json', '.yaml', '.yml')):
                    self.analysis_result["file_types"]["config"] += 1
                    
                self.analysis_result["total_files"] += 1
        
        # إيجاد التكرارات
        self._find_duplicates()
        
        # إنشاء ملخص
        self._generate_summary()
        
        return self.analysis_result
    
    def analyze_python_file(self, file_path: str) -> None:
        """تحليل ملف Python واحد"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            self.analysis_result["total_python_files"] += 1
            
            # حساب hash للملف
            file_hash = hashlib.md5(content.encode()).hexdigest()
            self.analysis_result["file_hashes"][file_hash].append(file_path)
            
            # تحليل AST
            analysis_data = self._analyze_ast(content, file_path)
            
            # تحديد نوع الملف
            file_type = self._determine_file_type(file_path, content)
            self.analysis_result["file_types"][file_type] += 1
            
            # تحديد الأهمية
            importance = self._determine_importance(
                file_path, content, 
                analysis_data["classes"], 
                analysis_data["functions"]
            )
            
            # إيجاد المشاكل
            issues = self._find_issues(content, file_path)
            
            # اقتراح موقع أفضل
            suggested_location = self._suggest_location(file_path, file_type)
            
            # حساب معدل التعقيد
            complexity = self._calculate_complexity(analysis_data)
            
            # إنشاء تقرير الملف
            file_report = {
                "path": file_path,
                "relative_path": str(Path(file_path).relative_to(self.project_root)),
                "type": file_type,
                "importance": importance,
                "stats": {
                    "lines": len(lines),
                    "loc": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
                    "classes": len(analysis_data["classes"]),
                    "functions": len(analysis_data["functions"]),
                    "imports": len(analysis_data["imports"])
                },
                "hash": file_hash,
                "issues": issues,
                "suggested_location": suggested_location,
                "complexity": complexity,
                "dependencies": list(analysis_data["dependencies"])
            }
            
            self.analysis_result["detailed_analysis"].append(file_report)
            
            # تصنيف الملفات الخاصة
            if len(lines) == 0 or len(content.strip()) == 0:
                self.analysis_result["empty_files"].append(file_path)
            elif len(lines) > 500:
                self.analysis_result["large_files"].append((file_path, len(lines)))
            
            if file_type == "test":
                self.analysis_result["test_files"].append(file_path)
            elif file_type == "config":
                self.analysis_result["config_files"].append(file_path)
                
        except Exception as e:
            print(f"❌ خطأ في تحليل {file_path}: {e}")
    
    def _analyze_ast(self, content: str, file_path: str) -> Dict:
        """تحليل AST للملف"""
        result = {
            "imports": [],
            "classes": [],
            "functions": [],
            "dependencies": set()
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result["imports"].append(alias.name)
                        result["dependencies"].add(alias.name.split('.')[0])
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        result["imports"].append(node.module)
                        result["dependencies"].add(node.module.split('.')[0])
                        
                elif isinstance(node, ast.ClassDef):
                    result["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    })
                    
                elif isinstance(node, ast.FunctionDef):
                    # تسجيل توقيع الدالة للكشف عن التكرارات
                    args = [arg.arg for arg in node.args.args]
                    signature = f"{node.name}({','.join(args)})"
                    self.analysis_result["function_signatures"][signature].append(file_path)
                    
                    result["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": len(node.args.args),
                        "decorators": len(node.decorator_list)
                    })
                    
        except:
            pass
            
        return result
    
    def _determine_file_type(self, file_path: str, content: str) -> str:
        """تحديد نوع الملف بناءً على المحتوى والمسار"""
        path_lower = file_path.lower()
        
        # اختبارات
        if 'test_' in os.path.basename(file_path) or '_test.py' in file_path:
            return 'test'
        elif '/tests/' in file_path or '/test/' in file_path:
            return 'test'
            
        # إعدادات
        elif 'config' in path_lower or 'settings' in path_lower:
            return 'config'
            
        # نماذج البيانات
        elif any(x in path_lower for x in ['model', 'entity', 'schema']):
            return 'model'
            
        # الخدمات
        elif 'service' in path_lower or 'manager' in path_lower:
            return 'service'
            
        # المستودعات
        elif 'repository' in path_lower or 'repo' in path_lower:
            return 'repository'
            
        # واجهات API
        elif any(x in path_lower for x in ['controller', 'endpoint', 'route', 'view']):
            return 'controller'
            
        # أدوات مساعدة
        elif any(x in path_lower for x in ['util', 'helper', 'common']):
            return 'utility'
            
        # ملفات التهيئة
        elif '__init__.py' in file_path:
            return 'init'
            
        # البنية التحتية
        elif 'infrastructure' in path_lower:
            return 'infrastructure'
            
        # المجال
        elif 'domain' in path_lower:
            return 'domain'
            
        else:
            return 'other'
    
    def _determine_importance(self, file_path: str, content: str, 
                            classes: List, functions: List) -> str:
        """تحديد أهمية الملف"""
        path_lower = file_path.lower()
        
        # Critical files - ملفات حرجة
        critical_patterns = [
            'main.py', 'app.py', 'wsgi.py', '__main__.py',
            'manage.py', 'server.py'
        ]
        if any(pattern in os.path.basename(file_path) for pattern in critical_patterns):
            return 'critical'
            
        # ملفات الأمان والمصادقة
        if any(x in path_lower for x in ['security', 'auth', 'child_safety', 'encryption']):
            return 'critical'
            
        # نماذج قاعدة البيانات الأساسية
        if 'models' in path_lower and any(x in path_lower for x in ['child', 'parent', 'device']):
            return 'critical'
            
        # ملفات البنية التحتية الحرجة
        if any(x in path_lower for x in ['database', 'cache', 'queue']):
            return 'critical'
            
        # High importance - أهمية عالية
        if len(classes) > 2 or len(functions) > 5:
            return 'high'
        elif any(x in path_lower for x in ['service', 'repository', 'controller']):
            return 'high'
        elif 'api' in path_lower and 'endpoint' in path_lower:
            return 'high'
            
        # Trash - قمامة
        if len(content.strip()) == 0:
            return 'trash'
        elif any(x in os.path.basename(file_path) for x in ['_old', '_backup', '_temp', '_copy', '_bak']):
            return 'trash'
        elif 'deprecated' in path_lower or 'obsolete' in path_lower:
            return 'trash'
            
        # Low importance - أهمية منخفضة
        if len(classes) == 0 and len(functions) == 0:
            return 'low'
        elif any(x in path_lower for x in ['example', 'sample', 'demo', 'test_data']):
            return 'low'
            
        return 'medium'
    
    def _find_issues(self, content: str, file_path: str) -> List[str]:
        """إيجاد المشاكل في الملف"""
        issues = []
        
        # فحص المشاكل الأمنية
        security_patterns = [
            (r'eval\s*\(', "Uses eval() - security risk"),
            (r'exec\s*\(', "Uses exec() - security risk"),
            (r'pickle\.loads', "Uses pickle.loads - security risk"),
            (r'os\.system', "Uses os.system - use subprocess instead"),
            (r'hardcoded.*password|password\s*=\s*["\']', "Possible hardcoded password")
        ]
        
        for pattern, issue in security_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(issue)
        
        # فحص جودة الكود
        if 'except:' in content or 'except Exception:' in content:
            issues.append("Generic exception handling")
            
        if re.search(r'print\s*\(', content) and 'test' not in file_path:
            issues.append("Print statements in production code")
            
        if 'TODO' in content or 'FIXME' in content or 'XXX' in content:
            issues.append("Contains TODO/FIXME/XXX")
            
        # فحص الحجم والتعقيد
        lines = content.splitlines()
        if len(lines) > 500:
            issues.append(f"File too large ({len(lines)} lines)")
        elif len(lines) > 300:
            issues.append(f"File is getting large ({len(lines)} lines)")
            
        if len(content.strip()) == 0:
            issues.append("Empty file")
            
        # فحص الاستيرادات
        if 'from . import *' in content or 'import *' in content:
            issues.append("Uses wildcard imports")
            
        # فحص المتغيرات العامة
        if re.search(r'^[A-Z_]+\s*=\s*(?!.*\()', content, re.MULTILINE):
            if 'constant' not in file_path and 'config' not in file_path:
                issues.append("Contains global variables")
                
        return issues
    
    def _suggest_location(self, current_path: str, file_type: str) -> Optional[str]:
        """اقتراح موقع أفضل للملف"""
        type_to_location = {
            'model': 'src/core/domain/entities/',
            'service': 'src/core/services/',
            'repository': 'src/infrastructure/persistence/repositories/',
            'controller': 'src/api/endpoints/',
            'test': 'tests/',
            'config': 'configs/',
            'utility': 'src/shared/utils/',
            'domain': 'src/core/domain/',
            'infrastructure': 'src/infrastructure/'
        }
        
        suggested = type_to_location.get(file_type)
        if not suggested:
            return None
            
        # التحقق من أن الملف ليس في المكان الصحيح
        if suggested in current_path:
            return None
            
        # إنشاء اسم ملف مقترح
        filename = os.path.basename(current_path)
        return os.path.join(suggested, filename)
    
    def _calculate_complexity(self, analysis_data: Dict) -> int:
        """حساب معدل التعقيد للملف"""
        complexity = 0
        
        # تعقيد بناءً على عدد الكلاسات والدوال
        complexity += len(analysis_data["classes"]) * 2
        complexity += len(analysis_data["functions"])
        
        # تعقيد بناءً على الاستيرادات
        complexity += len(analysis_data["imports"]) // 5
        
        return complexity
    
    def _find_duplicates(self) -> None:
        """إيجاد الملفات المكررة"""
        # التكرارات الكاملة (نفس الـ hash)
        for file_hash, files in self.analysis_result["file_hashes"].items():
            if len(files) > 1:
                self.analysis_result["duplicate_candidates"].append({
                    "type": "exact",
                    "hash": file_hash,
                    "files": files
                })
        
        # التكرارات الوظيفية (نفس توقيعات الدوال)
        for signature, files in self.analysis_result["function_signatures"].items():
            if len(files) > 1:
                # تجاهل الدوال الشائعة مثل __init__
                if signature not in ['__init__(self)', '__str__(self)', '__repr__(self)']:
                    self.analysis_result["duplicate_candidates"].append({
                        "type": "functional",
                        "signature": signature,
                        "files": files
                    })
    
    def _generate_summary(self) -> None:
        """إنشاء ملخص التحليل"""
        total_python = self.analysis_result["total_python_files"]
        
        # حساب الإحصائيات
        importance_stats = defaultdict(int)
        type_stats = defaultdict(int)
        total_issues = 0
        
        for file_report in self.analysis_result["detailed_analysis"]:
            importance_stats[file_report["importance"]] += 1
            type_stats[file_report["type"]] += 1
            total_issues += len(file_report["issues"])
        
        self.analysis_result["summary"] = {
            "total_files": self.analysis_result["total_files"],
            "python_files": total_python,
            "importance_distribution": dict(importance_stats),
            "type_distribution": dict(type_stats),
            "total_issues": total_issues,
            "duplicate_groups": len(self.analysis_result["duplicate_candidates"]),
            "empty_files": len(self.analysis_result["empty_files"]),
            "large_files": len(self.analysis_result["large_files"])
        }
    
    def save_report(self, output_file: str = "project_analysis.json") -> None:
        """حفظ تقرير التحليل"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_result, f, indent=2, ensure_ascii=False)
        print(f"✅ تم حفظ التقرير في: {output_file}")
    
    def print_summary(self) -> None:
        """طباعة ملخص التحليل"""
        summary = self.analysis_result.get("summary", {})
        
        print("\n" + "="*60)
        print("📊 ملخص تحليل المشروع")
        print("="*60)
        
        print(f"\n📁 إجمالي الملفات: {summary.get('total_files', 0)}")
        print(f"🐍 ملفات Python: {summary.get('python_files', 0)}")
        
        print("\n📈 توزيع الأهمية:")
        for importance, count in summary.get('importance_distribution', {}).items():
            emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢',
                'trash': '⚫'
            }.get(importance, '⚪')
            print(f"  {emoji} {importance}: {count} ملف")
        
        print("\n📂 توزيع الأنواع:")
        for file_type, count in summary.get('type_distribution', {}).items():
            print(f"  • {file_type}: {count} ملف")
        
        print(f"\n⚠️  إجمالي المشاكل المكتشفة: {summary.get('total_issues', 0)}")
        print(f"🔄 مجموعات الملفات المكررة: {summary.get('duplicate_groups', 0)}")
        print(f"📄 الملفات الفارغة: {summary.get('empty_files', 0)}")
        print(f"📦 الملفات الكبيرة: {summary.get('large_files', 0)}")


def main():
    """تشغيل المحلل"""
    analyzer = ProjectAnalyzer()
    
    print("🚀 بدء تحليل مشروع AI Teddy Bear...")
    print("⏳ قد يستغرق هذا بعض الوقت...")
    
    # تحليل المشروع
    result = analyzer.analyze_project()
    
    # طباعة الملخص
    analyzer.print_summary()
    
    # حفظ التقرير المفصل
    analyzer.save_report("project_analysis.json")
    
    # حفظ تقرير مبسط للمراجعة السريعة
    with open("analysis_summary.md", "w", encoding="utf-8") as f:
        f.write("# تقرير تحليل مشروع AI Teddy Bear\n\n")
        f.write(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        summary = result.get("summary", {})
        f.write("## 📊 الإحصائيات العامة\n\n")
        f.write(f"- إجمالي الملفات: {summary.get('total_files', 0)}\n")
        f.write(f"- ملفات Python: {summary.get('python_files', 0)}\n")
        f.write(f"- المشاكل المكتشفة: {summary.get('total_issues', 0)}\n")
        f.write(f"- الملفات المكررة: {summary.get('duplicate_groups', 0)} مجموعة\n\n")
        
        f.write("## ⚫ الملفات التي يجب حذفها فوراً\n\n")
        trash_files = [f for f in result["detailed_analysis"] if f["importance"] == "trash"]
        for file in trash_files[:20]:  # أول 20 ملف فقط
            f.write(f"- `{file['relative_path']}`: {', '.join(file['issues'])}\n")
        
        if len(trash_files) > 20:
            f.write(f"\n... و {len(trash_files) - 20} ملف آخر\n")
    
    print("\n✅ تم إنشاء التقارير:")
    print("  • project_analysis.json - التقرير المفصل")
    print("  • analysis_summary.md - ملخص للمراجعة السريعة")


if __name__ == "__main__":
    main() 